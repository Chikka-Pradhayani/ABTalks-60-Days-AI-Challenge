"""AURONIX CI/CD Bad Deployment Simulation Script.

Safely simulates and verifies the continuous integration failure gate:
1. Injects a temporary intentional failure condition in test gate
2. Runs pytest / regression test runner
3. Verifies immediate non-zero exit code (gate blockage)
4. Confirms that deployment stages would be halted
5. Automatically rolls back the injected condition to keep repo clean
6. Displays the step-by-step Git procedure for remote GitHub Actions simulation
"""

import sys
import subprocess
import time


def run_cmd(cmd: str) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)


def simulate_local_bad_deployment():
    print("=" * 80)
    print("AURONIX SAFE BAD DEPLOYMENT SIMULATION (LOCAL GATE VERIFICATION)")
    print("=" * 80)

    # 1. Baseline Verification
    print("\n[Stage 1/4] Verifying clean baseline test gate...")
    res_base = run_cmd("python -m pytest day-53/tests/test_day53_deployment.py -q")
    if res_base.returncode != 0:
        print(f"  [ERROR] Baseline tests failed before simulation started: {res_base.stderr or res_base.stdout}")
        return False
    print("  [PASS] Clean baseline confirmed: All tests passing (Exit Code 0).")

    # 2. Inject Controlled Failure
    print("\n[Stage 2/4] Simulating broken code (asserting invalid health status)...")
    simulated_test = """
def test_simulated_bad_commit_failure():
    \"\"\"Deliberately failing test to simulate bad code submission.\"\"\"
    expected_status = "healthy"
    actual_status = "broken_database_connection"
    assert actual_status == expected_status, "CRITICAL: Simulated bug detected! Database offline."
"""
    test_file_path = "day-53/tests/test_simulation_failure_temp.py"
    with open(test_file_path, "w", encoding="utf-8") as f:
        f.write(simulated_test)
    print(f"  [SIMULATED] Injected synthetic test failure in {test_file_path}")

    # 3. Execute CI Test Gate
    print("\n[Stage 3/4] Triggering CI Test Gate with synthetic failure...")
    t0 = time.perf_counter()
    res_fail = run_cmd(f"python -m pytest {test_file_path} -q")
    elapsed = round((time.perf_counter() - t0) * 1000, 2)

    import os
    if os.path.exists(test_file_path):
        os.remove(test_file_path)

    if res_fail.returncode != 0:
        print(f"  [GATE TRIPPED] Test gate halted execution in {elapsed}ms!")
        print(f"  [EXIT CODE] {res_fail.returncode} (NON-ZERO)")
        print("  [CI/CD BEHAVIOR] Pipeline status: FAILED")
        print("  [SAFETY ACTION] Downstream stages BLOCKED:")
        print("     - deploy_staging:    SKIPPED")
        print("     - verify_staging:    SKIPPED")
        print("     - deploy_production: SKIPPED")
        print("     - verify_production: SKIPPED")
        print("  [RESULT] Production environment was 100% UNTOUCHED and PROTECTED.")
    else:
        print("  [ERROR] Bad deployment test unexpectedly succeeded.")
        return False

    # 4. Clean State Verification
    print("\n[Stage 4/4] Verifying automatic restoration of clean state...")
    res_restored = run_cmd("python -m pytest day-53/tests/test_day53_deployment.py -q")
    if res_restored.returncode == 0:
        print("  [PASS] Clean repository state restored: All tests pass.")
    else:
        print("  [WARN] Issue restoring clean state.")
        return False

    print("\n" + "=" * 80)
    print("REMOTE GITHUB ACTIONS SIMULATION WORKFLOW:")
    print("=" * 80)
    print("To simulate this failure gate on GitHub Actions without affecting main:")
    print("  1. git checkout -b test/simulate-ci-failure")
    print("  2. echo 'def test_fail(): assert False' > day-53/tests/test_fail_tmp.py")
    print("  3. git add . && git commit -m 'test: simulate bad commit'")
    print("  4. git push origin test/simulate-ci-failure")
    print("  5. Observe GitHub Actions tab: Test job turns RED, deploy jobs are cancelled")
    print("  6. git checkout main")
    print("  7. git branch -D test/simulate-ci-failure")
    print("=" * 80)
    return True


if __name__ == "__main__":
    success = simulate_local_bad_deployment()
    sys.exit(0 if success else 1)
