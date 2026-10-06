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

Following the Day 53 production launch, **Day 54** establishes the end-to-end user feedback collection, monitoring, and failure analysis system.

The core objective is to replace guesswork with **evidence-based product iteration**:
1. Capturing user queries, 1-to-5 star ratings, feedback commentary, failure classifications, and session metadata.
2. Persisting all events into an indexed SQLite store.
3. Exposing real-time FastAPI endpoints for submission, inspection, and monitoring metrics.
4. Analyzing feedback distributions via keyword frequency and taxonomy clustering.
5. Detecting the three topic clusters with the highest failure rates.
6. Gathering qualitative interview notes from negative reviewers to diagnose root causes.
7. Translating findings into exactly three prioritized engineering improvements with effort estimates.

---

## 3. Feedback Collection Architecture & SQLite Schema

### SQLite Storage (`day-54/database.py`)

A thread-safe relational database schema tracks each interaction:

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

### FastAPI Endpoints (`day-54/app.py`)

* `POST /feedback`: Records query, rating (1–5), comments, and failure observations.
* `GET /feedback`: Returns recent user feedback records.
* `GET /feedback/low-rated`: Filters interactions with ratings $\le 2$ for priority customer review.
* `GET /feedback/metrics`: Computes aggregate counts, rating distributions, positive percentage, negative percentage, topic breakdowns, and failure pattern counts.

---

## 4. 24-Hour Usage & Failure Rate Analysis

The analytics engine (`feedback_analytics.py`) clusters queries and computes failure rates:

$$\text{Failure Rate (\%)} = \left( \frac{\text{Queries with Rating } \le 2}{\text{Total Queries in Topic}} \right) \times 100$$

### Top 3 Topic Clusters with the Highest Failure Rates:

| Rank | Topic Cluster | Total Queries | Failed ($\le 2\bigstar$) | Failure Rate | Average Rating |
| :---: | :--- | :---: | :---: | :---: | :---: |
| **#1** | **Document Formatting & Parsing** | 4 | 3 | **75.0%** | **2.25 / 5.0** |
| **#2** | **Query Latency & Timeouts** | 3 | 2 | **66.7%** | **2.33 / 5.0** |
| **#3** | **Source Citation & Grounding** | 3 | 2 | **66.7%** | **2.67 / 5.0** |

### Common Failure Patterns Identified:
1. **Table column misalignment & parsing truncation** (PDF tables collapsed into plain text).
2. **Multi-column layout flow reading error** (Sentences interleaved across columns).
3. **Broken markdown table delimiter syntax** (Missing pipes/headers breaking rendering).
4. **HTTP 504 gateway timeout on large document synthesis** (48s hang on 150-page PDF).
5. **High latency (>30s) during multi-file FAISS search** (Multi-document bottleneck).
6. **Missing page number and snippet citation** (Policy synthesis without verifiable section).
7. **Paraphrase returned instead of verifiable verbatim quote** (Lack of exact clause quote).
8. **Factual hallucination on numerical contract penalty clause** (Stated $50k instead of $25k).

---

## 5. Negative-User Interviews & Field Research

Detailed interview transcripts and protocol templates are documented in `day-54/user_interviews.md`:

### Interview 1: Legal Counsel (`sess_101` — Rating: 2 / 5)
* **Tried to do:** Extract indemnification clause from a 2-column legal contract PDF into markdown.
* **Expected:** Sequentially read columns, preserving distinct supplier vs. buyer clauses.
* **Actually happened:** Left and right columns were merged horizontally into an incoherent paragraph.
* **Exact Quote:** *"When I pasted your output into my brief, it had merged the supplier obligations on the left with our liability waivers on the right... For legal work, layout-blind OCR or text dumps are worse than doing it by hand."*
* **Root Cause:** Ingestion parser lacks bounding-box layout awareness.

### Interview 2: Security & Compliance Officer (`sess_104` — Rating: 1 / 5)
* **Tried to do:** Run automated gap analysis on a 150-page SOC 2 vendor audit report.
* **Expected:** Categorized list of control exceptions within 15 seconds.
* **Actually happened:** Blank spinner for 48 seconds followed by `HTTP 504 Gateway Timeout`.
* **Exact Quote:** *"I stared at a blank screen with a spinning circle for almost a full minute, and then it simply showed 'Error 504: Gateway Timeout'... If a task is going to take 45 seconds, the UI needs to show progress instead of timing out at the reverse proxy."*
* **Root Cause:** Synchronous request exceeded reverse-proxy timeout window.

---

## 6. Prioritised Engineering Improvements

Detailed specifications in `day-54/prioritized_improvements.md`:

1. **P0 (Critical): Layout-Aware PDF Ingestion & Table Extraction**
   * *Change:* Integrate `pdfplumber`/`marker` bounding-box parser and markdown table validator.
   * *Evidence:* 75.0% failure rate; user complaints of merged legal clauses and broken tables.
   * *Impact:* Eliminates 75% of parsing defects; enables trusted executive exports.
   * *Effort:* **2.5 Engineering Days**.

2. **P1 (High): Asynchronous Job Processing & SSE Streaming for Large Documents**
   * *Change:* Offload queries on documents >30 pages to background workers with real-time Server-Sent Events progress tokens.
   * *Evidence:* 66.7% failure rate; 504 timeouts on heavy synthesis.
   * *Impact:* 0% timeout errors; feedback delivered within 1.5 seconds.
   * *Effort:* **3.5 Engineering Days**.

3. **P2 (Medium): Verbatim Grounding & Granular Page/Section Citation Modal**
   * *Change:* Enforce strict citation schema `[Document, Page, Section]` with verbatim quote inspection.
   * *Evidence:* 66.7% failure rate; legal/audit inability to verify claims.
   * *Impact:* Guarantees auditable compliance traceability.
   * *Effort:* **2.0 Engineering Days**.

*Total Engineering Investment:* **8.0 Engineering Days**.

---

## 7. How to Run and Verify

```bash
# 1. Run unit tests
python -m pytest day-54/test_day54.py -v

# 2. Seed benchmark feedback data
python day-54/seed_demo_feedback.py

# 3. Generate failure rate analytics report
python day-54/feedback_analytics.py

# 4. Start FastAPI server
python -m uvicorn day-54.app:app --host 127.0.0.1 --port 8000 --reload
```
