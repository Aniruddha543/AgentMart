# AgentMart — Razorpay AI Buildathon (Track 1)

A general store — desk & stationery, electronics, home & kitchen, fashion,
books, fitness, beauty, groceries — with an **agent-readable catalog** any
AI buyer can query over plain HTTP, and a **conversational checkout agent**
(Gemini 3.6 Flash) that completes real purchases on Razorpay test-mode
APIs, with hard spending limits, a full audit trail, and payment failures
handled gracefully instead of silently retried.

## What changed from the first scaffold

- **Catalog**: 12 stationery items → **50 products across 8 categories**.
  `GET /catalog/categories` now lets an agent (or the storefront UI) orient
  itself before searching.
- **Cross-sell tool**: `get_recommendations` — same-category, tag-overlap
  ranked suggestions the agent may offer after an `add_to_cart`, never adds
  automatically. Directly answers Track 1's "upsell & cross-sell agent"
  example direction.
- **LLM**: switched to Gemini 3.6 Flash (`google-genai`), with a
  deterministic fast-path that handles explicit payment confirmations
  ("yes, proceed to payment") in plain Python instead of round-tripping
  through the model — fewer API calls, and the authorization moment is
  fully deterministic rather than dependent on the model calling the right
  tool at the right time.
- **New read-only endpoint**: `GET /cart/{session_id}` — lets the frontend
  show a live cart badge without ever bypassing the agent's guardrails
  (it's GET-only; nothing mutates cart or order state).
- **Frontend**: full storefront rebuild — see below.

## The guardrail model (unchanged in spirit, worth restating)

- `create_order` is refused by the tool executor unless `confirm_cart` was
  called first, with a fresh explicit buyer confirmation in that turn
  (`backend/orchestrator.py`). The model narrating confidently doesn't
  satisfy this — the executor checks state in SQLite, not the model's
  claim.
- `MAX_ORDER_PAISE` is a hard ceiling checked in
  `backend/razorpay_client.py` before any Razorpay API call.
- `MAX_AUTO_APPROVE_PAISE` triggers one extra confirmation round for
  larger carts.
- Every tool call is logged **before and after** execution in
  `backend/audit.py` — failures are on the record, not swallowed.
- Orders use a deterministic receipt (hash of session + cart) so a
  retried tool call can't double-charge.
- Even the storefront's "Ask agent to add" button doesn't call a raw
  cart-mutation endpoint — it sends a natural-language instruction through
  the same chat path everything else uses, so a click and a typed message
  produce identical audit trail entries.

## The new frontend

Single-file, no build step, `frontend/index.html`. Two things it's built
around:

1. **A real catalog to browse**, not just a chat box — category pills,
   search, product cards — because "make a merchant transactable by an AI
   buyer" only means something if there's an actual merchant with actual
   range to show.
2. **A ledger, not a log viewer** — the audit trail panel is styled like a
   bank passbook page (perforated top edge, ruled dashed lines, monospace
   entries, stamp-style "logged" / "flagged" tags) because that's the
   literal artifact Track 1 asks for: *"show the audit trail."* It updates
   live, in the same panel as the chat, so a judge can watch a tool call
   happen and immediately see its ledger line appear.

Layout: catalog fills the main pane; a dark dock on the right holds two
tabs — **Assistant** (chat) and **Ledger** (audit trail) — collapsing into
a full-screen slide-up sheet on mobile. Design tokens: `Fraunces` for the
brand mark and hero line, `Inter` for UI text, `IBM Plex Mono` for
everything numeric (prices, order IDs, ledger timestamps) — deliberately
not the cream+terracotta or dark+neon look every AI-generated storefront
defaults to.

## Project layout

```
backend/
  main.py             FastAPI app: /chat, /cart/{id}, /audit/{id}, mounts /catalog
  orchestrator.py      Gemini tool-calling loop + guardrail enforcement +
                        deterministic payment-confirmation fast path
  catalog.py           product catalog + categories + recommendations,
                        plain functions + HTTP router
  razorpay_client.py   Razorpay test-mode order creation, amount ceiling
  audit.py             append-only audit log (SQLite)
  db.py                SQLite schema + connection helper
  seed_data.py          seeds the 50-product, 8-category catalog
frontend/
  index.html           storefront + assistant/ledger dock (no build step)
```

## Setup

1. **Razorpay test-mode keys**: Dashboard → Settings → API Keys → toggle
   *Test Mode* → generate keys. Never use live keys for this project.
2. **Gemini API key**: from Google AI Studio.

```bash
cd agentmart
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# fill in GEMINI_API_KEY, RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET

python -m backend.seed_data          # populate the 50-product catalog
uvicorn backend.main:app --reload --port 8000
```

Open `http://localhost:8000/` — browse the catalog, click "Ask agent to
add" on a couple of products, or just talk to the assistant directly.

## Demoing the failure path (for your pitch)

Razorpay test mode has dedicated failure triggers so you don't need a real
declined card:

- UPI: enter `failure@razorpay` as the UPI ID at checkout to force an
  instant decline.
- Cards: use a test card number from Razorpay's
  [test card list](https://razorpay.com/docs/payments/payments/test-card-details/)
  — any future expiry, any CVV.

Script:
1. Browse a category, click "Ask agent to add" on two or three items.
2. Confirm the cart when the agent states the total.
3. Complete checkout with a **failing** test credential.
4. Ask the agent to check payment status — it should read the decline,
   explain it plainly, and offer exactly one bounded next step (retry or
   stop), not silently re-create the order.
5. Switch to the **Ledger** tab: the `tool_result:create_order` and the
   failed `tool_result:check_payment_status` entries are both stamped
   "flagged" and timestamped — point at this as your "audit trail" proof.

## What's intentionally out of scope

Single merchant, one buyer persona at a time, in-memory chat history
(swap for Redis/DB if you extend past the event), and polling instead of
a public webhook endpoint for payment status. Say these out loud as "next
steps" in your pitch — the panel is grading honesty about scope as much
as the build itself.

## Extending toward the actual protocol race

Expose the catalog as an [MCP](https://modelcontextprotocol.io) server
instead of plain REST, so any MCP-speaking AI buyer — not just HTTP
clients you write yourself — can transact against it. That's the more
literal reading of "make a merchant transactable by an AI buyer end to
end," and ties directly to the ACP/AP2/x402 protocol race referenced in
the track brief.
