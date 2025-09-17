#!/bin/bash
set -e

VAULT_ADDR=http://127.0.0.1:8200
VAULT_TOKEN=root   # dev token (replace if using real setup)

export VAULT_ADDR
export VAULT_TOKEN

echo "⏳ Enabling KV v2..."
vault secrets enable -version=2 -path=secret kv || true

echo "🔑 Writing sample secrets..."
vault kv put secret/db DB_USER=finops DB_PASSWORD=finops123 DB_NAME=finopsdb DB_HOST=db DB_PORT=5432
vault kv put secret/aws AWS_ACCESS_KEY_ID=dummy AWS_SECRET_ACCESS_KEY=dummy AWS_REGION=us-east-1
vault kv put secret/webhooks SLACK_WEBHOOK_URL=https://hooks.slack.com/services/XXX TEAMS_WEBHOOK_URL=https://outlook.office.com/webhook/XXX

echo "📜 Writing policy..."
vault policy write finops-policy /vault/policies/finops-policy.hcl

echo "👤 Enabling AppRole auth..."
vault auth enable approle || true

echo "🔗 Creating AppRole..."
vault write auth/approle/role/finops-role \
    token_policies="finops-policy" \
    secret_id_ttl=2h \
    token_ttl=1h \
    token_max_ttl=4h

APPROLE_ID=$(vault read -field=role_id auth/approle/role/finops-role/role-id)
SECRET_ID=$(vault write -field=secret_id -f auth/approle/role/finops-role/secret-id)

echo "✅ AppRole created!"
echo "ROLE_ID=$APPROLE_ID"
echo "SECRET_ID=$SECRET_ID"

# Save to vault/secrets so Vault Agent can read them
mkdir -p /vault/secrets
echo "$APPROLE_ID" > /vault/secrets/role_id
echo "$SECRET_ID" > /vault/secrets/secret_id

# Also export to .env for Docker Compose (optional, useful in dev)
echo "VAULT_ROLE_ID=$APPROLE_ID" >> ../.env
echo "VAULT_SECRET_ID=$SECRET_ID" >> ../.env
