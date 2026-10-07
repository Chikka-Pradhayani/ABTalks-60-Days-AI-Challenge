# Quantified AI Engineering Resume Experience

### Professional Summary
AI Systems and Machine Learning Engineer specializing in production-grade Retrieval-Augmented Generation (RAG), automated LLM evaluation harnesses, semantic caching, and defensive middleware. Proven track record of replacing subjective spot-checks with automated CI/CD quality gates, diagnosing complex retrieval failure modes, and optimizing multi-tier AI architectures for speed, cost, and reliability.

---

### Core Experience & Impact Bullets

#### Lead AI Engineer / Systems Developer — AURONIX (Enterprise AI Workbench)
* **Domain-Specific AI Evaluation & Hardening:**
  * Architected and executed an automated 30-question, 3-tier domain-specific evaluation benchmark (`eval_dataset.json`) across five quality dimensions (Correctness, Relevance, Completeness, Faithfulness, Hallucination Avoidance) using an LLM-as-judge framework.
  * Elevated Hard-Tier reasoning accuracy by **+0.83 points (3.69 to 4.52 / 5.0)** and reduced sycophantic model confabulation, boosting Hallucination Avoidance by **+1.13 points (3.57 to 4.70 / 5.0)** and lifting overall system quality from **4.39 to 4.72 / 5.0**.
  * Built an automated regression test runner (`regression_test_runner.py`) integrated as a blocking pre-deployment quality gate, requiring minimum threshold scores ($\ge 3.5/5.0$) across all evaluation dimensions.

* **Advanced Multi-Stage RAG Pipeline Design:**
  * Engineered a multi-stage retrieval architecture over a 50-document corporate knowledge base (`CORP-ENG`, `CORP-OPS`, `CORP-SEC`, `CORP-PROD`, `CORP-HR`) combining Conversational Query Rewriting, Hypothetical Document Embeddings (HyDE), and LLM-based Candidate Re-ranking.
  * Quantitatively benchmarked retrieval techniques against standard FAISS dense vector search: HyDE delivered a **+0.67 point quality improvement** ($3.60 \rightarrow 4.27/5.0$) on colloquial questions; Conversational Query Rewriting achieved a **+1.00 point gain** ($2.40 \rightarrow 3.40/5.0$) on elliptical follow-up queries; and Top-10 to Top-3 LLM cross-attention re-ranking delivered a **+1.07 point boost** ($2.47 \rightarrow 3.53/5.0$) by recovering buried runbooks.
  * Implemented technical keyphrase lexical boosting (`+0.75`) and expanded candidate retrieval to $k=4$, resolving multi-hop context omissions.

* **Performance Engineering & Semantic Caching:**
  * Profiled end-to-end pipeline latency across a 20-query enterprise workload, identifying repeated document re-tokenization (36.74 ms cold start) and prompt bloat as primary latency and cost bottlenecks.
  * Designed and deployed a Redis semantic caching layer with cosine similarity matching at $\ge 0.92$ threshold, reducing response latency from ~3.2ms baseline to **$2.0–2.6\text{ ms}$** and driving token consumption down to **16 tokens ($0.00000 API cost, 100% savings)** on cache hits.
  * Formulated monthly cost projections across scaling tiers (1k, 10k, and 100k queries/day) and verified zero quality degradation ($< 0.30$ point variance across all 30 Day 50 benchmark queries) under active semantic caching.

* **Robustness Middleware & Defensive Prompt Engineering:**
  * Developed a 6-layer defense-in-depth architecture handling **20 verified edge-case scenarios** across 5 categories (out-of-domain queries, malformed payloads, adversarial prompt injections, boundary conditions, and extreme token lengths >500 characters).
  * Implemented an automated input normalisation engine stripping null bytes, control characters, and homoglyphs before vector embedding, paired with global exception masking to eliminate raw stack-trace leakage.
  * Hardened system prompt contracts (System Prompt v2) with explicit `## CONSTRAINTS & REFUSALS` and multi-facet sub-query decomposition, enforcing a machine-parseable three-section schema (`Answer:`, `Sources:`, `Confidence:`) with a single-retry self-healing validation loop.

* **Production CI/CD, Containerization & Health Monitoring:**
  * Built a multi-stage Docker containerization pipeline with non-root security execution and automated container curl healthchecks (`/health`).
  * Engineered automated GitHub Actions CI/CD workflows enforcing a 2-gate quality barrier: Gate 1 running **25+ pytest unit tests** and Gate 2 running the **30-question AI regression evaluation**, deterministically halting deployments on test or threshold failure.
  * Configured isolated dual-environment cloud deployments separating Railway Staging from Railway Production with dedicated database paths, FAISS indexes, and API authentication keys, routing to a Next.js 14 App Router frontend deployed on Vercel with 5-minute UptimeRobot synthetic monitoring.

* **User Feedback Analytics & Reliability Post-Mortem:**
  * Created an indexed SQLite feedback storage system (`feedback.db`) tracking user star ratings (1–5), natural language commentary, and failure classifications across live sessions.
  * Analyzed real usage telemetry to identify top failure clusters: 75.0% failure rate in 2-column PDF document formatting and 66.7% failure rate in HTTP 504 gateway timeouts on 150-page documents.
  * Conducted structured qualitative user interviews and synthesized findings into a prioritized, evidence-based 8-day engineering remediation plan (P0 layout-aware parsing, P1 asynchronous SSE job queue, P2 granular verbatim citation modal).

---

### Technical Skills Summary
* **Languages & Frameworks:** Python 3.12, TypeScript, SQL, Bash, FastAPI, Next.js 14 (App Router), React, Pydantic.
* **AI & Retrieval Technologies:** RAG Pipelines, FAISS, OpenAI (gpt-4o-mini, text-embedding-3-small), TikToken, LangSmith Tracing, HyDE, Query Rewriting, Cross-Attention Re-ranking, TF-IDF.
* **Storage & Caching:** Redis (Semantic Vector Caching), SQLite (WAL Mode, Indexed Schemas).
* **Evaluation & Testing:** LLM-as-a-Judge Evaluation, Regression Gating, Adversarial Robustness Testing, Pytest, Profiling (`time.perf_counter`).
* **DevOps & Cloud:** Docker, GitHub Actions CI/CD, Railway, Vercel, UptimeRobot, Linux.
