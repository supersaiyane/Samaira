📌 Overview
-----------

Forecasting predicts **future cloud spend and usage** to enable:

*   **Budget planning** (finance/FinOps).
    
*   **Capacity planning** (engineering).
    
*   **Proactive anomaly detection** (compare forecast vs actual).
    
*   **Commitment planning** (RI / Savings Plans).
    

This project implements **multi-model forecasting** with **Prophet, ARIMA, and SMA**.The system automatically:

*   Trains models on 2 years of billing history.
    
*   Validates accuracy using MAPE & RMSE.
    
*   Picks the best model per service/account.
    
*   Stores forecasts in the forecasts table.
    
*   Notifies teams with summaries.
    

🏗️ Workflow
------------

### 1\. Input Data

*   **Billing Data** (billing table): Daily cost amounts per account/service (2 years lookback).
    
*   **Accounts/Services**: For grouping.
    
*   **Historical anomalies**: Used indirectly for validation.
    

### 2\. Processing Steps

1.  Extract billing history (2 years).
    
2.  Split into **train** (all but last 30 days) and **test** (last 30 days).
    
3.  Train & evaluate 3 models:
    
    *   **Prophet** (trend + seasonality).
        
    *   **ARIMA** (autoregressive + moving average).
        
    *   **SMA** (simple moving average baseline).
        
4.  Compare MAPE (accuracy) & RMSE (error).
    
5.  Select best-performing model.
    
6.  Forecast next **30, 90, 180 days**.
    
7.  Store results in DB with confidence intervals.
    

### 3\. Output

*   **forecasts table**:
    
    *   Forecast amount
        
    *   Horizon (30/90/180 days)
        
    *   Model used
        
    *   Confidence interval JSON (lower, upper, MAPE, RMSE)
        

⚙️ DAG Structure
----------------

*   **Task: generate\_forecasts**
    
    *   Queries billing for last 730 days.
        
    *   Groups by (account\_id, service\_id).
        
    *   Runs forecasting logic.
        
    *   Inserts into forecasts table.
        
    *   Sends summary notifications.
        
*   **Schedule**: Daily at **10:00 UTC**(after anomaly detection at 07:00 UTC and remediation at 08:00 UTC).
    

🧠 Technical Details
--------------------

### 1\. Prophet

*   Captures daily/weekly/yearly seasonality.
    
*   Good for recurring workload costs (e.g., monthly batch jobs).
    

### 2\. ARIMA

*   Works well with autocorrelated series (e.g., steady growth).
    
*   Sensitive to noise.
    

### 3\. SMA (baseline)

*   Uses last 7-day rolling mean.
    
*   Provides fallback if advanced models fail.
    

### 4\. Accuracy Metrics

*   MAPE = mean( | (y\_true - y\_pred) / y\_true | ) × 100Measures relative error %.
    
*   RMSE = sqrt(mean((y\_true - y\_pred)^2))Penalizes large deviations.
    

🛠️ Database Tables
-------------------

### forecasts

| Column                | Type         | Description                           |
|-----------------------|--------------|---------------------------------------|
| forecast_id           | SERIAL PK    | Unique forecast record                |
| account_id            | FK(accounts) | Related account                       |
| service_id            | FK(services) | Related service                       |
| generated_at          | TIMESTAMP    | When generated                        |
| forecast_period_start | DATE         | Start of forecast horizon             |
| forecast_period_end   | DATE         | End of forecast horizon               |
| forecast_amount       | NUMERIC      | Predicted spend                       |
| currency              | VARCHAR      | Default USD                           |
| model_used            | VARCHAR      | Prophet / ARIMA / SMA                 |
| confidence_interval   | JSONB        | Lower/upper bounds + accuracy metrics |

📊 Example Forecast Entry
-------------------------

```
{
  "forecast_id": 520,
  "account_id": 12,
  "service_id": 2,
  "generated_at": "2025-09-13T10:00:00Z",
  "forecast_period_start": "2025-09-14",
  "forecast_period_end": "2025-10-14",
  "forecast_amount": 12450.75,
  "currency": "USD",
  "model_used": "Prophet",
  "confidence_interval": {
    "lower": 11800.12,
    "upper": 13120.45,
    "mape": 4.2,
    "rmse": 320.55
  }
}



```

🔔 Notifications
----------------

*   📈 Forecasts Generated:- Account 12, Service EC2: $12,450 | Model=Prophet, MAPE=4.2- Account 12, Service S3: $1,980 | Model=ARIMA, MAPE=6.5
    
*   **Teams**: Card summary with top 10 forecasts.
    

✅ Key Benefits
--------------

*   Improves **budget accuracy** (forecasts next quarter spend).
    
*   Helps identify **commitment opportunities** (e.g., RIs, SPs).
    
*   Flags **forecast drift anomalies** if actuals deviate.
    
*   Provides **confidence intervals** for risk management.
    

❓ Review Questions
------------------

1.  Which 3 models are used for forecasting and why?
    
2.  How does the DAG select the “best” model?
    
3.  What’s the difference between **MAPE** and **RMSE**?
    
4.  How are forecasts stored in the database (which fields)?
    
5.  Why is forecasting scheduled at **10:00 UTC**?