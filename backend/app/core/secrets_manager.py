import os
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class SecretReloader(FileSystemEventHandler):
    def __init__(self, reload_callback):
        self.reload_callback = reload_callback

    def on_modified(self, event):
        if event.src_path.endswith(".env"):
            print(f"🔄 Secrets updated: {event.src_path}")
            self.reload_callback()

def load_secrets():
    """Load secrets from env into memory."""
    return {
        "DB_USER": os.getenv("DB_USER"),
        "DB_PASSWORD": os.getenv("DB_PASSWORD"),
        "DB_NAME": os.getenv("DB_NAME"),
        "DB_HOST": os.getenv("DB_HOST"),
        "DB_PORT": os.getenv("DB_PORT"),
        "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID"),
        "AWS_SECRET_ACCESS_KEY": os.getenv("AWS_SECRET_ACCESS_KEY"),
        "AWS_REGION": os.getenv("AWS_REGION"),
        "SLACK_WEBHOOK_URL": os.getenv("SLACK_WEBHOOK_URL"),
        "TEAMS_WEBHOOK_URL": os.getenv("TEAMS_WEBHOOK_URL"),
    }

# In-memory cache
CURRENT_SECRETS = load_secrets()

def start_secret_watcher():
    def reload():
        global CURRENT_SECRETS
        CURRENT_SECRETS = load_secrets()

    event_handler = SecretReloader(reload)
    observer = Observer()
    observer.schedule(event_handler, path="/vault/secrets", recursive=False)
    observer_thread = threading.Thread(target=observer.start, daemon=True)
    observer_thread.start()
    print("👀 Secret watcher started on /vault/secrets")
