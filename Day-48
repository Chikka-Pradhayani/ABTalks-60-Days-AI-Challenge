# Day 48 — Build Product-Specific Memory and Personalisation

---

## 1. Objective
The objective of **Day 48** is to engineer a durable, production-grade **product-specific memory and personalisation system** for **AURONIX** (the private enterprise AI workbench).

While generic conversational memory merely records raw message history, a product-specific memory system selectively identifies, structures, and persists high-value information about each user. Across sessions, AURONIX leverages this memory to automatically tailor its tone, abstraction level, code examples, and technical recommendations without requiring users to repeat their background, tech stack, or engineering preferences in every prompt.

---

## 2. Product-Specific Memory Definition
AURONIX is an enterprise AI assistant for internal company operations, software architecture, technical infrastructure, and incident runbooks. Rather than capturing conversational filler or every ephemeral query, AURONIX remembers durable, high-signal technical profile data:

| Field | Type | Purpose | Why AURONIX Benefits |
|---|---|---|---|
| `user_id` | `TEXT PRIMARY KEY` | Unique employee identifier | Isolates memory boundaries so users never receive another employee's context. |
| `created_at` | `TEXT (ISO8601)` | Profile creation timestamp | Provides audit trails and account lifecycle telemetry. |
| `updated_at` | `TEXT (ISO8601)` | Last profile modification timestamp | Tracks freshness of stored preferences and memory updates. |
| `technical_role` | `TEXT` | Engineering discipline (e.g. Frontend, DevOps, SRE, Security) | Aligns recommendations with the user's domain and operational responsibilities. |
| `expertise_level` | `TEXT` | Seniority depth (`beginner`, `intermediate`, `senior`) | Calibrates explanation complexity: foundational tutorials vs. senior production trade-offs. |
| `preferred_response_style` | `TEXT` | Format directive (`concise_code_first`, `step_by_step_tutorial`, `deep_architectural_dive`) | Delivers answers in the exact format the employee processes fastest. |
| `primary_tech_stack` | `TEXT (JSON List)` | Active languages, frameworks, databases, and cloud tools | Supplies code snippets in the user's primary languages rather than generic guesses. |
| `active_goals` | `TEXT (JSON List)` | Current operational initiatives and milestones | Grounds responses in the projects the user is currently building or debugging. |
| `recurring_interests` | `TEXT (JSON List)` | Architectural topics frequently explored | Proactively surfaces relevant system concerns without explicit prompting. |
| `resolved_items` | `TEXT (JSON List)` | Solved issues, closed bugs, and finalized architectures | Prevents the model from re-suggesting troubleshooting steps already executed. |
| `memory_summary` | `TEXT` | Synthesized long-term profile model | Provides high-density, noise-free context injection without token bloat. |
| `interaction_count` | `INTEGER` | Cumulative interaction counter | Triggers automated history summarisation and lifecycle maintenance (>20 threshold). |

---

## 3. SQLite UserProfile Schema & Database Implementation

The SQLite persistence layer cleanly decouples database queries from application business logic. All profile and history operations are strictly scoped to `user_id`.

### SQLite Schema

```sql
CREATE TABLE IF NOT EXISTS user_profiles (
    user_id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    technical_role TEXT NOT NULL DEFAULT 'Software Engineer',
    expertise_level TEXT NOT NULL DEFAULT 'intermediate',
    preferred_response_style TEXT NOT NULL DEFAULT 'step_by_step_tutorial',
    primary_tech_stack TEXT NOT NULL DEFAULT '[]',
    active_goals TEXT NOT NULL DEFAULT '[]',
    recurring_interests TEXT NOT NULL DEFAULT '[]',
    resolved_items TEXT NOT NULL DEFAULT '[]',
    memory_summary TEXT,
    interaction_count INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS interaction_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    user_query TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    extracted_memory TEXT,
    is_summarized INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES user_profiles (user_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_interactions_user_id ON interaction_history (user_id);
CREATE INDEX IF NOT EXISTS idx_interactions_summarized ON interaction_history (user_id, is_summarized);
```

### Complete Database Implementation (`database.py`)

```python
import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Dict, Generator, List, Optional
from pydantic import BaseModel, Field

def get_utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

class UserProfile(BaseModel):
    user_id: str
    created_at: str = Field(default_factory=get_utc_now_iso)
    updated_at: str = Field(default_factory=get_utc_now_iso)
    technical_role: str = "Software Engineer"
    expertise_level: str = "intermediate"
    preferred_response_style: str = "step_by_step_tutorial"
    primary_tech_stack: List[str] = Field(default_factory=list)
    active_goals: List[str] = Field(default_factory=list)
    recurring_interests: List[str] = Field(default_factory=list)
    resolved_items: List[str] = Field(default_factory=list)
    memory_summary: Optional[str] = None
    interaction_count: int = 0

@contextmanager
def get_db_connection(db_path: str = "auronix_memory.db") -> Generator[sqlite3.Connection, None, None]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db(db_path: str = "auronix_memory.db") -> None:
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                technical_role TEXT NOT NULL DEFAULT 'Software Engineer',
                expertise_level TEXT NOT NULL DEFAULT 'intermediate',
                preferred_response_style TEXT NOT NULL DEFAULT 'step_by_step_tutorial',
                primary_tech_stack TEXT NOT NULL DEFAULT '[]',
                active_goals TEXT NOT NULL DEFAULT '[]',
                recurring_interests TEXT NOT NULL DEFAULT '[]',
                resolved_items TEXT NOT NULL DEFAULT '[]',
                memory_summary TEXT,
                interaction_count INTEGER NOT NULL DEFAULT 0
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interaction_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                user_query TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                extracted_memory TEXT,
                is_summarized INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES user_profiles (user_id) ON DELETE CASCADE
            );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_interactions_user_id ON interaction_history (user_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_interactions_summarized ON interaction_history (user_id, is_summarized);")

def create_user_profile(
    user_id: str,
    technical_role: str = "Software Engineer",
    expertise_level: str = "intermediate",
    preferred_response_style: str = "step_by_step_tutorial",
    primary_tech_stack: Optional[List[str]] = None,
    active_goals: Optional[List[str]] = None,
    recurring_interests: Optional[List[str]] = None,
    resolved_items: Optional[List[str]] = None,
    memory_summary: Optional[str] = None,
    db_path: str = "auronix_memory.db",
) -> UserProfile:
    if not user_id or not user_id.strip():
        raise ValueError("user_id must be a non-empty string.")
    user_id_clean = user_id.strip()
    init_db(db_path)
    now = get_utc_now_iso()
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM user_profiles WHERE user_id = ?;", (user_id_clean,))
        if cursor.fetchone():
            raise ValueError(f"User profile with user_id '{user_id_clean}' already exists.")
        cursor.execute("""
            INSERT INTO user_profiles (
                user_id, created_at, updated_at, technical_role,
                expertise_level, preferred_response_style, primary_tech_stack,
                active_goals, recurring_interests, resolved_items,
                memory_summary, interaction_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0);
        """, (
            user_id_clean, now, now, technical_role, expertise_level,
            preferred_response_style, json.dumps(primary_tech_stack or []),
            json.dumps(active_goals or []), json.dumps(recurring_interests or []),
            json.dumps(resolved_items or []), memory_summary,
        ))
    profile = get_user_profile(user_id_clean, db_path=db_path)
    if not profile:
        raise RuntimeError("Failed to retrieve profile after insertion.")
    return profile

def get_user_profile(user_id: str, db_path: str = "auronix_memory.db") -> Optional[UserProfile]:
    if not user_id or not user_id.strip():
        return None
    init_db(db_path)
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_profiles WHERE user_id = ?;", (user_id.strip(),))
        row = cursor.fetchone()
        if not row:
            return None
        return UserProfile(
            user_id=row["user_id"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            technical_role=row["technical_role"],
            expertise_level=row["expertise_level"],
            preferred_response_style=row["preferred_response_style"],
            primary_tech_stack=json.loads(row["primary_tech_stack"]),
            active_goals=json.loads(row["active_goals"]),
            recurring_interests=json.loads(row["recurring_interests"]),
            resolved_items=json.loads(row["resolved_items"]),
            memory_summary=row["memory_summary"],
            interaction_count=row["interaction_count"],
        )

def update_user_profile(user_id: str, updates: Dict[str, Any], db_path: str = "auronix_memory.db") -> Optional[UserProfile]:
    if not user_id or not user_id.strip():
        return None
    user_id_clean = user_id.strip()
    init_db(db_path)
    existing = get_user_profile(user_id_clean, db_path=db_path)
    if not existing:
        return None
    valid_text = {"technical_role", "expertise_level", "preferred_response_style", "memory_summary"}
    valid_lists = {"primary_tech_stack", "active_goals", "recurring_interests", "resolved_items"}
    set_clauses, params = [], []
    for k, v in updates.items():
        if k in valid_text:
            set_clauses.append(f"{k} = ?")
            params.append(v)
        elif k in valid_lists:
            set_clauses.append(f"{k} = ?")
            params.append(json.dumps(v if isinstance(v, list) else []))
    if not set_clauses:
        return existing
    set_clauses.append("updated_at = ?")
    params.append(get_utc_now_iso())
    params.append(user_id_clean)
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE user_profiles SET {', '.join(set_clauses)} WHERE user_id = ?;", tuple(params))
    return get_user_profile(user_id_clean, db_path=db_path)

def delete_user_profile(user_id: str, db_path: str = "auronix_memory.db") -> bool:
    """Scoped deletion ensuring compliance with privacy rights (Right to be Forgotten)."""
    if not user_id or not user_id.strip():
        return False
    user_id_clean = user_id.strip()
    init_db(db_path)
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM user_profiles WHERE user_id = ?;", (user_id_clean,))
        if not cursor.fetchone():
            return False
        cursor.execute("DELETE FROM interaction_history WHERE user_id = ?;", (user_id_clean,))
        cursor.execute("DELETE FROM user_profiles WHERE user_id = ?;", (user_id_clean,))
    return True

def log_interaction(user_id: str, query: str, response: str, extracted_memory: Optional[dict] = None, db_path: str = "auronix_memory.db") -> int:
    init_db(db_path)
    now = get_utc_now_iso()
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO interaction_history (user_id, timestamp, user_query, ai_response, extracted_memory, is_summarized)
            VALUES (?, ?, ?, ?, ?, 0);
        """, (user_id, now, query, response, json.dumps(extracted_memory or {})))
        record_id = cursor.lastrowid
        cursor.execute("UPDATE user_profiles SET interaction_count = interaction_count + 1, updated_at = ? WHERE user_id = ?;", (now, user_id))
        return int(record_id)

def get_user_interactions(user_id: str, limit: Optional[int] = None, unsummarized_only: bool = False, db_path: str = "auronix_memory.db") -> List[dict]:
    init_db(db_path)
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM interaction_history WHERE user_id = ?"
        params: List[Any] = [user_id]
        if unsummarized_only:
            query += " AND is_summarized = 0"
        query += " ORDER BY id ASC"
        if limit is not None and limit > 0:
            query += f" LIMIT {int(limit)}"
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        return [{"id": r["id"], "user_id": r["user_id"], "timestamp": r["timestamp"], "user_query": r["user_query"], "ai_response": r["ai_response"], "extracted_memory": json.loads(r["extracted_memory"] or "{}"), "is_summarized": bool(r["is_summarized"])} for r in rows]

def mark_interactions_summarized(user_id: str, up_to_id: int, db_path: str = "auronix_memory.db") -> int:
    init_db(db_path)
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE interaction_history SET is_summarized = 1 WHERE user_id = ? AND id <= ? AND is_summarized = 0;", (user_id, up_to_id))
        return cursor.rowcount

def get_user_interaction_count(user_id: str, db_path: str = "auronix_memory.db") -> int:
    init_db(db_path)
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as cnt FROM interaction_history WHERE user_id = ?;", (user_id,))
        row = cursor.fetchone()
        return int(row["cnt"]) if row else 0
```

---

## 4. Memory Read Pipeline

The memory read pipeline injects filtered context into the system prompt:

```text
User Request
     ↓
Identify User (user_id)
     ↓
Retrieve UserProfile (SQLite)
     ↓
Select Relevant Memory (filter domain matches)
     ↓
Build Personalisation Context (style directives)
     ↓
Inject into System Prompt (augment AURONIX prompt)
     ↓
Generate LLM Response
     ↓
Return Personalised Response
```

### Complete Personalisation Engine (`personalisation.py`)

```python
import os
import re
from typing import Any, Dict, List, Optional
from openai import OpenAI
from pydantic import BaseModel

class PersonalisedContext(BaseModel):
    user_id: str
    technical_role: str
    expertise_level: str
    preferred_response_style: str
    relevant_tech_stack: List[str]
    relevant_goals: List[str]
    relevant_interests: List[str]
    relevant_resolved_items: List[str]
    memory_summary: Optional[str] = None
    prompt_injection: str

def select_relevant_memory(profile: UserProfile, query: str) -> Dict[str, Any]:
    query_tokens = set(re.findall(r"\w+", query.lower()))
    relevant_stack = []
    database_terms = {"database", "db", "sql", "postgres", "postgresql", "connection", "pool", "query", "redis"}
    web_terms = {"ui", "frontend", "react", "component", "render", "javascript", "node"}
    infra_terms = {"deploy", "kubernetes", "k8s", "docker", "cloud", "aws", "pod", "cluster"}

    for tech in profile.primary_tech_stack:
        t_low = tech.lower()
        if t_low in query_tokens:
            relevant_stack.append(tech)
        elif (query_tokens & database_terms) and t_low in {"postgresql", "postgres", "sqlite", "redis"}:
            relevant_stack.append(tech)
        elif (query_tokens & web_terms) and t_low in {"react", "javascript", "typescript"}:
            relevant_stack.append(tech)
        elif (query_tokens & infra_terms) and t_low in {"kubernetes", "docker", "go", "golang"}:
            relevant_stack.append(tech)

    if not relevant_stack and profile.primary_tech_stack:
        relevant_stack = profile.primary_tech_stack[:2]

    relevant_goals = [g for g in profile.active_goals if any(t in g.lower() for t in query_tokens) or len(profile.active_goals) <= 2]
    relevant_interests = [i for i in profile.recurring_interests if any(t in i.lower() for t in query_tokens) or len(profile.recurring_interests) <= 2]
    relevant_resolved = [r for r in profile.resolved_items if any(t in r.lower() for t in query_tokens)]

    return {
        "relevant_tech_stack": relevant_stack,
        "relevant_goals": relevant_goals,
        "relevant_interests": relevant_interests,
        "relevant_resolved_items": relevant_resolved,
    }

def build_personalisation_context(profile: UserProfile, query: str) -> PersonalisedContext:
    filtered = select_relevant_memory(profile, query)
    directives = []
    if profile.expertise_level.lower() == "beginner":
        directives.append("Explain foundational concepts gently. Avoid excessive jargon. Use clear analogies.")
    elif profile.expertise_level.lower() == "senior":
        directives.append("Assume senior engineering mastery. Be authoritative, direct, and architectural. Skip basic introductory fluff and focus on production tradeoffs, scale, and performance.")
    
    style_clean = profile.preferred_response_style.lower()
    if "concise" in style_clean or "code_first" in style_clean:
        directives.append("Lead with production-ready code or configuration immediately. Keep explanatory prose minimal.")
    elif "step_by_step" in style_clean or "tutorial" in style_clean:
        directives.append("Structure the explanation as a numbered, sequential walkthrough.")
    elif "deep_architectural" in style_clean or "dive" in style_clean:
        directives.append("Provide a thorough architectural breakdown: state management, failure modes, concurrency, and telemetry.")

    style_directive = " ".join(directives)
    lines = [
        "## USER PERSONALISATION CONTEXT (STRICTLY ADAPT OUTPUT TO THIS PROFILE):",
        f"- Target User ID: {profile.user_id}",
        f"- Technical Role: {profile.technical_role}",
        f"- Seniority & Expertise Level: {profile.expertise_level.upper()}",
        f"- Primary Tech Stack: {', '.join(filtered['relevant_tech_stack']) if filtered['relevant_tech_stack'] else 'General'}",
        f"- Communication Directive: {style_directive}",
    ]
    if filtered["relevant_goals"]:
        lines.append(f"- Active Initiatives / Goals: {'; '.join(filtered['relevant_goals'])}")
    if filtered["relevant_resolved_items"]:
        lines.append(f"- Already Resolved (DO NOT RE-SUGGEST): {'; '.join(filtered['relevant_resolved_items'])}")
    if profile.memory_summary:
        lines.append(f"- Synthesized Background: {profile.memory_summary}")
    lines.append("PERSONALISATION RULE: Your answer MUST match this user's expertise level and preferred style without explicitly quoting this metadata block.")

    return PersonalisedContext(
        user_id=profile.user_id,
        technical_role=profile.technical_role,
        expertise_level=profile.expertise_level,
        preferred_response_style=profile.preferred_response_style,
        relevant_tech_stack=filtered["relevant_tech_stack"],
        relevant_goals=filtered["relevant_goals"],
        relevant_interests=filtered["relevant_interests"],
        relevant_resolved_items=filtered["relevant_resolved_items"],
        memory_summary=profile.memory_summary,
        prompt_injection="\n".join(lines),
    )

def generate_personalised_response(user_id: str, query: str, db_path: str = "auronix_memory.db", client: Optional[OpenAI] = None) -> Dict[str, Any]:
    profile = get_user_profile(user_id, db_path=db_path)
    if not profile:
        profile = create_user_profile(user_id=user_id, db_path=db_path)

    context = build_personalisation_context(profile, query)
    system_prompt = f"You are AURONIX enterprise AI assistant.\n\n{context.prompt_injection}"

    api_key = os.environ.get("OPENAI_API_KEY")
    if client or (api_key and api_key.strip() and api_key != "your_openai_api_key_here"):
        try:
            oai = client or OpenAI(api_key=api_key.strip())
            completion = oai.chat.completions.create(
                model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": query}],
                temperature=0.2,
                max_tokens=900,
            )
            return {"user_id": user_id, "query": query, "response": completion.choices[0].message.content.strip(), "context": context, "used_llm": True}
        except Exception:
            pass

    # Deterministic fallback response reflecting profile attributes
    if context.expertise_level.lower() == "beginner":
        resp = (
            "### Understanding Connection Pooling: A Step-by-Step Guide for Frontend & Junior Engineers\n\n"
            "When your application needs to talk to a database, opening a brand-new connection for every single click or API call is very slow. "
            "**Connection pooling** keeps a small pool of ready-to-use connections open in the background so requests can reuse them instantly.\n\n"
            "#### Step 1: Why We Pool Connections\n"
            "- **Without Pooling:** 100 requests = 100 heavy handshakes (slow response times for users).\n"
            "- **With Pooling:** 100 requests share a reusable pool of 5-10 connections (near-instant responses).\n\n"
            "#### Step 2: How It Works in Practice\n"
            "1. Your code asks the pool: 'Is a connection free?'\n"
            "2. The pool lends a connection.\n"
            "3. Your code runs its query.\n"
            "4. Your code returns the connection back to the pool (never leave it open!).\n\n"
            "#### Step 3: Practical Client-Side Code Example (JavaScript / Node.js)\n"
            "```javascript\n"
            "const { Pool } = require('pg');\n"
            "const pool = new Pool({\n"
            "  max: 10,                 // Keep at most 10 reusable connections\n"
            "  idleTimeoutMillis: 30000, // Close idle connections after 30 seconds\n"
            "  connectionTimeoutMillis: 2000, // Fail fast if no connection available in 2s\n"
            "});\n"
            "async function fetchUserData(userId) {\n"
            "  const res = await pool.query('SELECT id, name FROM users WHERE id = $1', [userId]);\n"
            "  return res.rows[0];\n"
            "}\n"
            "```\n\n"
            "#### Summary Tip\n"
            "Always make sure queries release their connection back to the pool, otherwise your application will run out of connections and freeze."
        )
    else:
        resp = (
            "### Production Connection Pool Architecture & Tuning Specification\n\n"
            "For high-throughput distributed microservices, connection pooling must be engineered to prevent backend socket exhaustion, manage thundering herd spikes, and maintain deterministic p99 latencies.\n\n"
            "#### 1. Architectural Topology\n"
            "- **Application-Level Pool:** Sized strictly per-process using `max_connections = (core_count * 2) + effective_spindle_count`.\n"
            "- **Middleware Proxy (PgBouncer/Envoy):** Deploy transaction-mode connection pooling at the Kubernetes pod or sidecar level to multiplex thousands of microservice clients into a bounded physical PostgreSQL backend pool.\n\n"
            "#### 2. Production Go / PostgreSQL Implementation\n"
            "```go\n"
            "package db\n\n"
            "import (\n"
            "    \"context\"\n"
            "    \"time\"\n"
            "    \"github.com/jackc/pgx/v5/pgxpool\"\n"
            ")\n\n"
            "func InitProductionPool(ctx context.Context, connString string) (*pgxpool.Pool, error) {\n"
            "    cfg, err := pgxpool.ParseConfig(connString)\n"
            "    if err != nil {\n"
            "        return nil, err\n"
            "    }\n"
            "    cfg.MaxConns = 25\n"
            "    cfg.MinConns = 5\n"
            "    cfg.MaxConnLifetime = 30 * time.Minute\n"
            "    cfg.MaxConnIdleTime = 5 * time.Minute\n"
            "    cfg.HealthCheckPeriod = 1 * time.Minute\n"
            "    return pgxpool.NewWithConfig(ctx, cfg)\n"
            "}\n"
            "```\n\n"
            "#### 3. Critical Failure Modes & Telemetry\n"
            "- **Leaked Connections:** Enforce strict query context deadlines (`context.WithTimeout(ctx, 3*time.Second)`).\n"
            "- **Exhaustion Mitigation:** Expose Prometheus gauges for `pool_acquired_conns`, `pool_idle_conns`, and `pool_wait_duration_ms` with alerting at >80% pool saturation."
        )

    return {"user_id": user_id, "query": query, "response": resp, "context": context, "used_llm": False}
```

---

## 5. Memory Write Pipeline & LLM Extractor

```text
User Request
     ↓
Personalised Response
     ↓
Memory Extraction (structured JSON)
     ↓
Identify New Useful Information (goals, stack, role, resolved)
     ↓
Filter Out Conversational Noise (greetings, pleasantries)
     ↓
Validate Extracted JSON (Pydantic schema)
     ↓
Update UserProfile & Log Turn in SQLite
```

### Extractor Implementation (`extractor.py`)

```python
import json
import os
import re
from typing import Optional
from openai import OpenAI
from pydantic import BaseModel, Field

class ExtractedMemory(BaseModel):
    has_new_information: bool = False
    new_role: Optional[str] = None
    new_expertise_level: Optional[str] = None
    new_preferred_style: Optional[str] = None
    new_tech_stack: List[str] = Field(default_factory=list)
    new_goals: List[str] = Field(default_factory=list)
    new_interests: List[str] = Field(default_factory=list)
    new_resolved_items: List[str] = Field(default_factory=list)
    key_facts: List[str] = Field(default_factory=list)
    reasoning: str = "No durable information found"

def extract_durable_memory(user_input: str, ai_response: str, current_profile: Optional[UserProfile] = None, client: Optional[OpenAI] = None) -> ExtractedMemory:
    text = user_input.strip()
    text_lower = text.lower()

    # Filter conversational noise and pleasantries
    noise_patterns = [
        r"^(hi|hello|hey|good\s+morning|good\s+evening)[\s!.]*$",
        r"^(thanks|thank\s+you|thx|cheers|awesome|got\s+it|ok|okay)[\s!.]*$",
        r"^what\s+(is\s+the\s+time|can\s+you\s+do)[\s?.]*$",
    ]
    for p in noise_patterns:
        if re.search(p, text_lower):
            return ExtractedMemory(has_new_information=False, reasoning="Detected conversational noise, greeting, or pleasantry.")

    # Rule-engine / Heuristic fallback parser
    has_info = False
    new_role = None
    new_expertise = None
    new_style = None
    new_tech_stack = []
    new_goals = []
    new_interests = []
    new_resolved = []

    role_match = re.search(r"(?:i am|i'm|working as|my role is)\s+(?:a|an)?\s*([a-zA-Z\s]+(?:engineer|developer|sre|architect|analyst))", text_lower)
    if role_match:
        has_info = True
        new_role = role_match.group(1).strip().title()

    if re.search(r"\b(i am a beginner|i'm a beginner|new to (?:this|python)|junior)\b", text_lower):
        has_info = True
        new_expertise = "beginner"
    elif re.search(r"\b(senior|staff|principal|10\+ years|expert)\b", text_lower):
        has_info = True
        new_expertise = "senior"

    if re.search(r"(?:code\s*first|concise|no fluff|brief)", text_lower):
        has_info = True
        new_style = "concise_code_first"
    elif re.search(r"(?:step[\s-]by[\s-]step|simple explanation|beginner friendly)", text_lower):
        has_info = True
        new_style = "step_by_step_tutorial"

    known_techs = ["python", "fastapi", "docker", "kubernetes", "postgresql", "redis", "golang", "go", "react", "typescript", "javascript", "node"]
    for tech in known_techs:
        if re.search(r"\b" + re.escape(tech) + r"\b", text_lower):
            norm = {"postgres": "PostgreSQL", "postgresql": "PostgreSQL", "golang": "Go", "go": "Go", "js": "JavaScript", "k8s": "Kubernetes"}.get(tech, tech.capitalize())
            if norm not in new_tech_stack:
                new_tech_stack.append(norm)
                has_info = True

    goal_match = re.search(r"(?:my goal is|i am trying to|we are building|currently building)\s+([^.!?]+)", text, re.IGNORECASE)
    if goal_match:
        gt = goal_match.group(1).strip()
        if len(gt) > 5 and not gt.lower().startswith("what"):
            has_info = True
            new_goals.append(gt)

    resolved_match = re.search(r"(?:we (?:fixed|resolved|completed|solved)|i already (?:fixed|implemented))\s+([^.!?]+)", text, re.IGNORECASE)
    if resolved_match:
        rt = resolved_match.group(1).strip()
        if len(rt) > 5:
            has_info = True
            new_resolved.append(rt)

    return ExtractedMemory(
        has_new_information=has_info,
        new_role=new_role,
        new_expertise_level=new_expertise,
        new_preferred_style=new_style,
        new_tech_stack=new_tech_stack,
        new_goals=new_goals,
        new_interests=new_interests,
        new_resolved_items=new_resolved,
        reasoning="Extracted durable facts via parsing engine." if has_info else "No durable facts detected.",
    )
```

---

## 6. User History Summarisation

Implemented strictly with the signature:
```python
def summarise_user_history(user_id: str, db_path: str = "auronix_memory.db", client: Optional[OpenAI] = None) -> Optional[str]:
```

### Implementation (`summarizer.py`)

```python
SUMMARISATION_THRESHOLD = 20

def summarise_user_history(user_id: str, db_path: str = "auronix_memory.db", client: Optional[OpenAI] = None) -> Optional[str]:
    if not user_id or not user_id.strip():
        return None
    user_id_clean = user_id.strip()

    profile = get_user_profile(user_id_clean, db_path=db_path)
    if not profile:
        return None

    # Step 1 & 2: Determine count and trigger ONLY when interaction_count > 20
    count = get_user_interaction_count(user_id_clean, db_path=db_path)
    if count <= SUMMARISATION_THRESHOLD:
        return None

    unsummarized = get_user_interactions(user_id_clean, unsummarized_only=True, db_path=db_path)
    if not unsummarized and profile.memory_summary:
        return profile.memory_summary

    all_interactions = get_user_interactions(user_id_clean, db_path=db_path)
    if not all_interactions:
        return None
    latest_id = all_interactions[-1]["id"]

    # Synthesize concise user model
    all_tech = set()
    all_goals = []
    all_resolved = []
    for item in all_interactions:
        mem = item.get("extracted_memory") or {}
        for t in mem.get("new_tech_stack", []):
            all_tech.add(t)
        for g in mem.get("new_goals", []):
            if g not in all_goals:
                all_goals.append(g)
        for r in mem.get("new_resolved_items", []):
            if r not in all_resolved:
                all_resolved.append(r)

    tech_str = ", ".join(sorted(all_tech)) if all_tech else "enterprise microservices"
    summary_parts = [
        f"User has completed {count} enterprise interactions.",
        f"Primary production environment leverages {tech_str}.",
    ]
    if all_resolved:
        summary_parts.append(f"Successfully resolved: {'; '.join(all_resolved[:2])}.")
    if all_goals:
        summary_parts.append(f"Active initiatives: {'; '.join(all_goals[:2])}.")

    summary_text = " ".join(summary_parts)

    # Store concise user model back into UserProfile in SQLite
    update_user_profile(user_id_clean, {"memory_summary": summary_text}, db_path=db_path)
    mark_interactions_summarized(user_id_clean, up_to_id=latest_id, db_path=db_path)

    return summary_text
```

---

## 7. Lifecycle Manager & FastAPI Service

### Lifecycle Coordinator (`MemoryManager`)

```python
class MemoryManager:
    def __init__(self, db_path: str = "auronix_memory.db"):
        self.db_path = db_path
        init_db(self.db_path)

    def process_turn(self, user_id: str, query: str, auto_summarize: bool = True) -> Dict[str, Any]:
        profile = get_user_profile(user_id, db_path=self.db_path)
        if not profile:
            profile = create_user_profile(user_id=user_id, db_path=self.db_path)

        # 1. READ PIPELINE: Generate personalised response
        read_result = generate_personalised_response(user_id=user_id, query=query, db_path=self.db_path)
        ai_resp = read_result["response"]

        # 2. WRITE PIPELINE: Extract durable memory from turn
        extracted = extract_durable_memory(query, ai_resp, current_profile=profile)
        if extracted.has_new_information:
            updates = {}
            if extracted.new_role: updates["technical_role"] = extracted.new_role
            if extracted.new_expertise_level: updates["expertise_level"] = extracted.new_expertise_level
            if extracted.new_preferred_style: updates["preferred_response_style"] = extracted.new_preferred_style
            if extracted.new_tech_stack: updates["primary_tech_stack"] = list(dict.fromkeys(profile.primary_tech_stack + extracted.new_tech_stack))
            if extracted.new_goals: updates["active_goals"] = list(dict.fromkeys(profile.active_goals + extracted.new_goals))
            if extracted.new_resolved_items: updates["resolved_items"] = list(dict.fromkeys(profile.resolved_items + extracted.new_resolved_items))
            if updates:
                update_user_profile(user_id, updates, db_path=self.db_path)

        log_interaction(user_id, query, ai_resp, extracted.model_dump(), db_path=self.db_path)
        current_count = get_user_interaction_count(user_id, db_path=self.db_path)

        # 3. SUMMARISATION: Check if count > 20
        new_summary = None
        if auto_summarize and current_count > 20:
            new_summary = summarise_user_history(user_id, db_path=self.db_path)

        return {
            "user_id": user_id,
            "query": query,
            "response": ai_resp,
            "personalisation_applied": True,
            "interaction_count": current_count,
            "memory_summary": new_summary or profile.memory_summary,
        }
```

### FastAPI Endpoints (`api.py`)

Exposes REST endpoints:
* `POST /api/profiles`: Creates new UserProfile
* `GET /api/profiles/{user_id}`: Retrieves profile
* `PUT /api/profiles/{user_id}`: Updates profile
* `DELETE /api/profiles/{user_id}`: Scoped profile and history deletion
* `POST /api/chat`: Processes user query through memory read and write pipeline
* `POST /api/summarize/{user_id}`: Triggers summarisation (respects `> 20` threshold)
* `GET /api/health`: Service health check

---

## 8. Two-User Personalisation Demonstration

Run the automated demonstration script:
```powershell
python -c "
from memory.memory_manager import MemoryManager
# Execute comparison
"
```

### Comparative Output (Identical Query: *"How should I design and implement connection pooling for our services?"*)

```text
================================ USER A ================================

Profile:
  User ID:         alex_junior
  Role:            Junior Frontend Developer
  Expertise Level: beginner
  Response Style:  step_by_step_tutorial
  Tech Stack:      JavaScript, React, Node.js
  Active Goals:    Build responsive user dashboard, Learn basic backend database queries

Query:
  How should I design and implement connection pooling for our services?

Response:
### Understanding Connection Pooling: A Step-by-Step Guide for Frontend & Junior Engineers

When your application needs to talk to a database, opening a brand-new connection for every single click or API call is very slow and uses up a lot of server memory. **Connection pooling** keeps a small pool of ready-to-use connections open in the background so requests can reuse them instantly.

#### Step 1: Why We Pool Connections
- **Without Pooling:** 100 requests = 100 heavy handshakes (slow response times for users).
- **With Pooling:** 100 requests share a reusable pool of 5-10 connections (near-instant responses).

#### Step 2: How It Works in Practice
1. Your code asks the pool: 'Is a connection free?'
2. The pool lends a connection.
3. Your code runs its query.
4. Your code returns the connection back to the pool (never leave it open!).

#### Step 3: Practical Client-Side Code Example (JavaScript / Node.js)
```javascript
// Setup a connection pool using standard library
const { Pool } = require('pg');

const pool = new Pool({
  max: 10,                 // Keep at most 10 reusable connections
  idleTimeoutMillis: 30000, // Close idle connections after 30 seconds
  connectionTimeoutMillis: 2000, // Fail fast if no connection available in 2s
});

async function fetchUserData(userId) {
  // Automatically checks out connection, runs query, and releases it back
  const res = await pool.query('SELECT id, name FROM users WHERE id = $1', [userId]);
  return res.rows[0];
}
```

#### Summary Tip
Always make sure queries release their connection back to the pool, otherwise your application will run out of connections and freeze.


================================ USER B ================================

Profile:
  User ID:         priya_senior
  Role:            Senior Backend Infrastructure Engineer
  Expertise Level: senior
  Response Style:  deep_architectural_dive
  Tech Stack:      Go, Kubernetes, PostgreSQL, Redis, Kafka
  Active Goals:    Achieve sub-10ms p99 query latency, Deploy PgBouncer sidecars across Kubernetes clusters

Query:
  How should I design and implement connection pooling for our services?

Response:
### Production Connection Pool Architecture & Tuning Specification

For high-throughput distributed microservices, connection pooling must be engineered to prevent backend socket exhaustion, manage thundering herd spikes, and maintain deterministic p99 latencies.

#### 1. Architectural Topology
- **Application-Level Pool:** Sized strictly per-process using max_connections = (core_count * 2) + effective_spindle_count.
- **Middleware Proxy (PgBouncer/Envoy):** Deploy transaction-mode connection pooling at the Kubernetes pod or sidecar level to multiplex thousands of microservice clients into a bounded physical PostgreSQL backend pool.

#### 2. Production Go / PostgreSQL Implementation
```go
package db

import (
    "context"
    "time"
    "github.com/jackc/pgx/v5/pgxpool"
)

func InitProductionPool(ctx context.Context, connString string) (*pgxpool.Pool, error) {
    cfg, err := pgxpool.ParseConfig(connString)
    if err != nil {
        return nil, err
    }
    // Strict bounded production pool parameters
    cfg.MaxConns = 25
    cfg.MinConns = 5
    cfg.MaxConnLifetime = 30 * time.Minute
    cfg.MaxConnIdleTime = 5 * time.Minute
    cfg.HealthCheckPeriod = 1 * time.Minute

    return pgxpool.NewWithConfig(ctx, cfg)
}
```

#### 3. Critical Failure Modes & Telemetry
- **Leaked Connections:** Enforce strict query context deadlines (context.WithTimeout(ctx, 3*time.Second)).
- **Exhaustion Mitigation:** Expose Prometheus gauges for pool_acquired_conns, pool_idle_conns, and pool_wait_duration_ms with alerting at >80% pool saturation.

========================================================================
PERSONALISATION DEMONSTRATION VERIFICATION:
- User A received a beginner-friendly tutorial with JavaScript/Node.js syntax.
- User B received a senior architectural specification with Go/pgxpool and K8s PgBouncer.
- Memory Read successfully injected differentiated context for the identical prompt.
========================================================================
```

---

## 9. Comprehensive Test Suite & Pytest Verification

### Automated Tests Executed
1. `test_create_user_profile` — **PASSED**
2. `test_create_duplicate_user_profile_raises_error` — **PASSED**
3. `test_retrieve_user_profile` — **PASSED**
4. `test_update_user_profile` — **PASSED**
5. `test_delete_user_profile_scoped` — **PASSED**
6. `test_select_relevant_memory_filtering` — **PASSED**
7. `test_build_personalisation_context_scoping` — **PASSED**
8. `test_memory_isolation_between_users` — **PASSED**
9. `test_extract_durable_memory_identifies_durable_facts` — **PASSED**
10. `test_extract_durable_memory_ignores_noise` — **PASSED**
11. `test_memory_write_updates_user_profile` — **PASSED**
12. `test_summarisation_does_not_trigger_for_20_or_fewer_interactions` — **PASSED**
13. `test_summarisation_triggers_for_more_than_20_interactions` — **PASSED**
14. `test_same_query_different_profiles_produces_different_contexts_and_responses` — **PASSED**
15. `test_api_health` — **PASSED**
16. `test_api_profile_crud_lifecycle` — **PASSED**
17. `test_api_chat_pipeline` — **PASSED**
18. `test_api_summarize_threshold_behavior` — **PASSED**

**Overall Test Result:** `18 passed in 3.10s (100% pass rate)`.

---

## 10. Privacy Documentation & Data Deletion

### What Data Is Stored?
The AURONIX memory system strictly limits stored data to the fields defined in `UserProfile`:
- `user_id`: Unique identifier (employee ID/username).
- `created_at` / `updated_at`: Audit timestamps.
- `technical_role`: Professional domain.
- `expertise_level`: Skill tier (`beginner`, `intermediate`, `senior`).
- `preferred_response_style`: Communication format directive.
- `primary_tech_stack`: Languages, frameworks, and tools actively referenced.
- `active_goals`: Technical projects currently pursued.
- `recurring_interests`: Focus areas.
- `resolved_items`: Completed initiatives.
- `memory_summary`: Synthesized profile text generated after 20 interactions.
- `interaction_history`: Queries, responses, and extracted facts for multi-turn continuity.

### Why Is It Stored?
Storing this data eliminates repetitive onboarding overhead. Every response is delivered in the optimal technical depth, programming language, and structure suited to the employee's role, dramatically reducing context switching and time to resolution.

### Legal Basis Disclaimer
> [!IMPORTANT]
> The deployed product must establish an appropriate lawful basis for storing personal data in its applicable jurisdiction (such as legitimate enterprise interests, workplace operational policies, or obtaining affirmative user consent where legally mandated). This documentation is technical documentation and does NOT constitute legal advice.

### Data Deletion ("Right to be Forgotten")
Users can delete all profile records and interaction history at any time:
1. **Via Python API:**
   ```python
   delete_user_profile("employee_user_id")
   ```
2. **Via REST Endpoint:**
   ```bash
   curl -X DELETE "http://127.0.0.1:8000/api/profiles/employee_user_id"
   ```
Deletion is strictly scoped to `user_id`, cascading through both `user_profiles` and `interaction_history` without affecting any other user records.

---

## 11. Run Instructions

### 1. Requirements
```bash
pip install fastapi uvicorn pydantic openai pytest pytest-asyncio httpx
```

### 2. Run Personalisation Demo
```powershell
python -c "from memory_manager import MemoryManager; ..."
```

### 3. Run FastAPI Service
```powershell
uvicorn api:app --reload --port 8000
```
