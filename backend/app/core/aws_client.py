import boto3
import threading
import time
from app.core.secrets_manager import CURRENT_SECRETS

_aws_clients = {}
_lock = threading.Lock()

def get_aws_client(service_name: str):
    """Get or refresh a boto3 client for the given service."""
    global _aws_clients

    creds = (
        CURRENT_SECRETS.get("AWS_ACCESS_KEY_ID"),
        CURRENT_SECRETS.get("AWS_SECRET_ACCESS_KEY"),
        CURRENT_SECRETS.get("AWS_REGION"),
    )

    client_key = (service_name, creds)

    with _lock:
        # If no client exists OR creds changed → rebuild client
        if service_name not in _aws_clients or _aws_clients[service_name]["creds"] != creds:
            print(f"🔄 Refreshing AWS client for {service_name}")
            client = boto3.client(
                service_name,
                aws_access_key_id=creds[0],
                aws_secret_access_key=creds[1],
                region_name=creds[2],
            )
            _aws_clients[service_name] = {"client": client, "creds": creds}

        return _aws_clients[service_name]["client"]

def s3_client():
    return get_aws_client("s3")

def lambda_client():
    return get_aws_client("lambda")

def dynamodb_client():
    return get_aws_client("dynamodb")

def refresh_aws_clients_periodically(interval: int = 60):
    """Background loop that refreshes AWS clients when secrets rotate."""
    def loop():
        while True:
            with _lock:
                for service in list(_aws_clients.keys()):
                    get_aws_client(service)  # will rebuild if creds changed
            time.sleep(interval)

    t = threading.Thread(target=loop, daemon=True)
    t.start()
    print("👀 AWS client watcher started")
