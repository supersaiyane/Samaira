# 📘 FinOps Toolkit API Reference

Welcome to the **FinOps Toolkit API v1**.  
All endpoints are prefixed with:

```
/api/v1/
```

---

## 🔹 Accounts

### List Accounts
```
GET /api/v1/accounts/
```

### Get Account
```
GET /api/v1/accounts/{id}
```

### Create Account
```
POST /api/v1/accounts/
```
```json
{
  "cloud_provider": "AWS",
  "account_number": "123456789012",
  "account_name": "Dev Account",
  "owner_email": "dev@example.com"
}
```

### Delete Account
```
DELETE /api/v1/accounts/{id}
```

---

## 🔹 Services

### List Services
```
GET /api/v1/services/
```

### Get Service
```
GET /api/v1/services/{id}
```

### Create Service
```
POST /api/v1/services/
```
```json
{
  "cloud_provider": "AWS",
  "service_code": "AmazonEC2",
  "service_name": "EC2",
  "category": "Compute"
}
```

### Delete Service
```
DELETE /api/v1/services/{id}
```

---

## 🔹 Budgets

### List Budgets
```
GET /api/v1/budgets/
```

### Get Budget
```
GET /api/v1/budgets/{id}
```

### Create Budget
```
POST /api/v1/budgets/
```
```json
{
  "account_id": 1,
  "service_id": 2,
  "budget_name": "Monthly EC2 Budget",
  "budget_limit": 100.0,
  "currency": "USD"
}
```

### Delete Budget
```
DELETE /api/v1/budgets/{id}
```

---

## 🔹 Recommendations

### List Recommendations
```
GET /api/v1/recommendations/?status=pending
```

### Get Recommendation
```
GET /api/v1/recommendations/{id}
```

### Create Recommendation
```
POST /api/v1/recommendations/
```

### Update Recommendation
```
PATCH /api/v1/recommendations/{id}
```
```json
{
  "status": "applied"
}
```

### Delete Recommendation
```
DELETE /api/v1/recommendations/{id}
```

---

## 🔹 Anomalies

### List Anomalies
```
GET /api/v1/anomalies/
```

### Get Anomaly
```
GET /api/v1/anomalies/{id}
```

### Update Anomaly
```
PATCH /api/v1/anomalies/{id}
```
```json
{
  "status": "resolved"
}
```

### Delete Anomaly
```
DELETE /api/v1/anomalies/{id}
```

---

## 🔹 Savings

### List Savings
```
GET /api/v1/savings/
```

### Get Saving
```
GET /api/v1/savings/{id}
```

### Savings Summary
```
GET /api/v1/savings/summary
```

---

## 🔹 Forecasts

### List Forecasts
```
GET /api/v1/forecasts/
```

### Get Forecast
```
GET /api/v1/forecasts/{id}
```

---

## 🔹 Resources

### List Resources
```
GET /api/v1/resources/?account_id=1&region=us-east-1
```

### Get Resource
```
GET /api/v1/resources/{id}
```

### Create Resource
```
POST /api/v1/resources/
```
```json
{
  "account_id": 1,
  "service_id": 2,
  "resource_name": "i-1234567890abcdef",
  "region": "us-east-1",
  "resource_type": "m5.large",
  "tags": { "env": "prod" }
}
```

### Delete Resource
```
DELETE /api/v1/resources/{id}
```

---

## 🔹 Billing

### List Billing
```
GET /api/v1/billing/?account_id=1&start_date=2025-01-01&end_date=2025-01-31
```

### Get Billing
```
GET /api/v1/billing/{id}
```

---

## 🔹 Usage

### List Usage
```
GET /api/v1/usage/?resource_id=1&days=14
```

### Get Usage
```
GET /api/v1/usage/{id}
```

---

## 🔹 Clusters

### List Clusters
```
GET /api/v1/clusters/
```

### Get Cluster
```
GET /api/v1/clusters/{id}
```

### Cluster Resources
```
GET /api/v1/clusters/{id}/resources
```

### Create Cluster
```
POST /api/v1/clusters/
```
```json
{
  "account_id": 1,
  "cluster_name": "eks-prod-cluster",
  "cluster_type": "EKS",
  "region": "us-east-1"
}
```

### Delete Cluster
```
DELETE /api/v1/clusters/{id}
```

---

## 🔹 Logs

### List Logs
```
GET /api/v1/logs/?level=ERROR&component=backend
```

### Get Log
```
GET /api/v1/logs/{id}
```

---

## 🔹 Service Categories

### List Categories
```
GET /api/v1/service-categories/
```

### Get Category
```
GET /api/v1/service-categories/{id}
```

### Create Category
```
POST /api/v1/service-categories/
```
```json
{
  "category_name": "Compute"
}
```

---

## 🔹 Unmapped Services

### List Unmapped Services
```
GET /api/v1/unmapped-services/
```

### Delete Unmapped Service
```
DELETE /api/v1/unmapped-services/{id}
```

---

## 🔹 Instance Catalog

### List Instances
```
GET /api/v1/instance-catalog/?family=m5
```

### Get Instance
```
GET /api/v1/instance-catalog/m5.large
```

---

# ✅ Notes
- All APIs are async and return JSON responses.  
- Swagger UI available at: `http://localhost:8000/docs`  
- ReDoc available at: `http://localhost:8000/redoc`
