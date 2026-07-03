from datetime import datetime
from fastapi import APIRouter, HTTPException
from app.models import EventPublish, EventPublishResponse
from app.database import insert_event, get_recent_events
import app.event_bus as bus_module
import sqlite3

router = APIRouter(prefix="/api/events", tags=["events"])
VALID_TYPES = {"ORDER_PLACED","PAYMENT_CAPTURED","ORDER_SHIPPED","DELIVERY_CONFIRMED","RETURN_REQUESTED"}

@router.post("", status_code=202, response_model=EventPublishResponse)
async def publish_event(payload: EventPublish):
    if payload.event_type not in VALID_TYPES:
        raise HTTPException(422, f"Unknown event_type: {payload.event_type}")
    now = datetime.utcnow().isoformat()
    try:
        insert_event(payload.id, payload.event_type, payload.payload, payload.customer_id, now)
    except sqlite3.IntegrityError:
        raise HTTPException(409, f"Event {payload.id} already exists")
    await bus_module.bus.publish({
        "id": payload.id, "event_type": payload.event_type,
        "customer_id": payload.customer_id, "payload": payload.payload, "published_at": now
    })
    return {"event_id": payload.id, "status": "QUEUED", "published_at": now}

@router.get("")
def list_events(limit: int = 50):
    return get_recent_events(limit)