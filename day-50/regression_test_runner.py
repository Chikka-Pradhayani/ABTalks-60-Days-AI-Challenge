"""AURONIX Regression Test Runner.

Implements regression_test_runner() to verify that the AI product satisfies
all tier and dimensional thresholds, printing PASS/FAIL status with detailed
telemetry and persisting timestamped test records.
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, Any, Tuple

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from eval_runner import run_evaluation, save_timestamped_results

DEFAULT_MIN_THRESHOLDS = {
    "easy": 4.0,
    "medium": 3.5,
    "hard": 3.0,
    "overall": 3.5,
    "correctness": 3.5,
    "relevance": 3.5,
    "completeness": 3.0,
    "faithfulness": 3.5,
    "hallucination_avoidance": 3.5
}


def regression_test_runner(
    thresholds: Dict[str, float] = None,
    dataset_path: str = os.path.join(CURRENT_DIR, "eval_dataset.json"),
    results_dir: str = os.path.join(CURRENT_DIR, "results"),
    enable_fixes: bool = True
) -> Tuple[bool, Dict[str, Any]]:
    """Executes the complete regression test suite against minimum thresholds.

    Args:
        thresholds: Configurable minimum score thresholds for tiers and dimensions.
        dataset_path: Path to 30-question JSON dataset.
        results_dir: Directory where timestamped result artifacts are saved.
        enable_fixes: Whether to run with production fixes enabled.

    Returns:
        Tuple of (passed: bool, report: Dict[str, Any]).
    """
    active_thresholds = thresholds or DEFAULT_MIN_THRESHOLDS.copy()

    # 1. Run evaluation
    eval_summary = run_evaluation(dataset_path=dataset_path, enable_fixes=enable_fixes)

    tier_avgs = eval_summary["tier_averages"]
    dim_avgs = eval_summary["dimensional_averages"]

    all_scores = {
        "easy": tier_avgs["easy"],
        "medium": tier_avgs["medium"],
        "hard": tier_avgs["hard"],
        "overall": tier_avgs["overall"],
        **dim_avgs
    }

    # 2. Threshold checks
    failed_dimensions = []
    passed_dimensions = []

    for dim, min_req in active_thresholds.items():
        actual_val = all_scores.get(dim)
        if actual_val is None:
            continue
        if actual_val < min_req:
            failed_dimensions.append({
                "dimension": dim,
                "score": actual_val,
                "required": min_req,
                "deficit": round(min_req - actual_val, 2)
            })
        else:
            passed_dimensions.append({
                "dimension": dim,
                "score": actual_val,
                "required": min_req,
                "surplus": round(actual_val - min_req, 2)
            })

    passed = len(failed_dimensions) == 0

    # 3. Print output
    print("\n" + "=" * 80)
    print("REGRESSION TEST SUITE RESULT")
    print("=" * 80)
    if passed:
        print("\nSTATUS: PASS\n")
        print(f"Easy:    {tier_avgs['easy']} (Threshold: {active_thresholds.get('easy', 'N/A')})")
        print(f"Medium:  {tier_avgs['medium']} (Threshold: {active_thresholds.get('medium', 'N/A')})")
        print(f"Hard:    {tier_avgs['hard']} (Threshold: {active_thresholds.get('hard', 'N/A')})")
        print(f"Overall: {tier_avgs['overall']} (Threshold: {active_thresholds.get('overall', 'N/A')})")
        print("\nAll quality and safety dimensions satisfied minimum criteria.")
    else:
        print("\nSTATUS: FAIL\n")
        print("Failed Dimensions:")
        for fd in failed_dimensions:
            print(f"  Dimension: {fd['dimension'].capitalize()}")
            print(f"  Score:     {fd['score']}")
            print(f"  Required:  {fd['required']}")
            print(f"  Deficit:   -{fd['deficit']}\n")

    # 4. Save timestamped regression report
    os.makedirs(results_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    report_filename = f"regression_results_{ts}.json"
    report_filepath = os.path.join(results_dir, report_filename)

    regression_report = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "PASS" if passed else "FAIL",
        "thresholds": active_thresholds,
        "measured_scores": all_scores,
        "failed_dimensions": failed_dimensions,
        "passed_dimensions": passed_dimensions,
        "eval_run_id": f"eval_{ts}",
        "raw_results_file": report_filename
    }

    with open(report_filepath, "w", encoding="utf-8") as f:
        json.dump(regression_report, f, indent=2, ensure_ascii=False)

    print(f"\n[SAVED] Regression report stored at: {report_filepath}")
    return passed, regression_report


if __name__ == "__main__":
    passed, report = regression_test_runner()
    sys.exit(0 if passed else 1)
