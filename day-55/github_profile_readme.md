# GitHub Profile README

## Hi, I'm Pradhayani Chikka 👋
### AI Systems & Machine Learning Engineer | RAG, Evaluation & Production Resilience

I build production-grade AI systems, autonomous agents, and deterministic RAG architectures with an uncompromising focus on **empirical evaluation, system reliability, latency optimization, and production safety**.

Over the course of the intensive **ABTalks 60 Days AI Challenge**, I engineered end-to-end AI applications moving methodically from core machine learning intuitions to distributed vector retrieval, adversarial defenses, automated LLM-as-judge evaluation harnesses, and multi-cloud CI/CD deployment pipelines.

---

### 🛠️ Core Engineering Philosophy
* **Evaluation Over Guesswork:** Subjective "vibe checks" fail in production. Every AI system I build is anchored to multi-tier quantitative benchmarks with automated regression gates.
* **Defense in Depth:** Production LLMs must be hardened against sycophancy, false premises, prompt injection, and malformed payloads through modular normalisation and strict contract validation.
* **Systems Architecture Over API Wrapping:** Real AI engineering requires profiling latency bottlenecks, implementing semantic caching to eliminate redundant inference costs, and designing graceful fallbacks when upstream providers fail.

---

### 🚀 Top 3 Featured AI Engineering Projects

#### 1. AURONIX — Enterprise Autonomous Private AI Workbench
* **One-Line Technical Description:** Production-grade private enterprise RAG workbench featuring multi-stage retrieval (HyDE + query rewriting + cross-attention re-ranking), Redis semantic caching ($\ge 0.92$ similarity), hardened contract validation, and a 30-question automated regression test suite.
* **Key Technologies:** Python 3.12, FastAPI, Next.js 14 App Router, Redis, FAISS, OpenAI (gpt-4o-mini / text-embedding-3-small), SQLite (WAL mode), Docker, GitHub Actions, Pytest.
* **Architectural Decisions & Results:**
  * Evaluated across a 30-question domain-specific benchmark, elevating overall accuracy from **4.39 to 4.72 / 5.0** and hallucination avoidance from **3.57 to 4.70 / 5.0 (+1.13 pts)**.
  * Designed multi-stage retrieval with HyDE (+0.67 pts), conversational query rewriting (+1.00 pts), and LLM candidate re-ranking (+1.07 pts) over a 50-document corporate corpus.
  * Implemented Redis semantic caching achieving sub-2.5ms latency and **100% token cost reduction** on repeat/paraphrased queries without degrading answer quality.
  * Containerized with multi-stage Docker builds and automated CI/CD gating deploying to Railway (backend) and Vercel (frontend).
* **Repository Link:** [ABTalks-60-Days-AI-Challenge/day-50](https://github.com/Chikka-Pradhayani/ABTalks-60-Days-AI-Challenge/tree/main/day-50) | [day-52](https://github.com/Chikka-Pradhayani/ABTalks-60-Days-AI-Challenge/tree/main/day-52) | [day-53](https://github.com/Chikka-Pradhayani/ABTalks-60-Days-AI-Challenge/tree/main/day-53)
* **Live Deployment Link:** `https://auronix-app.vercel.app` *(Target configured on Vercel; Backend: `https://auronix-production.up.railway.app` on Railway — TODO: Verify active DNS status if cloud instances are paused)*.

---

#### 2. AI Research Assistant — Autonomous Multi-Step Research & Evaluation Agent
* **One-Line Technical Description:** Full-stack autonomous research assistant executing a 4-step workflow (topic exploration, information synthesis, report generation, and automated factual scoring) behind a decoupled FastAPI and Next.js interface.
* **Key Technologies:** Python, FastAPI, Next.js, React, Pydantic, scikit-learn, TF-IDF / Lexical Normalization.
* **Architectural Decisions & Results:**
  * Orchestrated a deterministic 4-stage agent pipeline: research topic ingestion $\rightarrow$ cross-source analysis $\rightarrow$ structured report drafting $\rightarrow$ factual ground-truth scoring.
  * Integrated an automated evaluation suite evaluating groundedness, correctness, and completeness against a reference dataset with regex text normalization.
  * Decoupled backend REST execution from frontend client polling, ensuring real-time multi-step state visualization for long-running synthesis jobs.
* **Repository Link:** [ABTalks-60-Days-AI-Challenge/Day-30.ipynb](https://github.com/Chikka-Pradhayani/ABTalks-60-Days-AI-Challenge/blob/main/Day-30.ipynb)
* **Live Deployment Link:** `TODO: Local demonstration in repository; deployment URL pending cloud deployment`.

---

#### 3. Production-Resilient RAG Assistant & Fault-Tolerant Circuit Breaker API
* **One-Line Technical Description:** Enterprise AI microservice pairing dense vector search with an automated Circuit Breaker pattern to isolate upstream model outages, prevent cascade failures, and enforce sliding-window rate limits.
* **Key Technologies:** Python, FastAPI, FAISS-CPU, Redis, scikit-learn, Pytest, Pydantic.
* **Architectural Decisions & Results:**
  * Implemented a stateful `CircuitBreaker` pattern that automatically trips to `OPEN` state after 3 consecutive upstream inference failures, blocking outbound calls for a 60-second recovery timeout and serving cached fallbacks.
  * Built structured Pydantic schema validation rejecting malformed queries and sliding-window rate limiting (20 requests/session/hour) to protect downstream vector indexes.
  * Profiled baseline vector retrieval across multi-category technical corpora, logging end-to-end latency in milliseconds to SQLite audit tables.
* **Repository Link:** [ABTalks-60-Days-AI-Challenge/Day-25.ipynb](https://github.com/Chikka-Pradhayani/ABTalks-60-Days-AI-Challenge/blob/main/Day-25.ipynb) | [Day-35.ipynb](https://github.com/Chikka-Pradhayani/ABTalks-60-Days-AI-Challenge/blob/main/Day-35.ipynb)
* **Live Deployment Link:** `TODO: Microservice benchmarked in notebook test harness; deployment URL pending cloud deployment`.

---

### 📊 Technical Skill Matrix
| Domain | Technologies & Systems |
|---|---|
| **AI / RAG Architecture** | Multi-stage Retrieval, HyDE, Conversational Query Rewriting, Cross-Attention Re-ranking, FAISS, Inverted Indexes |
| **Evaluation & Quality** | LLM-as-Judge Frameworks, Automated Regression Test Runners, Adversarial Testing, Hallucination Benchmarks |
| **Backend & Infrastructure** | Python 3.12, FastAPI, Pydantic, Redis Semantic Cache, SQLite (WAL Mode), REST APIs, Rate Limiting |
| **Frontend & UX** | Next.js 14 App Router, React, Tailwind CSS, Server-Sent Events (SSE) Streaming, Telemetry Dashboards |
| **DevOps & Production** | Docker (Multi-stage), GitHub Actions CI/CD, Railway, Vercel, UptimeRobot, Linux |

---

### 📬 Connect With Me
* **GitHub:** [@Chikka-Pradhayani](https://github.com/Chikka-Pradhayani)
* **LinkedIn:** `TODO: Add personal LinkedIn profile URL`
* **Email:** `TODO: Add professional contact email`
