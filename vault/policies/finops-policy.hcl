# ========================
# Database credentials
# ========================
path "secret/data/db" {
  capabilities = ["read"]
}

# ========================
# AWS credentials
# ========================
path "secret/data/aws" {
  capabilities = ["read"]
}

# ========================
# Webhook URLs (Slack/Teams)
# ========================
path "secret/data/webhooks" {
  capabilities = ["read"]
}

# ========================
# (Optional) Allow listing metadata
# This lets the agent check which keys exist under 'secret/'
# ========================
path "secret/metadata/*" {
  capabilities = ["list"]
}
