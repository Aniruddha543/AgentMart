"""
The "agent-readable catalog" piece of Track 1.

Two consumers of the same data:
  1. Our own orchestrator agent calls the plain functions directly.
  2. Any external AI buyer agent can call the same catalog over HTTP —
     structured JSON, stable schema, no HTML scraping required.
"""
from fastapi import APIRouter, HTTPException
from backend.db import get_conn

router = APIRouter(prefix="/catalog", tags=["catalog"])


def _row_to_product(r) -> dict:
    return {
        "id": r["id"],
        "name": r["name"],
        "description": r["description"],
        "price_paise": r["price_paise"],
        "price_display": f"₹{r['price_paise'] / 100:.2f}",
        "currency": r["currency"],
        "stock": r["stock"],
        "category": r["category"],
        "tags": [t for t in r["tags"].split(",") if t],
    }


def list_products(category: str | None = None, query: str | None = None) -> list[dict]:
    sql = "SELECT * FROM products WHERE stock > 0"
    params: list = []
    if category:
        sql += " AND category = ?"
        params.append(category)
    if query:
        sql += " AND (name LIKE ? OR description LIKE ? OR tags LIKE ?)"
        like = f"%{query}%"
        params += [like, like, like]
    with get_conn() as conn:
        rows = conn.execute(sql, params).fetchall()
    return [_row_to_product(r) for r in rows]


def get_product(product_id: str) -> dict | None:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    return _row_to_product(row) if row else None


def list_categories() -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT category, COUNT(*) as n FROM products WHERE stock > 0 GROUP BY category ORDER BY category"
        ).fetchall()
    return [{"category": r["category"], "count": r["n"]} for r in rows]


def get_recommendations(product_id: str, limit: int = 3) -> list[dict]:
    """
    Same-category, tag-overlap ranked recommendations — powers the
    agent's cross-sell/upsell tool. Deliberately simple (no ML) so the
    logic is auditable in a hackathon pitch.
    """
    base = get_product(product_id)
    if not base:
        return []
    base_tags = set(base["tags"])
    candidates = [p for p in list_products(category=base["category"]) if p["id"] != product_id]
    candidates.sort(key=lambda p: len(base_tags & set(p["tags"])), reverse=True)
    return candidates[:limit]


# ---- HTTP surface for external AI buyers ----

@router.get("/categories")
def http_list_categories():
    """Agent-readable category list with counts — lets a buyer agent browse before searching."""
    return {"categories": list_categories()}


@router.get("/products")
def http_list_products(category: str | None = None, q: str | None = None):
    """Agent-readable product listing. Stable schema, no auth required in test mode."""
    return {"products": list_products(category=category, query=q)}


@router.get("/products/{product_id}")
def http_get_product(product_id: str):
    product = get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="product_not_found")
    return product
