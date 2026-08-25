import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.db import init_db
from backend.catalog import router as catalog_router, get_product
from backend.orchestrator import run_turn, _latest_order, _get_cart, _cart_total_paise
from backend.audit import get_audit_trail


app = FastAPI(title="Agentic Checkout Demo")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(catalog_router)


# ---------------------------------------------------------
# In-memory conversation history
# ---------------------------------------------------------

_SESSIONS: dict[str, list] = {}


# ---------------------------------------------------------
# Startup
# ---------------------------------------------------------

@app.on_event("startup")
def on_startup():
    init_db()


# ---------------------------------------------------------
# Request model
# ---------------------------------------------------------

class ChatRequest(BaseModel):
    session_id: str
    message: str


# ---------------------------------------------------------
# Chat endpoint
# ---------------------------------------------------------

@app.post("/chat")
def chat(req: ChatRequest):

    history = _SESSIONS.get(
        req.session_id,
        []
    )

    # Run Gemini agent
    reply, updated_history = run_turn(
        req.session_id,
        req.message,
        history
    )

    # Save conversation history
    _SESSIONS[req.session_id] = updated_history

    # -----------------------------------------------------
    # Get latest Razorpay order
    # -----------------------------------------------------

    latest_order = _latest_order(
        req.session_id
    )

    order_id = None
    amount_paise = None
    order_status = None

    if latest_order:

        order_id = latest_order.get(
            "razorpay_order_id"
        )

        amount_paise = latest_order.get(
            "amount_paise"
        )

        order_status = latest_order.get(
            "status"
        )

    # -----------------------------------------------------
    # Return response to frontend
    # -----------------------------------------------------

    return {
        "reply": reply,

        # Razorpay information
        "order_id": order_id,
        "amount_paise": amount_paise,
        "order_status": order_status,

        # Audit trail
        "audit_trail": get_audit_trail(
            req.session_id
        ),
    }


# ---------------------------------------------------------
# Audit endpoint
# ---------------------------------------------------------

@app.get("/cart/{session_id}")
def get_cart(session_id: str):
    """
    Read-only cart view for the UI (badge count, mini-cart). Does not
    mutate anything and is not part of the guardrail chain — all cart
    changes still only happen through the agent's tool calls.
    """
    cart = _get_cart(session_id)
    items = []
    for i in cart["items"]:
        product = get_product(i["product_id"])
        if product:
            items.append(
                {
                    "product_id": i["product_id"],
                    "name": product["name"],
                    "qty": i["qty"],
                    "price_paise": product["price_paise"],
                    "line_total_paise": product["price_paise"] * i["qty"],
                }
            )
    return {
        "items": items,
        "confirmed": cart["confirmed"],
        "total_paise": _cart_total_paise(cart["items"]),
    }


@app.get("/audit/{session_id}")
def audit(session_id: str):

    return {
        "audit_trail": get_audit_trail(
            session_id
        )
    }


# ---------------------------------------------------------
# Health check
# ---------------------------------------------------------

@app.get("/health")
def health():

    return {
        "status": "ok"
    }


# ---------------------------------------------------------
# Public config (Razorpay publishable key only)
# ---------------------------------------------------------

@app.get("/config")
def config():
    """
    Only ever exposes RAZORPAY_KEY_ID (the publishable key Checkout.js
    needs client-side). RAZORPAY_KEY_SECRET never leaves the server.
    """
    return {
        "razorpay_key_id": os.getenv("RAZORPAY_KEY_ID", "")
    }


# ---------------------------------------------------------
# Serve frontend
# ---------------------------------------------------------

app.mount(
    "/",
    StaticFiles(
        directory="frontend",
        html=True
    ),
    name="frontend"
)