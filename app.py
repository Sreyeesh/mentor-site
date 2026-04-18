import os
from datetime import datetime

from dotenv import load_dotenv
from flask import (
    Flask, abort, make_response, redirect, render_template, request, url_for,
)
from flask_migrate import Migrate

if os.getenv('APP_ENV', '').startswith('dev') and os.path.exists('.env.dev'):
    load_dotenv('.env.dev')
else:
    load_dotenv()

POSTS_PER_PAGE = 10
app = Flask(__name__)
app.config.update(
    TEMPLATES_AUTO_RELOAD=True,
    SECRET_KEY=os.getenv('SECRET_KEY', 'dev-secret-change-me'),
    SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URL', 'sqlite:///blog.db'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)
SITE_CONFIG = {
    'name': os.getenv('SITE_NAME', 'Sreyeesh Garimella'),
    'tagline': os.getenv('SITE_TAGLINE', 'Senior Full-Stack Developer & Mentor'),
    'email': os.getenv('SITE_EMAIL', 'toucan.sg@gmail.com'),
    'site_url': os.getenv('SITE_URL', '').rstrip('/'),
    'meta_description': os.getenv(
        'SITE_META_DESCRIPTION',
        'Senior developer and mentor writing about software and building things.',
    ),
    'asset_version': os.getenv('ASSET_VERSION', '1'),
    'plausible_script_url': os.getenv('PLAUSIBLE_SCRIPT_URL', ''),
    'plausible_domain': os.getenv('PLAUSIBLE_DOMAIN', ''),
    'social_image': os.getenv('SITE_SOCIAL_IMAGE', 'images/SreyeeshProfilePic.jpg'),
}

from models import Post, db  # noqa: E402
from admin import init_admin  # noqa: E402
from blog import normalize_media_path  # noqa: E402

db.init_app(app)
Migrate(app, db)
init_admin(app)


def ctx(**kw):
    su = SITE_CONFIG['site_url']
    si = SITE_CONFIG['social_image']
    soc = si if si.startswith('http') else f"{su}/static/{si}"
    return {
        'config': SITE_CONFIG, 'current_year': datetime.now().year,
        'nav_links': [{'label': 'Blog', 'href': '/blog/'}],
        'site_links': {'home': '/', 'blog': '/blog/'},
        'blog_index_href': '/blog/',
        'canonical_url': request.url, 'social_image_url': soc,
        **kw,
    }


@app.route('/')
def home():
    return redirect(url_for('blog_index'), 301)


@app.route('/blog/')
def blog_index():
    page = request.args.get('page', 1, type=int)
    if page < 1:
        abort(404)
    pag = Post.query.filter_by(draft=False).order_by(Post.date.desc()).paginate(
        page=page, per_page=POSTS_PER_PAGE, error_out=False)
    if page > 1 and not pag.items:
        abort(404)
    return render_template('blog/list.html', **ctx(posts=pag.items, pagination=pag))


@app.route('/blog/page/<int:page>/')
def blog_page(page):
    if page < 2:
        return redirect(url_for('blog_index'), 301)
    pag = Post.query.filter_by(draft=False).order_by(Post.date.desc()).paginate(
        page=page, per_page=POSTS_PER_PAGE, error_out=False)
    if not pag.items:
        abort(404)
    return render_template('blog/list.html', **ctx(posts=pag.items, pagination=pag))


@app.route('/blog/<slug>/')
def blog_detail(slug):
    post = Post.query.filter_by(slug=slug, draft=False).first_or_404()
    related = Post.query.filter(Post.draft.is_(False), Post.slug != slug).order_by(
        Post.date.desc()).limit(3).all()
    val, is_ext = normalize_media_path(post.hero_image)
    hero = val if is_ext else (
        url_for('static', filename=val, _external=True) if val else None
    )
    su = SITE_CONFIG['site_url']
    return render_template('blog/detail.html', **ctx(
        post=post, related_posts=related, hero_image_url=hero,
        hero_asset_path=None if is_ext else val,
        canonical_url=f"{su}/blog/{slug}/" if su else request.base_url,
        social_image_url=hero or ctx()['social_image_url'],
    ))


@app.route('/blog/tag/<tag>/')
def blog_tag(tag):
    tag = tag.strip().lower()
    posts = [p for p in Post.query.filter_by(draft=False).all()
             if tag in [t.lower() for t in p.tag_list()]]
    return render_template('blog/tag.html', **ctx(posts=posts, tag=tag))


@app.route('/feed.xml')
def feed():
    posts = Post.query.filter_by(draft=False).order_by(Post.date.desc()).limit(20).all()
    su = SITE_CONFIG['site_url']
    r = make_response(render_template(
        'feed.xml', posts=posts, blog_href=f"{su}/blog/",
        site_url=su, config=SITE_CONFIG, now=datetime.utcnow()))
    r.headers['Content-Type'] = 'application/rss+xml; charset=utf-8'
    return r


@app.route('/sitemap.xml')
def sitemap():
    posts = Post.query.filter_by(draft=False).order_by(Post.date.desc()).all()
    su, today = SITE_CONFIG['site_url'], datetime.utcnow().date().isoformat()
    urls = [{'loc': f"{su}/blog/", 'lastmod': today,
             'changefreq': 'daily', 'priority': '1.0'}]
    for p in posts:
        lm = p.updated_at or p.date
        lm = lm.date() if hasattr(lm, 'date') else lm
        urls.append({'loc': f"{su}/blog/{p.slug}/", 'lastmod': lm,
                     'changefreq': 'monthly', 'priority': '0.8'})
    for t in sorted({t for p in posts for t in p.tag_list()}):
        urls.append({'loc': f"{su}/blog/tag/{t}/", 'lastmod': today,
                     'changefreq': 'weekly', 'priority': '0.5'})
    r = make_response(render_template('sitemap.xml', urls=urls))
    r.headers['Content-Type'] = 'application/xml'
    return r


@app.route('/robots.txt')
def robots_txt():
    su = SITE_CONFIG['site_url']
    r = make_response(f"User-agent: *\nAllow: /\nSitemap: {su}/sitemap.xml\n")
    r.headers['Content-Type'] = 'text/plain'
    return r


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host=os.getenv('HOST', '0.0.0.0'), port=int(os.getenv('PORT', 5000)),
            debug=os.getenv('FLASK_DEBUG', 'True').lower() == 'true')
