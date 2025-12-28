import json

import stripe


def test_webhook_creates_or_updates_checkout_record(
    monkeypatch,
    client,
    fetch_checkout_records,
):
    event_payload = {
        'type': 'checkout.session.completed',
        'data': {
            'object': {
                'id': 'cs_evt_123',
                'payment_status': 'paid',
                'customer_details': {'email': 'webhook@example.com'},
            }
        },
    }

    def fake_construct_event(payload, signature, secret):
        assert signature == 'sig_header'
        # The view should pass the configured endpoint secret through.
        assert secret == 'whsec_test_checkout'
        raw = payload.decode() if isinstance(payload, (bytes, bytearray)) else payload
        assert json.loads(raw) == event_payload
        return event_payload

    monkeypatch.setattr(
        stripe.Webhook,
        'construct_event',
        staticmethod(fake_construct_event),
    )

    response = client.post(
        '/stripe/webhook',
        data=json.dumps(event_payload),
        headers={'Stripe-Signature': 'sig_header'},
        content_type='application/json',
    )
    assert response.status_code == 200

    rows = fetch_checkout_records('cs_evt_123')
    assert len(rows) == 1
    row = rows[0]
    assert row['session_id'] == 'cs_evt_123'
    assert row['customer_email'] == 'webhook@example.com'
    assert row['payment_status'] == 'paid'


def test_webhook_bad_signature_returns_400(monkeypatch, client):
    def fake_construct_event(*args, **kwargs):
        raise stripe.error.SignatureVerificationError(
            message='invalid signature',
            sig_header='sig_bad',
        )

    monkeypatch.setattr(
        stripe.Webhook,
        'construct_event',
        staticmethod(fake_construct_event),
    )

    response = client.post(
        '/stripe/webhook',
        data='{}',
        headers={'Stripe-Signature': 'sig_bad'},
        content_type='application/json',
    )
    assert response.status_code == 400
