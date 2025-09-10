import os, requests, json

async def send_slack_message(message: str):
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if webhook_url:
        payload = {"text": message}
        requests.post(webhook_url, data=json.dumps(payload), headers={"Content-Type": "application/json"})

async def send_teams_message(message: str):
    webhook_url = os.getenv("TEAMS_WEBHOOK_URL")
    if webhook_url:
        payload = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "summary": "FinOps Notification",
            "themeColor": "0072C6",
            "title": "🔔 FinOps Notification",
            "text": message,
        }
        requests.post(webhook_url, data=json.dumps(payload), headers={"Content-Type": "application/json"})
