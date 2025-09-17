from app.core.webhook_client import send_slack_message, send_teams_message

def notify_cost_anomaly(summary: str):
    msg = f"⚠️ Cost anomaly detected: {summary}"
    try:
        send_slack_message(msg)
        send_teams_message(msg)
        print("✅ Alert sent to Slack and Teams")
    except Exception as e:
        print(f"❌ Failed to send alert: {e}")
