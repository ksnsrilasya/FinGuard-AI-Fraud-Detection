"""
backend/database.py

SQLite connection handling and table schema. Kept as a thin wrapper
(no ORM) so the code stays easy to read and reason about in an interview,
while still being organized cleanly by responsibility.
"""

import sqlite3
from contextlib import contextmanager
from backend.config import settings
from backend.logger import get_logger

logger = get_logger(__name__)


@contextmanager
def get_connection():
    conn = sqlite3.connect(settings.database_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_name TEXT NOT NULL,
                receiver_name TEXT NOT NULL,
                amount REAL NOT NULL,
                merchant_category TEXT NOT NULL,
                transaction_type TEXT NOT NULL,
                device_type TEXT NOT NULL,
                location TEXT NOT NULL,
                transaction_hour INTEGER NOT NULL,
                previous_fraud_history INTEGER NOT NULL,
                customer_age INTEGER NOT NULL,
                payment_method TEXT NOT NULL,
                fraud_probability REAL NOT NULL,
                confidence_score REAL NOT NULL,
                risk_level TEXT NOT NULL,
                reasons TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id INTEGER NOT NULL,
                is_correct INTEGER NOT NULL,
                notes TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (transaction_id) REFERENCES transactions (id)
            )
        """)
    logger.info("Database initialized at %s", settings.database_path)
