import json
import os
from datetime import datetime
from urllib import error as urllib_error
from urllib import parse as urllib_parse
from urllib import request as urllib_request

from dotenv import load_dotenv
from flask import (
    Flask,
    abort,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    url_for,
)
import stripe

import db


def _load_environment() -> None:
    """Load variables from the appropriate .env file.

    Precedence:
        1. ENV_FILE override
        2. .env.dev when FLASK_ENV/APP_ENV indicates development
        3. .env
        4. Fallback to dotenv defaults
    """

    env_file = os.getenv('ENV_FILE')
    env_hint = os.getenv('APP_ENV') or os.getenv('FLASK_ENV')

    if not env_file and env_hint:
        if env_hint.lower().startswith('dev') and os.path.exists('.env.dev'):
            env_file = '.env.dev'

    if not env_file:
        if os.path.exists('.env'):
            env_file = '.env'
        elif os.path.exists('.env.dev'):
            env_file = '.env.dev'

    load_dotenv(env_file)


_load_environment()


def _env(key: str, default: str = '') -> str:
    """Return a stripped environment value with an optional default."""

    value = os.getenv(key)
    if value is None:
        return default
    return value.strip()


BASE_PATH = _env('BASE_PATH')
if BASE_PATH and not BASE_PATH.startswith('/'):
    BASE_PATH = f"/{BASE_PATH}"
LEGACY_BASE_PATH = '/mentor-site'

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
from blog import find_post, load_posts, normalize_media_path  # noqa: E402


class BasePathMiddleware:
    """Allow serving the Flask app under a sub-path when BASE_PATH is set."""

    def __init__(self, wsgi_app, base_path: str):
        self.wsgi_app = wsgi_app
        self.base_path = base_path

    def __call__(self, environ, start_response):
        base_path = self.base_path
        if not base_path:
            return self.wsgi_app(environ, start_response)

        path_info = environ.get('PATH_INFO', '')
        if path_info.startswith(base_path):
            trimmed = path_info[len(base_path):]
            environ['PATH_INFO'] = trimmed or '/'
        return self.wsgi_app(environ, start_response)


SITE_CONFIG = {
    'name': os.getenv('SITE_NAME', 'Sreyeesh Garimella'),
    'tagline': os.getenv(
        'SITE_TAGLINE',
        'Technical Art, Direction & Game Dev Tutoring',
    ),
    'email': os.getenv('SITE_EMAIL', 'toucan.sg@gmail.com'),
    'calendly_link': os.getenv(
        'SITE_CALENDLY_LINK',
        'https://calendly.com/toucan-sg/consulting-link',
    ),
    'site_url': os.getenv('SITE_URL', '').rstrip('/'),
    'meta_description': os.getenv(
        'SITE_META_DESCRIPTION',
        (
            'Mentorship for technical artists, developers, and studios — '
            'tutoring in Unreal Engine workflows and creative pipelines that '
            'ship products faster.'
        ),
    ),
    'focus_areas': os.getenv(
        'SITE_FOCUS_AREAS',
        (
            'Technical art & tools tutoring,Art direction & cinematic '
            'feedback,Game development & Unreal mentoring,Pipeline programming '
            'and automation coaching'
        ),
    ).split(','),
    'asset_version': _env('ASSET_VERSION', '1'),
    'plausible_script_url': _env('PLAUSIBLE_SCRIPT_URL'),
    'plausible_domain': _env('PLAUSIBLE_DOMAIN'),
    'stripe_publishable_key': _env('STRIPE_PUBLISHABLE_KEY'),
    'stripe_price_id': _env('STRIPE_PRICE_ID'),
    'stripe_payment_link': _env(
        'STRIPE_PAYMENT_LINK', 'https://book.stripe.com/00w28kbMX8C15Q43qj4F203'
    ),
    'social_image': _env('SITE_SOCIAL_IMAGE', 'images/SreyeeshProfilePic.jpg'),
    'backend_base_url': _env('BACKEND_BASE_URL', '').rstrip('/'),
}

STRIPE_SECRET_KEY = _env('STRIPE_SECRET_KEY')
STRIPE_PRICE_ID = SITE_CONFIG['stripe_price_id']
STRIPE_SUCCESS_URL = _env('STRIPE_SUCCESS_URL')
STRIPE_CANCEL_URL = _env('STRIPE_CANCEL_URL')
STRIPE_API_BASE = 'https://api.stripe.com/v1'
STRIPE_ENDPOINT_SECRET = _env('STRIPE_ENDPOINT_SECRET')
ONE_OFF_PRICE_AMOUNT = 1500
ONE_OFF_CURRENCY = 'eur'
SITE_CONFIG['stripe_checkout_enabled'] = bool(
    STRIPE_SECRET_KEY and STRIPE_PRICE_ID
)
BACKEND_BASE_URL = SITE_CONFIG['backend_base_url']

if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY

db.init_db()


def _normalize_base_path(raw: str | None) -> str:
    if not raw:
        return ''
    raw = raw.strip()
    if not raw:
        return ''
    if not raw.startswith('/'):
        raw = f"/{raw}"
    normalized = raw.rstrip('/')
    if normalized == '':
        return ''
    return normalized


def configure_base_path(raw: str | None) -> None:
    normalized = _normalize_base_path(raw)
    app.config['SITE_BASE_PATH'] = normalized
    original_wsgi = app.config.setdefault('_ORIGINAL_WSGI_APP', app.wsgi_app)
    if normalized:
        app.wsgi_app = BasePathMiddleware(original_wsgi, normalized)
    else:
        app.wsgi_app = original_wsgi


configure_base_path(BASE_PATH)


@app.before_request
def _redirect_legacy_base_path():
    """Redirect /mentor-site/* requests when no base path is configured."""

    if _resolve_base_path():
        return

    fallback = LEGACY_BASE_PATH.rstrip('/')
    if not fallback:
        return

    path = request.path or '/'
    if not path.startswith(fallback):
        return

    remainder = path[len(fallback):] or '/'
    query_string = request.query_string.decode('utf-8')
    if query_string:
        remainder = f"{remainder}?{query_string}"
    return redirect(remainder, code=302)


def _resolve_base_path(override: str | None = None) -> str:
    if override is not None:
        return _normalize_base_path(override)
    return app.config.get('SITE_BASE_PATH', '')


def build_site_links(base_path_override: str | None = None) -> dict:
    base_path_value = _resolve_base_path(base_path_override)

    def prefix(path: str) -> str:
        if path == '/':
            return f"{base_path_value}/" if base_path_value else '/'
        if base_path_value:
            return f"{base_path_value}{path}"
        return path

    return {
        'home': prefix('/'),
        'mentoring': prefix('/mentoring/'),
        'schools': prefix('/schools-and-programs/'),
        'about': prefix('/about/'),
        'blog': prefix('/blog/'),
        'contact': prefix('/contact/'),
    }


def build_primary_nav(base_path_override: str | None = None) -> list:
    links = build_site_links(base_path_override)
    return [
        {'label': 'Home', 'href': links['home']},
        {'label': 'About', 'href': links['about']},
        {'label': 'Blog', 'href': links['blog']},
    ]


def _build_backend_endpoint(endpoint: str, **values) -> str:
    relative_url = url_for(endpoint, **values)
    if BACKEND_BASE_URL:
        return f"{BACKEND_BASE_URL}{relative_url}"
    site_url = SITE_CONFIG.get('site_url', '').rstrip('/')
    if site_url:
        return f"{site_url}{relative_url}"
    return relative_url


def build_checkout_endpoints() -> dict:
    return {
        'subscription': _build_backend_endpoint(
            'stripe_create_checkout_session'
        ),
        'one_time': _build_backend_endpoint('create_checkout_session'),
    }


def _build_canonical_url(base_path_value: str) -> str:
    site_url = SITE_CONFIG.get('site_url', '').rstrip('/')
    request_path = request.path or '/'
    if base_path_value and not request_path.startswith(base_path_value):
        if request_path == '/':
            request_path = f"{base_path_value}/"
        else:
            request_path = f"{base_path_value}{request_path}"
    if site_url:
        return f"{site_url}{request_path}"
    return f"{request.url_root.rstrip('/')}{request_path}"


def _build_social_image_url() -> str:
    social_image = SITE_CONFIG.get('social_image') or ''
    if social_image.startswith('http://') or social_image.startswith('https://'):
        return social_image
    image_path = social_image or 'images/SreyeeshProfilePic.jpg'
    asset_path = url_for('static', filename=image_path)
    site_url = SITE_CONFIG.get('site_url', '').rstrip('/')
    if site_url:
        return f"{site_url}{asset_path}"
    return url_for('static', filename=image_path, _external=True)


def build_page_context(
    *,
    base_path_override: str | None = None,
    **extra: object,
) -> dict:
    base_path_value = _resolve_base_path(base_path_override)
    canonical_url = _build_canonical_url(base_path_value)
    social_image_url = _build_social_image_url()
    context = {
        'config': SITE_CONFIG,
        'current_year': datetime.now().year,
        'base_path': base_path_value,
        'site_links': build_site_links(base_path_override),
        'nav_links': build_primary_nav(base_path_override),
        'checkout_endpoints': build_checkout_endpoints(),
        'canonical_url': canonical_url,
        'social_image_url': social_image_url,
    }
    context.update(extra)
    return context


def build_absolute_url(path: str) -> str:
    """Return a fully qualified URL for sitemap/robots usage."""

    site_url = SITE_CONFIG.get('site_url', '').rstrip('/')
    normalized_path = path if path.startswith('/') else f"/{path}"
    if site_url:
        return f"{site_url}{normalized_path}"
    base = request.url_root.rstrip('/')
    return f"{base}{normalized_path}"


def _create_stripe_checkout_session(body_params: list[tuple[str, str]]) -> dict:
    """Create a Checkout Session using Stripe's REST API."""

    if not STRIPE_SECRET_KEY:
        raise RuntimeError('Stripe secret key is not configured.')

    encoded = urllib_parse.urlencode(body_params).encode()
    request_obj = urllib_request.Request(
        f"{STRIPE_API_BASE}/checkout/sessions",
        data=encoded,
        method='POST',
    )
    request_obj.add_header('Authorization', f"Bearer {STRIPE_SECRET_KEY}")
    request_obj.add_header(
        'Content-Type',
        'application/x-www-form-urlencoded',
    )
    with urllib_request.urlopen(request_obj) as response:  # nosec: B310
        payload = response.read().decode('utf-8')
    return json.loads(payload)


@app.route('/')
def home():
    return render_template('home.html', **build_page_context(page_slug='home'))


@app.route('/mentoring/')
def mentoring():
    return render_template(
        'mentoring.html',
        **build_page_context(page_slug='mentoring'),
    )


@app.route('/schools-and-programs/')
def schools_and_programs():
    return render_template(
        'schools-and-programs.html',
        **build_page_context(page_slug='schools'),
    )


@app.route('/about/')
def about():
    return render_template(
        'about.html',
        **build_page_context(page_slug='about'),
    )


@app.route('/contact/')
def contact():
    return render_template(
        'contact.html',
        **build_page_context(page_slug='contact'),
    )


@app.route('/blog/')
def blog_index():
    posts = load_posts()
    links = build_site_links()
    return render_template(
        'blog/list.html',
        **build_page_context(
            page_slug='blog',
            posts=posts,
            home_href=links['home'],
            blog_index_href=links['blog'],
        ),
    )


@app.route('/blog/<slug>/')
def blog_detail(slug: str):
    posts = load_posts()
    post = find_post(slug, posts=posts)
    if post is None:
        abort(404)

    links = build_site_links()
    detail_path = f"{links['blog']}{post['slug']}/"

    site_url = SITE_CONFIG.get('site_url', '').rstrip('/')
    if site_url:
        canonical_url = f"{site_url}{detail_path}"
    else:
        canonical_url = request.base_url

    hero_value, is_external = normalize_media_path(post.get('hero_image'))
    hero_asset_path = None
    hero_image_url = None
    if hero_value:
        if is_external:
            hero_image_url = hero_value
        else:
            hero_asset_path = url_for('static', filename=hero_value)
            hero_image_url = (
                f"{site_url}{hero_asset_path}"
                if site_url
                else url_for('static', filename=hero_value, _external=True)
            )

    return render_template(
        'blog/detail.html',
        **build_page_context(
            page_slug='blog',
            post=post,
            posts=posts,
            home_href=links['home'],
            blog_index_href=links['blog'],
            canonical_url=canonical_url,
            hero_image_url=hero_image_url,
            social_image_url=hero_image_url or _build_social_image_url(),
        ),
    )


@app.route('/sitemap.xml')
def sitemap():
    posts = load_posts()
    links = build_site_links()
    urls = []

    static_pages = [
        links['home'],
        links['mentoring'],
        links['schools'],
        links['about'],
        links['blog'],
        links['contact'],
    ]

    for page in static_pages:
        urls.append(
            {
                'loc': build_absolute_url(page),
                'lastmod': datetime.utcnow().date().isoformat(),
                'changefreq': 'weekly',
            }
        )

    for post in posts:
        post_path = f"{links['blog']}{post['slug']}/"
        last_modified = post.get('updated_at') or post.get('date')
        urls.append(
            {
                'loc': build_absolute_url(post_path),
                'lastmod': last_modified,
                'changefreq': 'monthly',
            }
        )

    response = make_response(
        render_template('sitemap.xml', urls=urls),
    )
    response.headers['Content-Type'] = 'application/xml'
    return response


@app.route('/robots.txt')
def robots_txt():
    lines = [
        "User-agent: *",
        "Allow: /",
        f"Sitemap: {build_absolute_url('/sitemap.xml')}",
    ]
    response = make_response("\n".join(lines) + "\n")
    response.headers['Content-Type'] = 'text/plain'
    return response


@app.route('/stripe/create-checkout-session/', methods=['GET', 'POST'])
def stripe_create_checkout_session():
    if request.method != 'POST':
        mentoring_url = build_absolute_url(url_for('mentoring'))
        return redirect(mentoring_url, code=302)

    if not STRIPE_SECRET_KEY or not STRIPE_PRICE_ID:
        abort(404)

    payload = request.get_json(silent=True) if request.is_json else request.form
    payload = payload or {}
    price_id = payload.get('price_id') or STRIPE_PRICE_ID
    customer_email = payload.get('customer_email') or None

    mentoring_path = url_for('mentoring')
    success_url = payload.get('success_url') or STRIPE_SUCCESS_URL
    cancel_url = payload.get('cancel_url') or STRIPE_CANCEL_URL

    if not success_url:
        success_url = build_absolute_url(f"{mentoring_path}?checkout=success")
    if not cancel_url:
        cancel_url = build_absolute_url(f"{mentoring_path}?checkout=cancelled")

    body_params = [
        ('mode', 'subscription'),
        ('allow_promotion_codes', 'true'),
        ('automatic_tax[enabled]', 'true'),
        ('line_items[0][price]', price_id),
        ('line_items[0][quantity]', '1'),
        ('success_url', success_url),
        ('cancel_url', cancel_url),
    ]
    if customer_email:
        body_params.append(('customer_email', customer_email))

    try:
        session = _create_stripe_checkout_session(body_params)
    except urllib_error.HTTPError as exc:
        message = exc.reason
        try:
            error_payload = json.loads(exc.read().decode('utf-8'))
            message = (
                error_payload.get('error', {}).get('message')
                or message
                or 'Unable to contact Stripe.'
            )
        except Exception:
            message = message or 'Unable to contact Stripe.'
        if request.is_json:
            return jsonify({'error': message}), exc.code
        abort(exc.code or 502, description=message)
    except Exception as exc:  # pragma: no cover - defensive
        message = str(exc)
        if request.is_json:
            return jsonify({'error': message}), 400
        abort(502, description=message)

    checkout_url = session.get('url')
    if not checkout_url:
        missing_url_msg = 'Stripe response was missing a redirect URL.'
        if request.is_json:
            return jsonify({'error': missing_url_msg}), 500
        abort(502, description=missing_url_msg)

    if request.is_json:
        return jsonify({'url': checkout_url})
    return redirect(checkout_url, code=303)


@app.route('/tutoring')
def tutoring():
    return render_template(
        'tutoring.html',
        **build_page_context(page_slug='tutoring'),
    )


def _build_success_url() -> str:
    if STRIPE_SUCCESS_URL:
        return STRIPE_SUCCESS_URL
    base = url_for('schedule', _external=True)
    return f"{base}?session_id={{CHECKOUT_SESSION_ID}}"


def _build_cancel_url() -> str:
    if STRIPE_CANCEL_URL:
        return STRIPE_CANCEL_URL
    return url_for('tutoring', _external=True)


@app.route('/create-checkout-session', methods=['GET', 'POST'])
def create_checkout_session():
    if request.method != 'POST':
        mentoring_url = build_absolute_url(url_for('mentoring'))
        return redirect(mentoring_url, code=302)

    if not STRIPE_SECRET_KEY:
        abort(500, description='Stripe not configured.')

    payload = request.get_json(silent=True) or request.form or {}
    customer_email = payload.get('customer_email')

    session = stripe.checkout.Session.create(
        mode='payment',
        line_items=[
            {
                'quantity': 1,
                'price_data': {
                    'currency': ONE_OFF_CURRENCY,
                    'unit_amount': ONE_OFF_PRICE_AMOUNT,
                    'product_data': {
                        'name': '1:1 Tutoring Session',
                        'description': 'One-off mentoring session',
                    },
                },
            }
        ],
        success_url=_build_success_url(),
        cancel_url=_build_cancel_url(),
        customer_email=customer_email,
    )
    response = redirect(session.url, code=303)
    if request.is_json:
        response.headers['X-Checkout-URL'] = session.url
    return response


PREVIEW_MODE_MESSAGE = (
    'Access confirmed. Book your session below.'
)


@app.route('/schedule/')
@app.route('/schedule')
def schedule():
    session_id = request.args.get('session_id')
    preview_mode = (request.args.get('preview') or '').lower() in {
        '1',
        'true',
        'yes',
    }
    if not session_id:
        if app.debug or preview_mode:
            return render_template(
                'schedule.html',
                **build_page_context(
                    page_slug='schedule',
                    show_calendly=True,
                    message=PREVIEW_MODE_MESSAGE,
                    error=None,
                    calendly_link=SITE_CONFIG['calendly_link'],
                    session_id=None,
                ),
            )
        return (
            render_template(
                'schedule.html',
                **build_page_context(
                    page_slug='schedule',
                    error='Missing session_id parameter.',
                    show_calendly=False,
                ),
            ),
            400,
        )

    try:
        checkout_session = stripe.checkout.Session.retrieve(session_id)
    except Exception:
        if preview_mode:
            return render_template(
                'schedule.html',
                **build_page_context(
                    page_slug='schedule',
                    show_calendly=True,
                    message=PREVIEW_MODE_MESSAGE,
                    error=None,
                    calendly_link=SITE_CONFIG['calendly_link'],
                    session_id=session_id,
                ),
            )
        return (
            render_template(
                'schedule.html',
                **build_page_context(
                    page_slug='schedule',
                    error='Unable to verify your payment. Please contact support.',
                    show_calendly=False,
                ),
            ),
            400,
        )

    customer_email = None
    customer_details = checkout_session.get('customer_details') or {}
    if isinstance(customer_details, dict):
        customer_email = customer_details.get('email')

    payment_status = checkout_session.get('payment_status') or checkout_session.get(
        'status'
    )
    db.upsert_checkout_session(
        session_id,
        customer_email=customer_email,
        payment_status=payment_status,
    )

    is_paid = (payment_status or '').lower() in {'paid', 'complete'}
    if preview_mode:
        is_paid = True
    elif is_paid and not db.claim_schedule_access(session_id):
        return (
            render_template(
                'schedule.html',
                **build_page_context(
                    page_slug='schedule',
                    error=(
                        'This scheduling link has already been used. '
                        'Please contact support for help.'
                    ),
                    show_calendly=False,
                ),
            ),
            410,
        )

    return render_template(
        'schedule.html',
        **build_page_context(
            page_slug='schedule',
            show_calendly=is_paid,
            message=(
                'Payment received'
                if is_paid and not preview_mode
                else (
                    PREVIEW_MODE_MESSAGE
                    if preview_mode
                    else 'Waiting for payment confirmation.'
                )
            ),
            error=None if is_paid else None,
            calendly_link=SITE_CONFIG['calendly_link'],
            session_id=session_id,
        ),
    )


@app.route('/stripe/webhook', methods=['POST'])
def stripe_webhook():
    if not STRIPE_ENDPOINT_SECRET:
        abort(500, description='Stripe webhook secret is not configured.')

    payload = request.data
    sig_header = request.headers.get('Stripe-Signature', '')

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            STRIPE_ENDPOINT_SECRET,
        )
    except ValueError:
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError:
        return 'Invalid signature', 400

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        customer_details = session.get('customer_details') or {}
        db.upsert_checkout_session(
            session['id'],
            customer_email=customer_details.get('email'),
            payment_status=session.get('payment_status'),
        )

    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

    app.run(host=host, port=port, debug=debug)
