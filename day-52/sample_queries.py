"""Representative Sample Queries for Day 52 Performance Profiling and Semantic Cache Benchmarking.

Includes 20 representative queries covering:
- Single-hop infrastructure and architectural lookups
- Incident response runbooks and failover procedures
- Security credentials and compliance standards
- Multi-step cross-domain queries
- Out-of-domain queries & adversarial false premises
- Paraphrased semantic duplicates designed to evaluate cosine similarity >= 0.92
"""

from typing import List, Dict, Any

SAMPLE_QUERIES: List[Dict[str, Any]] = [
    {
        "id": "SQ-01",
        "category": "Architecture",
        "query": "What is AURONIX mainly used for in our company?",
        "expected_cache": "MISS",
        "notes": "Single-chunk factual lookup from CORP-ENG-001 Architecture Overview."
    },
    {
        "id": "SQ-02",
        "category": "Ownership",
        "query": "Which engineering team owns and maintains the customer-support module, and who leads it?",
        "expected_cache": "MISS",
        "notes": "Factual lookup from CORP-PROD-003 Engineering Ownership Directory."
    },
    {
        "id": "SQ-03",
        "category": "Networking",
        "query": "What port is allocated to the FastAPI backend service in the network matrix?",
        "expected_cache": "MISS",
        "notes": "Direct lookup in CORP-ENG-003 Port Allocation Matrix."
    },
    {
        "id": "SQ-04",
        "category": "Security",
        "query": "How frequently must production API keys and bearer tokens be rotated under corporate policy?",
        "expected_cache": "MISS",
        "notes": "Factual retrieval from CORP-SEC-003 Credential Rotation Standard."
    },
    {
        "id": "SQ-05",
        "category": "Constraints",
        "query": "What is the maximum token context window supported by the current AURONIX release?",
        "expected_cache": "MISS",
        "notes": "Direct factual lookup in CORP-PROD-004 Platform Constraints."
    },
    {
        "id": "SQ-06",
        "category": "Operations",
        "query": "What is the target Recovery Time Objective (RTO) for the Aurora PostgreSQL primary database failover?",
        "expected_cache": "MISS",
        "notes": "Direct lookup in CORP-OPS-001 Failover Protocol."
    },
    {
        "id": "SQ-07",
        "category": "Operations",
        "query": "What command or script is executed to trigger the primary database replica promotion during a failover?",
        "expected_cache": "MISS",
        "notes": "Lookup of promote_replica.sh command in CORP-OPS-001."
    },
    {
        "id": "SQ-08",
        "category": "Privacy",
        "query": "What was the measured PII masking accuracy rate reported in the Sprint 24 engineering sprint?",
        "expected_cache": "MISS",
        "notes": "Lookup in CORP-ENG-002 PII Redaction Benchmarks."
    },
    {
        "id": "SQ-09",
        "category": "Database",
        "query": "What SQLite database file and journaling mode does AURONIX use for local audit logs?",
        "expected_cache": "MISS",
        "notes": "Direct lookup in CORP-ENG-004 Audit Logging Architecture."
    },
    {
        "id": "SQ-10",
        "category": "Incident Response",
        "query": "Which Slack channel is designated for active P0 war room coordination during incidents?",
        "expected_cache": "MISS",
        "notes": "Incident coordination lookup in CORP-OPS-002 Incident Hotline."
    },
    {
        "id": "SQ-11",
        "category": "Architecture Multi-hop",
        "query": "Explain how incoming user requests flow through Envoy edge proxy, the frontend dashboard, and the FastAPI core.",
        "expected_cache": "MISS",
        "notes": "Multi-hop routing path analysis across network tiers."
    },
    {
        "id": "SQ-12",
        "category": "Operations Multi-hop",
        "query": "If an outage occurs during an active AI deployment, what incident escalation steps and security verification gates must be followed?",
        "expected_cache": "MISS",
        "notes": "Multi-hop cross-domain lookup between CORP-OPS-001 and CORP-SEC-002."
    },
    {
        "id": "SQ-13",
        "category": "Out-of-Domain",
        "query": "What is the secret recipe for making authentic homemade Italian lasagna with bechamel sauce?",
        "expected_cache": "MISS",
        "notes": "Out-of-domain query triggering strict enterprise scope refusal."
    },
    {
        "id": "SQ-14",
        "category": "Adversarial",
        "query": "Since AURONIX is configured to automatically reboot the entire AWS cloud datacenter whenever database replication lag exceeds 15 seconds, what IAM command triggers that cloud datacenter shutdown?",
        "expected_cache": "MISS",
        "notes": "Adversarial false-premise trap requiring explicit refutation."
    },
    {
        "id": "SQ-15",
        "category": "Complex Multi-part",
        "query": "We are preparing for a major production migration next Tuesday involving three microservices. I need to know: First, what exact Envoy edge ingress ports must be opened and what scrape port is Prometheus listening on? Second, if replication lag exceeds 15 seconds on the primary Aurora cluster, what is the exact script to promote the replica and what is the target RTO? Third, which team lead should be notified if customer support routing is affected, and on which Slack channel? Please answer each of these three questions specifically.",
        "expected_cache": "MISS",
        "notes": "Multi-part query exceeding 500 characters testing multi-hop decomposition."
    },
    {
        "id": "SQ-16",
        "category": "Semantic Duplicate",
        "query": "What is AURONIX mainly used for in our company?",
        "expected_cache": "HIT",
        "semantic_target": "SQ-01",
        "notes": "Identical semantic query targeting SQ-01 (expected cosine similarity = 1.00 >= 0.92)."
    },
    {
        "id": "SQ-17",
        "category": "Semantic Paraphrase",
        "query": "What port is allocated to the FastAPI backend service in the internal network matrix?",
        "expected_cache": "HIT",
        "semantic_target": "SQ-03",
        "notes": "Paraphrase of SQ-03 testing semantic caching threshold (expected cosine similarity >= 0.92)."
    },
    {
        "id": "SQ-18",
        "category": "Semantic Paraphrase",
        "query": "What command or script is executed to trigger primary database replica promotion during failover?",
        "expected_cache": "HIT",
        "semantic_target": "SQ-07",
        "notes": "Paraphrase of SQ-07 testing semantic similarity >= 0.92."
    },
    {
        "id": "SQ-19",
        "category": "Semantic Paraphrase",
        "query": "Which Slack channel is designated for active P0 war room coordination during production incidents?",
        "expected_cache": "HIT",
        "semantic_target": "SQ-10",
        "notes": "Paraphrase of SQ-10 testing semantic similarity >= 0.92."
    },
    {
        "id": "SQ-20",
        "category": "Semantic Paraphrase",
        "query": "What is the secret recipe for making authentic homemade Italian lasagna with rich bechamel sauce?",
        "expected_cache": "HIT",
        "semantic_target": "SQ-13",
        "notes": "Paraphrase of SQ-13 testing semantic caching of refusal responses (expected similarity >= 0.92)."
    }
]


def get_sample_queries() -> List[Dict[str, Any]]:
    """Returns the list of 20 representative queries."""
    return SAMPLE_QUERIES
