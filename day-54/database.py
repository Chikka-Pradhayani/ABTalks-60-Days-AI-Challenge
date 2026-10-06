"""Database setup and SQLite persistence operations for Day 54 User Feedback System.
Supports structured feedback collection, retrieval, and metric aggregations.
"""

import os
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# Default database location in day-54 directory
DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "feedback.db")


def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Return a SQLite connection with dict row factory."""
    target_path = db_path or os.environ.get("FEEDBACK_DB_PATH", DEFAULT_DB_PATH)
    conn = sqlite3.connect(target_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Optional[str] = None) -> None:
    """Initialize the feedback database schema and indexing."""
    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        query TEXT NOT NULL,
        rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
        feedback TEXT DEFAULT '',
        topic TEXT DEFAULT 'general',
        response TEXT DEFAULT '',
        failure_pattern TEXT DEFAULT '',
        user_id TEXT DEFAULT 'anonymous',
        session_id TEXT DEFAULT '',
        timestamp TEXT NOT NULL
    );
    """)

    # Indices for high-frequency analytical queries
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_feedback_timestamp ON feedback(timestamp);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_feedback_rating ON feedback(rating);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_feedback_topic ON feedback(topic);")

    conn.commit()
    conn.close()


def insert_feedback(
    query: str,
    rating: int,
    feedback: str = "",
    topic: str = "general",
    response: str = "",
    failure_pattern: str = "",
    user_id: str = "anonymous",
    session_id: str = "",
    timestamp: Optional[str] = None,
    db_path: Optional[str] = None,
) -> int:
    """Insert a feedback entry into the database and return the inserted id."""
    if not timestamp:
        timestamp = datetime.now(timezone.utc).isoformat()

    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO feedback (query, rating, feedback, topic, response, failure_pattern, user_id, session_id, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (query, rating, feedback, topic, response, failure_pattern, user_id, session_id, timestamp),
    )

    feedback_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return feedback_id


def get_all_feedback(db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve all feedback entries ordered by descending timestamp."""
    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM feedback ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_low_rated_feedback(threshold: int = 2, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve feedback records where rating <= threshold (negative/low rating)."""
    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM feedback WHERE rating <= ? ORDER BY id DESC", (threshold,))
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_feedback_count(db_path: Optional[str] = None) -> int:
    """Return the total number of feedback records in the database."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM feedback")
    count = cursor.fetchone()[0]
    conn.close()
    return count
