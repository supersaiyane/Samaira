LLM Usage in ai\_service.py
---------------------------

### 🎯 Goal

*   Let users query billing/usage/savings **in plain English**.
    
*   Hybrid approach:
    
    *   **YAML lookup** (fast, safe).
        
    *   **LLM fallback** (flexible, dynamic).
        
*   Ensure **guardrails + observability**.
    

### 🔹 Flow Overview

1.  User → /api/v1/ai/query?q=...
    
2.  ai\_service.py → process\_query
    
    *   **Step 1:** Try ai\_queries.yaml.
        
    *   **Step 2:** If no match → LLM generates SQL.
        
    *   **Step 3:** Guardrails → reject unsafe SQL.
        
    *   **Step 4:** Execute in Postgres.
        
    *   **Step 5:** Log in ai\_queries\_log.
        

### 🔹 YAML Lookup

*   File: backend/app/config/ai\_queries.yaml.
    
*   Example:
    

```
- patterns:
    - "top services"
  sql: |
    SELECT s.service_name, SUM(b.cost_amount) AS total_cost
    FROM billing b
    JOIN services s ON b.service_id = s.service_id
    WHERE b.usage_date >= CURRENT_DATE - INTERVAL '{days} days'
    GROUP BY s.service_name
    ORDER BY total_cost DESC
    LIMIT 5
  summary: "Top 5 services by cost in last {days} days"
  params:
    days: 30
```

*   ✅ Deterministic.
    
*   ❌ Limited coverage.
    

### 🔹 LLM Fallback

*   File: backend/app/services/llm\_adapter.py.
    
*   USE\_LLM\_FALLBACK=trueLLM\_PROVIDER=openai # or anthropic | ollamaLLM\_MODEL=gpt-4o-miniLLM\_API\_KEY=sk-xxxx
    
*   Example flow:
    

```
if not sql and settings.USE_LLM_FALLBACK:
    try:
        schema = await get_db_schema(db)
        sql = await llm.generate_sql(nl_query, schema)
        if sql and is_safe_sql(sql):
            source = "llm"
        else:
            status = "unsafe"
    except Exception:
        status = "llm_failed"
```

*   Providers supported:
    
    *   **OpenAI** (gpt-4o-mini, gpt-4o).
        
    *   **Anthropic** (claude-3.5-sonnet).
        
    *   **Ollama** (llama3 running locally via Docker).
        

### 🔹 Guardrails

*   ✅ Only allow SELECT.
    
*   ✅ Auto-add LIMIT 100.
    
*   ✅ Block DROP, DELETE, UPDATE, etc.
    

```
def is_safe_sql(sql: str) -> bool:
    parsed = sqlparse.parse(sql)
    for stmt in parsed:
        if stmt.get_type() != "SELECT":
            return False
    return True
```

### 🔹 Logging

Table: ai\_queries\_log

| id | query_text            | sql_generated |
|----|-----------------------|---------------|
| 1  | "top services"        | SELECT...     |
| 2  | "show me EC2 savings" | SELECT...     |
| 3  | "delete billing"      | DELETE ...    |
| 4  | "random question"     | NULL          |


Statuses: yaml | llm | ollama | unsafe | unsupported | llm\_failed.

### 🔹 Observability

*   Prometheus counter: finops\_ai\_queries\_total{status="llm"}.
    
*   Grafana dashboard:
    
    *   Pie chart → YAML vs LLM vs Ollama usage.
        
    *   Trend → queries per day.
        
    *   Table → top queries by frequency.
        

### ✅ Outcomes

*   Natural language access to FinOps data.
    
*   Hybrid model (safety + flexibility).
    
*   Complete audit trail of queries for training/improvement.
    
*   Resilient: works even if OpenAI is down (Ollama fallback).
    

⚡ **Summary**:

*   **Cost Forecasting v3** → adds LSTM + drift detection → smarter + safer predictions.
    
*   **LLM in ai\_service.py** → makes Samaira a conversational FinOps assistant, blending prebuilt queries with AI-generated SQL, with strict guardrails + logging.