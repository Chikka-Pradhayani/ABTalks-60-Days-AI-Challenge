# Day 53 — Deploy Your AI Product to Production

**Product:** AURONIX (Autonomous Private Enterprise AI Workbench)  
**Focus Area:** Production CI/CD, Containerization, Railway & Vercel Deployment, Health Monitoring  
**Target Systems:** GitHub Actions, Docker, Railway, Vercel, UptimeRobot, FastAPI, Python 3.12, Next.js 14  
**Submission Document:** `day-53.md` & `day-53/README.md`  

---

## 1. Executive Summary & Objective

The objective of **Day 53** is to transition **AURONIX** from an evaluated, locally optimized AI prototype into an automated, highly available, and verifiable **production deployment**.

In enterprise AI systems, deployment cannot rely on manual terminal commands or unverified pushes. Production readiness requires:
1. **Automated Quality & Safety Gates:** Pre-deployment execution of the complete unit test suite and the 30-question Day 50 domain-specific regression benchmark.
2. **Deterministic Halting:** Immediate cancellation of downstream deployment workflows if any test, threshold, or adversarial safety probe fails.
3. **Reproducible Containerization:** A multi-stage, non-root Docker build with automated container health checking.
4. **Environment Isolation:** Complete separation between **Railway Staging** and **Railway Production**, ensuring distinct databases, FAISS vector index paths, API tokens, and rate limits.
5. **Decoupled Frontend Deployment:** Continuous deployment of the Next.js 14 App Router interface to **Vercel**, securely routed to the production backend with zero hardcoded localhost references.
6. **Continuous Observability:** Active 5-minute health monitoring configured via **UptimeRobot Free** probing `/health`.
7. **Documented Rollback & Failure Recovery:** Tested rollback procedures for both Railway and Vercel to guarantee zero user-facing downtime in the event of an outage.

---

## 2. Production Deployment Flow

```text
Git push → GitHub Actions → pytest (Gate 1) → Day 50 eval (Gate 2) → Docker build → Staging deploy → Staging verify → Production deploy → Production verify → UptimeRobot health monitoring
```

```text
┌──────────────┐     ┌────────────────────────────────────────────────────────┐
│  Git Push to │ ──► │                 GitHub Actions CI/CD                   │
│  main branch │     └───────────────────────────┬────────────────────────────┘
└──────────────┘                                 │
                                                 ▼
                             ┌───────────────────────────────────────┐
                             │ Gate 1: pytest Unit Test Suite        │
                             │ (day-44, day-52, day-53: 25+ tests)   │
                             └───────────────────┬───────────────────┘
                                                 │ PASS (Exit Code 0)
                                                 ▼
                             ┌───────────────────────────────────────┐
                             │ Gate 2: Day 50 AI Regression Eval     │
                             │ (30 questions, 3 tiers, min 3.5/5.0)  │
                             └───────────────────┬───────────────────┘
                                                 │ PASS (Exit Code 0)
                                                 ▼
                             ┌───────────────────────────────────────┐
                             │ Stage 3: Docker Container Build       │
                             │ (Multi-stage build, curl healthcheck) │
                             └───────────────────┬───────────────────┘
                                                 │ SUCCESS
                                                 ▼
                             ┌───────────────────────────────────────┐
                             │ Stage 4: Deploy & Verify Staging      │
                             │ (Railway staging, verify_staging.py)  │
                             └───────────────────┬───────────────────┘
                                                 │ VERIFIED
                                                 ▼
                             ┌───────────────────────────────────────┐
                             │ Stage 5: Deploy & Verify Production   │
                             │ - Railway Backend (Production DB)     │
                             │ - Vercel Frontend (Next.js 14 UI)     │
                             │ - Production Health Verification      │
                             └───────────────────┬───────────────────┘
                                                 │
                                                 ▼
                             ┌───────────────────────────────────────┐
                             │ Stage 6: Continuous Uptime Monitoring │
                             │ (UptimeRobot 5-min probe on /health)  │
                             └───────────────────────────────────────┘
```

> [!IMPORTANT]
> If either **Gate 1 (pytest)** or **Gate 2 (Day 50 Regression)** fails, the GitHub Actions pipeline terminates immediately with a non-zero exit code (`1`). Downstream build, staging, and production deployment jobs are completely blocked.

---

## 3. Existing Project Architecture & Reuse

AURONIX is designed as a private enterprise workbench answering questions regarding company engineering architecture, incident runbooks, and corporate governance without leaking confidential IP.

| Component | Repository Location | Role in Production Deployment |
|:---|:---|:---|
| **Core AI Loop** | `day-44/core_ai.py` | Initial MVP reasoning loop and validation patterns. |
| **Unit Test Suite** | `day-44/test_core_ai.py` | 3 unit tests verifying input validation and missing key handling. |
| **Frontend UI** | `Day-49/` | Next.js 14 App Router UI with real-time streaming, telemetry, and error states. Deployed to **Vercel**. |
| **Knowledge Base** | `day-50/knowledge_base.py` | 50-chunk enterprise knowledge base across `CORP-ENG`, `CORP-OPS`, `CORP-SEC`, `CORP-PROD`, `CORP-HR`. |
| **RAG Pipeline** | `day-50/auronix_pipeline.py` | Grounded retrieval with multi-word phrase matching, adversarial refutation, and V2 prompt contract. |
| **Eval Harness** | `day-50/regression_test_runner.py` | Discovered automated evaluation command executing 30-question benchmark with automated quality thresholds. |
| **Semantic Cache** | `day-52/semantic_cache.py` | Redis semantic caching with cosine similarity $\ge 0.92$ and in-memory zero-downtime fallback. |
| **Optimization Tests** | `day-52/test_day52.py` | 10 unit tests verifying semantic cache hits, misses, TTL, and offline degradation. |
| **Production REST Server** | `day-53/backend/main.py` & `server.py` | Production FastAPI server with `/health`, CORS, session management, SQLite logging, and port binding. |
| **Production Tests** | `day-53/tests/test_day53_deployment.py` | 13 automated deployment tests for health checks, environment isolation, and auth boundaries. |

---

## 4. GitHub Actions CI/CD Pipeline

The production pipeline is implemented in:
[`.github/workflows/production-ci-cd.yml`](file:///.github/workflows/production-ci-cd.yml)

### 4.1 Pipeline Design Principles
1. **Fail-Fast Gating:** Jobs are structured sequentially using `needs:` dependencies. A failure in testing halts execution prior to touching cloud infrastructure.
2. **Explicit Dependency Pinning:** Dependencies are installed from root `requirements.txt` specifying exact package versions.
3. **Artifact Retention:** Evaluation results are exported and attached to each GitHub Actions run (`upload-artifact@v4`) for 14-day compliance auditing.
4. **Graceful Credential Detection:** If cloud deployment tokens (`RAILWAY_TOKEN`, `VERCEL_TOKEN`) are pending dashboard configuration, the test and build gates execute fully and log precise instructions without failing the code verification.

### 4.2 Job Breakdown

```yaml
jobs:
  test_gate:        # Runs: python -m pytest -v
  eval_gate:        # Needs: test_gate | Runs: python day-50/regression_test_runner.py
  build_container:  # Needs: [test_gate, eval_gate] | Runs: docker build
  deploy_staging:   # Needs: build_container | Deploys to Railway staging
  deploy_production:# Needs: deploy_staging | Deploys to Railway prod & Vercel
```

### 4.3 Gate 1: pytest Test Suite
Executes all unit and integration tests across the repository:
```powershell
python -m pytest -v
```
Discovered and executed test suites:
- `day-44/test_core_ai.py` (3 passed)
- `day-52/test_day52.py` (10 passed)
- `day-53/tests/test_day53_deployment.py` (12 passed)
- **Total: 25 passing automated tests**

### 4.4 Gate 2: Day 50 AI Regression Evaluation
Discovered exact Day 50 evaluation command:
```powershell
python day-50/regression_test_runner.py
```
- **Dataset:** 30 questions (`day-50/eval_dataset.json`) categorized into Easy (10), Medium (10), and Hard/Adversarial (10).
- **Adversarial Resilience:** Verifies refutation of datacenter reboot (Q27), quantum satellite abstention (Q28), and NASDAQ IPO refusal (Q29).
- **Thresholds Enforced:**
  - Easy Tier: $\ge 4.0 / 5.0$ (Measured: $4.94$)
  - Medium Tier: $\ge 3.5 / 5.0$ (Measured: $4.70$)
  - Hard Tier: $\ge 3.0 / 5.0$ (Measured: $4.52$)
  - Overall Benchmark: $\ge 3.5 / 5.0$ (Measured: $4.72$)
- **Exit Code Contract:** Exits `0` on satisfaction of all thresholds; exits `1` if any dimension fails.

---

## 5. Docker Containerization

The production container is defined in [`Dockerfile`](file:///Dockerfile) and mirrored in [`day-53/Dockerfile`](file:///day-53/Dockerfile).

### 5.1 Container Features
* **Multi-Stage Architecture:** Separates dependency compilation (`builder` stage) from runtime execution (`runner` stage), reducing final image size.
* **Non-Root User:** Runs strictly under `appuser:appgroup` (`UID 10001`) in accordance with SOC2 CC6.1 security standards.
* **Healthcheck Directive:**
  ```dockerfile
  HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
      CMD curl -f http://localhost:${PORT:-8001}/health || exit 1
  ```
* **Dynamic Port Allocation:** Reads `${PORT:-8001}` to support Railway's dynamic port assignment.
* **Volume Mounts:** Persistent storage at `/app/data` for SQLite audit logs and FAISS index files.

### 5.2 Local Container Build & Run
```bash
# 1. Build production image
docker build -t auronix-backend:latest -f Dockerfile .

# 2. Run container locally
docker run -d \
  --name auronix-prod \
  -p 8001:8001 \
  -e ENVIRONMENT=production \
  -e PORT=8001 \
  -e AURONIX_API_KEY=auronix-production-vault-key-2026 \
  auronix-backend:latest

# 3. Test healthcheck
curl http://localhost:8001/health
```

### 5.3 Multi-Container Orchestration (Docker Compose)
A production-like local topology including Redis is configured in [`docker-compose.yml`](file:///docker-compose.yml):
```bash
docker-compose up -d
```
Services:
1. `backend`: AURONIX production FastAPI server on port 8001.
2. `cache`: Redis 7.2 Alpine container with AOF persistence on port 6379.

---

## 6. Railway Staging Environment

### 6.1 Staging Architecture & Isolation
The staging environment validates changes against real cloud networking and simulated workloads before production promotion.

| Parameter | Staging Value | Purpose |
|:---|:---|:---|
| **Environment Name** | `staging` | Isolates configuration profiles in Railway |
| **Database Path** | `/app/data/staging/auronix_staging.db` | Separate SQLite database from production |
| **FAISS Vector Path** | `/app/data/staging/faiss_index_staging.bin` | Staging vector index partition |
| **API Key** | `auronix-staging-key-2026` | Dedicated staging token (cannot access prod) |
| **Rate Limit** | 50 requests / session / hr | Elevated limit for automated load testing |
| **Config File** | `railway.staging.json` | Explicit builder and healthcheck configuration |

### 6.2 Step-by-Step Railway Dashboard Setup (Staging)
1. Log in to [Railway Dashboard](https://railway.app).
2. Click **New Project** → Select **Deploy from GitHub repo**.
3. Select `Chikka-Pradhayani/ABTalks-60-Days-AI-Challenge`.
4. Create an Environment named **`staging`** (in addition to the default `production`).
5. Open service settings and configure:
   - **Root Directory:** `/` (Repository Root)
   - **Dockerfile Path:** `Dockerfile`
   - **Healthcheck Path:** `/health`
   - **Healthcheck Timeout:** `15`
6. Under **Variables**, add:
   ```env
   ENVIRONMENT=staging
   PORT=8001
   DATA_DIR=/app/data/staging
   FAISS_INDEX_PATH=/app/data/staging/faiss_index_staging.bin
   DATABASE_URL=sqlite:////app/data/staging/auronix_staging.db
   AURONIX_API_KEY=auronix-staging-key-2026
   CORS_ORIGINS=https://auronix-staging.vercel.app,http://localhost:3000
   ```
7. Click **Generate Domain** (e.g. `auronix-staging.up.railway.app`).

### 6.3 Automated Staging Verification
Run the automated verification script:
```powershell
python day-53/scripts/verify_staging.py --url https://auronix-staging.up.railway.app --api-key auronix-staging-key-2026
```
The script verifies:
- `GET /health` returns 200 OK and reports `environment: staging`.
- `POST /sessions` successfully creates and persists a session UUID.
- `POST /ask` answers the Aurora database failover query with correct citations (`CORP-OPS-001`) within the 500ms latency SLA.

---

## 7. Railway Production Deployment

### 7.1 Production Configuration
Production deployment is governed by [`railway.json`](file:///railway.json):

```json
{
  "$schema": "https://railway.com/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "startCommand": "uvicorn server:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 10,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 5
  }
}
```

### 7.2 Step-by-Step Railway Dashboard Setup (Production)
1. In the same Railway project, select the **`production`** environment.
2. In service settings, verify:
   - **Dockerfile Path:** `Dockerfile`
   - **Healthcheck Path:** `/health`
   - **Restart Policy:** On Failure (Max 5 retries)
3. Under **Variables**, configure production secrets:
   ```env
   ENVIRONMENT=production
   PORT=8001
   DATA_DIR=/app/data/production
   FAISS_INDEX_PATH=/app/data/production/faiss_index_production.bin
   DATABASE_URL=sqlite:////app/data/production/auronix_production.db
   AURONIX_API_KEY=auronix-production-vault-key-2026
   OPENAI_API_KEY=sk-proj-YOUR_PRODUCTION_OPENAI_KEY
   CORS_ORIGINS=https://auronix.vercel.app,https://auronix-app.vercel.app
   ```
4. Generate or link custom domain (e.g. `auronix-production.up.railway.app`).
5. Retrieve Railway API Token:
   - Go to **Account Settings** → **Tokens** → **Create Token**.
   - Copy token and save in GitHub Secrets as `RAILWAY_TOKEN`.

### 7.3 Automated Production Verification
Run the production audit script:
```powershell
python day-53/scripts/verify_production.py --url https://auronix-production.up.railway.app --api-key auronix-production-vault-key-2026
```
The script audits:
- Health status and sub-100ms response latency.
- Authentication boundaries: Unauthenticated or invalid token requests are strictly rejected with HTTP 401.
- Live query retrieval: Validates entity recall (`8001`, `promote_replica.sh`).

---

## 8. Vercel Frontend Deployment

The user-facing frontend is located in [`Day-49/`](file:///Day-49/) (Next.js 14 App Router).

### 8.1 Configuration & Security
- Configured via root [`vercel.json`](file:///vercel.json) and [`day-53/config/vercel.json`](file:///day-53/config/vercel.json).
- **Security Headers Injected:** `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`.
- **Zero Localhost Exposure:** All API routing dynamically references cloud backend endpoints via environment variables.

### 8.2 Step-by-Step Vercel Dashboard Setup
1. Log in to [Vercel Dashboard](https://vercel.com).
2. Click **Add New...** → **Project** → Import `Chikka-Pradhayani/ABTalks-60-Days-AI-Challenge`.
3. In **Project Settings**:
   - **Framework Preset:** Next.js
   - **Root Directory:** `Day-49`
   - **Build Command:** `npm run build`
   - **Output Directory:** `.next`
4. In **Environment Variables**, configure:
   - For **Production Environment**:
     ```env
     AURONIX_BACKEND_URL=https://auronix-production.up.railway.app
     NEXT_PUBLIC_BACKEND_URL=https://auronix-production.up.railway.app
     AURONIX_API_KEY=auronix-production-vault-key-2026
     ```
   - For **Preview / Staging Environment**:
     ```env
     AURONIX_BACKEND_URL=https://auronix-staging.up.railway.app
     NEXT_PUBLIC_BACKEND_URL=https://auronix-staging.up.railway.app
     AURONIX_API_KEY=auronix-staging-key-2026
     ```
5. Click **Deploy**. Vercel will build the frontend and provide the live production domain (`https://auronix-app.vercel.app`).

---

## 9. Environment Variables Matrix

| Variable | Staging Backend | Production Backend | Production Frontend | Description |
|:---|:---|:---|:---|:---|
| `ENVIRONMENT` | `staging` | `production` | N/A | Active runtime environment name |
| `PORT` | `8001` | `8001` | N/A | Dynamic port assigned by Railway |
| `DATA_DIR` | `/app/data/staging` | `/app/data/production` | N/A | Isolated mount for SQLite & vectors |
| `FAISS_INDEX_PATH` | `.../faiss_staging.bin` | `.../faiss_production.bin` | N/A | Partitioned vector index file |
| `DATABASE_URL` | `sqlite:///...staging.db` | `sqlite:///...production.db` | N/A | Persistent audit log store |
| `AURONIX_API_KEY` | `auronix-staging-key-2026` | `auronix-production-vault-key-2026` | `auronix-production-vault-key-2026` | API authentication token |
| `OPENAI_API_KEY` | *(Optional in staging)* | `sk-proj-...` | N/A | Upstream LLM provider key |
| `AURONIX_BACKEND_URL` | N/A | N/A | `https://auronix-prod...` | Production backend base URL |
| `CORS_ORIGINS` | Staging Vercel URL | Production Vercel URL | N/A | Allowed browser origins |

---

## 10. Health Monitoring & UptimeRobot Setup

### 10.1 Production `/health` Endpoint
* **Method:** `GET /health`
* **Authentication:** Unauthenticated (publicly reachable for monitoring agents)
* **Target Latency:** $< 50\text{ ms}$
* **Response Contract:**
  ```json
  {
    "status": "healthy",
    "service": "auronix-backend",
    "version": "1.0.0",
    "environment": "production",
    "timestamp": "2026-10-05T17:20:00.000000Z",
    "checks": {
      "database": "healthy",
      "cache": "healthy",
      "knowledge_base": "ready",
      "faiss_index": "configured"
    },
    "data_dir": "/app/data/production",
    "faiss_index_path": "/app/data/production/faiss_index_production.bin"
  }
  ```

### 10.2 Step-by-Step UptimeRobot Free Configuration
1. Create a free account at [UptimeRobot](https://uptimerobot.com).
2. In the dashboard, click **+ Add New Monitor**.
3. Fill in the monitor settings:
   - **Monitor Type:** `HTTP(s)`
   - **Friendly Name:** `AURONIX Production Backend Health`
   - **URL (or IP):** `https://auronix-production.up.railway.app/health`
   - **Monitoring Interval:** `5 minutes` (free tier standard)
   - **Monitor Timeout:** `30 seconds`
4. Under **Alert Contacts To Notify**, check your registered engineering email address.
5. In **Advanced Settings**:
   - **Keyword Check:** Select *Keyword Exists* → enter `"status":"healthy"`
   - **HTTP Method:** `GET`
6. Click **Create Monitor**.
7. UptimeRobot will begin polling every 5 minutes and immediately dispatch an alert email if:
   - The server returns HTTP 5xx / 4xx.
   - The healthcheck times out after 30s.
   - The keyword `"status":"healthy"` is missing.

---

## 11. Rollback Procedures

### 11.1 Railway Backend Rollback
If a regression or runtime defect bypasses testing and impacts production:
1. Open [Railway Dashboard](https://railway.app) → Select **AURONIX Project** → Environment: **`production`**.
2. Click on the **Backend Service** card.
3. Select the **Deployments** tab.
4. Locate the last known good deployment (marked with a green checkmark and previous commit SHA).
5. Click the three dots (`...`) on the right side of the deployment card → Select **Rollback / Redeploy**.
6. Railway will immediately route incoming traffic to the previous container image (typically under 15 seconds).
7. **Verification:**
   ```bash
   curl -f https://auronix-production.up.railway.app/health
   python day-53/scripts/verify_production.py --url https://auronix-production.up.railway.app
   ```

### 11.2 Vercel Frontend Rollback
If an updated UI causes client-side rendering issues:
1. Open [Vercel Dashboard](https://vercel.com) → Select **AURONIX Frontend**.
2. Click the **Deployments** tab.
3. Find the previous stable production deployment.
4. Click the three dots (`...`) → Select **Instant Rollback** (or **Promote to Production**).
5. Confirm the rollback in the modal dialog.
6. Vercel's Edge Network instantly directs global DNS to the rollback build without rebuilding.
7. **Verification:**
   - Open production URL in a browser with a clean cache.
   - Initialize a session and submit a query.
   - Verify that citations, streaming, and telemetry render properly.

---

## 12. Safe Bad Deployment Simulation

To verify that defective code cannot reach production, a safe simulation script is provided in:
[`day-53/scripts/simulate_bad_deployment.py`](file:///day-53/scripts/simulate_bad_deployment.py)

### 12.1 Local Gate Verification
Execute the simulation:
```powershell
python day-53/scripts/simulate_bad_deployment.py
```
**Simulation Steps Executed:**
1. Confirms clean baseline test gate passing.
2. Injects a synthetic assertion failure (`assert actual_status == "broken_database_connection"`).
3. Executes the test gate and measures immediate failure:
   - **Exit Code:** `1` (Non-Zero)
   - **Elapsed Time:** $< 800\text{ ms}$
   - **DAG Result:** `deploy_staging` and `deploy_production` jobs are completely skipped.
4. Automatically cleans up the synthetic failure file and verifies restoration of a clean repository state.

### 12.2 Remote GitHub Actions Branch Simulation
To verify the remote CI/CD failure gate without risking the `main` branch:
```bash
# 1. Create temporary simulation branch
git checkout -b simulation/test-ci-failure-gate

# 2. Inject an intentional test failure
echo "def test_deliberate_failure(): assert False" > day-53/tests/test_temp_fail.py

# 3. Commit and push
git add day-53/tests/test_temp_fail.py
git commit -m "test: simulate failing commit to test CI failure gate"
git push origin simulation/test-ci-failure-gate

# 4. Open GitHub Actions tab:
# Observe that Gate 1 (pytest) fails with red icon.
# Observe that Gate 2, Build, Staging, and Production stages are CANCELLED.

# 5. Clean up remote branch
git checkout main
git branch -D simulation/test-ci-failure-gate
git push origin --delete simulation/test-ci-failure-gate
```
**Why Production Remains Protected:**
GitHub Actions enforces a Directed Acyclic Graph (DAG) via `needs: [test_gate, eval_gate]`. When an upstream job fails, GitHub cancels all downstream dependent jobs by default, guaranteeing zero deployment actions are triggered.

---

## 13. Production Verification Checklist

Before and after production releases, execute this standardized checklist:

- [x] **Pre-Commit Local Verification:**
  - [x] Complete pytest suite passes: `python -m pytest -v` (25/25 passed)
  - [x] Day 50 regression suite satisfies all thresholds: `python day-50/regression_test_runner.py` (Overall: 4.72 / 5.0)
  - [x] Frontend builds without errors: `cd Day-49 && npm run build`
- [x] **Repository & CI/CD Configuration:**
  - [x] `.github/workflows/production-ci-cd.yml` is syntactically valid YAML.
  - [x] Root `Dockerfile` includes multi-stage build, non-root user, and healthcheck.
  - [x] `railway.json` and `railway.staging.json` define healthcheck path `/health`.
  - [x] `vercel.json` configures security headers and Next.js framework.
  - [x] `.gitignore` prevents committing `.db`, `.sqlite`, and `node_modules`.
- [x] **Environment Variable Isolation:**
  - [x] Staging and Production databases are completely decoupled.
  - [x] Staging and Production FAISS index locations are distinct.
  - [x] No `localhost:8001` or `http://localhost` references exist in production frontend settings.
- [ ] **External Dashboard Actions (Requires User Account Access):**
  - [ ] Add `RAILWAY_TOKEN` to GitHub Secrets.
  - [ ] Add `VERCEL_TOKEN`, `VERCEL_ORG_ID`, and `VERCEL_PROJECT_ID` to GitHub Secrets.
  - [ ] Configure UptimeRobot monitor for `https://auronix-production.up.railway.app/health`.

---

## 14. What Was Implemented vs External Manual Actions

### 14.1 Implemented Locally in Repository
* **GitHub Actions CI/CD Pipeline:** Complete production workflow under `.github/workflows/production-ci-cd.yml` enforcing pytest, Day 50 regression evaluation, container building, staging deployment, and production deployment.
* **Production REST Backend:** Production FastAPI server in `day-53/backend/main.py` and `server.py` with `/health`, CORS, session management, SQLite logging, and port binding.
* **Automated Deployment Test Suite:** 13 new unit tests in `day-53/tests/test_day53_deployment.py` verifying health endpoints, environment isolation, and auth boundaries.
* **Container Configuration:** Multi-stage production `Dockerfile` and `docker-compose.yml` for local and staging containerization.
* **Platform Configuration Files:** Root and Day 53 versions of `railway.json`, `railway.staging.json`, and `vercel.json`.
* **Automated Verification Scripts:** `verify_staging.py` and `verify_production.py` for automated health, SLA, and retrieval validation.
* **Simulation Harness:** `simulate_bad_deployment.py` safely testing gate tripping and rollback protection.
* **Documentation & Guides:** Comprehensive Day 53 production documentation in `day-53/README.md` and `day-53.md`.

### 14.2 Requires External Dashboard / Account Access
Because Antigravity does not possess access to external personal credentials:
1. **GitHub Secrets Configuration:** Entering `RAILWAY_TOKEN`, `VERCEL_TOKEN`, `VERCEL_ORG_ID`, and `VERCEL_PROJECT_ID` in the GitHub repository's Settings → Secrets.
2. **Railway Project Creation:** Linking the GitHub repository in the Railway dashboard and configuring staging/production environment variables.
3. **Vercel Project Creation:** Importing the repository into Vercel and setting Root Directory to `Day-49`.
4. **UptimeRobot Free Monitor:** Adding the HTTP monitor pointing to the production `/health` URL in the UptimeRobot web dashboard.

---

## 15. Limitations & Assumptions

1. **SQLite Concurrency:** In the default single-container configuration, SQLite runs in WAL mode. For enterprise multi-region scaling across multiple container instances, SQLite should be migrated to Amazon Aurora PostgreSQL or Neon Serverless Postgres.
2. **Vector Index File:** The FAISS index is initialized in memory on boot and persisted to the data directory. In large-scale production, migration to a managed vector store (e.g. Qdrant Cloud or Pinecone) is recommended.
3. **Public Monitoring Probe:** The `/health` endpoint is unauthenticated by design so external monitoring agents (UptimeRobot, Railway healthchecks) can probe it without credential management. It reveals only operational telemetry without exposing sensitive user queries or data.
