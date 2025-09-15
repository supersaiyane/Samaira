from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os
import psycopg2
import pandas as pd
import torch
import torch.nn as nn
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error

# =========================
# LSTM Model Definition
# =========================
class LSTMModel(nn.Module):
    def __init__(self, input_dim=1, hidden_dim=50, num_layers=2, output_dim=1):
        super(LSTMModel, self).__init__()
        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers, batch_first=True, dropout=0.2)
        self.fc = nn.Linear(hidden_dim, output_dim)

    def forward(self, x):
        out, _ = self.lstm(x)
        out = self.fc(out[:, -1, :])  # last time step
        return out

# =========================
# DB Connection
# =========================
def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME", "finopsdb"),
        user=os.getenv("DB_USER", "finops"),
        password=os.getenv("DB_PASSWORD", "finops123"),
        host=os.getenv("DB_HOST", "db"),
        port=os.getenv("DB_PORT", "5432"),
    )

# =========================
# Forecasting Logic
# =========================
def run_lstm_forecast():
    conn = get_db_connection()
    query = """
        SELECT usage_date, SUM(cost_amount) as cost
        FROM billing
        GROUP BY usage_date
        ORDER BY usage_date
    """
    df = pd.read_sql(query, conn)

    if df.empty or len(df) < 90:
        print("Not enough data for LSTM.")
        return

    # Scale data
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(df["cost"].values.reshape(-1, 1))

    # Sliding window
    def create_sequences(data, seq_length=30):
        xs, ys = [], []
        for i in range(len(data) - seq_length):
            xs.append(data[i:i+seq_length])
            ys.append(data[i+seq_length])
        return np.array(xs), np.array(ys)

    seq_len = 30
    X, y = create_sequences(scaled, seq_len)
    X_train, X_test = X[:-30], X[-30:]
    y_train, y_test = y[:-30], y[-30:]

    # Convert to torch tensors
    X_train = torch.tensor(X_train, dtype=torch.float32)
    y_train = torch.tensor(y_train, dtype=torch.float32)
    X_test = torch.tensor(X_test, dtype=torch.float32)
    y_test = torch.tensor(y_test, dtype=torch.float32)

    # Model init
    model = LSTMModel()
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    # Training
    model.train()
    for epoch in range(20):  # small epochs for demo
        optimizer.zero_grad()
        outputs = model(X_train)
        loss = criterion(outputs, y_train)
        loss.backward()
        optimizer.step()
        print(f"Epoch {epoch+1}/20, Loss={loss.item():.4f}")

    # Forecast next 30 days
    model.eval()
    preds = []
    last_seq = X[-1]
    with torch.no_grad():
        seq = last_seq.unsqueeze(0)
        for _ in range(30):
            pred = model(seq).item()
            preds.append(pred)
            new_seq = torch.cat((seq[:, 1:, :], torch.tensor([[[pred]]])), dim=1)
            seq = new_seq

    preds = scaler.inverse_transform(np.array(preds).reshape(-1, 1)).flatten()

    # Evaluate
    y_pred = model(X_test).detach().numpy()
    y_true = y_test.numpy()
    mape = mean_absolute_percentage_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))

    # Store in forecasts table
    cursor = conn.cursor()
    for i, val in enumerate(preds):
        forecast_date = (df["usage_date"].max() + timedelta(days=i+1)).date()
        cursor.execute("""
            INSERT INTO forecasts (account_id, service_id, forecast_period_start, forecast_period_end,
                                   forecast_amount, currency, model_used, confidence_interval)
            VALUES (%s, %s, %s, %s, %s, 'USD', %s, %s)
        """, (
            None,  # aggregated forecast (no specific account/service yet)
            None,
            forecast_date,
            forecast_date,
            float(val),
            "LSTM",
            {"mape": float(mape), "rmse": float(rmse)}
        ))
    conn.commit()
    cursor.close()
    conn.close()

# =========================
# DAG Definition
# =========================
default_args = {
    "owner": "finops",
    "depends_on_past": False,
    "email_on_failure": True,
    "email": ["alerts@finops-toolkit.com"],
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="cost_forecasting_lstm",
    default_args=default_args,
    description="LSTM-based cost forecasting (PyTorch)",
    schedule_interval="0 11 * * *",  # daily at 11 AM UTC
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["finops", "forecasting", "lstm"],
) as dag:

    forecast = PythonOperator(
        task_id="run_lstm_forecast",
        python_callable=run_lstm_forecast,
    )
