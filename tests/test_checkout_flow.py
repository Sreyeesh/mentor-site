from io import BytesIO
from types import SimpleNamespace
from urllib import error as urllib_error

import app as app_module
import stripe


CALENDLY_LINK = 'https://calendly.com/toucan-sg/consulting-link'


def test_tutoring_page_contains_cta(client):
    response = client.get('/tutoring')
    assert response.status_code == 200
    assert 'Book the €15 session' in response.get_data(as_text=True)


def test_create_checkout_session_redirects(monkeypatch, client):
    captured = {}
    fake_session = SimpleNamespace(
        id='cs_test_123',
        url='https://test.stripe.local/checkout/cs_test_123',
    )

    def fake_create(**kwargs):
        captured['kwargs'] = kwargs
        return fake_session

    monkeypatch.setattr(
        stripe.checkout.Session,
        'create',
        staticmethod(fake_create),
    )

    response = client.post(
        '/create-checkout-session',
        json={'customer_email': 'learner@example.com'},
    )
    assert response.status_code in (302, 303)
    assert response.headers['Location'] == fake_session.url

    params = captured['kwargs']
    assert params['mode'] == 'payment'
    line_item = params['line_items'][0]
    price_data = line_item.get('price_data', {})
    assert price_data.get('unit_amount') == 1500
    assert price_data.get('currency', '').lower() == 'eur'
    assert '{CHECKOUT_SESSION_ID}' in params['success_url']


def test_schedule_requires_session_id(client):
    response = client.get('/schedule')
    assert response.status_code == 400
    assert 'session_id' in response.get_data(as_text=True).lower()


def test_schedule_invalid_session_shows_error(monkeypatch, client):
    def fake_retrieve(session_id):
        raise stripe.error.InvalidRequestError(
            message='No such checkout session',
            param='session_id',
        )

    monkeypatch.setattr(
        stripe.checkout.Session,
        'retrieve',
        staticmethod(fake_retrieve),
    )

    response = client.get('/schedule?session_id=missing')
    body = response.get_data(as_text=True)
    assert response.status_code in (400, 500)
    assert 'error' in body.lower()
    assert '<iframe' not in body.lower()


def test_schedule_valid_session_shows_calendly(
    monkeypatch,
    client,
    fetch_checkout_records,
):
    retrieved = {
        'id': 'cs_paid_123',
        'status': 'complete',
        'payment_status': 'paid',
        'customer_details': {'email': 'paid@example.com'},
    }

    def fake_retrieve(session_id):
        assert session_id == retrieved['id']
        return retrieved

    monkeypatch.setattr(
        stripe.checkout.Session,
        'retrieve',
        staticmethod(fake_retrieve),
    )

    response = client.get(f"/schedule?session_id={retrieved['id']}")
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert 'Payment received' in body
    assert CALENDLY_LINK in body

    rows = fetch_checkout_records(retrieved['id'])
    assert len(rows) == 1
    row = rows[0]
    assert row['session_id'] == retrieved['id']
    assert row['customer_email'] == retrieved['customer_details']['email']
    assert row['payment_status'] == retrieved['payment_status']


def test_stripe_checkout_session_redirects(monkeypatch, client):
    fake_url = 'https://checkout.stripe.test/cs_123'

    def fake_call(params):
        assert isinstance(params, list)
        return {'url': fake_url}

    monkeypatch.setattr(
        app_module,
        '_create_stripe_checkout_session',
        fake_call,
    )

    response = client.post('/stripe/create-checkout-session/')
    assert response.status_code == 303
    assert response.headers['Location'] == fake_url


def test_stripe_checkout_session_http_error(monkeypatch, client):
    def fake_call(params):
        body = BytesIO(b'{"error":{"message":"Bad"}}')
        raise urllib_error.HTTPError(
            url='https://stripe.test',
            code=400,
            msg='Bad request',
            hdrs=None,
            fp=body,
        )

    monkeypatch.setattr(
        app_module,
        '_create_stripe_checkout_session',
        fake_call,
    )

    response = client.post('/stripe/create-checkout-session/')
    assert response.status_code == 400
    assert 'bad' in response.get_data(as_text=True).lower()


def test_stripe_checkout_session_missing_url(monkeypatch, client):
    monkeypatch.setattr(
        app_module,
        '_create_stripe_checkout_session',
        lambda params: {},
    )

    response = client.post('/stripe/create-checkout-session/')
    assert response.status_code == 502
