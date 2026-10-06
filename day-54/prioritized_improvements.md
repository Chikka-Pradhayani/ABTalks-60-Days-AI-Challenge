# Day 54 — Prioritised Product Improvement Roadmap

**Product:** AURONIX Enterprise Private AI Assistant  
**Source Evidence:** Day 54 User Feedback Analytics & Qualitative Pilot User Interviews  
**Methodology:** Impact vs. Effort Framework (RICE / ICE prioritization)  

---

## Overview

Based on our empirical feedback monitoring (16 benchmarked interaction cycles, 50% dissatisfaction rate in complex enterprise queries) and in-depth debriefs with negative reviewers, we have isolated three critical failure domains:
1. **Document Formatting & Parsing** (75.0% failure rate)
2. **Query Latency & Timeouts** (66.7% failure rate)
3. **Source Citation & Grounding** (66.7% failure rate)

Below are the **exactly 3 prioritized product engineering improvements**, structured with supporting feedback evidence, anticipated business and user impact, and concrete engineering sizing.

---

### Priority 1: High-Fidelity Table Extraction & Layout-Aware Document Ingestion

* **Priority:** **P0 (Critical — Immediate Sprint)**
* **Specific Product Change:**
  Replace naive flat text PDF extraction with a structured, layout-aware parsing pipeline. Integrate `pdfplumber` / `marker` table detection to extract tabular data directly into native GitHub-flavored Markdown tables and CSV representations, preserving multi-column boundaries and column headers. Add automated post-processing validation to ensure markdown table delimiters (`|`) are balanced before outputting to the user.
* **Supporting Evidence from Feedback:**
  * **Analytics Evidence:** Highest observed topic failure rate at **75.0%** across 4 evaluation queries.
  * **Observed Failure Patterns:** "Table column misalignment and parsing truncation", "Multi-column layout flow reading error", and "Broken markdown table delimiter syntax".
  * **User Debrief Quote:** *"When I pasted your output into my brief, it had merged the supplier obligations on the left with our liability waivers on the right... For legal work, layout-blind OCR or text dumps are worse than doing it by hand."* (`sess_101`)
* **Expected User Impact:**
  * Eliminates 75% of parsing errors in financial balance sheets, legal briefs, and vendor contracts.
  * Unlocks high-confidence copy-pasting for executive deliverables, saving 15–20 minutes of manual reformatting per report.
  * Drives a projected rating recovery from **2.25 / 5.0** to **> 4.2 / 5.0** for document formatting tasks.
* **Estimated Engineering Effort:**
  * **2.5 Engineering Days (1 Senior Backend Engineer)**:
    * 0.5 day: Ingestion pipeline update with `pdfplumber` table boundary recognition.
    * 1.0 day: Markdown table post-formatter and linter.
    * 1.0 day: Regression test fixtures across 10 multi-column PDF samples.

---

### Priority 2: Asynchronous Job Processing & SSE Streaming for Long Document Queries

* **Priority:** **P1 (High — Next Sprint)**
* **Specific Product Change:**
  Transition heavy RAG synthesis queries (documents > 30 pages or multi-file queries) from synchronous request-response HTTP endpoints to an asynchronous job execution model with **Server-Sent Events (SSE)** streaming. The client immediately receives an HTTP 202 Accepted with a job token and opens an SSE stream showing real-time stage progress (`"Chunking document (12/150)"`, `"Synthesizing compliance risks (4/18)"`), preventing reverse-proxy 504 timeouts.
* **Supporting Evidence from Feedback:**
  * **Analytics Evidence:** **66.7% failure rate** and lowest average rating (**2.33 / 5.0**) in the Query Latency & Timeouts topic cluster.
  * **Observed Failure Patterns:** "HTTP 504 gateway timeout on large document synthesis" (48-second hang) and "High latency (>30s) during multi-file FAISS similarity search".
  * **User Debrief Quote:** *"I stared at a blank screen with a spinning circle for almost a full minute, and then it simply showed 'Error 504: Gateway Timeout'... If a task is going to take 45 seconds, the UI needs to show progress instead of timing out at the reverse proxy."* (`sess_104`)
* **Expected User Impact:**
  * Zero 504 Gateway Timeout errors regardless of document size.
  * Dramatic reduction in perceived latency: users receive progressive token and status updates within 1.5 seconds instead of waiting blind.
  * Restores user confidence when operating during live meetings or time-critical reviews.
* **Estimated Engineering Effort:**
  * **3.5 Engineering Days (1 Fullstack / Backend Engineer)**:
    * 1.5 days: FastAPI background tasks / streaming response endpoint implementation (`StreamingResponse` / SSE).
    * 1.0 day: Next.js frontend event-source consumer and progress state bar.
    * 1.0 day: Railway / reverse proxy keep-alive configuration and end-to-end load verification.

---

### Priority 3: Verbatim Grounding & Granular Page/Section Citation Metadata

* **Priority:** **P2 (Medium — Subsequent Sprint)**
* **Specific Product Change:**
  Enforce strict citation schemas on all RAG synthesis outputs. Update system prompts and vector chunk metadata extraction so that every factual claim includes `[Document Name, Page X, Section Y.Z]` and a clickable verbatim quote snippet modal. If the exact answer is not present in the indexed text, instruct the model to explicitly state "Information not found in provided sources" rather than paraphrasing speculative answers.
* **Supporting Evidence from Feedback:**
  * **Analytics Evidence:** **66.7% failure rate** in the Source Citation & Grounding cluster.
  * **Observed Failure Patterns:** "Missing page number and snippet citation in RAG output" and "Paraphrase returned instead of verifiable verbatim quote".
  * **User Debrief:** HR manager (`sess_106`) and procurement lead (`sess_107`) noted they could not legally rely on paraphrased policy statements without verifying source page numbers.
* **Expected User Impact:**
  * Zero hallucinated or unverifiable contractual clauses.
  * Auditable compliance traceability for enterprise risk, legal, and auditing teams.
  * Elevates product trust score and enables enterprise compliance sign-off.
* **Estimated Engineering Effort:**
  * **2.0 Engineering Days (1 AI / Prompt Engineer)**:
    * 0.5 day: Embed page and section metadata during PyPDF/vector store chunk creation.
    * 1.0 day: Structured Pydantic citation output schema and prompt grounding few-shot examples.
    * 0.5 day: Regression tests against Day 50 benchmark queries.

---

## Prioritization Summary Matrix

| Rank | Improvement Initiative | Primary Topic Cluster | Failure Rate | Priority | Expected Rating Impact | Engineering Effort |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| **#1** | **Layout-Aware PDF & Table Parser** | Document Formatting & Parsing | **75.0%** | **P0** | $2.25 \rightarrow 4.50$ | 2.5 Days |
| **#2** | **SSE Streaming & Async Large-Doc Engine** | Query Latency & Timeouts | **66.7%** | **P1** | $2.33 \rightarrow 4.30$ | 3.5 Days |
| **#3** | **Verbatim Page/Section Citation Modal** | Source Citation & Grounding | **66.7%** | **P2** | $2.67 \rightarrow 4.60$ | 2.0 Days |

*Total Engineering Investment:* **8.0 Engineering Days** to resolve top 3 enterprise churn drivers.
