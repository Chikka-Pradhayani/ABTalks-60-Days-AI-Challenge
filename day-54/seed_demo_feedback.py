"""Demo & Benchmark Feedback Seeding Script for Day 54.

NOTE: This script seeds representative sample data to simulate real-world user interactions
for demonstration and verification of the analytics pipeline.
It is explicitly separated from real user data and clearly marked as Demo/Benchmark Data.
"""

from datetime import datetime, timedelta, timezone
from database import init_db, insert_feedback

DEMO_FEEDBACK_DATA = [
    # Document Formatting & Parsing (High Failure Cluster)
    {
        "query": "Extract the balance sheet tables from Q3 financial PDF and convert them into CSV format",
        "rating": 1,
        "feedback": "The table columns were completely misaligned and the numbers in column 3 merged into column 4.",
        "topic": "Document Formatting & Parsing",
        "response": "Extracted text: Assets Liabilities 100M 20M...",
        "failure_pattern": "Table column misalignment and parsing truncation",
        "user_id": "cfo_analyst_01@enterprise.corp",
    },
    {
        "query": "Parse this 2-column legal contract PDF and output the indemnification clause as markdown",
        "rating": 2,
        "feedback": "It read across both columns horizontally like one paragraph instead of reading down column 1 first.",
        "topic": "Document Formatting & Parsing",
        "response": "Indemnification: The buyer seller shall agree...",
        "failure_pattern": "Multi-column layout flow reading error",
        "user_id": "legal_counsel@lawfirm.io",
    },
    {
        "query": "Format the revenue breakdown markdown into a clean table structure",
        "rating": 2,
        "feedback": "Markdown syntax was broken with missing pipes on row 4.",
        "topic": "Document Formatting & Parsing",
        "response": "| Region | Revenue | | NA | $12M |",
        "failure_pattern": "Broken markdown table delimiter syntax",
        "user_id": "operations_mgr@retail.com",
    },
    {
        "query": "Summarize the formatted bullet points in the product requirements document",
        "rating": 4,
        "feedback": "Good summary, but lost the sub-bullets nesting.",
        "topic": "Document Formatting & Parsing",
        "response": "- Feature A - Feature B...",
        "failure_pattern": "",
        "user_id": "pm_user@techcorp.com",
    },

    # Query Latency & Timeouts (Second High Failure Cluster)
    {
        "query": "Analyze our 150-page vendor audit report for security non-compliance issues",
        "rating": 1,
        "feedback": "The request took 48 seconds and ended in a 504 Gateway Timeout error. Nothing was returned.",
        "topic": "Query Latency & Timeouts",
        "response": "",
        "failure_pattern": "HTTP 504 gateway timeout on large document synthesis",
        "user_id": "security_officer@fintech.net",
    },
    {
        "query": "Find all mentions of arbitration clauses in all 5 attached master service agreements",
        "rating": 2,
        "feedback": "Extremely slow. Took over 35 seconds to respond. Unacceptable when sitting on a client call.",
        "topic": "Query Latency & Timeouts",
        "response": "Arbitration clauses found in MSA 1 and 3...",
        "failure_pattern": "High latency (>30s) during multi-file FAISS similarity search",
        "user_id": "attorney_bob@legalgroup.com",
    },
    {
        "query": "Search for compliance violation risks in this PDF",
        "rating": 4,
        "feedback": "Accurate findings, but response was slightly slow (~12s).",
        "topic": "Query Latency & Timeouts",
        "response": "Found 3 potential compliance risks in Section 4.2...",
        "failure_pattern": "",
        "user_id": "compliance_lead@bank.com",
    },

    # Source Citation & Grounding (Third High Failure Cluster)
    {
        "query": "Where specifically does the policy state that employees can roll over unused PTO?",
        "rating": 2,
        "feedback": "It said PTO can be rolled over up to 5 days, but didn't tell me what page or section number that came from.",
        "topic": "Source Citation & Grounding",
        "response": "Employees may roll over up to 5 unused PTO days into the following year.",
        "failure_pattern": "Missing page number and snippet citation in RAG output",
        "user_id": "hr_manager@consulting.com",
    },
    {
        "query": "Quote the exact contractual liability cap from Schedule B",
        "rating": 2,
        "feedback": "Gave me a paraphrased summary instead of the exact quote and source page reference.",
        "topic": "Source Citation & Grounding",
        "response": "Liability is capped at the fees paid over the previous 12 months.",
        "failure_pattern": "Paraphrase returned instead of verifiable verbatim quote",
        "user_id": "procurement_lead@megacorp.com",
    },
    {
        "query": "Cite the ISO 27001 control requirements for encryption at rest from the audit document",
        "rating": 4,
        "feedback": "Accurate citation, verified on page 42.",
        "topic": "Source Citation & Grounding",
        "response": "As stated in Section A.10.1 (Page 42), cryptographic controls are required...",
        "failure_pattern": "",
        "user_id": "lead_auditor@securityfirm.com",
    },

    # Hallucination & Factual Accuracy (Moderate Failure)
    {
        "query": "What is the penalty fee if the vendor terminates the SLA before Month 6?",
        "rating": 2,
        "feedback": "The AI claimed the penalty is $50,000, but Section 8.1 clearly states it is $25,000.",
        "topic": "Hallucination & Factual Accuracy",
        "response": "The contract imposes a $50,000 early termination liquidated damages penalty.",
        "failure_pattern": "Factual hallucination on numerical contract penalty clause",
        "user_id": "vendor_manager@enterprises.org",
    },
    {
        "query": "List all software licenses permitted under our corporate open source policy",
        "rating": 5,
        "feedback": "Completely spot on. Caught MIT, Apache-2.0, and BSD-3 without any error.",
        "topic": "Hallucination & Factual Accuracy",
        "response": "Permitted licenses: MIT, Apache 2.0, BSD 2-Clause, BSD 3-Clause, ISC.",
        "failure_pattern": "",
        "user_id": "tech_lead@devshop.io",
    },

    # Authentication & Access Control (Low Failure)
    {
        "query": "Why did my API token expire after only 15 minutes?",
        "rating": 3,
        "feedback": "Explained the JWT expiration policy, but didn't help me refresh without logging in again.",
        "topic": "Authentication & Access Control",
        "response": "Tokens expire after 15 minutes in accordance with standard enterprise OAuth2 TTL.",
        "failure_pattern": "Lack of automated token refresh workflow",
        "user_id": "dev_integrator@saas.com",
    },
    {
        "query": "How do I generate an API key for my service account?",
        "rating": 5,
        "feedback": "Clear step-by-step instructions. Worked on first try.",
        "topic": "Authentication & Access Control",
        "response": "Navigate to Settings -> API Keys -> Create Key and assign scopes.",
        "failure_pattern": "",
        "user_id": "devops_engineer@cloudteam.org",
    },

    # General Inquiries (Positive Cluster)
    {
        "query": "What file types can I upload to AURONIX?",
        "rating": 5,
        "feedback": "Fast and helpful.",
        "topic": "General Inquiries",
        "response": "AURONIX currently supports PDF, DOCX, TXT, CSV, and Markdown files.",
        "failure_pattern": "",
        "user_id": "new_user@trial.com",
    },
    {
        "query": "Explain how AURONIX protects confidential enterprise data",
        "rating": 5,
        "feedback": "Great concise security explanation.",
        "topic": "General Inquiries",
        "response": "AURONIX utilizes private self-hosted vector stores with strict role-based access control.",
        "failure_pattern": "",
        "user_id": "compliance_director@corp.com",
    },
]


def seed_demo_data():
    """Populate database with demo/benchmark feedback data."""
    init_db()
    base_time = datetime.now(timezone.utc) - timedelta(hours=22)

    count = 0
    for i, item in enumerate(DEMO_FEEDBACK_DATA):
        timestamp = (base_time + timedelta(hours=i * 1.2)).isoformat()
        insert_feedback(
            query=item["query"],
            rating=item["rating"],
            feedback=item["feedback"],
            topic=item["topic"],
            response=item["response"],
            failure_pattern=item["failure_pattern"],
            user_id=item["user_id"],
            session_id=f"sess_{100 + i}",
            timestamp=timestamp,
        )
        count += 1

    print(f" Successfully seeded {count} demo feedback records into SQLite database.")


if __name__ == "__main__":
    seed_demo_data()
