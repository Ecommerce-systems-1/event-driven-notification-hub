import sqlite3, os, json
from contextlib import contextmanager

DB_PATH = os.environ.get("DB_PATH", "notifications.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

@contextmanager
def db_session():
    conn = get_conn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

RULES_SEED = [
    ("ORDER_PLACED",       "EMAIL",  "email_order_placed"),
    ("ORDER_PLACED",       "SMS",    "sms_order_placed"),
    ("ORDER_PLACED",       "PUSH",   "push_order_placed"),
    ("PAYMENT_CAPTURED",   "EMAIL",  "email_payment_captured"),
    ("ORDER_SHIPPED",      "EMAIL",  "email_order_shipped"),
    ("ORDER_SHIPPED",      "SMS",    "sms_order_shipped"),
    ("DELIVERY_CONFIRMED", "EMAIL",  "email_delivery_confirmed"),
    ("RETURN_REQUESTED",   "EMAIL",  "email_return_requested"),
]
EVENT_TYPES = ["ORDER_PLACED","PAYMENT_CAPTURED","ORDER_SHIPPED","DELIVERY_CONFIRMED","RETURN_REQUESTED"]

def init_db():
    with db_session() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS event_types (code TEXT PRIMARY KEY, description TEXT);
        CREATE TABLE IF NOT EXISTS notification_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL, channel TEXT NOT NULL, template_id TEXT NOT NULL,
            UNIQUE(event_type, channel)
        );
        CREATE TABLE IF NOT EXISTS events (
            id TEXT PRIMARY KEY, event_type TEXT NOT NULL, payload TEXT NOT NULL,
            customer_id TEXT NOT NULL, published_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id TEXT NOT NULL, channel TEXT NOT NULL, customer_id TEXT NOT NULL,
            template_id TEXT, rendered_body TEXT, delivered_at TEXT NOT NULL,
            UNIQUE(event_id, channel)
        );
        """)
        if conn.execute("SELECT COUNT(*) FROM event_types").fetchone()[0] == 0:
            for et in EVENT_TYPES:
                conn.execute("INSERT INTO event_types VALUES (?,?)", (et, et.replace("_"," ").title()))
            for et, ch, tmpl in RULES_SEED:
                conn.execute("INSERT OR IGNORE INTO notification_rules(event_type,channel,template_id) VALUES (?,?,?)",
                             (et, ch, tmpl))

def load_rules(event_type: str) -> list:
    with db_session() as conn:
        rows = conn.execute(
            "SELECT channel, template_id FROM notification_rules WHERE event_type=?",
            (event_type,)
        ).fetchall()
    return [dict(r) for r in rows]

def insert_event(event_id, event_type, payload, customer_id, published_at):
    with db_session() as conn:
        conn.execute("INSERT INTO events VALUES (?,?,?,?,?)",
                     (event_id, event_type, json.dumps(payload), customer_id, published_at))

def insert_notification(event_id, channel, customer_id, template_id, rendered_body, delivered_at):
    with db_session() as conn:
        try:
            conn.execute(
                "INSERT INTO notifications(event_id,channel,customer_id,template_id,rendered_body,delivered_at) VALUES (?,?,?,?,?,?)",
                (event_id, channel, customer_id, template_id, rendered_body, delivered_at)
            )
        except Exception:
            pass  # Deduplication: unique constraint silently skips

def get_notifications(customer_id: str) -> list:
    with db_session() as conn:
        rows = conn.execute(
            "SELECT * FROM notifications WHERE customer_id=? ORDER BY id DESC LIMIT 100",
            (customer_id,)
        ).fetchall()
    return [dict(r) for r in rows]

def get_recent_events(limit: int = 50) -> list:
    with db_session() as conn:
        rows = conn.execute(
            "SELECT * FROM events ORDER BY published_at DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(r) for r in rows]