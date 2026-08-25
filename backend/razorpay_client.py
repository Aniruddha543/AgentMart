"""
Razorpay test-mode wrapper. Two guardrails live here, not just in the
prompt, so a prompt-injected agent can't talk its way past them:

  - MAX_ORDER_PAISE is a hard ceiling enforced in code before any API call.
  - Every order is created with a receipt derived from (session_id, cart
    hash) so a retried tool call can't silently double-charge.
"""
import os
import hashlib
import razorpay

MAX_ORDER_PAISE = int(os.getenv("MAX_ORDER_PAISE", "2000000"))


class OrderTooLargeError(Exception):
    pass


def _client() -> razorpay.Client:
    key_id = os.getenv("RAZORPAY_KEY_ID")
    key_secret = os.getenv("RAZORPAY_KEY_SECRET")
    if not key_id or not key_secret:
        raise RuntimeError("RAZORPAY_KEY_ID / RAZORPAY_KEY_SECRET not set (test mode keys required).")
    client = razorpay.Client(auth=(key_id, key_secret))
    return client


def receipt_for(session_id: str, items: list[dict]) -> str:
    """Deterministic receipt = idempotency key. Same cart -> same receipt."""
    basis = session_id + "|" + "|".join(f"{i['product_id']}:{i['qty']}" for i in items)
    return "chk_" + hashlib.sha256(basis.encode()).hexdigest()[:20]


def create_order(session_id: str, amount_paise: int, items: list[dict]) -> dict:
    if amount_paise <= 0:
        raise ValueError("amount_paise must be positive")
    if amount_paise > MAX_ORDER_PAISE:
        raise OrderTooLargeError(
            f"Order amount {amount_paise} paise exceeds hard ceiling {MAX_ORDER_PAISE} paise."
        )
    client = _client()
    receipt = receipt_for(session_id, items)
    order = client.order.create(
        {
            "amount": amount_paise,
            "currency": "INR",
            "receipt": receipt,
            "payment_capture": 1,
            "notes": {"session_id": session_id},
        }
    )
    return order


def fetch_payment_status(razorpay_order_id: str) -> dict:
    """
    In a real integration this is driven by the payment webhook, not polling.
    For the demo we poll order->payments so the whole flow works without
    exposing a public webhook URL.
    """
    client = _client()
    payments = client.order.payments(razorpay_order_id)
    items = payments.get("items", [])
    if not items:
        return {"status": "pending", "payments": []}
    latest = items[-1]
    return {"status": latest.get("status", "unknown"), "payments": items}
