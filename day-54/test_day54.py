"""Automated test suite for Day 54 User Feedback Collection and Analytics pipeline.
Validates database storage, API endpoints, classification clustering, and metrics.
"""

import os
import tempfile
import pytest
from fastapi.testclient import TestClient

from database import (
    get_all_feedback,
    get_connection,
    get_feedback_count,
    get_low_rated_feedback,
    init_db,
    insert_feedback,
)
from app import app
from feedback_analytics import analyze_feedback, classify_topic

client = TestClient(app)


@pytest.fixture(autouse=True)
def isolated_db(monkeypatch):
    """Provide an isolated temporary SQLite database for each test."""
    temp_dir = tempfile.mkdtemp()
    temp_db_path = os.path.join(temp_dir, "test_feedback.db")
    monkeypatch.setenv("FEEDBACK_DB_PATH", temp_db_path)
    init_db(temp_db_path)
    yield temp_db_path


def test_database_init_and_insert(isolated_db):
    """Verify table creation, record insertion, and queries."""
    fid = insert_feedback(
        query="How to export PDF to markdown?",
        rating=5,
        feedback="Super quick and clean!",
        topic="Document Formatting & Parsing",
        db_path=isolated_db,
    )
    assert fid == 1
    assert get_feedback_count(isolated_db) == 1

    records = get_all_feedback(isolated_db)
    assert len(records) == 1
    assert records[0]["query"] == "How to export PDF to markdown?"
    assert records[0]["rating"] == 5


def test_get_low_rated_feedback(isolated_db):
    """Verify filtering of negative ratings."""
    insert_feedback(query="Query 1", rating=1, feedback="Failed", db_path=isolated_db)
    insert_feedback(query="Query 2", rating=2, feedback="Poor format", db_path=isolated_db)
    insert_feedback(query="Query 3", rating=4, feedback="Great", db_path=isolated_db)
    insert_feedback(query="Query 4", rating=5, feedback="Flawless", db_path=isolated_db)

    low_rated = get_low_rated_feedback(threshold=2, db_path=isolated_db)
    assert len(low_rated) == 2
    assert {r["rating"] for r in low_rated} == {1, 2}


def test_api_submit_and_list_feedback(isolated_db):
    """Test POST /feedback and GET /feedback endpoints."""
    payload = {
        "query": "Extract table from annual report PDF",
        "rating": 1,
        "feedback": "Table columns got squished together",
        "topic": "Document Formatting & Parsing",
        "failure_pattern": "Table column misalignment",
    }
    response = client.post("/feedback", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    assert data["id"] == 1

    # List
    list_resp = client.get("/feedback")
    assert list_resp.status_code == 200
    items = list_resp.json()
    assert len(items) == 1
    assert items[0]["query"] == payload["query"]
    assert items[0]["rating"] == 1


def test_api_metrics_endpoint(isolated_db):
    """Test GET /feedback/metrics aggregation."""
    # Seed 3 records: 1 negative, 1 neutral, 1 positive
    insert_feedback(query="Q1", rating=1, db_path=isolated_db)
    insert_feedback(query="Q2", rating=3, db_path=isolated_db)
    insert_feedback(query="Q3", rating=5, db_path=isolated_db)

    resp = client.get("/feedback/metrics")
    assert resp.status_code == 200
    metrics = resp.json()
    assert metrics["total_queries"] == 3
    assert metrics["positive_ratings"] == 1
    assert metrics["neutral_ratings"] == 1
    assert metrics["negative_ratings"] == 1
    assert metrics["positive_rate_pct"] == pytest.approx(33.33, 0.1)
    assert metrics["negative_rate_pct"] == pytest.approx(33.33, 0.1)


def test_topic_classification_logic():
    """Verify rule-based keyword topic matching."""
    t1 = classify_topic("How do I parse a 2-column legal contract pdf layout?")
    assert t1 == "Document Formatting & Parsing"

    t2 = classify_topic("The search took 45 seconds and ended in a timeout delay.")
    assert t2 == "Query Latency & Timeouts"

    t3 = classify_topic("Where is the page quote or citation reference in the text?")
    assert t3 == "Source Citation & Grounding"

    t4 = classify_topic("General hello world question")
    assert t4 == "General Inquiries"


def test_feedback_analytics_top_clusters(isolated_db):
    """Test that failure rates and top-3 clusters are computed accurately."""
    # Cluster A: Document Formatting (3 total, 2 failed -> 66.7%)
    insert_feedback(query="Extract pdf table layout", rating=1, db_path=isolated_db)
    insert_feedback(query="Format table column csv", rating=2, db_path=isolated_db)
    insert_feedback(query="Markdown font format", rating=4, db_path=isolated_db)

    # Cluster B: Query Latency (2 total, 2 failed -> 100%)
    insert_feedback(query="Slow response timeout delay", rating=1, db_path=isolated_db)
    insert_feedback(query="Latency wait speed", rating=2, db_path=isolated_db)

    # Cluster C: General Inquiries (2 total, 0 failed -> 0%)
    insert_feedback(query="Hello support", rating=5, db_path=isolated_db)
    insert_feedback(query="General overview", rating=5, db_path=isolated_db)

    results = analyze_feedback(isolated_db)
    assert results["total_queries"] == 7
    assert len(results["top_failing_clusters"]) >= 2

    top_cluster = results["top_failing_clusters"][0]
    assert top_cluster["topic"] == "Query Latency & Timeouts"
    assert top_cluster["failure_rate_pct"] == 100.0

    second_cluster = results["top_failing_clusters"][1]
    assert second_cluster["topic"] == "Document Formatting & Parsing"
    assert pytest.approx(second_cluster["failure_rate_pct"], 0.1) == 66.67
