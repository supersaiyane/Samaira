pid_file = "/vault/pidfile"

auto_auth {
  method "approle" {
    mount_path = "auth/approle"
    config = {
      role_id_file_path = "/vault/secrets/role_id"
      secret_id_file_path = "/vault/secrets/secret_id"
    }
  }

  sink "file" {
    config = {
      path = "/vault/secrets/token"
    }
  }
}

template {
  source      = "/vault/templates/db.ctmpl"
  destination = "/vault/secrets/db.env"
}

template {
  source      = "/vault/templates/aws.ctmpl"
  destination = "/vault/secrets/aws.env"
}

template {
  source      = "/vault/templates/webhooks.ctmpl"
  destination = "/vault/secrets/webhooks.env"
}
