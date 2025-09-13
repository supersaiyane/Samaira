# Allow FinOps app read-only access to specific secrets
path "secret/data/db" {
  capabilities = ["read"]
}

path "secret/data/aws" {
  capabilities = ["read"]
}

path "secret/data/webhooks" {
  capabilities = ["read"]
}
