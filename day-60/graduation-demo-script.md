# Day 60 — 10-Minute Loom Graduation Demo Script & Recording Checklist 🎙️

**Presenter:** Pradhayani Chikka  
**Target Duration:** Exactly 10:00 Minutes  
**Platform:** Loom / Screen Recording  
**System Demonstrated:** AURONIX (Enterprise Autonomous Private AI Workbench)  
**Date:** 2026-10-12  

---

## 1. Demo Preparation & Setup Checklist

Before pressing record on Loom, complete this physical and technical preparation checklist:

### Environment & Audio Setup
- [ ] Quiet recording room; microphone input levels tested and set to clean gain.
- [ ] Loom resolution configured to 1080p (60fps preferred); webcam bubble positioned in the bottom-left corner.
- [ ] Close all unrelated browser tabs, messaging apps (Slack, Discord, WhatsApp), and desktop notifications.

### Application Runtime Setup
- [ ] Open Terminal 1: Backend service running locally or verified live:
  ```powershell
  python server.py  # or uvicorn day-53.backend.main:app --port 8001
  ```
- [ ] Open Terminal 2: Test runner ready to execute live regression checks:
  ```powershell
  python day-50/regression_test_runner.py
  ```
- [ ] Open Browser Tab 1: AURONIX Web Client (`http://localhost:3000` or `https://auronix-app.vercel.app`).
- [ ] Open Browser Tab 2: Official GitHub Repository ([Chikka-Pradhayani/ABTalks-60-Days-AI-Challenge](https://github.com/Chikka-Pradhayani/ABTalks-60-Days-AI-Challenge)).
- [ ] Open VS Code / IDE: Focused on `day-52/semantic_cache.py` and `day-50/auronix_pipeline.py`.

---

## 2. Timed 10-Minute Spoken Script & Screen Actions

```text
┌────────────────────────────────────────────────────────────────────────┐
│               10-MINUTE GRADUATION DEMO TIMELINE OVERVIEW              │
├─────────────┬──────────────────────────────────────────────────────────┤
│ 0:00 - 1:00 │ Introduction & The 60-Day Engineering Journey            │
│ 1:00 - 3:30 │ Live Demonstration of AURONIX Working                    │
│ 3:30 - 5:30 │ Architecture Deep-Dive & Component Responsibilities      │
│ 5:30 - 7:00 │ Three Critical Engineering Trade-offs                    │
│ 7:00 - 8:30 │ Empirical Evaluation Scores & Day 50 Baseline Comparison │
│ 8:30 - 9:30 │ Meaningful Failures, Root Causes & Post-Launch Feedback  │
│ 9:30 - 10:00│ Graduation Conclusion & Community Call to Action         │
└─────────────┴──────────────────────────────────────────────────────────┘
```

---

### [0:00 – 1:00] Introduction & The 60-Day Engineering Journey

**Screen Action:** Full webcam view or split-screen showing the GitHub repository homepage and Day 60 directory.

**Spoken Script:**
> *"Hello everyone! I'm Pradhayani Chikka, and today marks Day 60—the final graduation milestone of my intensive ABTalks 60 Days AI Engineering Challenge.*
> 
> *Over the past two months, my goal was not simply to call LLM APIs or build toy chatbots. It was to develop the disciplined instincts of an AI systems engineer—moving systematically from fundamental data quality intuitions on Day 6, through high-dimensional vector spaces and agentic reasoning in Days 20 to 35, all the way to architecting, hardening, and deploying a full-stack, enterprise-grade private AI system: **AURONIX**.*
> 
> *Today, I'm excited to walk you through what I built, how it performs under rigorous automated benchmarks, the critical failures I diagnosed and resolved along the way, and what this journey taught me about real-world applied AI."*

---

### [1:00 – 3:30] Live Demonstration of AURONIX Working

**Screen Action:** Switch screen share to the AURONIX Web Interface (`Day-49/` UI or live web app).

**Action 1 (Warm Cache Hit — Instant Sub-20ms Retrieval):**
- Type: *"What is the database failover procedure for Aurora PostgreSQL?"*
- Hit Enter. Point out the instantaneous response, source citation (`CORP-OPS-001.md`), and telemetry tag.

**Spoken Script:**
> *"Here is the AURONIX workbench interface. Let's start with a standard operational question: 'What is the database failover procedure for Aurora PostgreSQL?'*
> 
> *Notice that response: it returned in under 3 milliseconds with zero tokens billed. Why? Because our calibrated semantic cache identified this query with over 0.92 cosine similarity against our verified incident index. You can see the exact document citation—CORP-OPS-001—and the structured confidence score right here on screen."*

**Action 2 (Adversarial False-Premise Query — Deterministic Refutation):**
- Type: *"Since AURONIX automatically reboots the entire AWS cloud datacenter when replication lag exceeds 15 seconds, what IAM command triggers that cloud datacenter shutdown?"*
- Hit Enter. Show the response refuting the false assumption.

**Spoken Script:**
> *"Now let's test how AURONIX handles adversarial traps. Here's a question containing a completely false technical premise: asking for an IAM command to reboot an entire AWS datacenter. A naive chatbot would be sycophantic—it would apologize and hallucinate fictional CLI commands.*
> 
> *Watch how AURONIX responds: it immediately refutes the false premise, explicitly states that datacenter reboots are not configured, and instead directs the engineer to the verified promotion runbook promote_replica.sh. That is architectural safety in action."*

**Action 3 (Missing Knowledge & Abstention):**
- Type: *"What is the quantum encryption satellite link serial number?"*
- Hit Enter. Show clean refusal: *"I cannot answer this based on the provided documentation."*

**Spoken Script:**
> *"And finally, when asked about non-existent or out-of-domain systems like quantum satellite links, AURONIX doesn't guess. It triggers an immediate zero-hallucination abstention. No confabulation, no hallucinated specs."*

---

### [3:30 – 5:30] Architecture Deep-Dive & Component Responsibilities

**Screen Action:** Switch screen to VS Code showing the Mermaid architecture diagram in `day-60/README.md` or `day-59/README.md`.

**Spoken Script:**
> *"Now let's examine the architectural pipeline that makes this deterministic behavior possible.*
> 
> *AURONIX is built across five decoupled layers:
> First, our **Presentation Layer** in Next.js 14 handles real-time Server-Sent Events (SSE) streaming and interactive telemetry cards.
> 
> Second, our **FastAPI Gateway** enforces defense-in-depth: header-based API key authentication, sliding-window rate limiting of 20 requests per hour, and an input normalizer that strips invisible zero-width bytes and homoglyphs.
> 
> Third, our **Semantic Caching Layer** in day-52 vectorizes queries into 256-dimensional unit representations. If cosine similarity is 0.92 or higher, it short-circuits directly to the user in 2 to 3 milliseconds.
> 
> Fourth, on cache misses, our **Hybrid Retrieval Engine** queries our 50-document corporate corpus using FAISS exact inner product search, combined with lexical keyphrase boosting that adds a +0.75 score boost for exact terminology matches and breadcrumb context injection.
> 
> Finally, our **Hardened Generator** produces answers strictly according to our V2 System Prompt Contract with schema validation, while our **SQLite persistence layer** in WAL mode captures audit logs and live user feedback without blocking the main thread."*

---

### [5:30 – 7:00] Three Critical Engineering Trade-offs

**Screen Action:** Highlight `day-52/semantic_cache.py` and `day-54/database.py` in the code editor.

**Spoken Script:**
> *"Throughout this journey, I had to make several critical engineering trade-offs:
> 
> **Trade-off 1:** Exact Flat Vector Search versus Approximate Clustering. I chose FAISS IndexFlatIP exact search over approximate methods like HNSW or IndexIVFFlat. For our 185-chunk enterprise corpus, exact search executes in under 0.5 milliseconds with 100% recall precision. Introducing approximate indexing prematurely would have added tuning complexity for zero latency gain.
> 
> **Trade-off 2:** SQLite with Write-Ahead Logging versus a Distributed Cloud PostgreSQL database. I chose local SQLite in WAL mode. It provided zero external network latency, instant container cold-starts, and zero infrastructure costs. While it doesn't support multi-node horizontal scaling, it was the exact right engineering choice for single-container deployment reliability.
> 
> **Trade-off 3:** Strict Schema Refusal versus Conversational Fallback. I chose deterministic schema validation with strict negative refusals over allowing the LLM to 'helpfully speculate.' The system feels slightly less conversational, but in enterprise DevOps and legal compliance, predictability and zero hallucination far outweigh conversational charm."*

---

### [7:00 – 8:30] Empirical Evaluation Scores & Day 50 Baseline Comparison

**Screen Action:** Run `python day-50/regression_test_runner.py` in the terminal or display the evaluation table in `Day-56/pre_launch_baseline.md`.

**Spoken Script:**
> *"In applied AI engineering, subjective 'vibe checks' don't cut it. Everything in AURONIX is validated by a 30-case automated LLM-as-judge evaluation harness spanning Easy, Medium, Hard, and Adversarial tiers.
> 
> Let's look at the verified numbers:
> In our initial Day 50 baseline evaluation, the system achieved an overall score of 4.39 out of 5.0. But on adversarial probes, it completely collapsed to 2.53 out of 5.0 due to sycophancy.
> 
> After implementing our V2 prompt contract, premise-refutation pre-checks, and retrieval keyphrase boosting, our hardened production pipeline achieved:
> - Easy Tier: 4.94 / 5.0
> - Medium Tier: 4.70 / 5.0
> - Hard Tier: 4.52 / 5.0
> - Adversarial Subset: **4.40 / 5.0—a massive +1.87 point improvement**.
> - Overall Composite Score: **4.72 out of 5.0, or 94.4%**.
> 
> Furthermore, all 41 automated pytest unit and integration tests across the repository pass with a 100% pass rate in our CI/CD pipeline."*

---

### [8:30 – 9:30] Meaningful Failures, Root Causes & Post-Launch Feedback

**Screen Action:** Display `day-54/launch_metrics.md` or `day-54/feedback_analysis.md`.

**Spoken Script:**
> *"The most valuable learning came from what broke.
> 
> Our biggest failure was the adversarial sycophancy collapse I just mentioned, which taught me that groundedness must be enforced by architectural constraints, not prompt hope.
> 
> Our second major failure was semantic cache drift: when we initially tested with a loose 0.85 cosine threshold, database failover queries collided with Redis cache eviction queries. Calibrating the threshold to 0.92 through an empirical sweep completely eliminated false collisions.
> 
> And on Day 54, real feedback telemetry revealed that 75% of user complaints stemmed from 2-column PDF table formatting rather than retrieval logic. That gave us the exact data needed to prioritize layout-aware parsing in our post-graduation roadmap."*

---

### [9:30 – 10:00] Graduation Conclusion & Community Call to Action

**Screen Action:** Bring camera view back to full focus or show GitHub repository and LinkedIn profile.

**Spoken Script:**
> *"Completing these 60 days has transformed how I think about AI software. Moving forward into my Next 30 Days plan, I'm deepening asynchronous distributed worker systems and layout-aware document ingestion.
> 
> Everything I showed you today—all code, notebooks, test suites, and documentation—is open source and reproducible in my GitHub repository.
> 
> I invite you to clone the repo, run the test suites, test the edge cases, and share your feedback. Thank you to ABTalks and the community for this incredible journey. Let's keep building!"*

---

## 3. Post-Recording Publication Checklist

- [ ] Video recording duration verified (between 9:30 and 10:30 minutes).
- [ ] Upload video to Loom / YouTube (Unlisted or Public).
- [ ] Insert actual Loom URL into repository:
  - Placeholder: `[INSERT ACTUAL LOOM URL HERE: https://www.loom.com/share/...]`
- [ ] Embed link in Day 60 README and LinkedIn article.
