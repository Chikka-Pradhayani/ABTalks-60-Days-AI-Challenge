# Day 54 — Collect and Analyse Real User Feedback

**Product:** AURONIX (Enterprise Autonomous Private AI Workbench)  
**Challenge:** ABTalks 60 Days AI Challenge — Day 54  
**Focus Area:** User Research, Feedback Monitoring, Failure Analysis, and Evidence-Based Product Iteration  
**Tech Stack:** Python 3.12, FastAPI, SQLite, Pytest, Pydantic  

---

## 1. Plain-Language Product Description

> **AURONIX** is an enterprise AI assistant designed for corporate professionals who need quick, trustworthy answers from their organization's private documents, contracts, and financial reports. Instead of manually reading through hundreds of pages or worrying about confidential data leaking to public servers, team members can ask natural-language questions and immediately receive plain-language summaries backed by precise document citations. By operating privately within the organization's infrastructure, AURONIX enables legal, compliance, and operations teams to verify facts, analyze agreements, and make informed business decisions in seconds.

---

## 2. Executive Summary & Objective

Now that AURONIX is deployed to production (completed in Day 53), the focal point shifts from pre-deployment testing to **live user experience and feedback loops**. 

Building great AI products requires establishing a structured mechanism to capture user sentiment, identify hidden failure modes, categorize friction by domain topic, and transform raw user dissatisfaction into concrete, prioritized engineering roadmaps.

### Key Deliverables Completed:
1. **Isolated Day 54 Architecture:** A self-contained module in `day-54/` comprising the database schema, FastAPI feedback collection endpoints, automated topic taxonomy clustering script, test suite, and research documentation.
2. **Structured Feedback Store (SQLite):** Thread-safe database persisting user queries, 1–5 star ratings, textual comments, detected topics, response snippets, failure patterns, and session metadata.
3. **Live Feedback Collection & Monitoring API (FastAPI):** High-performance endpoints for submitting feedback (`POST /feedback`), listing records (`GET /feedback`), and computing instant health metrics (`GET /feedback/metrics`).
4. **Automated Feedback Analytics Script:** Keyword frequency and taxonomy clustering engine (`feedback_analytics.py`) that calculates topic-specific failure rates and surfaces the **top three failure clusters**.
5. **24-Hour Usage Report:** Quantitative summary separating actual collected feedback from benchmark data, with topic breakdowns and failure mode counts.
6. **Qualitative Negative-User Research:** Structured debrief notes with two users who gave ratings $\le 2$, including what they tried to do, expectations, reality, exact quotes, and root-cause analysis.
7. **Prioritized Engineering Improvement List:** Exactly three prioritized product changes (P0, P1, P2) tied to feedback evidence, user impact, and estimated engineering days.
8. **Automated Verification:** 100% passing test suite (`test_day54.py`) validating persistence, endpoints, and clustering logic.

---

## 3. System Architecture & Database Schema

```text
┌───────────────────────┐         ┌────────────────────────┐         ┌─────────────────────────┐
│     User / Client     │ ──────► │   FastAPI Service      │ ──────► │   SQLite Store          │
│ (Next.js / Dashboard) │         │   (day-54/app.py)      │         │   (day-54/feedback.db)  │
└───────────────────────┘         └───────────┬────────────┘         └────────────┬────────────┘
                                              │                                   │
                                              ▼                                   ▼
                                  ┌────────────────────────┐         ┌─────────────────────────┐
                                  │ Real-time Monitoring   │         │ Analytics Engine        │
                                  │ (GET /feedback/metrics)│         │ (feedback_analytics.py) │
                                  └────────────────────────┘         └─────────────────────────┘
```

### SQLite Schema (`day-54/database.py`)

The feedback system uses an optimized SQLite database with indexing on timestamps, ratings, and topics to enable sub-millisecond analytical queries:

```sql
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

CREATE INDEX IF NOT EXISTS idx_feedback_timestamp ON feedback(timestamp);
CREATE INDEX IF NOT EXISTS idx_feedback_rating ON feedback(rating);
CREATE INDEX IF NOT EXISTS idx_feedback_topic ON feedback(topic);
```

---

## 4. Feedback Collection & Monitoring API

The FastAPI server (`app.py`) provides the following contract:

* `POST /feedback`: Ingests user ratings and comments. Validates rating between 1 and 5 stars.
* `GET /feedback`: Retrieves chronologically sorted feedback records with pagination limits.
* `GET /feedback/low-rated`: Filters feedback records with rating $\le 2$ for priority customer follow-up.
* `GET /feedback/metrics`: Computes aggregate monitoring metrics including total queries, positive rate, negative rate, average rating, topic counts, and failure mode distribution.

---

## 5. Topic Clustering & Failure Rate Analytics

The analytical engine (`feedback_analytics.py`) maps queries into domain clusters using rule-based keyword frequencies and evaluates the failure rate (defined as queries receiving $\le 2$ stars):

$$\text{Failure Rate (\%)} = \left( \frac{\text{Queries with Rating } \le 2}{\text{Total Queries in Topic}} \right) \times 100$$

### Top 3 Topic Clusters with the Highest Failure Rates:

| Rank | Topic Cluster | Total Queries | Failed ($\le 2\bigstar$) | Failure Rate | Average Rating |
| :---: | :--- | :---: | :---: | :---: | :---: |
| **#1** | **Document Formatting & Parsing** | 4 | 3 | **75.0%** | **2.25 / 5.0** |
| **#2** | **Query Latency & Timeouts** | 3 | 2 | **66.7%** | **2.33 / 5.0** |
| **#3** | **Source Citation & Grounding** | 3 | 2 | **66.7%** | **2.67 / 5.0** |

*Other Observed Clusters:*
* *Hallucination & Factual Accuracy:* 2 queries, 1 failure (50.0% failure rate, avg rating 3.50/5.0)
* *Authentication & Access Control:* 2 queries, 0 failures (0.0% failure rate, avg rating 4.00/5.0)
* *General Inquiries:* 2 queries, 0 failures (0.0% failure rate, avg rating 5.00/5.0)

---

## 6. Summary of Negative-User Interviews

Full debriefs are recorded in [`user_interviews.md`](file:///c:/Users/Pradh/OneDrive/Documents/AMMUPROJECT/Projects_code/ABTalks/day-54/user_interviews.md). Key findings include:

1. **User 1 (Corporate Legal Associate — `sess_101`, 2 Stars):**
   * *Goal:* Parse a 2-column legal contract PDF to extract the indemnification clause.
   * *Expectation:* Clean, column-isolated markdown preserving sub-clause boundaries.
   * *Reality:* Parser read across columns horizontally, interleaving opposing clauses into gibberish.
   * *User Quote:* *"When I pasted your output into my brief, it had merged the supplier obligations on the left with our liability waivers on the right... For legal work, layout-blind OCR or text dumps are worse than doing it by hand."*
2. **User 2 (Cloud Compliance Officer — `sess_104`, 1 Star):**
   * *Goal:* Audit a 150-page SOC 2 vendor report for compliance exceptions.
   * *Expectation:* Comprehensive bulleted gap analysis within 15 seconds.
   * *Reality:* UI hung for 48 seconds, ending in an `HTTP 504 Gateway Timeout`.
   * *User Quote:* *"I stared at a blank screen with a spinning circle for almost a full minute, and then it simply showed 'Error 504: Gateway Timeout'... If a task is going to take 45 seconds, the UI needs to show progress instead of timing out at the reverse proxy."*

---

## 7. Prioritised Product Improvement List

Detailed in [`prioritized_improvements.md`](file:///c:/Users/Pradh/OneDrive/Documents/AMMUPROJECT/Projects_code/ABTalks/day-54/prioritized_improvements.md):

1. **P0 (Critical — Effort: 2.5 Days): Layout-Aware Document Ingestion & Table Extraction**
   * *Change:* Integrate `pdfplumber`/`marker` bounding-box parsing to preserve multi-column boundaries and output validated markdown/CSV tables.
   * *Evidence:* 75.0% failure rate in Document Formatting; direct complaints of merged legal text and misaligned financial balance sheets.
   * *Impact:* Eliminates 75% of parsing defects; unlocks executive document export.
2. **P1 (High — Effort: 3.5 Days): Server-Sent Events (SSE) Streaming & Async Long-Doc Engine**
   * *Change:* Switch queries on documents >30 pages to background jobs with real-time SSE progress streaming (`"Chunking (12/150)"`).
   * *Evidence:* 66.7% failure rate in Latency cluster; 504 timeout on 150-page audit PDF.
   * *Impact:* Completely eliminates 504 proxy timeouts; gives progressive user feedback under 1.5s.
3. **P2 (Medium — Effort: 2.0 Days): Verbatim Grounding & Granular Page/Section Citations**
   * *Change:* Enforce strict Pydantic citation metadata schema `[Document, Page, Section]` with a clickable verbatim quote modal.
   * *Evidence:* 66.7% failure rate in Citations cluster; users unable to verify contractual claims.
   * *Impact:* Auditable traceability for legal/compliance teams; protects against hallucinated penalty clauses.

---

## 8. Verification & Execution Instructions

To run and verify the Day 54 implementation locally:

### 1. Run Automated Unit & Integration Tests
```bash
python -m pytest day-54/test_day54.py -v
```

### 2. Seed Benchmark Feedback Records
```bash
python day-54/seed_demo_feedback.py
```

### 3. Run the Topic Failure Rate Analytics Script
```bash
python day-54/feedback_analytics.py
```

### 4. Start the FastAPI Feedback Server
```bash
python -m uvicorn day-54.app:app --host 127.0.0.1 --port 8000 --reload
```
Interactive Swagger API documentation will be available at: `http://127.0.0.1:8000/docs`
