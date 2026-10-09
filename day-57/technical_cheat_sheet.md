# Day 57 — Task 6: Fifteen-Concept AI Engineering Cheat Sheet

A concise, high-yield technical cheat sheet covering exactly **15 fundamental AI Engineering concepts**. Designed for rapid review right before a technical interview.

---

## 1. Retrieval-Augmented Generation (RAG)
* **Explanation in My Words:** Augmenting an LLM's prompt at inference time with relevant, factual excerpts dynamically retrieved from external databases, allowing the model to answer questions using private or real-time data without retraining.
* **Why It Matters in Production:** Eliminates model cutoff limitations, connects internal enterprise data securely, provides source attributions, and reduces hallucination risk by anchoring responses to retrieved text.
* **Practical Example:** In AURONIX, an employee asks for the failover runbook; the system retrieves `CORP-OPS-001` from the internal database and feeds it into the LLM context to generate step-by-step guidance.
* **Likely Interview Follow-Up:** *"When would you choose fine-tuning over RAG, and can they be combined?"*

---

## 2. Embeddings and Semantic Similarity
* **Explanation in My Words:** Dense vector representations of text where geometric distance (such as cosine similarity or Euclidean distance) corresponds to semantic meaning rather than literal keyword matching.
* **Why It Matters in Production:** Enables the system to match queries with documents that mean the same thing even when they use completely different vocabularies (e.g., *"error connecting"* matching *"network timeout"*).
* **Practical Example:** Generating 256-dimensional unit vectors for incoming queries and calculating `dot(A, B) / (norm(A) * norm(B))` to determine whether two support requests describe the same problem.
* **Likely Interview Follow-Up:** *"Why is cosine similarity preferred over Euclidean (L2) distance for text embeddings?"*

---

## 3. Chunking Strategies
* **Explanation in My Words:** The algorithmic methodology used to segment long, unstructured documents into manageable, coherent text passages suitable for vector embedding and LLM context windows.
* **Why It Matters in Production:** Chunks that are too small lack contextual meaning; chunks that are too large dilute vector specificity and overflow token budgets. Clean chunking prevents splitting code blocks, tables, and sentences in half.
* **Practical Example:** Hierarchical parent-child chunking: indexing 200-token child chunks for precise vector retrieval, but passing the surrounding 800-token parent chunk to the LLM during generation.
* **Likely Interview Follow-Up:** *"How do you handle chunking structured documents like JSON schemas, Markdown tables, or code?"*

---

## 4. Vector Databases and Nearest-Neighbour Search
* **Explanation in My Words:** Specialized databases optimized to store, index, and query millions of high-dimensional vectors at millisecond latency using Approximate Nearest Neighbor (ANN) algorithms.
* **Why It Matters in Production:** Exact $k$-NN brute-force search is $O(N)$ and degrades at scale; ANN algorithms like HNSW (Hierarchical Navigable Small World) achieve $O(\log N)$ search latency, enabling real-time lookups across millions of chunks.
* **Practical Example:** Storing 500,000 document vectors in Qdrant or Milvus with HNSW indexing and metadata filtering for tenant ID and user access permissions.
* **Likely Interview Follow-Up:** *"What is the trade-off between index build time, memory consumption, and search recall in HNSW?"*

---

## 5. Hybrid Retrieval and Reranking
* **Explanation in My Words:** A two-stage retrieval pipeline combining keyword search (BM25) and dense vector search, followed by a cross-encoder model that re-scores the combined candidate pool.
* **Why It Matters in Production:** Dense search misses exact alphanumeric strings (like error code `ERR_403_AUTH` or part numbers), while BM25 misses semantic synonyms. Combining them via Reciprocal Rank Fusion (RRF) and cross-encoders delivers superior recall and precision.
* **Practical Example:** In AURONIX, BM25 captures exact script names (`promote_replica.sh`), dense search captures conceptual intent (*"database lag"*), and breadcrumb re-ranking boosts runbook hierarchy.
* **Likely Interview Follow-Up:** *"Why not run a cross-encoder across all documents in your corpus instead of using a vector database first?"*

---

## 6. Prompt Engineering and Context Management
* **Explanation in My Words:** The systematic structuring of system instructions, few-shot examples, dynamic context, and output schemas to guide model reasoning deterministically within token limits.
* **Why It Matters in Production:** LLMs suffer from "Lost in the Middle" syndrome when context is bloated. Disciplined context placement and structured output constraints (JSON/Pydantic schemas) ensure deterministic API behavior.
* **Practical Example:** Our AURONIX V2 Production Prompt explicitly defines `ROLE`, `CONSTRAINTS & REFUSALS`, and an exact output schema (`Answer:`, `Sources:`, `Confidence:`), preventing drift across model versions.
* **Likely Interview Follow-Up:** *"How do you mitigate 'Lost in the Middle' attention degradation in large context windows?"*

---

## 7. Hallucination Mitigation and Grounded Generation
* **Explanation in My Words:** Architectural and prompting safeguards that prevent an LLM from fabricating false information, accepting leading false premises, or extrapolating beyond retrieved facts.
* **Why It Matters in Production:** In legal, medical, and enterprise incident response, a plausible hallucination is far more dangerous than an honest refusal. Factual grounding builds user trust.
* **Practical Example:** Implementing an explicit premise verification layer and Natural Language Inference (NLI) entailment check that verifies every generated claim directly against source chunks.
* **Likely Interview Follow-Up:** *"How do you distinguish between hallucination caused by retrieval failure versus generator sycophancy?"*

---

## 8. LLM Evaluation and Regression Testing
* **Explanation in My Words:** Replacing subjective "vibe checks" with reproducible, automated test harnesses (often using an LLM-as-a-judge or deterministic metrics) across multi-tier test datasets.
* **Why It Matters in Production:** Prompt edits or model version bumps often silently break existing capabilities. Automated evaluation gates in CI/CD catch regressions before deployment.
* **Practical Example:** Running `day-50/eval_runner.py` across 30 curated test cases in GitHub Actions, computing a composite score across 5 weighted dimensions and blocking PRs if the score drops below 4.5.
* **Likely Interview Follow-Up:** *"How do you validate that your LLM Judge isn't biased toward longer or more verbose answers?"*

---

## 9. Retrieval Evaluation Metrics
* **Explanation in My Words:** Statistical formulas used to measure the quality of search rankings before any generation takes place, including Recall@k, Mean Reciprocal Rank (MRR), and nDCG.
* **Why It Matters in Production:** Decouples retrieval bugs from generation bugs. If retrieval recall is 50%, no amount of prompt engineering will fix the final answer.
* **Practical Example:** Computing Recall@4 (is the target runbook among the top 4 chunks?) and MRR (is the target runbook the first result returned?) across 100 historical queries.
* **Likely Interview Follow-Up:** *"When would you prioritize Mean Reciprocal Rank over nDCG?"*

---

## 10. Semantic Caching
* **Explanation in My Words:** Caching LLM query-response pairs in a vector store or key-value store and retrieving them when an incoming query has a semantic similarity score above a strict threshold.
* **Why It Matters in Production:** Slashes query latency from seconds to milliseconds, drastically reduces token API costs, and mitigates upstream LLM provider rate limits for common queries.
* **Practical Example:** In AURONIX [`day-52/semantic_cache.py`](file:///day-52/semantic_cache.py), calculating cosine similarity against cached vectors with a threshold of $\ge 0.92$, returning warm queries in $<15\text{ms}$ and saving token costs.
* **Likely Interview Follow-Up:** *"How do you handle cache invalidation when underlying enterprise documentation updates?"*

---

## 11. Token Usage and Inference Cost Optimization
* **Explanation in My Words:** Strategies to minimize the volume of input and output tokens processed by commercial model APIs while preserving output quality.
* **Why It Matters in Production:** Unchecked token consumption can bankrupt an AI product at scale. Efficient context pruning and model tiering directly preserve profit margins.
* **Practical Example:** Routing simple FAQ queries to lightweight, low-cost models (GPT-4o-mini or Claude 3.5 Haiku) and reserving larger frontier models only for complex multi-hop reasoning.
* **Likely Interview Follow-Up:** *"What techniques can compress retrieved context without losing critical information?"*

---

## 12. Latency Measurement and Performance Profiling
* **Explanation in My Words:** Instrumenting high-resolution timing probes at each individual stage of the AI pipeline (input guardrail, embedding, vector search, reranking, TTFT, generation).
* **Why It Matters in Production:** Pinpoints whether latency spikes stem from database index misses, network hops, or slow model generation, allowing targeted performance tuning.
* **Practical Example:** Tracking Time to First Token (TTFT), tokens per second (TPS), and total round-trip latency using `time.perf_counter()` as implemented in AURONIX Day 52 profiler.
* **Likely Interview Follow-Up:** *"What is the difference between Time to First Token (TTFT) and Time Per Output Token (TPOT), and how do you optimize each?"*

---

## 13. API Design, Rate Limiting, and Resilience
* **Explanation in My Words:** Designing robust REST/gRPC endpoints with input validation, sliding-window rate limiters, timeouts, retries with exponential backoff, and circuit breakers.
* **Why It Matters in Production:** Protects internal infrastructure from abuse, prevents cascading failures when model providers go down, and ensures clean contract integration for frontends.
* **Practical Example:** In AURONIX [`day-53/backend/main.py`](file:///day-53/backend/main.py), enforcing a 20 request/session/hour sliding-window rate limit that returns HTTP 429 when exceeded.
* **Likely Interview Follow-Up:** *"How would you implement a distributed rate limiter that works across 10 autoscaled container instances?"*

---

## 14. Production Observability and CI/CD
* **Explanation in My Words:** Continuous logging, tracing, and metric collection for production AI interactions (requests, token usage, latency, user feedback), paired with automated build and deployment pipelines.
* **Why It Matters in Production:** Enables engineering teams to detect drift, debug live user complaints, audit compliance, and safely deploy prompt or code updates.
* **Practical Example:** Logging user queries, latency, and feedback into SQLite/PostgreSQL with OpenTelemetry spans, and using GitHub Actions to run unit tests and evaluation harnesses on every pull request.
* **Likely Interview Follow-Up:** *"What specific telemetry signals indicate that your production model or retrieval quality is drifting?"*

---

## 15. Personalization, Privacy, and Responsible AI
* **Explanation in My Words:** Tailoring responses to user roles and preferences while enforcing strict PII redaction, access control, bias mitigation, and data security governance.
* **Why It Matters in Production:** Prevents private corporate data or user credentials from leaking into model prompts or training data, ensuring compliance with SOC2, HIPAA, and GDPR.
* **Practical Example:** Scrubbing email addresses, auth tokens, and social security numbers with regex/Presidio before prompt assembly, and appending tenant ID filters to vector queries to isolate enterprise client data.
* **Likely Interview Follow-Up:** *"How do you implement Role-Based Access Control (RBAC) in a vector retrieval system without creating separate vector databases for every user role?"*

---
