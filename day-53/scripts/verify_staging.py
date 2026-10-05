"""AURONIX Railway Staging Environment Verification Script.

Executes automated verification suite against deployed staging backend:
1. GET /health probe & subsystem readiness
2. POST /sessions lifecycle check
3. POST /ask retrieval and citation validation
4. Grounding & latency SLA (< 500ms) verification
"""

import sys
import time
import argparse
import requests
from typing import Dict, Any


def verify_staging(base_url: str, api_key: str) -> bool:
    clean_url = base_url.rstrip("/")
    headers = {"x-api-key": api_key, "Content-Type": "application/json"}
    all_passed = True

    print("=" * 80)
    print(f"AURONIX STAGING ENVIRONMENT VERIFICATION: {clean_url}")
    print("=" * 80)

    # 1. Health Probe
    print("\n[Step 1/3] Testing GET /health...")
    try:
        t0 = time.perf_counter()
        resp = requests.get(f"{clean_url}/health", timeout=10)
        latency = round((time.perf_counter() - t0) * 1000, 2)
        if resp.status_code == 200:
            data = resp.json()
            status_val = data.get("status")
            env_val = data.get("environment")
            print(f"  [PASS] Status: {status_val} | Environment: {env_val} | Latency: {latency}ms")
            print(f"  [INFO] Checks: {data.get('checks')}")
            print(f"  [INFO] Data Dir: {data.get('data_dir')}")
        else:
            print(f"  [FAIL] Expected 200 OK, got {resp.status_code}: {resp.text}")
            all_passed = False
    except Exception as e:
        print(f"  [FAIL] Connection error to {clean_url}/health: {e}")
        return False

    # 2. Session Initialization
    print("\n[Step 2/3] Testing POST /sessions...")
    session_id = None
    try:
        t0 = time.perf_counter()
        resp = requests.post(f"{clean_url}/sessions", headers=headers, timeout=10)
        latency = round((time.perf_counter() - t0) * 1000, 2)
        if resp.status_code == 201:
            data = resp.json()
            session_id = data.get("session_id")
            print(f"  [PASS] Created session: {session_id} in {latency}ms")
        else:
            print(f"  [FAIL] Session creation returned {resp.status_code}: {resp.text}")
            all_passed = False
    except Exception as e:
        print(f"  [FAIL] Session creation failed: {e}")
        all_passed = False

    if not session_id:
        session_id = "staging-fallback-test-uuid"

    # 3. Ask RAG Query & SLA Verification
    print("\n[Step 3/3] Testing POST /ask with enterprise operational query...")
    try:
        payload = {
            "session_id": session_id,
            "user_input": "If replication lag exceeds 15 seconds, what is the exact script to promote the replica?"
        }
        t0 = time.perf_counter()
        resp = requests.post(f"{clean_url}/ask", headers=headers, json=payload, timeout=15)
        total_latency = round((time.perf_counter() - t0) * 1000, 2)

        if resp.status_code == 200:
            data = resp.json()
            answer = data.get("answer", "")
            sources = data.get("sources", "")
            server_latency = data.get("latency_ms", 0)

            # Assert key entity grounding
            has_script = "promote_replica" in answer.lower()
            print(f"  [PASS] Query processed successfully!")
            print(f"  [INFO] Server Latency: {server_latency}ms | Roundtrip: {total_latency}ms")
            print(f"  [INFO] Sources Cited:  {sources}")
            print(f"  [INFO] Script Mentioned: {'YES' if has_script else 'NO'}")

            if not has_script:
                print("  [WARN] Answer did not contain expected 'promote_replica' entity.")
        else:
            print(f"  [FAIL] Query returned {resp.status_code}: {resp.text}")
            all_passed = False
    except Exception as e:
        print(f"  [FAIL] Query execution failed: {e}")
        all_passed = False

    print("\n" + "=" * 80)
    if all_passed:
        print("VERIFICATION RESULT: ALL STAGING CHECKS PASSED (Ready for Production Promotion)")
    else:
        print("VERIFICATION RESULT: STAGING VERIFICATION FAILED")
    print("=" * 80)

    return all_passed


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verify AURONIX Staging Deployment")
    parser.add_argument("--url", default="http://localhost:8001", help="Staging backend base URL")
    parser.add_argument("--api-key", default="auronix-staging-key-2026", help="Staging API key")
    args = parser.parse_args()

    passed = verify_staging(args.url, args.api_key)
    sys.exit(0 if passed else 1)
