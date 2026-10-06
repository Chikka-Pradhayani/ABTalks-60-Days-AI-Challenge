"""FastAPI application for Day 54 User Feedback Collection and Real-time Monitoring.
Exposes endpoints to submit user feedback, query analytics, and inspect low-rated interactions.
"""

import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field

from database import (
    DEFAULT_DB_PATH,
    get_all_feedback,
    get_connection,
    get_low_rated_feedback,
    init_db,
    insert_feedback,
)


class FeedbackCreate(BaseModel):
    query: str = Field(..., min_length=1, description="The user query or prompt submitted to the AI system")
    rating: int = Field(..., ge=1, le=5, description="1 to 5 star rating (1=terrible, 5=excellent)")
    feedback: Optional[str] = Field("", description="Optional written comment or complaint from the user")
    topic: Optional[str] = Field("general", description="Categorization topic (e.g., auth, query, latency, formatting)")
    response: Optional[str] = Field("", description="The AI response generated for the query")
    failure_pattern: Optional[str] = Field("", description="Observed failure reason (e.g. hallucination, timeout, wrong_format)")
    user_id: Optional[str] = Field("anonymous", description="User identifier or email")
    session_id: Optional[str] = Field("", description="Active session ID")
    timestamp: Optional[str] = Field(None, description="ISO formatted timestamp (defaults to UTC now)")


class FeedbackResponse(BaseModel):
    id: int
    query: str
    rating: int
    feedback: str
    topic: str
    response: str
    failure_pattern: str
    user_id: str
    session_id: str
    timestamp: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ensure database schema is created on startup."""
    init_db()
    yield


app = FastAPI(
    title="AURONIX Feedback Collection & Analytics API",
    description="Enterprise user research and feedback analysis API for Day 54 of the 60 Days AI Challenge.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/", tags=["General"])
def root():
    """API Root with product description and health overview."""
    return {
        "product": "AURONIX",
        "day": 54,
        "title": "User Feedback Collection & Analytics System",
        "description": (
            "AURONIX is an enterprise AI assistant that enables professionals to instantly query, analyze, "
            "and extract structured insights from large private documents without technical expertise. "
            "This Day 54 module captures real-world user ratings and feedback, grouping failure modes and "
            "transforming user input into prioritized product engineering updates."
        ),
        "status": "healthy",
        "endpoints": {
            "submit_feedback": "POST /feedback",
            "list_feedback": "GET /feedback",
            "summary_metrics": "GET /feedback/metrics",
            "low_rated_feedback": "GET /feedback/low-rated",
        },
    }


@app.post("/feedback", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED, tags=["Feedback"])
def submit_feedback(payload: FeedbackCreate):
    """Submit user feedback for an AI query and store in SQLite."""
    feedback_id = insert_feedback(
        query=payload.query,
        rating=payload.rating,
        feedback=payload.feedback or "",
        topic=payload.topic or "general",
        response=payload.response or "",
        failure_pattern=payload.failure_pattern or "",
        user_id=payload.user_id or "anonymous",
        session_id=payload.session_id or "",
        timestamp=payload.timestamp,
    )

    return {
        "status": "success",
        "message": "Feedback successfully recorded",
        "id": feedback_id,
        "rating": payload.rating,
        "timestamp": payload.timestamp or datetime.now(timezone.utc).isoformat(),
    }


@app.get("/feedback", response_model=List[FeedbackResponse], tags=["Feedback"])
def list_feedback(limit: int = Query(100, ge=1, le=1000)):
    """Retrieve all collected feedback records ordered by latest submission."""
    records = get_all_feedback()
    return records[:limit]


@app.get("/feedback/low-rated", response_model=List[FeedbackResponse], tags=["Feedback"])
def list_low_rated_feedback(threshold: int = Query(2, ge=1, le=5)):
    """Filter queries that received negative feedback (rating <= threshold)."""
    return get_low_rated_feedback(threshold=threshold)


@app.get("/feedback/metrics", tags=["Monitoring & Analytics"])
def get_metrics():
    """Calculate aggregated feedback metrics for monitoring."""
    conn = get_connection()
    cursor = conn.cursor()

    # Total count
    cursor.execute("SELECT COUNT(*) FROM feedback")
    total_queries = cursor.fetchone()[0]

    if total_queries == 0:
        conn.close()
        return {
            "status": "pending_data",
            "message": "No feedback data recorded yet.",
            "total_queries": 0,
            "positive_ratings": 0,
            "neutral_ratings": 0,
            "negative_ratings": 0,
            "positive_rate_pct": 0.0,
            "negative_rate_pct": 0.0,
            "average_rating": 0.0,
            "topic_breakdown": {},
            "failure_pattern_breakdown": {},
        }

    # Rating distribution
    cursor.execute("SELECT COUNT(*) FROM feedback WHERE rating >= 4")
    positive_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM feedback WHERE rating = 3")
    neutral_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM feedback WHERE rating <= 2")
    negative_count = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(rating) FROM feedback")
    avg_rating = round(float(cursor.fetchone()[0]), 2)

    # Topics breakdown
    cursor.execute("SELECT topic, COUNT(*) as cnt FROM feedback GROUP BY topic ORDER BY cnt DESC")
    topics = {row["topic"]: row["cnt"] for row in cursor.fetchall()}

    # Failure patterns breakdown
    cursor.execute(
        "SELECT failure_pattern, COUNT(*) as cnt FROM feedback WHERE failure_pattern != '' GROUP BY failure_pattern ORDER BY cnt DESC"
    )
    failure_patterns = {row["failure_pattern"]: row["cnt"] for row in cursor.fetchall()}

    conn.close()

    return {
        "status": "active",
        "total_queries": total_queries,
        "positive_ratings": positive_count,
        "neutral_ratings": neutral_count,
        "negative_ratings": negative_count,
        "positive_rate_pct": round((positive_count / total_queries) * 100, 2),
        "negative_rate_pct": round((negative_count / total_queries) * 100, 2),
        "average_rating": avg_rating,
        "topic_breakdown": topics,
        "failure_pattern_breakdown": failure_patterns,
    }
