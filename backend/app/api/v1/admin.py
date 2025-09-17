from fastapi import APIRouter
from app.core import secrets_manager

router = APIRouter()

@router.post("/reload-secrets")
def reload_secrets():
    secrets_manager.CURRENT_SECRETS = secrets_manager.load_secrets()
    return {"status": "reloaded"}
