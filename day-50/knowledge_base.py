"""AURONIX Enterprise Knowledge Base.

Contains the 50-document benchmark corpus spanning the five core domains
of AURONIX: CORP-ENG, CORP-OPS, CORP-SEC, CORP-PROD, and CORP-HR.
"""

from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class DocumentChunk:
    chunk_id: str
    doc_id: str
    title: str
    breadcrumb: str
    text: str
    metadata: Dict[str, Any]


CORPUS_DOCUMENTS: List[Dict[str, Any]] = [
    # ---------------------------------------------------------
    # 1. CORP-ENG: Engineering & Architecture
    # ---------------------------------------------------------
    {
        "doc_id": "CORP-ENG-001",
        "title": "Auronix Core System Architecture",
        "category": "CORP-ENG",
        "sections": [
            {
                "breadcrumb": "Auronix Core System Architecture > Architecture Overview",
                "text": "AURONIX is an autonomous private AI workbench engineered for internal company operations, technical infrastructure, software architecture, and incident runbooks. It allows employees to query private enterprise documentation without leaking proprietary intellectual property to public consumer chatbots. The platform couples deterministic grounding with neural semantic retrieval to ensure zero hallucinations."
            },
            {
                "breadcrumb": "Auronix Core System Architecture > Component Decomposition",
                "text": "AURONIX implements a four-tier architecture: 1) Client SPA Layer: Next.js 14 and React dashboard running on Port 3000. 2) Transport & Gateway Layer: Envoy API Gateway terminating TLS on Port 443 with mTLS for internal services. 3) Application Core: FastAPI ASGI backend running on Port 8001 providing CallSession management and PII sanitization. 4) Storage & Inference Layer: Qdrant/FAISS vector index on Port 6333/6334, Redis session cache on Port 6379, and SQLite WAL persistent request logging in auronix.db."
            },
            {
                "breadcrumb": "Auronix Core System Architecture > Privacy Guarantees",
                "text": "Data privacy is enforced by isolating tenant memory boundaries and sanitizing user inputs. All queries pass through an automated PII extraction and regex masking engine before vector search or LLM inference. No employee data is ever stored in unencrypted form or used to train foundation models."
            }
        ]
    },
    {
        "doc_id": "CORP-ENG-002",
        "title": "FastAPI Backend Core & SQLite Persistence",
        "category": "CORP-ENG",
        "sections": [
            {
                "breadcrumb": "FastAPI Backend Core > RESTful Endpoint Specifications",
                "text": "The FastAPI backend core exposes four primary endpoints: 1) GET /health - Unauthenticated service health probe. 2) POST /sessions - Authenticated session creation keyed by UUID. 3) POST /ask - Authenticated conversational query endpoint tracking latency in milliseconds and retrieval scores. 4) POST /feedback - Authenticated user feedback collection for grounding and hallucination flags."
            },
            {
                "breadcrumb": "FastAPI Backend Core > SQLite Audit Logging",
                "text": "Persistent request and response auditing is handled via SQLite database auronix.db in Write-Ahead Logging (WAL) mode. The request_logs table records session_id, user_query, response_text, latency_ms, retrieval_score, and timestamp for every completed API transaction."
            },
            {
                "breadcrumb": "FastAPI Backend Core > Rate Limiting",
                "text": "To prevent denial-of-service and quota exhaustion, an in-memory sliding-window rate limiter enforces a strict ceiling of 20 requests per session per hour. Exceeding this threshold results in an HTTP 429 Rate Limit Exceeded response."
            }
        ]
    },
    {
        "doc_id": "CORP-ENG-003",
        "title": "Microservice Mesh & Network Topology",
        "category": "CORP-ENG",
        "sections": [
            {
                "breadcrumb": "Microservice Mesh > Port Allocation Matrix",
                "text": "The AURONIX microservice network topology allocates standard internal ports: Port 443/8443 for Envoy Edge Ingress Gateway, Port 3000 for Next.js Frontend Dashboard, Port 8001 for FastAPI Backend Core, Port 6333 (HTTP) and Port 6334 (gRPC) for Vector Search Database, Port 6379 for Redis Session Cache, and Port 9090 for Prometheus metrics scraping."
            },
            {
                "breadcrumb": "Microservice Mesh > Intra-Service Security",
                "text": "All intra-service traffic across the Kubernetes cluster enforces mutual TLS (mTLS) with automated 30-day certificate rotation managed by HashiCorp Vault. Plaintext HTTP traffic between internal microservices is blocked by network security policy."
            }
        ]
    },
    {
        "doc_id": "CORP-ENG-005",
        "title": "Sprint 24 Engineering Progress Report",
        "category": "CORP-ENG",
        "sections": [
            {
                "breadcrumb": "Sprint 24 Engineering Report > Executive Summary",
                "text": "During Sprint 24, the engineering team successfully completed the FAISS vector pipeline integration and achieved a 98% PII masking accuracy rate on synthetic call transcripts. The team also verified that retrieval latency averaged under 0.35 milliseconds for local index lookups."
            },
            {
                "breadcrumb": "Sprint 24 Engineering Report > Benchmark Milestones",
                "text": "System benchmarks confirmed 99.95% uptime for the FastAPI backend service over 100,000 synthetic requests. Vector index memory footprint was measured at 128MB for the 50-document benchmark corpus."
            }
        ]
    },
    {
        "doc_id": "CORP-ENG-006",
        "title": "Voice Telemetry & Real-Time Processing",
        "category": "CORP-ENG",
        "sections": [
            {
                "breadcrumb": "Voice Telemetry > Latency & Web Speech API",
                "text": "AURONIX incorporates browser-native Web Speech API for Speech-to-Text (STT) and Speech-Synthesis (TTS). Real-time telemetry targets include < 150ms speech recognition turnaround and end-to-end response speech playback under 800ms."
            }
        ]
    },

    # ---------------------------------------------------------
    # 2. CORP-OPS: Incident Response & DevOps Playbooks
    # ---------------------------------------------------------
    {
        "doc_id": "CORP-OPS-001",
        "title": "P0/P1 Incident Management & Failover Protocol",
        "category": "CORP-OPS",
        "sections": [
            {
                "breadcrumb": "P0/P1 Incident Management > Immediate Response Protocol",
                "text": "When a P0 (Critical Service Outage) or P1 (Major Degradation) occurs, the responding engineer must immediately: 1) Declare the incident in Slack channel #incident-ops and open the bridge hotline #incident-p0-hotline. 2) Page the on-call Incident Commander (IC) via PagerDuty priority channel #sre-p0-escalations within 3 minutes. 3) Assume role of initial Incident Commander until handover."
            },
            {
                "breadcrumb": "P0/P1 Incident Management > Primary Database Failover Sequence",
                "text": "If database replication lag exceeds 15 seconds or unrecoverable connection timeout occurs, execute the primary database failover script: ./scripts/promote_replica.sh --cluster prod-db-core --force. The secondary read replica in us-east-2 automatically assumes write leadership within an RTO target of < 30 seconds with an RPO of 0 data loss."
            },
            {
                "breadcrumb": "P0/P1 Incident Management > Traffic Rerouting & Cache Flush",
                "text": "Following replica promotion, switch Envoy edge ingress upstream pool to healthy standby pods and flush Redis cache partitions on Port 6379 to eliminate stale read connections. Post-incident root cause analysis (RCA) must be filed within 24 hours pursuant to SOP-882."
            }
        ]
    },
    {
        "doc_id": "CORP-OPS-002",
        "title": "Canary Deployments & Automated Rollback Guide",
        "category": "CORP-OPS",
        "sections": [
            {
                "breadcrumb": "Canary Deployments > Automated Rollback Triggers",
                "text": "Canary releases route 5% of production traffic to newly deployed pods. If HTTP 5xx error rate exceeds 1.5% or p99 response latency exceeds 450ms over a 2-minute evaluation window, the automated rollback controller terminates the canary and restores the previous stable container image via ./scripts/rollback_release.sh."
            }
        ]
    },
    {
        "doc_id": "CORP-OPS-003",
        "title": "Database Query Timeout Configurations",
        "category": "CORP-OPS",
        "sections": [
            {
                "breadcrumb": "Database Configurations > OLTP Online Query Timeout",
                "text": "Under the OLTP High-Availability Runbook v3, all standard synchronous user queries executed against PostgreSQL have an enforced strict connection timeout of 15 seconds. Queries exceeding 15 seconds are terminated by pg_terminate_backend to preserve connection pool capacity."
            },
            {
                "breadcrumb": "Database Configurations > Batch ETL Offline Query Timeout",
                "text": "Under the Data Engineering Batch ETL Specification v2, scheduled offline migration jobs and vector index backfill tasks are allocated a maximum query timeout of 60 seconds before termination."
            }
        ]
    },

    # ---------------------------------------------------------
    # 3. CORP-SEC: Security, Compliance & PII Governance
    # ---------------------------------------------------------
    {
        "doc_id": "CORP-SEC-002",
        "title": "AI Deployment Security Gate & Readiness Checklist",
        "category": "CORP-SEC",
        "sections": [
            {
                "breadcrumb": "AI Deployment Security Gate > Production Readiness Checklist",
                "text": "Before any internal AI model or service is approved for production deployment, four mandatory security gates must be verified: 1) Automated PII redaction regression test achieving >= 95% detection rate. 2) Static code vulnerability scan with zero high or critical CVE findings. 3) Role-Based Access Control (RBAC) boundary test verifying that restricted documents are blocked from unauthorized roles. 4) Audit logging verification confirming request and latency persistence in SQLite."
            }
        ]
    },
    {
        "doc_id": "CORP-SEC-003",
        "title": "Credential & API Key Rotation Standard",
        "category": "CORP-SEC",
        "sections": [
            {
                "breadcrumb": "Credential Rotation Standard > Lifecycle & Expiration",
                "text": "All production API keys, service bearer tokens, and database credentials must undergo mandatory 90-day rotation. Secrets are managed dynamically via HashiCorp Vault. In accordance with SOC2 CC6.1, keys must never be hardcoded into source code or committed to git repositories."
            },
            {
                "breadcrumb": "Credential Rotation Standard > Emergency Revocation",
                "text": "In the event of suspected credential exposure or compromise, execute immediate revocation via HashiCorp Vault CLI: vault token revoke -mode=path secret/auronix. Re-issue fresh credentials with automated zero-downtime dual-key staging."
            }
        ]
    },
    {
        "doc_id": "CORP-SEC-004",
        "title": "PII Sanitization & Entity Masking Specification",
        "category": "CORP-SEC",
        "sections": [
            {
                "breadcrumb": "PII Sanitization > Entity Masking Rules",
                "text": "The PII sanitization engine intercepts all natural language queries and strips Personally Identifiable Information using deterministic regex and named-entity recognition. Detected phone numbers are replaced with [PHONE], email addresses with [EMAIL], credit cards with [CARD], and social security numbers with [SSN] before context retrieval."
            }
        ]
    },
    {
        "doc_id": "CORP-SEC-005",
        "title": "Executive Strategy Archive & RBAC Boundaries",
        "category": "CORP-SEC",
        "sections": [
            {
                "breadcrumb": "Executive Strategy Archive > Restricted Vision 2027",
                "text": "The Vision 2027 M&A Strategy document contains confidential corporate acquisition targets and executive revenue roadmaps. Access is strictly restricted to authenticated users presenting role: EXECUTIVE or role: ADMIN. For all other roles (e.g. DEVELOPER, EMPLOYEE), the retrieval engine enforces an RBAC filter, blocking the document and returning: 'Information is restricted for role DEVELOPER. Accessible sections: Public Corporate Goals.'"
            }
        ]
    },
    {
        "doc_id": "CORP-SEC-006",
        "title": "Zero-Hallucination & Governance Policy",
        "category": "CORP-SEC",
        "sections": [
            {
                "breadcrumb": "Zero-Hallucination Policy > Verification Guardrails",
                "text": "AURONIX operates under a strict zero-hallucination governance standard: 1) Deterministic Grounding: All assertions must cite indexed corporate runbooks or specifications. 2) Abstention Protocol: If retrieved source context does not support an assertion with confidence >= 0.70, or if context is missing, the assistant must explicitly state that internal documentation does not contain the answer. 3) Never invent policy names, passwords, or employee credentials."
            }
        ]
    },

    # ---------------------------------------------------------
    # 4. CORP-PROD: Product Management & Capabilities
    # ---------------------------------------------------------
    {
        "doc_id": "CORP-PROD-001",
        "title": "Platform Capability Matrix & Feature Registry",
        "category": "CORP-PROD",
        "sections": [
            {
                "breadcrumb": "Platform Capability Matrix > Feature Registry",
                "text": "The current release of AURONIX includes the following production capabilities: 1) Web Chat Workbench with Next.js 14 streaming interface. 2) Voice Telemetry with Web Speech STT/TTS. 3) PII Masking Engine with real-time entity sanitization. 4) RBAC Vector Retrieval over enterprise runbooks. 5) SQLite WAL Audit Logging and latency telemetry."
            }
        ]
    },
    {
        "doc_id": "CORP-PROD-002",
        "title": "H2/H3 Product Roadmap & Upcoming Milestones",
        "category": "CORP-PROD",
        "sections": [
            {
                "breadcrumb": "H2/H3 Product Roadmap > Upcoming Milestones",
                "text": "The planned H2/H3 roadmap for AURONIX introduces: 1) Multi-tenant vector partitioning allowing separate namespace isolation per corporate department. 2) Enterprise Single Sign-On (SSO) with SAML 2.0 and OIDC integrations. 3) Offline on-premise LLM inference with quantized models for air-gapped environments."
            }
        ]
    },
    {
        "doc_id": "CORP-PROD-003",
        "title": "Engineering Ownership Directory & Module Allocations",
        "category": "CORP-PROD",
        "sections": [
            {
                "breadcrumb": "Engineering Ownership Directory > Module Allocations",
                "text": "Module ownership assignments: The customer-support module is owned and maintained by the Core Experience Team, led by Sarah Jenkins (Slack: #team-core-cx). The vector retrieval engine is maintained by the Platform AI Infrastructure Team led by David Chen (Slack: #ai-infra). The security and auth layer is owned by InfoSec Engineering (Slack: #infosec-ops)."
            }
        ]
    },
    {
        "doc_id": "CORP-PROD-004",
        "title": "Platform Constraints & Known Limitations",
        "category": "CORP-PROD",
        "sections": [
            {
                "breadcrumb": "Platform Constraints > System Boundaries",
                "text": "The current version of AURONIX has the following documented boundaries: 1) No live external internet access: AURONIX cannot query the public web or third-party APIs at runtime. 2) Voice interface is English-only in the current release; multilingual speech is planned for H3. 3) Maximum token context window is capped at 8,192 tokens."
            }
        ]
    },

    # ---------------------------------------------------------
    # 5. CORP-HR: HR, Operations & Workplace Policies
    # ---------------------------------------------------------
    {
        "doc_id": "CORP-HR-001",
        "title": "Remote Work Guidelines & Home Office Allowance",
        "category": "CORP-HR",
        "sections": [
            {
                "breadcrumb": "Remote Work Guidelines > Expense Allowance",
                "text": "Eligible full-time employees are provided a one-time home office equipment setup stipend of $1,000 upon hire, plus a recurring monthly internet reimbursement of $75 submitted through the corporate expense portal Expensify."
            }
        ]
    },
    {
        "doc_id": "CORP-HR-002",
        "title": "Employee Onboarding & Access Request Protocol",
        "category": "CORP-HR",
        "sections": [
            {
                "breadcrumb": "Employee Onboarding > Access Provisioning",
                "text": "New employees receive default tier-1 access credentials on Day 1. Elevated access to sensitive repositories or administrative clusters requires an approved Jira Service Management ticket signed by the employee's direct engineering manager."
            }
        ]
    }
]


def get_all_chunks() -> List[DocumentChunk]:
    """Flattens all corpus documents into standardized searchable chunks."""
    chunks = []
    chunk_idx = 0
    for doc in CORPUS_DOCUMENTS:
        doc_id = doc["doc_id"]
        title = doc["title"]
        for s_idx, sec in enumerate(doc["sections"]):
            c_id = f"{doc_id}_c{s_idx:03d}"
            chunks.append(
                DocumentChunk(
                    chunk_id=c_id,
                    doc_id=doc_id,
                    title=title,
                    breadcrumb=sec["breadcrumb"],
                    text=f"[{sec['breadcrumb']}]\n{sec['text']}",
                    metadata={
                        "doc_id": doc_id,
                        "title": title,
                        "category": doc["category"],
                        "breadcrumb": sec["breadcrumb"],
                        "chunk_index": s_idx,
                    },
                )
            )
            chunk_idx += 1
    return chunks
