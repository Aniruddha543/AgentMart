"""
Seeds a multi-category fake merchant catalog — "AgentMart", a general store
spanning desk/stationery, electronics, home, fashion, books, fitness,
beauty, and groceries. Run once: python -m backend.seed_data
"""
from backend.db import get_conn, init_db

# (id, name, description, price_paise, stock, category, tags)
PRODUCTS = [
    # --- Desk & Stationery ---
    ("p001", "Fountain Pen — Walnut", "Walnut-barrel fountain pen, medium nib.", 129900, 40, "Desk & Stationery", "pen,gift,writing"),
    ("p002", "Notebook — Dot Grid A5", "160gsm dot-grid notebook, 200 pages.", 45900, 120, "Desk & Stationery", "notebook,paper"),
    ("p003", "Desk Lamp — Warm LED", "Adjustable warm-white LED desk lamp.", 249900, 25, "Desk & Stationery", "lamp,light,desk"),
    ("p004", "Mechanical Keyboard — 65%", "Hot-swappable 65% board, brown switches.", 599900, 15, "Desk & Stationery", "keyboard,tech,desk"),
    ("p005", "Ceramic Mug — Matte Black", "350ml matte black stoneware mug.", 39900, 200, "Desk & Stationery", "mug,gift,desk"),
    ("p006", "Leather Pen Case", "Hand-stitched leather case, holds 3 pens.", 89900, 60, "Desk & Stationery", "case,gift,writing"),
    ("p007", "Ink Bottle — Midnight Blue", "50ml bottled fountain pen ink.", 29900, 90, "Desk & Stationery", "ink,writing"),
    ("p008", "Desk Mat — Wool Felt", "600x300mm wool-felt desk mat, charcoal.", 69900, 45, "Desk & Stationery", "mat,desk"),
    ("p009", "Sticky Notes — Set of 5", "5 pads of recycled sticky notes.", 19900, 300, "Desk & Stationery", "notes,paper"),
    ("p010", "Wireless Mouse — Silent", "2.4GHz silent-click wireless mouse.", 179900, 35, "Desk & Stationery", "mouse,tech,desk"),
    ("p011", "Planner — 2026 Weekly", "12-month weekly planner, hardcover.", 79900, 70, "Desk & Stationery", "planner,paper"),
    ("p012", "Cable Organizer Tray", "Bamboo cable + accessory tray.", 54900, 55, "Desk & Stationery", "organizer,desk"),

    # --- Electronics ---
    ("p013", "Wireless Earbuds — ANC", "Active noise cancelling, 30hr case battery.", 449900, 50, "Electronics", "audio,tech,gift"),
    ("p014", "Power Bank — 20000mAh", "USB-C PD 65W fast-charge power bank.", 249900, 80, "Electronics", "charging,tech,travel"),
    ("p015", "Smart Watch — Fitness", "AMOLED display, heart-rate + SpO2 tracking.", 799900, 30, "Electronics", "wearable,fitness,tech"),
    ("p016", "Portable SSD — 1TB", "USB-C 1TB external SSD, 1050MB/s read.", 649900, 40, "Electronics", "storage,tech"),
    ("p017", "Webcam — 1080p", "Autofocus 1080p webcam with privacy shutter.", 219900, 60, "Electronics", "video,tech,desk"),
    ("p018", "Bluetooth Speaker — Mini", "IPX7 waterproof mini Bluetooth speaker.", 189900, 90, "Electronics", "audio,travel,gift"),
    ("p019", "USB-C Hub — 7-in-1", "HDMI, SD, 3x USB-A, PD passthrough.", 249900, 65, "Electronics", "tech,desk"),
    ("p020", "Phone Stand — Aluminium", "Adjustable aluminium phone/tablet stand.", 69900, 150, "Electronics", "accessory,desk"),

    # --- Home & Kitchen ---
    ("p021", "French Press — 600ml", "Borosilicate glass French press, 4-cup.", 129900, 45, "Home & Kitchen", "coffee,kitchen,gift"),
    ("p022", "Cast Iron Skillet — 10\"", "Pre-seasoned cast iron skillet.", 189900, 35, "Home & Kitchen", "kitchen,cooking"),
    ("p023", "Ceramic Dinner Set — 4pc", "4-piece stoneware dinner plate set.", 279900, 25, "Home & Kitchen", "kitchen,dining"),
    ("p024", "Electric Kettle — 1.7L", "Rapid-boil stainless steel kettle.", 159900, 55, "Home & Kitchen", "kitchen,appliance"),
    ("p025", "Throw Blanket — Wool Blend", "130x180cm woven throw blanket.", 149900, 40, "Home & Kitchen", "home,cozy,gift"),
    ("p026", "Scented Candle — Sandalwood", "45hr burn, soy wax, sandalwood + oud.", 59900, 100, "Home & Kitchen", "home,gift,candle"),
    ("p027", "Knife Set — 5pc", "5-piece forged kitchen knife set with block.", 349900, 20, "Home & Kitchen", "kitchen,cooking"),
    ("p028", "Air Plant Terrarium", "Glass terrarium with 2 air plants.", 84900, 30, "Home & Kitchen", "home,plants,gift"),

    # --- Fashion & Apparel ---
    ("p029", "Merino Wool Sweater", "Crew-neck merino wool sweater, unisex.", 349900, 50, "Fashion & Apparel", "apparel,winter"),
    ("p030", "Canvas Tote Bag", "14oz heavyweight canvas tote, reinforced straps.", 79900, 120, "Fashion & Apparel", "bag,accessory"),
    ("p031", "Leather Belt — Tan", "Full-grain leather belt, brass buckle.", 119900, 70, "Fashion & Apparel", "accessory,leather"),
    ("p032", "Running Socks — 3 Pack", "Moisture-wicking cushioned running socks.", 49900, 200, "Fashion & Apparel", "socks,fitness"),
    ("p033", "Denim Jacket — Classic", "Mid-wash straight-cut denim jacket.", 399900, 35, "Fashion & Apparel", "apparel,denim"),
    ("p034", "Wool Beanie", "Ribbed-knit wool beanie, one size.", 39900, 150, "Fashion & Apparel", "accessory,winter"),

    # --- Books ---
    ("p035", "The Pragmatic Founder", "Field notes on building early-stage startups.", 59900, 80, "Books", "business,nonfiction"),
    ("p036", "Systems of Thought", "An illustrated primer on systems thinking.", 74900, 60, "Books", "nonfiction,design"),
    ("p037", "Midnight in Kolkata", "A literary novel set across two monsoons.", 44900, 90, "Books", "fiction,novel"),
    ("p038", "Cooking with Fire", "A chef's guide to open-flame cooking.", 89900, 40, "Books", "cookbook,kitchen"),

    # --- Fitness & Outdoors ---
    ("p039", "Yoga Mat — Non-slip", "6mm non-slip TPE yoga mat with strap.", 99900, 100, "Fitness & Outdoors", "fitness,yoga"),
    ("p040", "Resistance Bands — Set of 5", "5 resistance levels, door anchor included.", 69900, 130, "Fitness & Outdoors", "fitness,home-gym"),
    ("p041", "Insulated Water Bottle — 1L", "24hr cold retention, stainless steel.", 89900, 160, "Fitness & Outdoors", "fitness,hydration,gift"),
    ("p042", "Trail Running Backpack — 10L", "Hydration-compatible trail running vest.", 249900, 40, "Fitness & Outdoors", "fitness,outdoors,bag"),
    ("p043", "Foam Roller — High Density", "45cm high-density recovery foam roller.", 79900, 70, "Fitness & Outdoors", "fitness,recovery"),

    # --- Beauty & Personal Care ---
    ("p044", "Sandalwood Beard Oil", "Cold-pressed beard oil, 30ml.", 49900, 110, "Beauty & Personal Care", "grooming,gift"),
    ("p045", "Vitamin C Serum — 30ml", "10% vitamin C brightening serum.", 84900, 90, "Beauty & Personal Care", "skincare"),
    ("p046", "Bamboo Toothbrush Set — 4pk", "Biodegradable bamboo-handle toothbrushes.", 29900, 200, "Beauty & Personal Care", "eco,personal-care"),

    # --- Groceries ---
    ("p047", "Single-Origin Coffee Beans — 250g", "Washed Arabica, medium roast, Coorg.", 54900, 150, "Groceries", "coffee,gourmet"),
    ("p048", "Raw Forest Honey — 500g", "Unprocessed multi-floral raw honey.", 44900, 120, "Groceries", "gourmet,gift"),
    ("p049", "Dark Chocolate — 70% Cacao", "Single-origin dark chocolate bar, 100g.", 24900, 250, "Groceries", "snack,gift"),
    ("p050", "Herbal Tea Sampler — 6 Blends", "Caffeine-free loose-leaf tea sampler box.", 59900, 90, "Groceries", "tea,gift"),
]


def seed():
    init_db()
    with get_conn() as conn:
        conn.execute("DELETE FROM products")
        for pid, name, desc, price, stock, cat, tags in PRODUCTS:
            conn.execute(
                """INSERT OR REPLACE INTO products
                   (id, name, description, price_paise, currency, stock, category, tags)
                   VALUES (?, ?, ?, ?, 'INR', ?, ?, ?)""",
                (pid, name, desc, price, stock, cat, tags),
            )
    categories = sorted({p[5] for p in PRODUCTS})
    print(f"Seeded {len(PRODUCTS)} products across {len(categories)} categories:")
    for c in categories:
        print(f"  - {c}")


if __name__ == "__main__":
    seed()
