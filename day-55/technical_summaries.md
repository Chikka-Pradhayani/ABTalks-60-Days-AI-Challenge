# Three Technical Summaries

---

## Technical Summary 1 — RAG Architecture Decisions: Overcoming Lexical Gaps and Ranking Noise

When architecting the retrieval engine for AURONIX—an enterprise AI workbench querying internal documentation—we quickly discovered that naive single-vector similarity search collapses in production environments. Standard bi-encoder retrieval embeds user queries with models like `text-embedding-3-small` (1536 dimensions) and performs inner-product cosine search on a FAISS index. However, in enterprise settings, this approach fails across two distinct vectors: lexical asymmetry (informal, colloquial employee questions mismatching formal corporate documentation) and conversational ellipsis (follow-up queries where pronouns obscure the target entity).

To solve this, we systematically evaluated and integrated a multi-stage retrieval architecture:
1. **Conversational Query Rewriting:** An LLM pre-processing step inspecting the prior two conversation turns to resolve ambiguous pronouns (*"Who leads it?"* $\rightarrow$ *"Who leads the customer-support team?"*).
2. **Hypothetical Document Embeddings (HyDE):** An intermediate step where the model generates a concise hypothetical excerpt of what an internal runbook might state, shifting retrieval from query-to-document space into document-to-document space ($\mathbf{d}_{\text{hypo}} \cdot \mathbf{d}$). The hypothetical text is quarantined strictly to vector search and never exposed to the generation context.
3. **Cross-Attention Candidate Re-ranking:** Querying FAISS for an expanded pool of Top 10 candidate chunks ($k=10$), evaluating all ten via LLM cross-attention scoring, and filtering down to the Top 3 most relevant chunks for generation context injection.

We benchmarked these techniques against baseline vector search using the Day 29 LLM Judge Framework. On indirect, colloquial queries, HyDE increased factual retrieval quality from **3.60 to 4.27 / 5.0 (+0.67 pts)** without adding measurable latency on pre-warmed pipelines ($0.22\text{ ms} \rightarrow 0.21\text{ ms}$). On pronoun-heavy follow-up queries, Conversational Query Rewriting elevated response quality from **2.40 to 3.40 / 5.0 (+1.00 pt)** with only $0.03\text{ ms}$ overhead. Finally, candidate re-ranking promoted critical runbooks buried at ranks 4–7 into the top 3, increasing quality from **2.47 to 3.53 / 5.0 (+1.07 pts)** at a modest latency cost of $+0.24\text{ ms}$.

The trade-off was accepting incremental latency and token overhead on cold queries in exchange for eliminating context misses. Ultimately, empirical evaluation proved that all three techniques were essential, establishing a unified pipeline that feeds high-precision context into downstream synthesis.

*(Word count: ~365 words)*

---

## Technical Summary 2 — Building AI Evaluation Systems: From "Vibe Checks" to Automated CI/CD Gates

Evaluating generative AI systems in enterprise environments cannot rely on subjective manual spot-checking. Production systems require automated, reproducible, quantitative evaluation benchmarks that detect subtle hallucinations, sycophancy, and regression across releases. During the challenge, we designed an automated evaluation harness anchored by a domain-specific 30-question benchmark (`eval_dataset.json`) and an LLM-as-judge scoring engine adapted from Day 29.

The dataset was structured across three challenge tiers:
* **Easy Tier (10 Qs):** Single-document direct lookups (e.g., API port numbers, primary programming languages).
* **Medium Tier (10 Qs):** Cross-domain multi-document synthesis (e.g., linking SOC 2 key rotation protocols with incident escalation).
* **Hard Tier (10 Qs):** Adversarial prompts, false premises (e.g., asking how Puppet manages Aurora database failover when Aurora is managed via custom bash scripts), missing-knowledge traps, and multi-part queries (>500 characters).

The automated judge evaluates each response across five distinct dimensions on a 1.0 to 5.0 scale: Correctness, Relevance, Completeness, Faithfulness, and Hallucination Avoidance. Responses are programmatically validated against a strict contract (`Answer:`, `Sources:`, `Confidence:`), rejecting ungrounded claims.

Baseline evaluation revealed a stark vulnerability: while Easy queries scored **4.94 / 5.0**, the Hard Tier scored a dismal **3.69 / 5.0**, driven by a **3.57 / 5.0** score in Hallucination Avoidance. The model demonstrated sycophancy, uncritically accepting false user premises and inventing plausible configurations.

This empirical discovery directly drove three engineering interventions: implementing technical keyphrase boosting (`+0.75`) with candidate pool expansion ($k=4$), embedding an explicit negative-constraint refusal contract (`## CONSTRAINTS & REFUSALS`) in System Prompt v2, and adding multi-facet query decomposition. Re-running the evaluation suite demonstrated a massive leap: Hard Tier scores surged from **3.69 to 4.52 / 5.0 (+0.83 pts)**, and Hallucination Avoidance jumped from **3.57 to 4.70 / 5.0 (+1.13 pts)**, lifting overall quality from **4.39 to 4.72 / 5.0**.

By embedding this runner into our GitHub Actions CI/CD pipeline (`regression_test_runner.py`), we converted evaluation from an afterthought into an automated deployment gate that halts builds if any quality score drops below 3.5.

*(Word count: ~355 words)*

---

## Technical Summary 3 — A Specific Debugging Problem: Diagnosing and Eliminating Sycophantic Hallucinations on False Premises

During the execution of our Day 50 automated evaluation suite, our pipeline exhibited a critical failure pattern on adversarial test queries. While the system performed near-flawlessly on factual inquiries, its Hallucination Avoidance score plummeted to **3.57 / 5.0** on queries containing false assumptions. For example, when prompted with *"Explain the procedure for promoting the PostgreSQL Aurora replica using the puppet-db-failover module"*, the system generated a highly convincing, detailed bash script referencing fictitious Puppet manifests, despite our operational runbooks (`CORP-OPS-002`) clearly specifying that Aurora promotion is executed manually via `promote_replica.sh`.

We systematically investigated the end-to-end trace:
1. **Retrieval Inspection:** Vector search correctly retrieved `CORP-OPS-002` (Aurora database maintenance) and `CORP-ENG-003` (infrastructure configuration) with similarity scores $>0.78$. The retrieval step was not dropping the documentation.
2. **Context Inspection:** The retrieved text clearly stated that Puppet is never used for database state mutations.
3. **Generation Trace:** The failure occurred entirely within the LLM inference step. The model prioritized answering the user's explicit question affirmatively over enforcing the negative boundary present in the context.

The root cause was foundation model sycophancy combined with unconstrained generation: default system prompts instruct models to be "helpful", which LLMs interpret as confirming the user's premise rather than correcting them.

We tested two initial fixes that failed:
* *Failed Approach 1:* Setting temperature to 0.0. The model still hallucinated because the most probable completion in an unconstrained prompt was still sycophantic.
* *Failed Approach 2:* Increasing the cosine similarity threshold in FAISS. This caused false negatives, dropping legitimate multi-hop context chunks on complex queries.

The final fix required a two-part intervention:
1. **Prompt Contract Hardening:** We added explicit negative refutation rules to `## CONSTRAINTS & REFUSALS`: *"If a user prompt asserts an untrue architectural premise, you must explicitly refute the false assumption in the first sentence before providing verified facts."*
2. **Lexical Keyphrase Boosting & $k=4$ Expansion:** We boosted exact keyword matches by `+0.75` to guarantee that contradictory runbook clauses were positioned at rank 1.

Re-running the 30-question benchmark verified the resolution: Hallucination Avoidance climbed from **3.57 to 4.70 / 5.0 (+1.13 pts)**, and the Hard Tier rose to **4.52 / 5.0**. The engineering lesson was clear: generative models will hallucinate to be agreeable unless their operational boundaries are fortified with explicit negative constraints and evaluated against adversarial traps.

*(Word count: ~390 words)*
