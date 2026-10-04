"""AURONIX Day 52 Quality Protection and Regression Evaluation Suite.

Reuses the Day 50 evaluation dataset (30 questions) and the Day 50 LLM Judge:
1. Evaluates Phase 1: Baseline (Pre-Optimisation)
2. Evaluates Phase 2: After Semantic Caching
3. Evaluates Phase 3: After Additional Optimisation (Adaptive Context Pruning)
4. Evaluates Phase 4: Combined (Semantic Caching + Adaptive Context Pruning)
5. Verifies the Strict Quality Protection Rule:
   - No individual quality dimension (Correctness, Relevance, Completeness, Faithfulness,
     Hallucination Avoidance, Overall) may drop by more than 0.30 below the baseline.
6. Saves detailed evaluation comparisons to results/evaluation_results_day52.json.
"""

import os
import sys
import json
import time
from typing import Dict, Any, List

# Ensure local imports
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(CURRENT_DIR)
DAY50_DIR = os.path.join(REPO_ROOT, "day-50")
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)
if DAY50_DIR not in sys.path:
    sys.path.insert(0, DAY50_DIR)

from judge import llm_judge
from optimized_pipeline import OptimizedPipeline

DATASET_PATH = os.path.join(DAY50_DIR, "eval_dataset.json")


def evaluate_configuration(
    pipeline: OptimizedPipeline,
    config_name: str,
    dataset: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Runs the 30-question Day 50 evaluation suite on a specific pipeline configuration."""
    eval_entries = []
    latencies = []

    print(f"\nEvaluating Configuration: {config_name} ({len(dataset)} questions)...")

    for idx, item in enumerate(dataset, start=1):
        q_id = item["id"]
        query = item["question"]
        tier = item["tier"]
        expected = item["expected_answer"]
        is_adv = item.get("adversarial", False)

        # Run pipeline
        out = pipeline.run(query)
        latencies.append(out["total_latency_ms"])

        # Judge
        judge_out = llm_judge(
            question=query,
            context=out.get("retrieved_context", ""),
            answer=out["answer"],
            ground_truth=expected,
            tier=tier,
            adversarial=is_adv
        )

        entry = {
            "id": q_id,
            "tier": tier,
            "adversarial": is_adv,
            "cache_hit": out.get("cache_hit", False),
            "latency_ms": out["total_latency_ms"],
            "scores": {
                "correctness": judge_out["correctness"],
                "relevance": judge_out["relevance"],
                "completeness": judge_out["completeness"],
                "faithfulness": judge_out["faithfulness"],
                "hallucination_avoidance": judge_out["hallucination_avoidance"],
                "overall_score": judge_out["overall_score"]
            }
        }
        eval_entries.append(entry)

    # Compute aggregate dimensional scores
    dimensions = ["correctness", "relevance", "completeness", "faithfulness", "hallucination_avoidance", "overall_score"]
    dim_averages = {}
    for d in dimensions:
        dim_averages[d] = round(sum(e["scores"][d] for e in eval_entries) / len(eval_entries), 3)

    # Tier averages
    tier_scores = {"easy": [], "medium": [], "hard": []}
    for e in eval_entries:
        tier_scores[e["tier"]].append(e["scores"]["overall_score"])

    tier_averages = {
        tier: round(sum(scores) / len(scores), 3) for tier, scores in tier_scores.items()
    }

    avg_latency = round(sum(latencies) / len(latencies), 3)

    print(f"  Overall Score: {dim_averages['overall_score']} / 5.0 | Avg Latency: {avg_latency:.3f}ms")

    return {
        "config_name": config_name,
        "dimensional_scores": dim_averages,
        "tier_scores": tier_averages,
        "avg_latency_ms": avg_latency,
        "eval_entries": eval_entries
    }


def run_full_quality_suite(
    results_dir: str = os.path.join(CURRENT_DIR, "results")
) -> Dict[str, Any]:
    """Runs all 4 phases and verifies the 0.3 quality protection rule."""
    os.makedirs(results_dir, exist_ok=True)

    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    print("=" * 80)
    print("DAY 52: DAY 50 QUALITY PROTECTION EVALUATION SUITE")
    print("Goal: Verify optimization does not reduce any evaluation dimension by > 0.3")
    print("=" * 80)

    # Phase 1: Baseline (Pre-Optimisation)
    pipe_baseline = OptimizedPipeline(
        enable_cache=False,
        enable_adaptive_retrieval=False,
        enable_fixes=True
    )
    res_baseline = evaluate_configuration(pipe_baseline, "Baseline (Pre-Optimisation)", dataset)

    # Phase 2: Semantic Caching (run twice to evaluate warm cache hits on duplicate runs)
    pipe_cache = OptimizedPipeline(
        enable_cache=True,
        enable_adaptive_retrieval=False,
        enable_fixes=True
    )
    # Warm up cache
    for item in dataset[:10]:
        pipe_cache.run(item["question"])
    res_cache = evaluate_configuration(pipe_cache, "Semantic Caching Only", dataset)

    # Phase 3: Additional Optimisation Only (Adaptive Context Pruning)
    pipe_opt = OptimizedPipeline(
        enable_cache=False,
        enable_adaptive_retrieval=True,
        enable_fixes=True
    )
    res_opt = evaluate_configuration(pipe_opt, "Adaptive Context Pruning Only", dataset)

    # Phase 4: Combined (Semantic Caching + Adaptive Context Pruning)
    pipe_combined = OptimizedPipeline(
        enable_cache=True,
        enable_adaptive_retrieval=True,
        enable_fixes=True
    )
    # Warm up cache for subset
    for item in dataset[:10]:
        pipe_combined.run(item["question"])
    res_combined = evaluate_configuration(pipe_combined, "Combined Optimised", dataset)

    # Dimensional Quality Protection Analysis (0.3 limit)
    dimensions = ["correctness", "relevance", "completeness", "faithfulness", "hallucination_avoidance", "overall_score"]
    delta_analysis = {}
    all_passed = True

    base_dims = res_baseline["dimensional_scores"]
    comb_dims = res_combined["dimensional_scores"]

    for d in dimensions:
        delta = round(comb_dims[d] - base_dims[d], 3)
        # Quality rule: drops cannot exceed 0.30 (i.e. delta cannot be < -0.30)
        passed = delta >= -0.30
        if not passed:
            all_passed = False
        delta_analysis[d] = {
            "baseline": base_dims[d],
            "combined": comb_dims[d],
            "delta": delta,
            "allowed_max_drop": -0.30,
            "passed": passed
        }

    evaluation_report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "quality_rule_satisfied": all_passed,
        "configurations": {
            "baseline": {
                "dimensional_scores": res_baseline["dimensional_scores"],
                "tier_scores": res_baseline["tier_scores"],
                "avg_latency_ms": res_baseline["avg_latency_ms"]
            },
            "semantic_cache_only": {
                "dimensional_scores": res_cache["dimensional_scores"],
                "tier_scores": res_cache["tier_scores"],
                "avg_latency_ms": res_cache["avg_latency_ms"]
            },
            "adaptive_retrieval_only": {
                "dimensional_scores": res_opt["dimensional_scores"],
                "tier_scores": res_opt["tier_scores"],
                "avg_latency_ms": res_opt["avg_latency_ms"]
            },
            "combined_optimised": {
                "dimensional_scores": res_combined["dimensional_scores"],
                "tier_scores": res_combined["tier_scores"],
                "avg_latency_ms": res_combined["avg_latency_ms"]
            }
        },
        "dimensional_protection_check": delta_analysis
    }

    report_path = os.path.join(results_dir, "evaluation_results_day52.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(evaluation_report, f, indent=2)

    print("\n" + "=" * 80)
    print("DAY 50 QUALITY PROTECTION RESULTS")
    print("=" * 80)
    print(f"{'Dimension':<25} | {'Baseline':<10} | {'Combined':<10} | {'Delta':<8} | {'Status':<6}")
    print("-" * 70)
    for d, check in delta_analysis.items():
        status = "PASS" if check["passed"] else "FAIL"
        print(f"{d:<25} | {check['baseline']:<10.3f} | {check['combined']:<10.3f} | {check['delta']:<+8.3f} | {status:<6}")
    print("=" * 80)
    print(f"Overall Quality Rule Satisfied (Drop <= 0.30): {all_passed}")
    print(f"Report saved to: {report_path}\n")

    return evaluation_report


if __name__ == "__main__":
    run_full_quality_suite()
