"""
SQLite setup for the demo. One file, zero external deps, easy to inspect
in the pitch ("here's the raw audit trail, nothing hidden").
"""
import os
import sqlite3
from contextlib import contextmanager

DB_PATH = os.getenv("DB_PATH", "./checkout_agent.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS products (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    description TEXT NOT NULL,
    price_paise INTEGER NOT NULL,
    currency    TEXT NOT NULL DEFAULT 'INR',
    stock       INTEGER NOT NULL,
    category    TEXT NOT NULL,
    tags        TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS carts (
    session_id TEXT PRIMARY KEY,
    items_json TEXT NOT NULL DEFAULT '[]',
    confirmed  INTEGER NOT NULL DEFAULT 0,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS orders (
    id                TEXT PRIMARY KEY,
    session_id        TEXT NOT NULL,
    razorpay_order_id TEXT,
    amount_paise      INTEGER NOT NULL,
    status            TEXT NOT NULL DEFAULT 'created',
    receipt           TEXT NOT NULL,
    created_at        TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS audit_log (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    step       TEXT NOT NULL,
    detail     TEXT NOT NULL,
    ts         TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.executescript(SCHEMA)
