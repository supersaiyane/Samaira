import requests
from app.core.secrets_manager import CURRENT_SECRETS

def send_slack_message(message: str):
    """Send a message to Slack using the current webhook URL."""
    webhook = CURRENT_SECRETS.get("SLACK_WEBHOOK_URL")
    if not webhook:
        raise RuntimeError("🚨 Slack webhook not configured in secrets")
    resp = requests.post(webhook, json={"text": message})
    if resp.status_code != 200:
        raise RuntimeError(f"Slack error {resp.status_code}: {resp.text}")
    return resp.status_code

def send_teams_message(message: str):
    """Send a message to Microsoft Teams using the current webhook URL."""
    webhook = CURRENT_SECRETS.get("TEAMS_WEBHOOK_URL")
    if not webhook:
        raise RuntimeError("🚨 Teams webhook not configured in secrets")
    resp = requests.post(webhook, json={"text": message})
    if resp.status_code != 200:
        raise RuntimeError(f"Teams error {resp.status_code}: {resp.text}")
    return resp.status_code
