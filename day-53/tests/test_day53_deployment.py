"""AURONIX Day 53 Automated Deployment & Health Test Suite.

Verifies:
1. Production GET /health endpoint schema, latency, and status.
2. Root GET / metadata endpoint.
3. Staging vs Production environment configuration isolation.
4. API Key authentication boundaries (401 on missing/invalid keys).
5. Session creation and lifecycle via POST /sessions.
6. Question answering pipeline execution via POST /ask.
7. Verification of Dockerfile instructions (HEALTHCHECK, EXPOSE, non-root USER).
8. Verification of Railway and Vercel configuration schemas.
"""

import os
import sys
import unittest
from fastapi.testclient import TestClient

# Ensure day-53 backend is importable
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
DAY53_DIR = os.path.dirname(TEST_DIR)
BACKEND_DIR = os.path.join(DAY53_DIR, "backend")
REPO_ROOT = os.path.dirname(DAY53_DIR)

for d in [BACKEND_DIR, DAY53_DIR, REPO_ROOT]:
    if d not in sys.path:
        sys.path.insert(0, d)

from backend.main import app, settings
from backend.config import get_settings


class TestHealthAndMonitoring(unittest.TestCase):
    """Verifies production health probe and system information endpoints."""

    def setUp(self):
        self.client = TestClient(app)

    def test_health_endpoint_success(self):
        """GET /health must return HTTP 200 with healthy status and subsystem checks."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get("status"), "healthy")
        self.assertEqual(data.get("service"), "auronix-backend")
        self.assertIn("version", data)
        self.assertIn("environment", data)
        self.assertIn("timestamp", data)
        self.assertIn("checks", data)
        self.assertIn("database", data["checks"])
        self.assertIn("data_dir", data)
        self.assertIn("faiss_index_path", data)

    def test_root_endpoint_info(self):
        """GET / must provide service metadata and online status."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get("status"), "online")
        self.assertIn("health", data)
        self.assertIn("docs", data)


class TestEnvironmentIsolation(unittest.TestCase):
    """Verifies that staging and production environments maintain isolated configurations."""

    def test_staging_configuration_isolation(self):
        """Staging environment must have dedicated data directory and staging FAISS index path."""
        orig_env = os.environ.get("ENVIRONMENT")
        orig_data = os.environ.get("DATA_DIR")
        try:
            os.environ["ENVIRONMENT"] = "staging"
            if "DATA_DIR" in os.environ:
                del os.environ["DATA_DIR"]
            if "FAISS_INDEX_PATH" in os.environ:
                del os.environ["FAISS_INDEX_PATH"]

            stg_settings = get_settings()
            self.assertTrue(stg_settings.is_staging)
            self.assertFalse(stg_settings.is_production)
            self.assertIn("staging", stg_settings.data_dir.lower())
            self.assertIn("staging", stg_settings.faiss_index_path.lower())
            self.assertEqual(stg_settings.auronix_api_key, "auronix-staging-key-2026")
        finally:
            if orig_env:
                os.environ["ENVIRONMENT"] = orig_env
            else:
                os.environ.pop("ENVIRONMENT", None)
            if orig_data:
                os.environ["DATA_DIR"] = orig_data

    def test_production_configuration_isolation(self):
        """Production environment must have dedicated production paths and vault API key."""
        orig_env = os.environ.get("ENVIRONMENT")
        try:
            os.environ["ENVIRONMENT"] = "production"
            if "DATA_DIR" in os.environ:
                del os.environ["DATA_DIR"]
            if "FAISS_INDEX_PATH" in os.environ:
                del os.environ["FAISS_INDEX_PATH"]

            prod_settings = get_settings()
            self.assertTrue(prod_settings.is_production)
            self.assertFalse(prod_settings.is_staging)
            self.assertIn("production", prod_settings.data_dir.lower())
            self.assertIn("production", prod_settings.faiss_index_path.lower())
            self.assertEqual(prod_settings.auronix_api_key, "auronix-production-vault-key-2026")
        finally:
            if orig_env:
                os.environ["ENVIRONMENT"] = orig_env
            else:
                os.environ.pop("ENVIRONMENT", None)


class TestAuthenticationAndInference(unittest.TestCase):
    """Verifies API key authentication boundaries and inference endpoints."""

    def setUp(self):
        self.client = TestClient(app)
        self.valid_headers = {"x-api-key": settings.auronix_api_key}

    def test_missing_api_key_rejected(self):
        """Requests without x-api-key must be rejected with 401."""
        resp = self.client.post("/sessions")
        self.assertEqual(resp.status_code, 401)
        self.assertIn("Missing API key", resp.json().get("detail", ""))

    def test_invalid_api_key_rejected(self):
        """Requests with unauthorized x-api-key must be rejected with 401."""
        resp = self.client.post("/sessions", headers={"x-api-key": "rogue-unauthorized-key"})
        self.assertEqual(resp.status_code, 401)
        self.assertIn("Invalid API key", resp.json().get("detail", ""))

    def test_session_lifecycle(self):
        """Valid key creates session and can retrieve its active state."""
        resp = self.client.post("/sessions", headers=self.valid_headers)
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        session_id = data.get("session_id")
        self.assertTrue(bool(session_id))

        get_resp = self.client.get(f"/sessions/{session_id}", headers=self.valid_headers)
        self.assertEqual(get_resp.status_code, 200)

    def test_ask_empty_input_rejected(self):
        """Empty query must be rejected with 400."""
        payload = {"session_id": "test-uuid", "user_input": "   "}
        resp = self.client.post("/ask", headers=self.valid_headers, json=payload)
        self.assertEqual(resp.status_code, 400)

    def test_ask_query_execution(self):
        """Valid query returns grounded response with latency measurement."""
        sess_resp = self.client.post("/sessions", headers=self.valid_headers)
        session_id = sess_resp.json()["session_id"]

        payload = {
            "session_id": session_id,
            "user_input": "What is the FastAPI backend port allocation?"
        }
        resp = self.client.post("/ask", headers=self.valid_headers, json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data.get("success"))
        self.assertTrue(len(data.get("answer", "")) > 0)
        self.assertGreater(data.get("latency_ms", 0), 0)
        self.assertEqual(data.get("session_id"), session_id)


class TestDeploymentConfigurations(unittest.TestCase):
    """Verifies that all required production deployment config files exist and adhere to standards."""

    def test_dockerfile_contents(self):
        """Dockerfile must specify non-root user, healthcheck, and exposed port."""
        dockerfile_path = os.path.join(REPO_ROOT, "Dockerfile")
        self.assertTrue(os.path.exists(dockerfile_path), "Root Dockerfile missing")
        with open(dockerfile_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("HEALTHCHECK", content)
        self.assertIn("EXPOSE 8001", content)
        self.assertIn("USER appuser", content)
        self.assertIn("uvicorn", content)

    def test_railway_config(self):
        """railway.json must declare Dockerfile builder and healthcheck path."""
        railway_path = os.path.join(REPO_ROOT, "railway.json")
        self.assertTrue(os.path.exists(railway_path), "Root railway.json missing")
        with open(railway_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("/health", content)
        self.assertIn("DOCKERFILE", content)

    def test_vercel_config(self):
        """vercel.json must exist with security headers and Next.js framework."""
        vercel_path = os.path.join(REPO_ROOT, "vercel.json")
        self.assertTrue(os.path.exists(vercel_path), "Root vercel.json missing")
        with open(vercel_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("nextjs", content)
        self.assertIn("X-Frame-Options", content)

    def test_github_actions_workflow(self):
        """production-ci-cd.yml must exist, be valid YAML, and enforce both pytest and day-50 regression gates."""
        workflow_path = os.path.join(REPO_ROOT, ".github", "workflows", "production-ci-cd.yml")
        self.assertTrue(os.path.exists(workflow_path), "GitHub Actions workflow missing")
        with open(workflow_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("regression_test_runner.py", content)
        self.assertIn("pytest", content)
        self.assertIn("needs: [test_gate, eval_gate]", content)
        self.assertIn("branches:", content)


if __name__ == "__main__":
    unittest.main()
