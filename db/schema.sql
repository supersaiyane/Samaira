-- ========================
-- 1. Accounts (multi-cloud)
-- ========================
CREATE TABLE accounts (
    account_id SERIAL PRIMARY KEY,
    cloud_provider VARCHAR(20) NOT NULL,       -- AWS, Azure, GCP
    account_number VARCHAR(100) NOT NULL,      -- AWS Account ID / Azure Sub ID / GCP Project ID
    account_name VARCHAR(255),
    owner_email VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ========================
-- 2. Service Categories
-- ========================
CREATE TABLE service_categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) UNIQUE NOT NULL, -- Compute, Storage, Database, Networking
    description TEXT
);

-- ========================
-- 3. Services (normalized)
-- ========================
CREATE TABLE services (
    service_id SERIAL PRIMARY KEY,
    cloud_provider VARCHAR(20) NOT NULL,
    service_code VARCHAR(100) NOT NULL,         -- e.g., AmazonEC2, AzureVM, BigQuery
    service_name VARCHAR(255) NOT NULL,         -- Human-readable name
    category_id INT REFERENCES service_categories(category_id),
    UNIQUE (cloud_provider, service_code)
);

-- ========================
-- 4. Resources
-- ========================
CREATE TABLE resources (
    resource_id SERIAL PRIMARY KEY,
    account_id INT REFERENCES accounts(account_id),
    service_id INT REFERENCES services(service_id),
    resource_name VARCHAR(255),                -- e.g., i-12345, eks-cluster-1
    region VARCHAR(50),
    resource_type VARCHAR(100),                -- instanceType, DB type, Storage class
    tags JSONB,                                -- for cost allocation tags
    created_at TIMESTAMPTZ DEFAULT NOW(),
    terminated_at TIMESTAMPTZ
);

-- ========================
-- 5. Billing (partitioned by month)
-- ========================
CREATE TABLE billing (
    billing_id BIGSERIAL PRIMARY KEY,
    account_id INT REFERENCES accounts(account_id),
    service_id INT REFERENCES services(service_id),
    resource_id INT REFERENCES resources(resource_id),
    usage_date DATE NOT NULL,                  -- day-level granularity
    cost_amount NUMERIC(18,6) NOT NULL,
    currency VARCHAR(10) DEFAULT 'USD',
    usage_type VARCHAR(100),                   -- e.g., BoxUsage:m5.large
    usage_quantity NUMERIC(18,6),
    pricing_unit VARCHAR(50),                  -- Hours, GB-Mo, Requests
    metadata JSONB,                            -- raw CUR/CE fields
    created_at TIMESTAMPTZ DEFAULT NOW()
) PARTITION BY RANGE (usage_date);

-- Example partitions
CREATE TABLE billing_2024_01 PARTITION OF billing
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- ========================
-- 6. Usage (partitioned)
-- ========================
CREATE TABLE usage (
    usage_id BIGSERIAL PRIMARY KEY,
    resource_id INT REFERENCES resources(resource_id),
    metric_name VARCHAR(100),                  -- CPUUtilization, NetworkIn, etc.
    metric_value NUMERIC(18,6),
    unit VARCHAR(50),
    collected_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
) PARTITION BY RANGE (collected_at);

-- ========================
-- 7. Clusters
-- ========================
CREATE TABLE clusters (
    cluster_id SERIAL PRIMARY KEY,
    account_id INT REFERENCES accounts(account_id),
    cluster_name VARCHAR(255),
    cluster_type VARCHAR(50),                  -- EKS, AKS, GKE
    region VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Link resources to clusters (N:M)
CREATE TABLE cluster_resources (
    cluster_id INT REFERENCES clusters(cluster_id),
    resource_id INT REFERENCES resources(resource_id),
    PRIMARY KEY (cluster_id, resource_id)
);

-- ========================
-- 8. Recommendations
-- ========================
CREATE TABLE recommendations (
    rec_id SERIAL PRIMARY KEY,
    resource_id INT REFERENCES resources(resource_id),
    rec_type VARCHAR(50),                      -- Rightsize, Idle, ReservedInstance, SavingsPlan
    current_config JSONB,
    recommended_config JSONB,
    estimated_savings NUMERIC(18,6),
    currency VARCHAR(10) DEFAULT 'USD',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    status VARCHAR(50) DEFAULT 'pending'       -- pending, applied, dismissed
);

-- ========================
-- 9. Anomalies
-- ========================
CREATE TABLE anomalies (
    anomaly_id SERIAL PRIMARY KEY,
    account_id INT REFERENCES accounts(account_id),
    service_id INT REFERENCES services(service_id),
    detected_at TIMESTAMPTZ DEFAULT NOW(),
    metric VARCHAR(100),                       -- cost, usage
    observed_value NUMERIC(18,6),
    expected_value NUMERIC(18,6),
    deviation_percent NUMERIC(6,2),
    details JSONB
);

-- ========================
-- 10. Savings (historical)
-- ========================
CREATE TABLE savings (
    saving_id SERIAL PRIMARY KEY,
    account_id INT REFERENCES accounts(account_id),
    resource_id INT REFERENCES resources(resource_id),
    rec_id INT REFERENCES recommendations(rec_id),
    implemented_at TIMESTAMPTZ DEFAULT NOW(),
    actual_savings NUMERIC(18,6),
    currency VARCHAR(10) DEFAULT 'USD'
);

-- ========================
-- 11. Forecasts
-- ========================
CREATE TABLE forecasts (
    forecast_id SERIAL PRIMARY KEY,
    account_id INT REFERENCES accounts(account_id),
    service_id INT REFERENCES services(service_id),
    generated_at TIMESTAMPTZ DEFAULT NOW(),
    forecast_period_start DATE,
    forecast_period_end DATE,
    forecast_amount NUMERIC(18,6),
    currency VARCHAR(10) DEFAULT 'USD',
    model_used VARCHAR(50),                    -- Prophet, ARIMA, etc.
    confidence_interval JSONB
);

-- ========================
-- 12. Logs (application + system)
-- ========================
CREATE TABLE logs (
    log_id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    level VARCHAR(20),                         -- INFO, WARN, ERROR
    component VARCHAR(100),                    -- backend, airflow, ingestion, ai_engine
    message TEXT,
    correlation_id UUID,
    user_id VARCHAR(255),
    extra JSONB
);

-- ========================
-- 13. Unmapped Services (for new AWS/Azure/GCP)
-- ========================
CREATE TABLE unmapped_services (
    id SERIAL PRIMARY KEY,
    cloud_provider VARCHAR(20) NOT NULL,
    service_name VARCHAR(255) NOT NULL,
    first_seen TIMESTAMPTZ DEFAULT NOW(),
    last_seen TIMESTAMPTZ DEFAULT NOW()
);

-- ========================
-- 14. Instance Catalog (for EC2 families & sizes)
-- ========================
CREATE TABLE instance_catalog (
    instance_type VARCHAR(50) PRIMARY KEY,       -- e.g., m5.xlarge
    family VARCHAR(20) NOT NULL,                 -- e.g., m5
    size VARCHAR(20) NOT NULL,                   -- e.g., xlarge
    vcpu INT,
    memory_gb NUMERIC,
    storage TEXT,
    network_performance TEXT,
    generation TEXT,
    baremetal BOOLEAN DEFAULT false,
    gpu_count INT DEFAULT 0,
    last_updated TIMESTAMPTZ DEFAULT NOW()
);

-- ========================
-- 15. Budgets (per account / service / global)
-- ========================
CREATE TABLE budgets (
    budget_id SERIAL PRIMARY KEY,
    account_id INT REFERENCES accounts(account_id) ON DELETE CASCADE,
    service_id INT REFERENCES services(service_id) ON DELETE CASCADE,
    budget_name VARCHAR(255) NOT NULL,
    budget_limit NUMERIC(18,6) NOT NULL,     -- budgeted amount
    currency VARCHAR(10) DEFAULT 'USD',
    period VARCHAR(20) DEFAULT 'monthly',    -- monthly, quarterly, yearly
    start_date DATE DEFAULT CURRENT_DATE,
    end_date DATE,                           -- optional
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);


-- ========================
-- 16. Insights (For ai-driven insights and reports)
-- ========================
CREATE TABLE insights (
    insight_id SERIAL PRIMARY KEY,
    account_id INT REFERENCES accounts(account_id),
    service_id INT REFERENCES services(service_id),
    insight_type VARCHAR(50),       -- trend, savings, idle, forecast_gap
    severity VARCHAR(20),           -- info, warning, critical
    message TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);


-- ========================
-- 17. AI Queries Log (NL → SQL history)
-- ========================
CREATE TABLE ai_queries_log (
    id SERIAL PRIMARY KEY,
    query_text TEXT NOT NULL,          -- natural language query
    sql_generated TEXT,                -- SQL we built/generated
    status VARCHAR(50) NOT NULL,       -- yaml | llm | unsafe | unsupported
    created_at TIMESTAMPTZ DEFAULT NOW()
);


-- ========================
-- Indexing (OLAP-friendly)
-- ========================
CREATE INDEX idx_billing_date_account_service ON billing (usage_date, account_id, service_id);
CREATE INDEX idx_usage_time_resource ON usage (collected_at, resource_id);
CREATE INDEX idx_recommendations_resource ON recommendations (resource_id);
CREATE INDEX idx_anomalies_date_account ON anomalies (detected_at, account_id);
CREATE INDEX idx_instance_family ON instance_catalog (family);
CREATE INDEX idx_budgets_account_service ON budgets (account_id, service_id);
CREATE INDEX idx_insights_account ON insights (account_id);
CREATE INDEX idx_insights_service ON insights (service_id);
CREATE INDEX idx_insights_type ON insights (insight_type);
CREATE INDEX idx_aiqueries_status ON ai_queries_log (status);
CREATE INDEX idx_aiqueries_created_at ON ai_queries_log (created_at);

