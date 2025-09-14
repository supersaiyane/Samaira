📘 Instance Catalog Module
==========================

1\. Context & Problem Statement
-------------------------------

In FinOps, **rightsizing and cost optimization** depend on accurate metadata about available cloud resources (e.g., EC2 instance families, sizes, and prices).If this catalog is stale or incomplete:

*   Rightsizing recommendations become inaccurate (e.g., suggesting non-existent instance types).
    
*   Savings projections become unreliable.
    
*   Teams lose trust in the FinOps platform.
    

👉 The **Instance Catalog module** ensures we always have an up-to-date reference of instance families, sizes, and pricing, synced directly from AWS Pricing API.

2\. Architecture Overview
-------------------------

**Components:**

*   **Airflow DAG**: instance\_catalog\_updater
    
    *   Runs weekly to fetch fresh instance data.
        
*   **AWS Pricing API**:
    
    *   Used to pull EC2 instance families, attributes, and prices.
        
*   **Database Table**: instance\_catalog
    
    *   Stores structured metadata (family, size, vCPUs, memory, storage, region, on-demand/hourly price).
        
*   **FastAPI Backend**:
    
    *   Provides APIs to query the catalog for rightsizing and forecasting services.
        

**High-Level Flow:**

```
flowchart TD
    A[AWS Pricing API] -->|Sync| B[Airflow DAG: instance_catalog_updater]
    B --> C[Postgres: instance_catalog table]
    C --> D[FastAPI /api/v1/catalog]
    D --> E[Rightsizing & Forecasting Modules]

```

3\. Database Schema (instance\_catalog)
---------------------------------------

```
CREATE TABLE instance_catalog (
    id SERIAL PRIMARY KEY,
    family VARCHAR(50) NOT NULL,
    size VARCHAR(50) NOT NULL,
    vcpus INT,
    memory_gb NUMERIC,
    storage VARCHAR(50),
    network VARCHAR(50),
    region VARCHAR(50),
    price_per_hour NUMERIC,
    currency VARCHAR(10) DEFAULT 'USD',
    last_updated TIMESTAMPTZ DEFAULT NOW()
);

```

4\. Airflow DAG (instance\_catalog\_updater)
--------------------------------------------

**Key Steps:**

1.  **Fetch EC2 metadata** via AWS Pricing API.
    
2.  Normalize JSON → structured rows (family, size, vCPUs, memory, price, etc.).
    
3.  Upsert into instance\_catalog table.
    
    *   Old rows replaced.
        
    *   New rows inserted.
        
4.  Notify via Slack/Teams with summary (✅ Updated 392 instance types).
    

**Pseudo-code snippet:**

```
pricing = boto3.client("pricing", region_name="us-east-1")


response = pricing.get_products(
    ServiceCode="AmazonEC2",
    Filters=[{"Type": "TERM_MATCH", "Field": "operatingSystem", "Value": "Linux"}],
    MaxResults=100
)


for item in response["PriceList"]:
    product = json.loads(item)
    instance_type = product["product"]["attributes"]["instanceType"]
    vcpus = product["product"]["attributes"].get("vcpu")
    mem = product["product"]["attributes"].get("memory")
    price = extract_on_demand_price(product)
    upsert_instance_type(instance_type, vcpus, mem, price)

```

5\. API Endpoints (FastAPI)
---------------------------

*   GET /api/v1/catalog
    
    *   Returns all instance families.
        
*   GET /api/v1/catalog/{family}
    
    *   Returns sizes available for a given family.
        
*   GET /api/v1/catalog/{family}/{size}
    
    *   Returns metadata + pricing for a specific instance type.
        

**Example Request:**

```
GET /api/v1/catalog/m5
```

**Response:**

```
[
  {"family": "m5", "size": "large", "vcpus": 2, "memory_gb": 8, "price_per_hour": 0.096},
  {"family": "m5", "size": "xlarge", "vcpus": 4, "memory_gb": 16, "price_per_hour": 0.192}
]

```

6\. Edge Cases & Failure Handling
---------------------------------

*   **API Rate Limits** → Implement retries with exponential backoff.
    
*   **Region Mismatches** → Default to us-east-1 if AWS API returns global prices.
    
*   **Currency Differences** → Normalize to USD; support extension for multi-currency later.
    
*   **Data Drift** → Mark last\_updated column, flag stale rows.
    

7\. Best Practices
------------------

*   Sync **weekly** (cost vs. freshness trade-off).
    
*   Cache locally for faster lookups.
    
*   Store **historical catalogs** if needed for auditing past recommendations.
    
*   Add **unit tests** for parsing AWS Pricing API responses.
    

8\. Interview / Onboarding Q&A
------------------------------

1.  **Q:** Why do we need an instance\_catalog table if AWS already provides a Pricing API?**A:** Because the API is slow, rate-limited, and not reliable for real-time lookups during rightsizing.
    
2.  **Q:** What happens if AWS adds a new instance type tomorrow?**A:** The weekly DAG sync will capture it and insert it into our instance\_catalog.
    
3.  **Q:** How is this catalog used in rightsizing?**A:** It provides the “next size down” mapping and price deltas required to compute savings.
    
4.  **Q:** What if the DAG fails mid-run?**A:** The upsert strategy ensures partial failures don’t corrupt existing data.