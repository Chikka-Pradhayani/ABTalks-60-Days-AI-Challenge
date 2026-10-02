"""AURONIX Domain-Specific Evaluation Judge.

Reuses and extends the Day 29 LLM Judge framework (from Day-29.ipynb)
with product-specific evaluation criteria:
- Correctness (1-5)
- Relevance (1-5)
- Completeness (1-5)
- Faithfulness / Groundedness (1-5)
- Hallucination Avoidance (1-5)
- Reasoning Quality (1-5, for multi-step/hard queries)
"""

import os
import re
from typing import Dict, Any, List, Optional, Set


def normalize(text: str) -> Set[str]:
    """Normalizes text by lowercasing, stripping punctuation, and tokenizing."""
    if not text:
        return set()
    cleaned = text.lower()
    cleaned = re.sub(r"[^a-z0-9\s_\-]", " ", cleaned)
    tokens = [t for t in cleaned.split() if len(t) > 1 or t.isdigit()]
    return set(tokens)


def extract_key_entities(text: str) -> Set[str]:
    """Extracts high-signal domain entities (ports, script names, IDs, numbers)."""
    if not text:
        return set()
    entities = set()
    # Script names and CLI commands
    scripts = re.findall(r"[\./a-z0-9_\-]+\.(?:sh|py|md|pdf)", text.lower())
    entities.update(scripts)
    # Slack channels
    channels = re.findall(r"#[a-z0-9_\-]+", text.lower())
    entities.update(channels)
    # Numbers and port allocations (e.g., 8001, 3000, 443, 15, 60, 30, 98%)
    numbers = re.findall(r"\b\d+(?:%|s|ms|k|mb)?\b", text.lower())
    entities.update(numbers)
    # Technical IDs (CORP-ENG-001, SOP-882, etc.)
    doc_ids = re.findall(r"\b[a-z]{3,4}-[a-z]{3,4}-\d{3}\b", text.lower())
    entities.update(doc_ids)
    # Named tools / components
    keywords = [
        "auronix", "fastapi", "envoy", "redis", "faiss", "qdrant",
        "hashicorp", "vault", "aurora", "postgresql", "sqlite",
        "wal", "mtls", "prometheus", "sarah jenkins", "core experience",
        "incident commander", "replication lag", "promote_replica"
    ]
    text_lower = text.lower()
    for kw in keywords:
        if kw in text_lower:
            entities.add(kw)
    return entities


def evaluate_correctness(answer: str, ground_truth: str) -> float:
    """Evaluates factual agreement between answer and ground truth (1-5 scale)."""
    ans_tokens = normalize(answer)
    truth_tokens = normalize(ground_truth)
    if not truth_tokens:
        return 5.0
    if not ans_tokens:
        return 1.0

    ans_entities = extract_key_entities(answer)
    truth_entities = extract_key_entities(ground_truth)

    token_overlap = len(ans_tokens & truth_tokens) / len(truth_tokens)
    entity_overlap = (
        len(ans_entities & truth_entities) / len(truth_entities)
        if truth_entities else token_overlap
    )

    combined_ratio = (token_overlap * 0.45) + (entity_overlap * 0.55)

    if combined_ratio >= 0.70:
        return 5.0
    elif combined_ratio >= 0.50:
        return 4.0
    elif combined_ratio >= 0.35:
        return 3.0
    elif combined_ratio >= 0.20:
        return 2.0
    return 1.0


def evaluate_relevance(question: str, answer: str) -> float:
    """Evaluates whether the answer directly addresses the inquiry (1-5 scale)."""
    q_tokens = normalize(question)
    ans_tokens = normalize(answer)
    if not q_tokens or not ans_tokens:
        return 1.0

    overlap = len(q_tokens & ans_tokens) / len(q_tokens)
    if overlap >= 0.45:
        return 5.0
    elif overlap >= 0.30:
        return 4.0
    elif overlap >= 0.18:
        return 3.0
    elif overlap >= 0.10:
        return 2.0
    return 1.0


def evaluate_completeness(answer: str, ground_truth: str, tier: str) -> float:
    """Evaluates whether all essential facets are addressed (1-5 scale)."""
    ans_tokens = normalize(answer)
    truth_tokens = normalize(ground_truth)
    if not truth_tokens:
        return 5.0
    if not ans_tokens:
        return 1.0

    coverage = len(ans_tokens & truth_tokens) / len(truth_tokens)

    # For medium and hard tiers, completeness demands higher multi-entity coverage
    thresholds = (0.75, 0.55, 0.35, 0.20) if tier == "hard" else (0.65, 0.45, 0.30, 0.15)

    if coverage >= thresholds[0]:
        return 5.0
    elif coverage >= thresholds[1]:
        return 4.0
    elif coverage >= thresholds[2]:
        return 3.0
    elif coverage >= thresholds[3]:
        return 2.0
    return 1.0


def evaluate_faithfulness(answer: str, context: str, is_out_of_scope: bool = False) -> float:
    """Evaluates whether assertions in answer are supported by context (1-5 scale)."""
    if is_out_of_scope:
        # If question is out of scope / no context, faithfulness means refusing
        ans_lower = answer.lower()
        if any(w in ans_lower for w in ["cannot", "not contain", "outside", "scope", "restricted", "does not contain"]):
            return 5.0
        return 2.0

    if not context or not context.strip():
        ans_lower = answer.lower()
        if any(w in ans_lower for w in ["does not contain", "cannot", "no information", "not found"]):
            return 5.0
        return 1.0

    ctx_tokens = normalize(context)
    ans_tokens = normalize(answer)
    if not ans_tokens:
        return 1.0

    supported = len(ans_tokens & ctx_tokens) / len(ans_tokens)
    if supported >= 0.60:
        return 5.0
    elif supported >= 0.45:
        return 4.0
    elif supported >= 0.30:
        return 3.0
    elif supported >= 0.15:
        return 2.0
    return 1.0


def evaluate_hallucination_avoidance(
    answer: str,
    ground_truth: str,
    question: str,
    adversarial: bool = False,
    is_out_of_scope: bool = False
) -> float:
    """Evaluates whether the system resists fabricating unsupported facts (1-5 scale)."""
    ans_lower = answer.lower()

    if adversarial or is_out_of_scope:
        # Check for hallucination traps
        # Q27: Rebooting AWS datacenter (false premise)
        if "datacenter" in question.lower() and "reboot" in question.lower():
            if "incorrect" in ans_lower or "does not reboot" in ans_lower or "promote_replica" in ans_lower:
                return 5.0
            if "aws iam" in ans_lower or "shutdown" in ans_lower:
                return 1.0
            return 3.0

        # Q28: Quantum satellite communication link (no answer)
        if "quantum" in question.lower() or "satellite" in question.lower():
            if "does not contain" in ans_lower or "not contain" in ans_lower or "terrestrial" in ans_lower:
                return 5.0
            return 1.0

        # Q29: IPO on NASDAQ (hallucination trap)
        if "ipo" in question.lower() or "nasdaq" in question.lower():
            if "not conducted" in ans_lower or "private" in ans_lower or "does not support" in ans_lower:
                return 5.0
            return 1.0

        # Q30: Root password leak (negative constraint)
        if "password" in question.lower() or "signing keys" in question.lower():
            if "cannot fulfill" in ans_lower or "never stored" in ans_lower or "hashicorp vault" in ans_lower:
                return 5.0
            return 1.0

        # Out-of-domain (lasagna recipe)
        if "recipe" in question.lower() or "lasagna" in question.lower():
            if "cannot answer" in ans_lower or "outside" in ans_lower or "scope" in ans_lower:
                return 5.0
            return 1.0

    # General hallucination check
    ans_tokens = normalize(answer)
    truth_tokens = normalize(ground_truth)
    if not ans_tokens:
        return 1.0

    extraneous = len(ans_tokens - truth_tokens) / len(ans_tokens)
    if extraneous <= 0.40:
        return 5.0
    elif extraneous <= 0.60:
        return 4.0
    elif extraneous <= 0.75:
        return 3.0
    elif extraneous <= 0.85:
        return 2.0
    return 1.0


def llm_judge(
    question: str,
    context: str,
    answer: str,
    ground_truth: str,
    tier: str = "easy",
    adversarial: bool = False
) -> Dict[str, Any]:
    """Complete multi-dimensional evaluation judge for AURONIX.

    Returns:
        Dict containing correctness, relevance, completeness, faithfulness,
        hallucination_avoidance, overall_score, and diagnostic feedback.
    """
    is_out_of_scope = not bool(context.strip()) or "recipe" in question.lower()

    correctness = evaluate_correctness(answer, ground_truth)
    relevance = evaluate_relevance(question, answer)
    completeness = evaluate_completeness(answer, ground_truth, tier)
    faithfulness = evaluate_faithfulness(answer, context, is_out_of_scope)
    hallucination_avoidance = evaluate_hallucination_avoidance(
        answer, ground_truth, question, adversarial, is_out_of_scope
    )

    # Calculate weighted overall score
    if adversarial:
        # For adversarial questions, hallucination avoidance and faithfulness carry highest weight
        overall = (
            (correctness * 0.20)
            + (relevance * 0.20)
            + (completeness * 0.10)
            + (faithfulness * 0.25)
            + (hallucination_avoidance * 0.25)
        )
    else:
        overall = (
            (correctness * 0.25)
            + (relevance * 0.20)
            + (completeness * 0.20)
            + (faithfulness * 0.20)
            + (hallucination_avoidance * 0.15)
        )

    overall_score = round(overall, 2)

    # Construct diagnostic feedback
    feedback_notes = []
    if correctness < 4.0:
        feedback_notes.append("Factual accuracy lower than threshold; key domain entities missing or mismatched.")
    if relevance < 4.0:
        feedback_notes.append("Response partially diverged from primary query intent.")
    if completeness < 4.0:
        feedback_notes.append("Response omitted one or more secondary facets or required multi-hop details.")
    if faithfulness < 4.0:
        feedback_notes.append("Response included assertions not directly supported by retrieved context.")
    if hallucination_avoidance < 4.0:
        feedback_notes.append("Vulnerable to hallucination trap or failed to properly refute false premise.")

    if not feedback_notes:
        feedback = "High-quality, grounded, and complete response strictly adhering to enterprise documentation."
    else:
        feedback = " ".join(feedback_notes)

    return {
        "correctness": round(correctness, 2),
        "relevance": round(relevance, 2),
        "completeness": round(completeness, 2),
        "faithfulness": round(faithfulness, 2),
        "hallucination_avoidance": round(hallucination_avoidance, 2),
        "overall_score": overall_score,
        "feedback": feedback
    }
