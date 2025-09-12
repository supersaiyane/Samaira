from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.models.ai_queries_log import AIQueryLog
from sqlalchemy.ext.asyncio import AsyncSession
import re
import datetime
import os
import yaml

async def process_query(db: AsyncSession, nl_query: str):
    nlq = nl_query.lower()
    sql = None
    summary = None

    # --- Examples ---
    if "top" in nlq and "services" in nlq and "cost" in nlq:
        days = 30
        match = re.search(r"last (\d+) days", nlq)
        if match:
            days = int(match.group(1))

        sql = f"""
            SELECT s.service_name, SUM(b.cost_amount) AS total_cost
            FROM billing b
            JOIN services s ON b.service_id = s.service_id
            WHERE b.usage_date >= CURRENT_DATE - INTERVAL '{days} days'
            GROUP BY s.service_name
            ORDER BY total_cost DESC
            LIMIT 5
        """
        summary = f"Top 5 services by cost in last {days} days"

    elif "savings" in nlq and "ec2" in nlq:
        sql = """
            SELECT SUM(s.actual_savings) AS total_savings
            FROM savings s
            JOIN resources r ON s.resource_id = r.resource_id
            JOIN services sv ON r.service_id = sv.service_id
            WHERE sv.service_name = 'EC2'
        """
        summary = "Total EC2 savings so far"

    elif "idle" in nlq and "resources" in nlq:
        sql = """
            SELECT r.resource_name, SUM(b.cost_amount) AS total_cost
            FROM billing b
            JOIN resources r ON b.resource_id = r.resource_id
            JOIN usage u ON r.resource_id = u.resource_id
            WHERE u.metric_value < 1
              AND b.usage_date >= CURRENT_DATE - INTERVAL '30 days'
            GROUP BY r.resource_name
            HAVING SUM(b.cost_amount) > 100
        """
        summary = "Idle resources costing more than $100 in last 30 days"

    else:
        return {
            "query": nl_query,
            "sql": None,
            "result": None,
            "summary": "❓ Query type not supported yet"
        }

    result = await db.execute(text(sql))
    rows = result.mappings().all()

    return {
        "query": nl_query,
        "sql": sql,
        "result": rows,
        "summary": summary
    }


def load_ai_queries():
    path = os.getenv("AI_QUERIES_FILE", "config/ai_queries.yaml")
    with open(path, "r") as f:
        return yaml.safe_load(f)["queries"]

AI_QUERIES = load_ai_queries()


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
    month_match = re.search(r"(january|february|march|april|may|june|july|august|september|october|november|december)", nlq)
    if month_match:
        month_str = month_match.group(1).capitalize()
        filters["month_filter"] = "AND date_trunc('month', b.usage_date) = date_trunc('month', DATE :month_start)"
        params["month_start"] = datetime.strptime(month_str, "%B").date().replace(day=1)

    return filters, params


async def process_query(db: AsyncSession, nl_query: str):
    nlq = nl_query.lower()
    sql, summary = None, None
    params = {}

    for q in AI_QUERIES:
        if any(p in nlq for p in q["patterns"]):
            sql = q["sql"]
            summary = q.get("summary", "")
            params = q.get("params", {})
            break

    if not sql:
                # Log unsupported query
        log_entry = AIQueryLog(query_text=nl_query, status="unsupported")
        db.add(log_entry)
        await db.commit()
        
        return {
            "query": nl_query,
            "sql": None,
            "result": None,
            "summary": "❓ Query not supported yet"
        }

    # Dynamic placeholder substitution
    filters, dynamic_params = build_filters(nlq)
    sql = sql.format(**filters, **params)
    summary = summary.format(**params)
    params.update(dynamic_params)

    result = await db.execute(text(sql), params)
    rows = result.mappings().all()

        # Log supported query
    log_entry = AIQueryLog(query_text=nl_query, status="supported")
    db.add(log_entry)
    await db.commit()

    return {
        "query": nl_query,
        "sql": sql,
        "result": rows,
        "summary": summary
    }

