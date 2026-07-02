import asyncio
import pytest
from app.event_bus import EventBus

@pytest.mark.asyncio
async def test_publish_and_consume():
    bus = EventBus()
    event = {"id": "evt-1", "event_type": "ORDER_PLACED", "customer_id": "C1", "payload": {}}
    await bus.publish(event)
    received = await asyncio.wait_for(bus.consume(), timeout=1.0)
    assert received["id"] == "evt-1"

@pytest.mark.asyncio
async def test_queue_size_tracks_pending():
    bus = EventBus()
    await bus.publish({"id": "e1"})
    await bus.publish({"id": "e2"})
    assert bus.pending() == 2