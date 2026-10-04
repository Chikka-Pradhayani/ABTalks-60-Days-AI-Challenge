"""AURONIX End-to-End Performance and Cost Profiler.

Profiles the complete AI pipeline across 20 representative queries:
1. Logs per-step execution time in milliseconds:
   - input_validation_normalization
   - semantic_cache_lookup
   - knowledge_retrieval_ranking
   - prompt_assembly
   - llm_inference
   - response_formatting
2. Logs OpenAI API token counts:
   - Input tokens
   - Output tokens
   - Total tokens
3. Calculates estimated API costs based on official OpenAI pricing models:
   - gpt-4o-mini: $0.15 / 1M input tokens, $0.60 / 1M output tokens
   - text-embedding-3-small: $0.02 / 1M tokens
4. Computes:
   - Average cost per query
   - Average latency per query
   - Latency breakdown per individual pipeline stage
5. Exports structured profiles to JSON and CSV formats.
"""

import os
import csv
import json
import time
from typing import Dict, Any, List, Optional
from collections import defaultdict

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
    _ENCODER = tiktoken.get_encoding("cl100k_base")
except Exception:
    TIKTOKEN_AVAILABLE = False
    _ENCODER = None


# Official OpenAI pricing as of 2024-2026 (per 1,000,000 tokens)
MODEL_PRICING = {
    "gpt-4o-mini": {
        "input_per_million": 0.15,
        "output_per_million": 0.60,
    },
    "gpt-4o": {
        "input_per_million": 2.50,
        "output_per_million": 10.00,
    },
    "text-embedding-3-small": {
        "input_per_million": 0.02,
        "output_per_million": 0.00,
    }
}


def count_tokens(text: str) -> int:
    """Counts tokens accurately using tiktoken cl100k_base with character fallback."""
    if not text:
        return 0
    if TIKTOKEN_AVAILABLE and _ENCODER:
        try:
            return len(_ENCODER.encode(text))
        except Exception:
            pass
    # Fallback heuristic: ~4 characters per token
    return max(1, len(text) // 4)


def estimate_api_cost(
    input_tokens: int,
    output_tokens: int,
    model: str = "gpt-4o-mini",
    embedding_tokens: int = 0
) -> float:
    """Computes exact estimated USD cost for an OpenAI invocation."""
    pricing = MODEL_PRICING.get(model, MODEL_PRICING["gpt-4o-mini"])
    input_cost = (input_tokens / 1_000_000.0) * pricing["input_per_million"]
    output_cost = (output_tokens / 1_000_000.0) * pricing["output_per_million"]

    emb_pricing = MODEL_PRICING["text-embedding-3-small"]
    emb_cost = (embedding_tokens / 1_000_000.0) * emb_pricing["input_per_million"]

    return round(input_cost + output_cost + emb_cost, 7)


class PipelineProfiler:
    """Session profiler recording step latencies, token counts, and API costs."""

    def __init__(self, session_name: str = "auronix_profile"):
        self.session_name = session_name
        self.query_profiles: List[Dict[str, Any]] = []

    def record_query(
        self,
        query_id: str,
        query_text: str,
        step_latencies_ms: Dict[str, float],
        input_tokens: int,
        output_tokens: int,
        cache_hit: bool,
        model: str = "gpt-4o-mini",
        embedding_tokens: int = 0,
        extra_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Records metrics for a single query."""
        total_tokens = input_tokens + output_tokens + embedding_tokens
        total_latency_ms = round(sum(step_latencies_ms.values()), 3)

        cost = estimate_api_cost(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model=model,
            embedding_tokens=embedding_tokens
        )

        profile_entry = {
            "query_id": query_id,
            "query_text": query_text,
            "cache_hit": cache_hit,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "embedding_tokens": embedding_tokens,
            "total_tokens": total_tokens,
            "estimated_cost_usd": cost,
            "step_latencies_ms": step_latencies_ms,
            "total_latency_ms": total_latency_ms,
            "metadata": extra_metadata or {}
        }
        self.query_profiles.append(profile_entry)
        return profile_entry

    def compute_summary(self) -> Dict[str, Any]:
        """Calculates aggregated metrics across all recorded queries."""
        total_queries = len(self.query_profiles)
        if total_queries == 0:
            return {"total_queries": 0}

        total_cost = sum(q["estimated_cost_usd"] for q in self.query_profiles)
        total_latency = sum(q["total_latency_ms"] for q in self.query_profiles)
        total_input_tokens = sum(q["input_tokens"] for q in self.query_profiles)
        total_output_tokens = sum(q["output_tokens"] for q in self.query_profiles)
        total_emb_tokens = sum(q["embedding_tokens"] for q in self.query_profiles)
        cache_hits = sum(1 for q in self.query_profiles if q["cache_hit"])

        # Stage latency aggregations
        stage_times = defaultdict(list)
        for q in self.query_profiles:
            for stage, ms in q["step_latencies_ms"].items():
                stage_times[stage].append(ms)

        stage_breakdown = {}
        for stage, times in stage_times.items():
            avg_time = sum(times) / len(times)
            stage_breakdown[stage] = {
                "mean_ms": round(avg_time, 3),
                "min_ms": round(min(times), 3),
                "max_ms": round(max(times), 3),
                "pct_of_total": round((avg_time / (total_latency / total_queries) * 100), 2) if total_latency > 0 else 0.0
            }

        avg_cost_per_query = total_cost / total_queries
        avg_latency_per_query = total_latency / total_queries

        return {
            "session_name": self.session_name,
            "total_queries": total_queries,
            "cache_hits": cache_hits,
            "cache_hit_rate_pct": round((cache_hits / total_queries) * 100, 2),
            "total_cost_usd": round(total_cost, 6),
            "avg_cost_per_query_usd": round(avg_cost_per_query, 7),
            "avg_latency_per_query_ms": round(avg_latency_per_query, 3),
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "total_embedding_tokens": total_emb_tokens,
            "avg_input_tokens_per_query": round(total_input_tokens / total_queries, 1),
            "avg_output_tokens_per_query": round(total_output_tokens / total_queries, 1),
            "stage_breakdown": stage_breakdown,
        }

    def save_json(self, filepath: str) -> str:
        """Saves profiling session data to a JSON file."""
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        data = {
            "summary": self.compute_summary(),
            "queries": self.query_profiles
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return filepath

    def save_csv(self, filepath: str) -> str:
        """Saves detailed query-by-query breakdown to a CSV file."""
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        if not self.query_profiles:
            return filepath

        fieldnames = [
            "query_id", "cache_hit", "input_tokens", "output_tokens",
            "total_tokens", "estimated_cost_usd", "total_latency_ms"
        ]

        # Collect all unique step names
        all_steps = sorted({s for q in self.query_profiles for s in q["step_latencies_ms"].keys()})
        fieldnames.extend([f"step_{s}_ms" for s in all_steps])
        fieldnames.append("query_text")

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for q in self.query_profiles:
                row = {
                    "query_id": q["query_id"],
                    "cache_hit": q["cache_hit"],
                    "input_tokens": q["input_tokens"],
                    "output_tokens": q["output_tokens"],
                    "total_tokens": q["total_tokens"],
                    "estimated_cost_usd": q["estimated_cost_usd"],
                    "total_latency_ms": q["total_latency_ms"],
                    "query_text": q["query_text"]
                }
                for s in all_steps:
                    row[f"step_{s}_ms"] = q["step_latencies_ms"].get(s, 0.0)
                writer.writerow(row)

        return filepath
