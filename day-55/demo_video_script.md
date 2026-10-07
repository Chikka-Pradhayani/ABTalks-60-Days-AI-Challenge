# Three-Minute Loom Demo Script & Storyboard: AURONIX

> **Recording Status:** Scripted and Storyboarded (Ready for Recording)  
> *Note: This document provides the exact production script, visual cues, and preparation checklist for recording a concise, recruiter-ready 3-minute technical walkthrough of AURONIX on Loom.*

---

## Technical Overview & Metadata
* **Product:** AURONIX (Enterprise Autonomous Private AI Workbench)
* **Target Audience:** Engineering Hiring Managers, AI Tech Leads, and Senior AI Engineers
* **Format:** Loom (Camera bubble bottom-left, browser window full screen)
* **Target Duration:** Exactly 3 minutes (180 seconds)

---

## Scene-by-Scene Storyboard & Script

### Segment 1: Introduction (0:00 – 0:20 | 20 seconds)
* **Visual:** Full-screen browser displaying the AURONIX Next.js 14 Workbench UI (`http://localhost:3000` or `https://auronix-app.vercel.app`) with the headline: *"AURONIX — Enterprise Autonomous Private AI Workbench"*.
* **Camera:** Presenter visible in bottom-left circle, looking into camera.
* **Script:**
  > *"Hi everyone, I'm Pradhayani. When engineering, legal, or DevOps teams need answers during a production outage or compliance audit, digging through hundreds of pages of internal wikis wastes critical time—and pasting proprietary company IP into consumer chatbots introduces serious security risks.*  
  > *This is **AURONIX**: an autonomous, private enterprise AI workbench designed to deliver verified, citation-grounded operational answers from internal runbooks and contracts with deterministic reliability."*

---

### Segment 2: Live Product Demo (0:20 – 1:20 | 60 seconds)
* **Visual:** Browser interaction.
  1. *[0:20]* Type an operational query into the prompt input box:  
     `"What is the escalation procedure and first action for a P0 incident, and who needs to be paged?"`
  2. *[0:25]* Click "Submit" (or hit Enter).
  3. *[0:30]* Camera pans to streaming response: Observe real-time token rendering via Server-Sent Events (SSE) and live latency telemetry tag (`~180ms latency`).
  4. *[0:45]* Highlight the structured three-section output:
     * `Answer:` Concise, step-by-step incident protocol.
     * `Sources:` Click the source pill to open the citation card displaying `CORP-OPS-001 (P0/P1 Incident Runbook)`.
     * `Confidence:` Showing `High (0.94)`.
  5. *[1:00]* Submit a follow-up pronoun question: `"What Slack channel do they use?"`  
     Point out that the system immediately resolves the conversational context to the Core Incident response team and answers accurately without context loss.
* **Script:**
  > *"Let's look at the live workbench in action. I'll ask a critical operational question: 'What is the escalation procedure for a P0 incident, and who gets paged?'*  
  > *As I submit, you can see the response streaming in real time via Server-Sent Events with execution telemetry. Notice that AURONIX doesn't just dump conversational text. It enforces a strict, machine-parseable contract: an executive Answer, exact document citations linking to our `CORP-OPS-001` incident runbook, and a calibrated confidence score.*  
  > *If I ask a follow-up with pronouns—'What Slack channel do they use?'—the conversational rewriter automatically maps the elliptical query to the incident response team, retrieving the exact war-room channel without missing a beat."*

---

### Segment 3: Architecture Decision (1:20 – 2:10 | 50 seconds)
* **Visual:** Switch browser tab to the Mermaid Architecture Diagram in `day-50/README.md` or `day-55/auronix_product_page.md`. Highlight the multi-stage retrieval block (HyDE, Query Rewriter, Cross-Attention Re-ranking) and Redis Semantic Caching.
* **Script:**
  > *"Under the hood, we made a crucial architecture decision: we moved beyond naive single-vector similarity search.*  
  > *In testing, we found that colloquial queries—like 'If everything crashes, what's the playbook?'—suffered severe semantic mismatch with formal corporate documentation. Standard bi-encoder vector search dropped the critical runbook completely, scoring just 2.0 out of 5.*  
  > *Instead of blindly increasing chunk size or switching to expensive frontier models, we engineered a multi-stage pipeline combining Hypothetical Document Embeddings (HyDE) and cross-attention candidate re-ranking.*  
  > *HyDE shifts search into document-to-document embedding space, lifting retrieval quality by **+0.67 points** with zero latency penalty. Then, cross-attention re-ranks the top 10 candidates down to the top 3, boosting factual precision by **+1.07 points** while keeping prompt tokens compact and cost-efficient."*

---

### Segment 4: Engineering Challenge (2:10 – 2:40 | 30 seconds)
* **Visual:** Switch tab to the Day 50 Evaluation Summary Report (`day-50/reports/evaluation_summary_report.md`), highlighting the Hard Tier score progression table (`3.69 -> 4.52`) and Hallucination Avoidance table (`3.57 -> 4.70`).
* **Script:**
  > *"Our hardest technical challenge surfaced during our automated 30-question benchmark. Baseline evaluation revealed that on Hard-tier queries, our system scored only 3.69 out of 5, and Hallucination Avoidance dropped to 3.57.*  
  > *The root cause was LLM sycophancy: when users asked questions with false assumptions—like asking how Puppet manages Aurora database failovers—the model fabricated fictitious scripts to be agreeable.*  
  > *Lowering temperature to zero failed. We solved this by implementing technical keyphrase boosting (+0.75) and embedding explicit negative-constraint refutation contracts in System Prompt v2. On re-evaluation, Hallucination Avoidance surged by **+1.13 points to 4.70 / 5.0**, and our automated regression gates passed with zero deficit."*

---

### Segment 5: Reflection & Future Work (2:40 – 3:00 | 20 seconds)
* **Visual:** Return to the live app or Day 54 Feedback Analysis report (`day-54/usage_report_24h.md`), highlighting the 75% PDF parsing failure finding. Presenter looks directly into camera.
* **Script:**
  > *"If I were building AURONIX again from day one, I would prioritize layout-aware document ingestion earlier. In our Day 54 user feedback analysis, 75% of negative reviews stemmed from multi-column PDF tables interleaving into plain text.*  
  > *Our immediate next sprint integrates bounding-box layout parsing and asynchronous background workers for 100+ page documents.  
  > Thanks for watching—all source code, evaluation datasets, and CI/CD pipelines are available on my GitHub repository!"*

---

## Pre-Recording Checklist
- [ ] Next.js frontend running locally (`npm run dev` in `Day-49/` on port 3000) or verify live Vercel URL.
- [ ] FastAPI backend running (`python -m uvicorn day-53.backend.main:app --port 8001`) with Redis cache connected or fallback active.
- [ ] Pre-warm browser tabs:
  - Tab 1: Live Workbench interface with clean session.
  - Tab 2: Architecture diagram (`day-55/auronix_product_page.md` rendered).
  - Tab 3: Evaluation results report (`day-50/reports/evaluation_summary_report.md`).
- [ ] Test sample queries in advance to verify low latency response and proper SSE token streaming.
- [ ] Frame Loom recording: Mic tested, 1080p resolution selected, webcam background clear, 3-minute timer visible.
