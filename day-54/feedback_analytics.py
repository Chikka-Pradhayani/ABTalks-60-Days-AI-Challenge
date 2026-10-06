"""Feedback Analytics and Topic Failure Rate Detector for Day 54.

Analyzes stored feedback queries:
1. Groups incoming queries into topics using keyword frequency and taxonomy detection.
2. Calculates failure rates (rating <= 2) for each detected topic cluster.
3. Identifies and prints the top 3 topic clusters with the highest failure rates.
4. Generates structured 24-hour summary analytics.
"""

import os
import re
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

from database import DEFAULT_DB_PATH, get_connection

# Domain topic keyword mapping for rule-based taxonomy clustering
TOPIC_KEYWORDS = {
    "Document Formatting & Parsing": [
        "pdf", "table", "format", "csv", "json", "parse", "header", "markdown", "column", "layout", "font"
    ],
    "Query Latency & Timeouts": [
        "slow", "latency", "timeout", "delay", "freeze", "wait", "hang", "speed", "fast", "seconds"
    ],
    "Hallucination & Factual Accuracy": [
        "hallucinate", "wrong", "fake", "incorrect", "false", "made up", "fabricated", "accuracy", "error", "lie"
    ],
    "Source Citation & Grounding": [
        "cite", "citation", "source", "reference", "page", "quote", "grounding", "link", "where"
    ],
    "Authentication & Access Control": [
        "login", "auth", "token", "password", "key", "permission", "unauthorized", "session", "expire"
    ],
    "Context Window & File Size": [
        "length", "cutoff", "truncated", "tokens", "limit", "large file", "50mb", "context", "exceeded"
    ],
}


def classify_topic(query: str, manual_topic: Optional[str] = None) -> str:
    """Classify a query into a topic cluster using manual topic or keyword frequencies."""
    if manual_topic and manual_topic != "general":
        # Check if manual topic matches known clusters
        for cluster_name in TOPIC_KEYWORDS:
            if manual_topic.lower() in cluster_name.lower():
                return cluster_name
        return manual_topic.capitalize()

    text = query.lower()
    matches = defaultdict(int)

    for cluster, keywords in TOPIC_KEYWORDS.items():
        for kw in keywords:
            if re.search(r"\b" + re.escape(kw) + r"\b", text):
                matches[cluster] += 1

    if matches:
        return max(matches.items(), key=lambda x: x[1])[0]

    return "General Inquiries"


def analyze_feedback(db_path: Optional[str] = None) -> Dict[str, Any]:
    """Run comprehensive feedback analytics on database records."""
    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM feedback")
    rows = cursor.fetchall()
    conn.close()

    total_count = len(rows)
    if total_count == 0:
        return {
            "status": "pending_data",
            "message": "No feedback records found in database.",
            "total_queries": 0,
            "clusters": [],
            "top_failing_clusters": [],
        }

    # Group metrics by cluster
    cluster_stats = defaultdict(lambda: {"total": 0, "failures": 0, "successes": 0, "ratings": []})
    failure_patterns = defaultdict(int)

    for row in rows:
        rating = int(row["rating"])
        query = str(row["query"])
        manual_topic = str(row["topic"]) if row["topic"] else "general"
        pattern = str(row["failure_pattern"]) if row["failure_pattern"] else ""

        cluster = classify_topic(query, manual_topic)
        cluster_stats[cluster]["total"] += 1
        cluster_stats[cluster]["ratings"].append(rating)

        # Rating <= 2 is classified as failure/dissatisfaction
        if rating <= 2:
            cluster_stats[cluster]["failures"] += 1
            if pattern:
                failure_patterns[pattern] += 1
            else:
                failure_patterns["Unclassified user dissatisfaction"] += 1
        else:
            cluster_stats[cluster]["successes"] += 1

    # Calculate failure rates
    results = []
    for cluster, stats in cluster_stats.items():
        total = stats["total"]
        failures = stats["failures"]
        fail_rate = round((failures / total) * 100, 2)
        avg_rating = round(sum(stats["ratings"]) / total, 2)

        results.append({
            "topic": cluster,
            "total_queries": total,
            "failed_queries": failures,
            "success_queries": stats["successes"],
            "failure_rate_pct": fail_rate,
            "average_rating": avg_rating,
        })

    # Sort descending by failure rate, then by total failures
    results.sort(key=lambda x: (x["failure_rate_pct"], x["failed_queries"]), reverse=True)
    top_3_failing = results[:3]

    # Global summary
    total_positive = sum(1 for r in rows if int(r["rating"]) >= 4)
    total_neutral = sum(1 for r in rows if int(r["rating"]) == 3)
    total_negative = sum(1 for r in rows if int(r["rating"]) <= 2)

    return {
        "status": "completed",
        "total_queries": total_count,
        "positive_ratings": total_positive,
        "positive_rate_pct": round((total_positive / total_count) * 100, 2),
        "neutral_ratings": total_neutral,
        "negative_ratings": total_negative,
        "negative_rate_pct": round((total_negative / total_count) * 100, 2),
        "clusters": results,
        "top_failing_clusters": top_3_failing,
        "failure_patterns": dict(failure_patterns),
    }


def print_analytics_report(db_path: Optional[str] = None) -> None:
    """Print formatted terminal report of feedback analytics."""
    data = analyze_feedback(db_path)

    print("=" * 80)
    print(" DAY 54: REAL USER FEEDBACK & TOPIC FAILURE ANALYSIS REPORT")
    print(" Product: AURONIX Enterprise Private AI Assistant")
    print("=" * 80)

    if data["status"] == "pending_data":
        print("\n [!] STATUS: Pending Real User Data")
        print("     No feedback recorded in SQLite database yet.")
        print("     Run 'python seed_demo_feedback.py' to populate representative benchmark data")
        print("     or submit live queries via POST /feedback.\n")
        print("=" * 80)
        return

    print(f"\nTotal Queries Analyzed: {data['total_queries']}")
    print(f"Positive Ratings (4-5*): {data['positive_ratings']} ({data['positive_rate_pct']}%)")
    print(f"Neutral Ratings  (3*):   {data['neutral_ratings']}")
    print(f"Negative Ratings (1-2*): {data['negative_ratings']} ({data['negative_rate_pct']}%)")
    print("-" * 80)

    print("\n[+] TOP 3 TOPIC CLUSTERS WITH THE HIGHEST FAILURE RATES:")
    print("-" * 80)
    print(f"{'Rank':<5} | {'Topic Cluster':<35} | {'Total':<6} | {'Failures':<8} | {'Failure Rate':<12} | {'Avg Rating'}")
    print("-" * 80)

    for idx, item in enumerate(data["top_failing_clusters"], 1):
        print(
            f"{idx:<5} | {item['topic']:<35} | {item['total_queries']:<6} | "
            f"{item['failed_queries']:<8} | {item['failure_rate_pct']:>6.1f}%      | {item['average_rating']:.2f} / 5.0"
        )

    print("-" * 80)

    print("\n[+] ALL DETECTED TOPIC CLUSTERS (RANKED BY FAILURE RATE):")
    for cluster in data["clusters"]:
        print(f"  * {cluster['topic']}:")
        print(f"      Queries: {cluster['total_queries']} | Failed: {cluster['failed_queries']} | Failure Rate: {cluster['failure_rate_pct']}% | Avg Rating: {cluster['average_rating']}/5.0")

    print("\n[+] COMMON FAILURE PATTERNS IDENTIFIED:")
    if data["failure_patterns"]:
        for pattern, count in data["failure_patterns"].items():
            print(f"  * {pattern}: {count} occurrences")
    else:
        print("  * No explicit failure patterns recorded.")

    print("=" * 80)


if __name__ == "__main__":
    print_analytics_report()
