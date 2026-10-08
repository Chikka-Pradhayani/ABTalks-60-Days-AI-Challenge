# Day 56 — End-to-End Production User Journey

**Target Environment:** Railway Production Cloud vs Local Production Engine  
**Service:** `auronix-backend` (FastAPI REST Core + RAG Pipeline)  
**Execution Timestamp:** 2026-10-08 23:12:19 IST  
**Audit Designation:** **PRODUCTION USER JOURNEY COMPLIANCE AUDIT**  

---

## 1. Executive Summary & Production Accessibility Disclosure

The objective of this audit is to validate five end-to-end user journeys that represent the normal core workflow of enterprise engineers and operations personnel using AURONIX.

### Live Production Cloud Accessibility Status:
- **Cloud Probe Target:** `https://auronix-production.up.railway.app/health`
- **Cloud Probe Result:** `HTTP 404 Not Found` (`{"status":"error","code":404,"message":"Application not found"}`)
- **Official Compliance Designation:** As mandated by the technical audit rules:
  > **LIVE CLOUD EXECUTION STATUS: BLOCKED (Remote Railway Domain Unreachable)**
  
  The remote Railway cloud instance is currently unprovisioned or awaiting domain mapping. In accordance with strict audit integrity guidelines, remote cloud success is **NOT fabricated**. Instead, the user journey checklist was executed against the **identical production Docker container runtime environment (`ENVIRONMENT=production`)** locally, and the results are documented below alongside the blocked remote cloud checklist.

---

## 2. Five End-to-End User Journeys

### User Journey 1: Technical Infrastructure Ingress Query
- **User Persona:** DevOps Engineer configuring Kubernetes network ingress and firewall rules.
- **Task:** Query AURONIX for the designated FastAPI backend port allocation and network interface binding.
- **Endpoint:** `POST /ask`
- **Payload:**
  ```json
  {
    "session_id": "a5573502-1dbe-4ffa-b896-6990748790a1",
    "user_input": "What is the FastAPI backend port allocation and default host interface?"
  }
  ```
- **Expected Result:** HTTP 200 OK; correctly cites Port 8001 and interface 0.0.0.0 grounded in `CORP-ENG-003` with low latency.
- **Actual Result (Local Production Container):**
  - Status Code: `HTTP 200 OK`
  - Latency: `770.0ms` (cold-start initialization)
  - Retrieved Sources: `CORP-ENG-003 (Microservice Mesh > Port Allocation Matrix)`, `CORP-ENG-002`
  - Grounded Answer: *"Port 8001 is allocated to the FastAPI Backend Core in the internal microservice network matrix..."*
- **Pass / Fail:** **PASS (Local Prod Container)** / **BLOCKED (Remote Cloud)**
- **Issues Encountered:** Initial container boot required model initialization latency (770ms).
- **Fix Applied:** Pre-warmed model pipeline during application startup lifespan (`@asynccontextmanager lifespan`).

---

### User Journey 2: High-Severity Incident Failover Runbook
- **User Persona:** Site Reliability Engineer (SRE) managing an active P0 database incident.
- **Task:** Retrieve the exact failover script and Recovery Time Objective (RTO) when Aurora PostgreSQL replication lag exceeds 15 seconds.
- **Endpoint:** `POST /ask`
- **Payload:**
  ```json
  {
    "session_id": "a5573502-1dbe-4ffa-b896-6990748790a1",
    "user_input": "If Aurora PostgreSQL database replication lag exceeds 15 seconds, what is the exact script to promote the replica and what is the target RTO?"
  }
  ```
- **Expected Result:** HTTP 200 OK; specifies `promote_replica.sh` and RTO $< 30\text{s}$ grounded in `CORP-OPS-001`.
- **Actual Result (Local Production Container):**
  - Status Code: `HTTP 200 OK`
  - Latency: `15.32ms`
  - Retrieved Sources: `CORP-OPS-001 (P0/P1 Incident Management > Primary Database Failover Sequence)`, `CORP-OPS-003`
  - Grounded Answer: *"The target Recovery Time Objective (RTO) for the Aurora PostgreSQL primary database failover is less than 30 seconds (< 30s) with an RPO of 0 data loss. The operational script is promote_replica.sh..."*
- **Pass / Fail:** **PASS (Local Prod Container)** / **BLOCKED (Remote Cloud)**
- **Issues Encountered:** None.
- **Fix Applied:** None required; RAG semantic grounding operated deterministically.

---

### User Journey 3: Enterprise Policy & Security Gates
- **User Persona:** Security Compliance Officer reviewing corporate deployment readiness.
- **Task:** Inquire regarding the mandatory pre-deployment security verification gates required under corporate policy `CORP-SEC-002`.
- **Endpoint:** `POST /ask`
- **Payload:**
  ```json
  {
    "session_id": "a5573502-1dbe-4ffa-b896-6990748790a1",
    "user_input": "What are the four mandatory pre-deployment security verification gates required under CORP-SEC-002?"
  }
  ```
- **Expected Result:** HTTP 200 OK; enumerates the four security gates (SAST vulnerability scanning, container image scan, secret leakage check, automated regression test).
- **Actual Result (Local Production Container):**
  - Status Code: `HTTP 200 OK`
  - Latency: `17.34ms`
  - Retrieved Sources: `CORP-SEC-002 (AI Deployment Security Gate > Production Readiness Checklist)`, `CORP-SEC-006`
  - Grounded Answer: *"According to AI Deployment Security Gate & Readiness Checklist [CORP-SEC-002]: Before any internal AI model or service is promoted to production, four security verification gates must pass: 1. Static Application Security Testing (SAST), 2. Container image vulnerability scanning, 3. Automated secret scanning, and 4. Automated regression suite..."*
- **Pass / Fail:** **PASS (Local Prod Container)** / **BLOCKED (Remote Cloud)**
- **Issues Encountered:** In baseline evaluation (Day 50 Q12), this query dropped CORP-SEC-002 due to naive top-2 retrieval.
- **Fix Applied:** Top-k expansion implemented in production pipeline resolved the multi-document retrieval truncation.

---

### User Journey 4: Telemetry Pipeline & Edge Ingress Inquiries
- **User Persona:** Platform Engineer checking Prometheus monitoring and Envoy edge configuration.
- **Task:** Retrieve the Prometheus scrape port and Envoy edge ingress port assignments.
- **Endpoint:** `POST /ask`
- **Payload:**
  ```json
  {
    "session_id": "a5573502-1dbe-4ffa-b896-6990748790a1",
    "user_input": "What scrape port is Prometheus listening on and what Envoy edge ingress ports must be open?"
  }
  ```
- **Expected Result:** HTTP 200 OK; identifies Prometheus on port 9090 and Envoy on 80/443.
- **Actual Result (Local Production Container):**
  - Status Code: `HTTP 200 OK`
  - Latency: `17.60ms`
  - Retrieved Sources: `CORP-ENG-003 (Microservice Mesh > Port Allocation Matrix)`, `CORP-OPS-001`, `CORP-ENG-001`
  - Grounded Answer: *"According to Microservice Mesh & Network Topology [CORP-ENG-003]: Prometheus scrape metrics listen on port 9090, while Envoy edge ingress operates on ports 80 (HTTP) and 443 (HTTPS)..."*
- **Pass / Fail:** **PASS (Local Prod Container)** / **BLOCKED (Remote Cloud)**
- **Issues Encountered:** None.
- **Fix Applied:** None required.

---

### User Journey 5: Grounding Quality User Feedback Ingestion
- **User Persona:** AI Product Manager submitting real-user accuracy rating and operational telemetry.
- **Task:** Submit a 5-star rating and verification comment for the database failover response into SQLite persistence.
- **Endpoint:** `POST /feedback`
- **Payload:**
  ```json
  {
    "session_id": "a5573502-1dbe-4ffa-b896-6990748790a1",
    "user_query": "If Aurora PostgreSQL database replication lag exceeds 15 seconds, what is the exact script to promote the replica and what is the target RTO?",
    "rating": 5,
    "comment": "Accurately retrieved database promotion script promote_replica.sh and RTO parameters."
  }
  ```
- **Expected Result:** HTTP 200 OK / 201 Created; returns confirmation message and persists record into `feedback` table.
- **Actual Result (Local Production Container):**
  - Status Code: `HTTP 200 OK`
  - Latency: `21.86ms`
  - Response Body:
    ```json
    {
      "success": true,
      "message": "Feedback submitted successfully."
    }
    ```
- **Pass / Fail:** **PASS (Local Prod Container)** / **BLOCKED (Remote Cloud)**
- **Issues Encountered:** None.
- **Fix Applied:** Input lengths on `user_query` and `comment` hardened in Day 56 to prevent database bloat.

---

## 3. Production Journey Summary Matrix

| Task ID | Scenario | Local Production Engine | Remote Railway Cloud | Latency | Grounding Accuracy |
|:---:|:---|:---:|:---:|:---:|:---:|
| **Journey 1** | Technical Infrastructure Ingress Query | **PASS** | **BLOCKED** | 770.0ms | 100% (Port 8001, 0.0.0.0) |
| **Journey 2** | High-Severity Incident Failover Runbook | **PASS** | **BLOCKED** | 15.32ms | 100% (`promote_replica.sh`, RTO < 30s) |
| **Journey 3** | Enterprise Policy & Security Gates | **PASS** | **BLOCKED** | 17.34ms | 100% (4 Gates Enumerated) |
| **Journey 4** | Telemetry Pipeline & Edge Ingress | **PASS** | **BLOCKED** | 17.60ms | 100% (Prometheus 9090, Envoy 80/443) |
| **Journey 5** | Grounding Quality User Feedback | **PASS** | **BLOCKED** | 21.86ms | 100% (Persisted to SQLite) |

**Overall Journey Assessment:**  
The application core successfully executes all five critical enterprise user journeys with 100% citation grounding and average sub-20ms warm latency. Cloud production verification remains blocked until live Railway deployment is linked.
