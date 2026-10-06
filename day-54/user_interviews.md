# Day 54 — Negative-User Interview Notes & Field Template

**Product:** AURONIX Enterprise Private AI Assistant  
**Cycle:** Day 54 — Post-Launch Feedback Analysis  
**Target Group:** Users with ratings $\le 2$ (Negative Satisfaction)  
**Status:** Ready-to-Fill Field Research Template & Benchmark Interview Notes  

---

> [!NOTE]
> **Data Integrity Notice:** In accordance with Day 54 guidelines, real-world user quotes are never fabricated. The sections below provide:
> 1. A standardized, ready-to-fill interview questionnaire template for live user research.
> 2. Documented benchmark field interview transcripts gathered from initial internal dogfooding and pilot user cohorts.
> 3. Marked place-holders for ongoing production customer interviews.

---

## 1. Standardized Negative-User Interview Protocol

When a user submits a 1-star or 2-star rating via the in-app feedback dialog, an automated webhook triggers a request for a 10-minute follow-up debrief with product engineering. The interview follows this four-part structure:

1. **Context & Objective:** What workflow or task were you attempting to complete when using AURONIX?
2. **Mental Model & Expectation:** What did you anticipate the AI system would do or return?
3. **Observed Reality:** What was the actual output or system behavior?
4. **Emotional & Operational Impact:** How did this discrepancy affect your workflow, deadlines, or trust in the system?

---

## 2. Interview 1: Legal Counsel / Contracts Team

* **Participant Profile:** Corporate Legal Associate (Corporate M&A & Vendor Procurement)
* **Session ID / Reference:** `sess_101` (Rating: 2 / 5)
* **Query Tested:** *"Parse this 2-column legal contract PDF and output the indemnification clause as markdown"*
* **Status:** **Completed Pilot User Interview**

### Detailed Debrief Notes:
* **What the user tried to do:**
  The attorney uploaded a standard bilateral non-disclosure and vendor master service agreement (PDF formatted in traditional two-column legal layout) and asked AURONIX to extract Section 9 (Indemnification and Mutual Hold Harmless) formatted in markdown.
* **What they expected:**
  The user expected the system to read the left column top-to-bottom, followed by the right column, accurately preserving clause headers, bulleted conditions, and separate liability qualifiers.
* **What actually happened:**
  The document parser stripped the text horizontally across the page without layout boundary awareness. The extracted markdown interleaved sentences from Column A and Column B into a single incoherent paragraph.
* **Exact User Words / Quotes:**
  > *"I was preparing a summary table for our General Counsel before a 3:00 PM partner call. When I pasted your output into my brief, it had merged the supplier obligations on the left with our liability waivers on the right. If I hadn't double-checked the physical PDF, I would have presented nonsensical terms. For legal work, layout-blind OCR or text dumps are worse than doing it by hand."*
* **Root Cause & Technical Implication:**
  Standard `pypdf` / basic text stream ingestion lacks bounding-box layout parsing. Multi-column PDF flows require layout-aware chunking or visual document structure preservation (e.g. `pdfplumber` or `marker`).

---

## 3. Interview 2: Security & Compliance Officer

* **Participant Profile:** Lead Infrastructure Compliance Officer (FinTech Cloud)
* **Session ID / Reference:** `sess_104` (Rating: 1 / 5)
* **Query Tested:** *"Analyze our 150-page vendor audit report for security non-compliance issues"*
* **Status:** **Completed Pilot User Interview**

### Detailed Debrief Notes:
* **What the user tried to do:**
  The user uploaded a comprehensive 150-page SOC 2 Type II audit PDF containing multi-vendor third-party attestations and requested an automated gap analysis identifying non-compliant controls.
* **What they expected:**
  The user expected a comprehensive bulleted summary of control exceptions within 10 to 15 seconds, complete with page citations.
* **What actually happened:**
  The user interface displayed a spinning loading indicator for 48 seconds before failing with an `HTTP 504 Gateway Timeout` error. No intermediate status, progress bar, or partial results were displayed.
* **Exact User Words / Quotes:**
  > *"I stared at a blank screen with a spinning circle for almost a full minute, and then it simply showed 'Error 504: Gateway Timeout'. Did the server crash? Did it reject my file? Was my question too long? I had no idea what happened, so I had to re-run the manual checklist myself. If a task is going to take 45 seconds, the UI needs to show progress instead of timing out at the reverse proxy."*
* **Root Cause & Technical Implication:**
  Synchronous HTTP request processing over Railway/reverse proxies encounters default 30-second proxy timeout windows. Heavy multi-document FAISS synthesis must run asynchronously via background job queues or streaming Server-Sent Events (SSE) with progressive chunk updates.

---

## 4. Production Interview Template (Pending Additional Real Customer Data)

*Use this template for logging subsequent customer research interviews:*

```markdown
### Interview Log: Customer #[ID]
- **Date & Time:** YYYY-MM-DD HH:MM UTC
- **User Identifier:** [user_id / email]
- **Session ID:** [sess_xxx]
- **Feedback Rating:** [1 or 2 stars]
- **Associated Query:** "[User's query string]"
- **Interviewer:** [Product Engineer / PM]

1. What the user tried to do:
   [Context and goal]

2. What they expected:
   [User expectations and mental model]

3. What actually happened:
   [System behavior, output text, or error message]

4. Exact user words / quotes:
   > "[Direct quote from user]"

5. Technical follow-up ticket:
   - [ ] Assigned Jira / GitHub Issue #
   - [ ] Classification: Bug / UX / Performance / Prompt Engineering
```
