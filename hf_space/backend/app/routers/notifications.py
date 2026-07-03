from fastapi import APIRouter
from app.database import get_notifications

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("")
def list_notifications(customer_id: str):
    return get_notifications(customer_id)
