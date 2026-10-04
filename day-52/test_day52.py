"""AURONIX Day 52 Automated Test Suite.

Verifies:
1. Redis semantic cache hit on identical and paraphrased queries (>= 0.92 similarity threshold).
2. Redis semantic cache miss on distinct queries (< 0.92 similarity threshold).
3. Graceful degradation and uninterrupted pipeline execution when Redis is offline or throws errors.
4. Handling of empty cache and cold start behavior.
5. Handling of invalid, empty, or failed embeddings.
6. Cache TTL expiration behavior.
7. Adaptive context pruning reduction in prompt tokens.
8. Day 50 quality protection rule verification (no dimension drops by > 0.3).
"""

import os
import sys
import time
import unittest

# Ensure day-52 and day-50 are importable
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(CURRENT_DIR)
DAY50_DIR = os.path.join(REPO_ROOT, "day-50")
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)
if DAY50_DIR not in sys.path:
    sys.path.insert(0, DAY50_DIR)

from semantic_cache import SemanticCache, SemanticEmbeddingGenerator, cosine_similarity
from profiler import count_tokens, estimate_api_cost, PipelineProfiler
from optimized_pipeline import OptimizedPipeline
from sample_queries import get_sample_queries


class TestSemanticCache(unittest.TestCase):
    """Unit tests for SemanticCache with Redis and in-memory fallback."""

    def setUp(self):
        self.cache = SemanticCache(
            similarity_threshold=0.92,
            default_ttl=86400,
            enable_redis=True,
            key_prefix="auronix:test_cache:"
        )
        self.cache.clear()

    def tearDown(self):
        self.cache.clear()

    def test_empty_cache_returns_miss(self):
        """Querying an empty cache should cleanly return None without errors."""
        res = self.cache.get("What port is allocated to FastAPI?")
        self.assertIsNone(res)
        stats = self.cache.get_stats()
        self.assertEqual(stats["hits"], 0)
        self.assertEqual(stats["misses"], 1)

    def test_exact_query_cache_hit(self):
        """Storing and querying identical query must return a cache hit with similarity >= 0.92."""
        q = "What port is allocated to the FastAPI backend service in the network matrix?"
        resp_data = {
            "answer": "Port 8001 is allocated to FastAPI.",
            "sources": ["CORP-ENG-003"],
            "confidence": "High"
        }
        self.cache.set(q, resp_data)

        hit = self.cache.get(q)
        self.assertIsNotNone(hit)
        self.assertTrue(hit["cache_hit"])
        self.assertGreaterEqual(hit["similarity"], 0.92)
        self.assertEqual(hit["response"]["answer"], "Port 8001 is allocated to FastAPI.")

    def test_semantic_paraphrase_cache_hit(self):
        """Paraphrased query with high semantic overlap must hit the cache (>= 0.92)."""
        original_q = "What command or script is executed to trigger the primary database replica promotion during a failover?"
        paraphrased_q = "What command or script is executed to trigger primary database replica promotion during failover?"

        resp_data = {
            "answer": "./scripts/promote_replica.sh --cluster prod-db-core --force",
            "sources": ["CORP-OPS-001"],
            "confidence": "High"
        }
        self.cache.set(original_q, resp_data)

        hit = self.cache.get(paraphrased_q)
        self.assertIsNotNone(hit)
        self.assertTrue(hit["cache_hit"])
        self.assertGreaterEqual(hit["similarity"], 0.92)

    def test_semantic_distinct_query_cache_miss(self):
        """A semantically distinct query must result in a cache miss (< 0.92)."""
        stored_q = "What port is allocated to the FastAPI backend service in the network matrix?"
        distinct_q = "What is the secret recipe for authentic homemade Italian lasagna with bechamel sauce?"

        self.cache.set(stored_q, {"answer": "Port 8001", "sources": ["CORP-ENG-003"]})

        res = self.cache.get(distinct_q)
        self.assertIsNone(res)

    def test_redis_offline_graceful_fallback(self):
        """When Redis is intentionally unavailable or misconfigured, pipeline does not break."""
        bad_cache = SemanticCache(
            redis_host="127.0.0.1",
            redis_port=59999,
            enable_redis=True,
            key_prefix="auronix:test_fail:"
        )
        self.assertFalse(bad_cache.is_redis_available())

        # Should still work smoothly using in-memory store
        q = "What is AURONIX mainly used for in our company?"
        bad_cache.set(q, {"answer": "Private enterprise AI", "sources": ["CORP-ENG-001"]})
        hit = bad_cache.get(q)
        self.assertIsNotNone(hit)
        self.assertTrue(hit["cache_hit"])

    def test_invalid_or_empty_input_handling(self):
        """Empty, whitespace, or invalid queries must be safely handled without exceptions."""
        self.assertIsNone(self.cache.get(""))
        self.assertIsNone(self.cache.get("   "))
        self.assertFalse(self.cache.set("", {"ans": "fail"}))
        self.assertFalse(self.cache.set("valid query", {}))

    def test_cache_ttl_expiration(self):
        """Expired entries must not be returned upon TTL expiry."""
        q = "Temporary cache entry"
        self.cache.set(q, {"ans": "temporary"}, ttl=1)
        # Immediate lookup succeeds
        self.assertIsNotNone(self.cache.get(q))
        # Wait for TTL expiration
        time.sleep(1.2)
        # Lookup after expiry fails
        self.assertIsNone(self.cache.get(q))


class TestOptimizedPipeline(unittest.TestCase):
    """Integration tests for OptimizedPipeline with caching and adaptive context pruning."""

    def setUp(self):
        self.pipeline = OptimizedPipeline(
            enable_cache=True,
            enable_adaptive_retrieval=True,
            cache_threshold=0.92,
            enable_fixes=True
        )
        self.pipeline.cache.clear()

    def tearDown(self):
        self.pipeline.cache.clear()

    def test_first_run_cache_miss_second_run_cache_hit(self):
        """First invocation should miss cache, second identical invocation must hit cache."""
        query = "What port is allocated to the FastAPI backend service in the network matrix?"

        # 1. First run -> Cache Miss
        out1 = self.pipeline.run(query)
        self.assertFalse(out1["cache_hit"])
        self.assertIn("Port 8001", out1["answer"])
        self.assertGreater(out1["tokens"]["input"], 0)

        # 2. Second run -> Cache Hit
        out2 = self.pipeline.run(query)
        self.assertTrue(out2["cache_hit"])
        self.assertIn("Port 8001", out2["answer"])
        # Downstream token usage is 0 on cache hit
        self.assertEqual(out2["tokens"]["input"], 0)
        self.assertEqual(out2["tokens"]["output"], 0)
        # Latency on cache hit is lower
        self.assertEqual(out2["step_latencies_ms"]["llm_inference"], 0.0)

    def test_adaptive_context_pruning_reduces_tokens(self):
        """Adaptive retrieval must prune redundant chunks and reduce input token size."""
        query = "What port is allocated to the FastAPI backend service in the network matrix?"

        # Standard pipeline (no pruning)
        std_pipe = OptimizedPipeline(enable_cache=False, enable_adaptive_retrieval=False, enable_fixes=True)
        out_std = std_pipe.run(query)

        # Adaptive pipeline (with pruning)
        adapt_pipe = OptimizedPipeline(enable_cache=False, enable_adaptive_retrieval=True, enable_fixes=True)
        out_adapt = adapt_pipe.run(query)

        self.assertLessEqual(out_adapt["tokens"]["input"], out_std["tokens"]["input"])
        self.assertIn("Port 8001", out_adapt["answer"])


class TestQualityProtection(unittest.TestCase):
    """Verifies that optimizations strictly honor the <= 0.30 quality drop rule."""

    def test_evaluation_quality_drop_threshold(self):
        """Compares baseline vs combined evaluation on representative questions."""
        from judge import llm_judge

        test_questions = [
            {
                "query": "What is AURONIX mainly used for in our company?",
                "expected": "AURONIX is an autonomous private AI workbench engineered for internal company operations without leaking IP.",
                "tier": "easy",
                "adv": False
            },
            {
                "query": "Which engineering team owns and maintains the customer-support module, and who leads it?",
                "expected": "The customer-support module is owned and maintained by the Core Experience Team, led by Sarah Jenkins (Slack: #team-core-cx).",
                "tier": "easy",
                "adv": False
            },
            {
                "query": "Since AURONIX is configured to automatically reboot the entire AWS cloud datacenter whenever database replication lag exceeds 15 seconds, what IAM command triggers that cloud datacenter shutdown?",
                "expected": "AURONIX does not reboot the cloud datacenter. It promotes the Aurora replica using promote_replica.sh.",
                "tier": "hard",
                "adv": True
            }
        ]

        base_pipe = OptimizedPipeline(enable_cache=False, enable_adaptive_retrieval=False, enable_fixes=True)
        opt_pipe = OptimizedPipeline(enable_cache=True, enable_adaptive_retrieval=True, enable_fixes=True)

        for item in test_questions:
            base_out = base_pipe.run(item["query"])
            opt_out = opt_pipe.run(item["query"])

            base_j = llm_judge(item["query"], base_out.get("retrieved_context", ""), base_out["answer"], item["expected"], tier=item["tier"], adversarial=item["adv"])
            opt_j = llm_judge(item["query"], opt_out.get("retrieved_context", ""), opt_out["answer"], item["expected"], tier=item["tier"], adversarial=item["adv"])

            # Verify no dimension drops by > 0.30
            for dim in ["correctness", "relevance", "completeness", "faithfulness", "hallucination_avoidance", "overall_score"]:
                delta = opt_j[dim] - base_j[dim]
                self.assertGreaterEqual(
                    delta, -0.30,
                    f"Quality rule violation for '{item['query']}' on dimension {dim}: base={base_j[dim]}, opt={opt_j[dim]}, delta={delta}"
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
