from django.conf import settings
from stripe import StripeClient


def create_checkout(*, course, amount):
    """Создаёт продукт, цену и сессию Stripe Checkout."""

    client = StripeClient(settings.STRIPE_SECRET_KEY, max_network_retries=2)

    product = client.v1.products.create({"name": course.title})

    price = client.v1.prices.create(
        {
            "product": product.id,
            "currency": "rub",
            "unit_amount": int(amount * 100),
        }
    )

    session = client.v1.checkout.sessions.create(
        {
            "mode": "payment",
            "line_items": [{"price": price.id, "quantity": 1}],
            "success_url": settings.STRIPE_SUCCESS_URL,
            "cancel_url": settings.STRIPE_CANCEL_URL,
            "payment_method_types": ["card"],
        }
    )

    return {
        "stripe_product_id": product.id,
        "stripe_price_id": price.id,
        "stripe_session_id": session.id,
        "payment_url": session.url,
    }


def retrieve_checkout(*, session_id):
    """Читает состояние созданной сессии из Stripe."""

    client = StripeClient(settings.STRIPE_SECRET_KEY, max_network_retries=2)
    session = client.v1.checkout.sessions.retrieve(session_id)

    return {
        "status": session.status,
        "payment_status": session.payment_status,
    }
