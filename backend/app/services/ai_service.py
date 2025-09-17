import os
import re
import yaml
import datetime
import sqlparse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.ai_queries_log import AIQueryLog
from openai import AsyncOpenAI
from app.services.llm_adapter import LLMAdapter
from app.core.config import settings
import prometheus_client as prom


llm = LLMAdapter()


# ==============================
# Prometheus Metrics
# ==============================
AI_QUERIES_TOTAL = prom.Counter(
    "finops_ai_queries_total",
    "Total number of AI queries processed",
    ["status"]  # yaml | llm | ollama | unsupported | unsafe | llm_failed
)

# ==============================
# Load AI Queries (from YAML)
# ==============================
def load_ai_queries():
    path = os.getenv("AI_QUERIES_FILE", "config/ai_queries.yaml")
    with open(path, "r") as f:
        return yaml.safe_load(f)["queries"]

AI_QUERIES = load_ai_queries()

# ==============================
# Build Dynamic Filters
# ==============================
def build_filters(nlq: str):
    filters = {"account_filter": "", "service_filter": "", "month_filter": ""}
    params = {}

    # Account filter
    acct_match = re.search(r"(prod|dev|sandbox|finance|account\s+\d+)", nlq)
    if acct_match:
        filters["account_filter"] = "AND a.account_name ILIKE :account_name"
        params["account_name"] = f"%{acct_match.group(1)}%"

    # Service filter
    svc_match = re.search(r"(ec2|eks|lambda|rds|s3)", nlq)
    if svc_match:
        filters["service_filter"] = "AND s.service_name ILIKE :service_name"
        params["service_name"] = f"%{svc_match.group(1)}%"

    # Month filter
    month_match = re.search(
        r"(january|february|march|april|may|june|july|august|september|october|november|december)",
        nlq,
    )
    if month_match:
        month_str = month_match.group(1).capitalize()
        filters["month_filter"] = (
            "AND date_trunc('month', b.usage_date) = date_trunc('month', DATE :month_start)"
        )
        params["month_start"] = datetime.datetime.strptime(month_str, "%B").date().replace(day=1)

    return filters, params


# ==============================
# Schema Introspection
# ==============================
async def get_db_schema(db: AsyncSession) -> str:
    q = """
    SELECT table_name, column_name, data_type
    FROM information_schema.columns
    WHERE table_schema = 'public'
    ORDER BY table_name, ordinal_position;
    """
    result = await db.execute(text(q))
    rows = result.all()
    schema = {}
    for table, col, dtype in rows:
        schema.setdefault(table, []).append(f"{col} ({dtype})")
    return "\n".join([f"{t}: {', '.join(cols)}" for t, cols in schema.items()])


# ==============================
# LLM SQL Generator
# ==============================
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def generate_sql_with_llm(nl_query: str, db_schema: str) -> str:
    prompt = f"""
    Convert this natural language request into a SAFE SQL query.
    Schema:
    {db_schema}

    Rules:
    - Only SELECT queries are allowed.
    - Always include LIMIT 100 if not specified.
    - No DELETE, DROP, UPDATE, INSERT, or ALTER.

    Question: {nl_query}
    """
    resp = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return resp.choices[0].message.content.strip()


# ==============================
# Guardrails
# ==============================
def is_safe_sql(sql: str) -> bool:
    parsed = sqlparse.parse(sql)
    for stmt in parsed:
        if stmt.get_type() != "SELECT":
            return False
    return True


# ==============================
# Main Query Processor
# ==============================
# ==============================
# Main Query Processor
# ==============================
# ==============================
# Main Query Processor
# ==============================
async def process_query(db: AsyncSession, nl_query: str):
    nlq = nl_query.lower()
    sql, summary, params, source = None, None, {}, None

    # --- Step 1: Try YAML queries ---
    for q in AI_QUERIES:
        if any(p in nlq for p in q["patterns"]):
            sql = q["sql"]
            summary = q.get("summary", "")
            params = q.get("params", {})
            source = "yaml"
            break

    # --- Step 2: If no YAML match → LLM fallback ---
    if not sql and settings.USE_LLM_FALLBACK:
        try:
            schema = await get_db_schema(db)
            sql = await llm.generate_sql(nl_query, schema)  # primary provider
            if sql and is_safe_sql(sql):
                source = "llm"
                summary = "Dynamic AI-generated answer"
            else:
                # Unsafe or empty SQL
                log_entry = AIQueryLog(
                    query_text=nl_query,
                    sql_generated=sql,
                    status="unsafe"
                )
                db.add(log_entry)
                await db.commit()
                return {
                    "query": nl_query,
                    "sql": sql,
                    "result": None,
                    "summary": "🚫 Unsafe query blocked",
                }
        except Exception as e:
            # --- Step 2a: Try Ollama fallback ---
            try:
                schema = await get_db_schema(db)
                os.environ["LLM_PROVIDER"] = "ollama"
                ollama_llm = LLMAdapter()  # re-init with Ollama
                sql = await ollama_llm.generate_sql(nl_query, schema)
                if sql and is_safe_sql(sql):
                    source = "ollama"
                    summary = "Dynamic AI-generated answer (Ollama fallback)"
                else:
                    log_entry = AIQueryLog(
                        query_text=nl_query,
                        sql_generated=sql,
                        status="unsafe"
                    )
                    db.add(log_entry)
                    await db.commit()
                    return {
                        "query": nl_query,
                        "sql": sql,
                        "result": None,
                        "summary": "🚫 Unsafe query blocked (Ollama fallback)",
                    }
            except Exception as e2:
                # If Ollama also fails → mark as llm_failed
                log_entry = AIQueryLog(
                    query_text=nl_query,
                    sql_generated=None,
                    status="llm_failed"
                )
                db.add(log_entry)
                await db.commit()
                return {
                    "query": nl_query,
                    "sql": None,
                    "result": None,
                    "summary": f"⚠️ LLM + Ollama fallback failed: {str(e2)}",
                }

    # --- Step 3: If still no SQL ---
    if not sql:
        log_entry = AIQueryLog(
            query_text=nl_query,
            sql_generated=None,
            status="unsupported"
        )
        db.add(log_entry)
        await db.commit()
        return {
            "query": nl_query,
            "sql": None,
            "result": None,
            "summary": "❓ Query not supported yet",
        }

    # --- Step 4: Apply filters & params ---
    filters, dynamic_params = build_filters(nlq)
    sql = sql.format(**filters, **params)
    params.update(dynamic_params)

    # --- Step 5: Execute SQL ---
    
    result = await db.execute(text(sql), params)
    rows = result.mappings().all()

    # --- Step 5a: Log query ---
    log_entry = AIQueryLog(
        query_text=nl_query,
        sql_generated=sql,
        status=source or "unsupported"
    )
    db.add(log_entry)
    await db.commit()

    # Increment Prometheus counter
    AI_QUERIES_TOTAL.labels(status=source or "unsupported").inc()


    # --- Step 6: Log successful query ---
    log_entry = AIQueryLog(
        query_text=nl_query,
        sql_generated=sql,
        status=source or "yaml"
    )
    db.add(log_entry)
    await db.commit()

    return {
        "query": nl_query,
        "sql": sql,
        "result": rows,
        "summary": summary,
    }

    nlq = nl_query.lower()
    sql, summary, params, source = None, None, {}, None

    # --- Step 1: Try YAML queries ---
    for q in AI_QUERIES:
        if any(p in nlq for p in q["patterns"]):
            sql = q["sql"]
            summary = q.get("summary", "")
            params = q.get("params", {})
            source = "yaml"
            break

    # --- Step 2: If no YAML match → LLM fallback ---
    if not sql and settings.USE_LLM_FALLBACK:
        try:
            schema = await get_db_schema(db)
            sql = await llm.generate_sql(nl_query, schema)
            if sql and is_safe_sql(sql):
                source = "llm"
                summary = "Dynamic AI-generated answer"
            else:
                # Unsafe or empty SQL
                log_entry = AIQueryLog(
                    query_text=nl_query,
                    sql_generated=sql,
                    status="unsafe"
                )
                db.add(log_entry)
                await db.commit()
                return {
                    "query": nl_query,
                    "sql": sql,
                    "result": None,
                    "summary": "🚫 Unsafe query blocked",
                }
        except Exception as e:
            # LLM failed, fallback gracefully
            log_entry = AIQueryLog(
                query_text=nl_query,
                sql_generated=None,
                status="llm_failed"
            )
            db.add(log_entry)
            await db.commit()
            return {
                "query": nl_query,
                "sql": None,
                "result": None,
                "summary": f"⚠️ LLM fallback failed: {str(e)}",
            }

    # --- Step 3: If still no SQL ---
    if not sql:
        log_entry = AIQueryLog(
            query_text=nl_query,
            sql_generated=None,
            status="unsupported"
        )
        db.add(log_entry)
        await db.commit()
        return {
            "query": nl_query,
            "sql": None,
            "result": None,
            "summary": "❓ Query not supported yet",
        }

    # --- Step 4: Apply filters & params ---
    filters, dynamic_params = build_filters(nlq)
    sql = sql.format(**filters, **params)
    params.update(dynamic_params)

    # --- Step 5: Execute SQL ---
    result = await db.execute(text(sql), params)
    rows = result.mappings().all()

    # --- Step 6: Log successful query ---
    log_entry = AIQueryLog(
        query_text=nl_query,
        sql_generated=sql,
        status=source or "yaml"
    )
    db.add(log_entry)
    await db.commit()

    return {
        "query": nl_query,
        "sql": sql,
        "result": rows,
        "summary": summary,
    }

    nlq = nl_query.lower()
    sql, summary, params, source = None, None, {}, None

    # --- Step 1: Try YAML queries ---
    for q in AI_QUERIES:
        if any(p in nlq for p in q["patterns"]):
            sql = q["sql"]
            summary = q.get("summary", "")
            params = q.get("params", {})
            source = "yaml"
            break

    # --- Step 2: If no YAML match → LLM ---


    if not sql and settings.USE_LLM_FALLBACK:
            schema = await get_db_schema(db)  
    sql = await llm.generate_sql(nl_query, schema) 
    source = "llm"
    summary = "Dynamic AI-generated answer"
    
    if not sql:
        schema = await get_db_schema(db)
        sql = await generate_sql_with_llm(nl_query, schema)

        if not is_safe_sql(sql):
            log_entry = AIQueryLog(query_text=nl_query, status="unsafe")
            db.add(log_entry)
            await db.commit()
            return {
                "query": nl_query,
                "sql": sql,
                "result": None,
                "summary": "🚫 Unsafe query blocked",
            }

        summary = "Dynamic AI-generated answer"
        source = "llm"

    # --- Step 3: Apply filters & params ---
    filters, dynamic_params = build_filters(nlq)
    sql = sql.format(**filters, **params)
    params.update(dynamic_params)

    # --- Step 4: Execute SQL ---
    result = await db.execute(text(sql), params)
    rows = result.mappings().all()

    # --- Step 5: Log query ---
    log_entry = log_entry = AIQueryLog(
    query_text=nl_query,
    sql_generated=sql,
    status=source or "unsupported"
)
    db.add(log_entry)
    await db.commit()

    return {
        "query": nl_query,
        "sql": sql,
        "result": rows,
        "summary": summary,
    }
