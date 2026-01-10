from fastapi import APIRouter

router = APIRouter()

@router.get("/clients")
def list_clients():
    # Mocked for demo purposes
    return {
        "clients": ["client_001", "client_002"]
    }