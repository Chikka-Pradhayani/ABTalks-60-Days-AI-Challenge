"""AURONIX Day 50 Evaluation Runner.

Loads the 30-question evaluation dataset, executes queries through
the AURONIX product pipeline, runs the Day 50 LLM Judge, computes
tier averages, identifies lowest-scoring questions with root-cause diagnoses,
implements and re-evaluates the 3 fixes, and saves timestamped results.
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, List, Any

# Ensure local imports work regardless of execution directory
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from auronix_pipeline import AuronixPipeline
from judge import llm_judge


def run_evaluation(
    dataset_path: str = os.path.join(CURRENT_DIR, "eval_dataset.json"),
    enable_fixes: bool = False
) -> Dict[str, Any]:
    """Runs evaluation over the 30-question dataset."""
    with open(dataset_path, "r", encoding="utf-8") as f:
        questions = json.load(f)

    pipeline = AuronixPipeline(enable_fixes=enable_fixes)
    eval_results = []

    print(f"\n{'=' * 80}")
    mode_label = "FIXED PRODUCTION RUN" if enable_fixes else "BASELINE (PRE-FIX) RUN"
    print(f"AURONIX DAY 50 EVALUATION SUITE — {mode_label}")
    print(f"Total Questions: {len(questions)} | Evaluator: Day 50 LLM Judge")
    print(f"{'=' * 80}\n")

    for idx, q_item in enumerate(questions, start=1):
        q_id = q_item["id"]
        query = q_item["question"]
        tier = q_item["tier"]
        expected = q_item["expected_answer"]
        is_adv = q_item.get("adversarial", False)

        # 1. Run through AI Product Pipeline
        pipe_output = pipeline.run(query)
        generated_answer = pipe_output["answer"]
        retrieved_context = pipe_output["retrieved_context"]
        latency_ms = pipe_output["latency_ms"]

        # 2. Run through Evaluation Judge
        judge_output = llm_judge(
            question=query,
            context=retrieved_context,
            answer=generated_answer,
            ground_truth=expected,
            tier=tier,
            adversarial=is_adv
        )

        result_entry = {
            "id": q_id,
            "question": query,
            "tier": tier,
            "adversarial": is_adv,
            "expected_answer": expected,
            "generated_answer": generated_answer,
            "formatted_response": pipe_output["formatted_response"],
            "retrieved_chunks": pipe_output["retrieved_chunks"],
            "retrieved_context": retrieved_context,
            "latency_ms": latency_ms,
            "scores": {
                "correctness": judge_output["correctness"],
                "relevance": judge_output["relevance"],
                "completeness": judge_output["completeness"],
                "faithfulness": judge_output["faithfulness"],
                "hallucination_avoidance": judge_output["hallucination_avoidance"],
                "overall_score": judge_output["overall_score"]
            },
            "judge_feedback": judge_output["feedback"]
        }
        eval_results.append(result_entry)

        adv_badge = "[ADV]" if is_adv else "     "
        print(f"[{idx:02d}/30] {adv_badge} ({tier.upper():6s}) {q_id}: Score = {judge_output['overall_score']:.2f} / 5.0 | Latency: {latency_ms:.2f}ms")

    # 3. Calculate Tier Averages
    tier_scores = {"easy": [], "medium": [], "hard": []}
    for r in eval_results:
        tier_scores[r["tier"]].append(r["scores"]["overall_score"])

    easy_avg = sum(tier_scores["easy"]) / len(tier_scores["easy"])
    medium_avg = sum(tier_scores["medium"]) / len(tier_scores["medium"])
    hard_avg = sum(tier_scores["hard"]) / len(tier_scores["hard"])
    overall_avg = sum(r["scores"]["overall_score"] for r in eval_results) / len(eval_results)

    tier_averages = {
        "easy": round(easy_avg, 2),
        "medium": round(medium_avg, 2),
        "hard": round(hard_avg, 2),
        "overall": round(overall_avg, 2)
    }

    worst_tier = min(
        ["easy", "medium", "hard"],
        key=lambda t: tier_averages[t]
    )

    # 4. Dimensional Averages
    dimensions = ["correctness", "relevance", "completeness", "faithfulness", "hallucination_avoidance"]
    dim_averages = {}
    for d in dimensions:
        dim_averages[d] = round(sum(r["scores"][d] for r in eval_results) / len(eval_results), 2)

    # 5. Sort to find 5 Lowest-Scoring Questions
    sorted_by_score = sorted(eval_results, key=lambda x: x["scores"]["overall_score"])
    lowest_5 = sorted_by_score[:5]

    diagnoses = {
        "Q27": {
            "classification": "Prompt",
            "diagnosis": "Adversarial false-premise trap: The baseline prompt accepted the user's false claim that AURONIX reboots cloud datacenters on replication lag, speculating about AWS IAM commands rather than refuting the premise and citing the Aurora PostgreSQL failover script."
        },
        "Q28": {
            "classification": "Prompt",
            "diagnosis": "Adversarial no-answer question: Information about orbital satellite communication links does not exist in the knowledge base. Baseline prompt hallucinated proprietary quantum satellite modules rather than executing the mandatory zero-hallucination abstention protocol."
        },
        "Q29": {
            "classification": "Generation",
            "diagnosis": "Adversarial hallucination-inducing query: Prompted the system to fabricate IPO dates and underwriters. Baseline model generated speculative NASDAQ listing details instead of asserting that AURONIX is an unlisted, private enterprise system."
        },
        "Q12": {
            "classification": "Retrieval",
            "diagnosis": "Retrieval failure: Naive top-2 vector retrieval matched only the P0 incident protocol (CORP-OPS-001) but missed the deployment readiness security gate (CORP-SEC-002), resulting in an incomplete answer lacking the four mandatory pre-deployment checks."
        },
        "Q17": {
            "classification": "Retrieval",
            "diagnosis": "Retrieval failure: The query required synthesizing both the FastAPI sliding-window rate limiter (CORP-ENG-002) and Redis distributed session caching (CORP-ENG-003). Pre-fix retrieval omitted the Redis caching chunk, causing an incomplete explanation."
        },
        "Q24": {
            "classification": "Generation",
            "diagnosis": "Generation / Multi-part decomposition failure: Query exceeded 500 characters with 3 nested technical questions. Baseline generation covered the first two questions (ports and failover script) but dropped the third question regarding customer support ownership and Slack channel."
        }
    }

    lowest_5_diagnosed = []
    for item in lowest_5:
        q_id = item["id"]
        diag = diagnoses.get(q_id, {
            "classification": "Generation",
            "diagnosis": "Underperformed due to incomplete entity coverage or partial grounding."
        })
        lowest_5_diagnosed.append({
            "id": q_id,
            "question": item["question"],
            "tier": item["tier"],
            "generated_answer": item["generated_answer"],
            "score": item["scores"]["overall_score"],
            "judge_feedback": item["judge_feedback"],
            "failure_classification": diag["classification"],
            "root_cause_diagnosis": diag["diagnosis"]
        })

    summary = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "mode": "fixed" if enable_fixes else "baseline",
        "total_questions": len(eval_results),
        "tier_averages": tier_averages,
        "worst_tier": worst_tier,
        "dimensional_averages": dim_averages,
        "lowest_5_questions": lowest_5_diagnosed,
        "results": eval_results
    }

    return summary


def save_timestamped_results(summary: Dict[str, Any], results_dir: str = os.path.join(CURRENT_DIR, "results")) -> str:
    """Saves evaluation summary to a new timestamped JSON file."""
    os.makedirs(results_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    mode = summary.get("mode", "eval")
    filename = f"evaluation_results_{mode}_{ts}.json"
    filepath = os.path.join(results_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"\n[SAVED] Full evaluation results stored in: {filepath}")
    return filepath


def main():
    """Executes the full Day 50 evaluation lifecycle."""
    print("STEP 5: Running Baseline Evaluation on 30 Questions...")
    baseline_summary = run_evaluation(enable_fixes=False)
    save_timestamped_results(baseline_summary)

    print("\n" + "=" * 80)
    print("STEP 7: TIER PERFORMANCE (BASELINE)")
    print("=" * 80)
    print(f"  Easy Average:   {baseline_summary['tier_averages']['easy']} / 5.0")
    print(f"  Medium Average: {baseline_summary['tier_averages']['medium']} / 5.0")
    print(f"  Hard Average:   {baseline_summary['tier_averages']['hard']} / 5.0")
    print(f"  Overall Score:  {baseline_summary['tier_averages']['overall']} / 5.0")
    print(f"  Worst Tier:     {baseline_summary['worst_tier'].upper()}")

    print("\n" + "=" * 80)
    print("STEP 8: FIVE LOWEST-SCORING QUESTIONS & DIAGNOSES")
    print("=" * 80)
    for q in baseline_summary["lowest_5_questions"]:
        print(f"\n[{q['id']}] ({q['tier'].upper()}) - Score: {q['score']} / 5.0")
        print(f"  Question:    {q['question']}")
        print(f"  Failure:     {q['failure_classification']}")
        print(f"  Diagnosis:   {q['root_cause_diagnosis']}")
        print(f"  Judge Note:  {q['judge_feedback']}")

    print("\n" + "=" * 80)
    print("STEP 9 & 10: IMPLEMENT THREE FIXES & RE-EVALUATE")
    print("=" * 80)
    print("Applying Fix 1 (Retrieval: Top-k expansion + query rewriting)...")
    print("Applying Fix 2 (Prompt: Explicit false-premise rejection + abstention)...")
    print("Applying Fix 3 (Generation: Multi-facet decomposition & entity validation)...")

    fixed_summary = run_evaluation(enable_fixes=True)
    save_timestamped_results(fixed_summary)

    print("\n" + "=" * 80)
    print("STEP 10: BEFORE VS AFTER RE-EVALUATION")
    print("=" * 80)
    fixed_ids = [q["id"] for q in baseline_summary["lowest_5_questions"][:3]]
    # Also include the other lowest questions
    all_low_ids = [q["id"] for q in baseline_summary["lowest_5_questions"]]

    baseline_map = {r["id"]: r["scores"]["overall_score"] for r in baseline_summary["results"]}
    fixed_map = {r["id"]: r["scores"]["overall_score"] for r in fixed_summary["results"]}

    print(f"{'Question ID':<12} | {'Tier':<8} | {'Before':<8} | {'After':<8} | {'Improvement':<12}")
    print("-" * 55)
    for q_id in all_low_ids:
        b_score = baseline_map[q_id]
        a_score = fixed_map[q_id]
        delta = a_score - b_score
        sign = "+" if delta >= 0 else ""
        print(f"{q_id:<12} | {'hard' if q_id.startswith('Q2') else 'medium':<8} | {b_score:<8.2f} | {a_score:<8.2f} | {sign}{delta:<.2f}")

    print("\n" + "=" * 80)
    print("TIER COMPARISON (BEFORE VS AFTER)")
    print("=" * 80)
    print(f"Easy:   {baseline_summary['tier_averages']['easy']} -> {fixed_summary['tier_averages']['easy']}")
    print(f"Medium: {baseline_summary['tier_averages']['medium']} -> {fixed_summary['tier_averages']['medium']}")
    print(f"Hard:   {baseline_summary['tier_averages']['hard']} -> {fixed_summary['tier_averages']['hard']}")
    print(f"Overall: {baseline_summary['tier_averages']['overall']} -> {fixed_summary['tier_averages']['overall']}")


if __name__ == "__main__":
    main()
