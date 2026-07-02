import uuid, time, pytest
from fastapi.testclient import TestClient

@pytest.fixture(autouse=True)
def setup(tmp_path, monkeypatch):
    monkeypatch.setenv("DB_PATH", str(tmp_path / "test.db"))
    import app.database as db_mod
    db_mod.DB_PATH = str(tmp_path / "test.db")
    db_mod.init_db()

@pytest.fixture
def client():
    from app.main import app
    with TestClient(app) as c:
        yield c

def test_publish_event_success(client):
    event_id = str(uuid.uuid4())
    r = client.post("/api/events", json={
        "id": event_id,
        "event_type": "ORDER_PLACED",
        "customer_id": "CUST-001",
        "payload": {"order_id": "ORD-001", "customer_name": "Alice", "total": "49.99"}
    })
    assert r.status_code == 202
    assert r.json()["event_id"] == event_id

def test_duplicate_event_rejected(client):
    event_id = str(uuid.uuid4())
    payload = {"id": event_id, "event_type": "ORDER_PLACED",
               "customer_id": "C1", "payload": {"order_id": "O1"}}
    client.post("/api/events", json=payload)
    r = client.post("/api/events", json=payload)
    assert r.status_code == 409

def test_invalid_event_type_rejected(client):
    r = client.post("/api/events", json={
        "id": str(uuid.uuid4()),
        "event_type": "INVENTED_EVENT",
        "customer_id": "C1",
        "payload": {}
    })
    assert r.status_code == 422

def test_notifications_appear_after_event(client):
    event_id = str(uuid.uuid4())
    client.post("/api/events", json={
        "id": event_id,
        "event_type": "ORDER_PLACED",
        "customer_id": "CUST-002",
        "payload": {"order_id": "ORD-002", "customer_name": "Bob", "total": "99.00"}
    })
    time.sleep(0.3)  # let asyncio processor run
    r = client.get("/api/notifications?customer_id=CUST-002")
    assert r.status_code == 200
    notifs = r.json()
    channels = {n["channel"] for n in notifs}
    assert "EMAIL" in channels
    assert "SMS" in channels
    assert "PUSH" in channels

def test_notification_deduplication(client):
    event_id = str(uuid.uuid4())
    payload = {"id": event_id, "event_type": "ORDER_PLACED",
               "customer_id": "C3", "payload": {"order_id": "O3", "customer_name": "C", "total": "10"}}
    client.post("/api/events", json=payload)
    time.sleep(0.3)
    # Re-process same event manually via processor
    from app.processor import _process
    import asyncio
    asyncio.get_event_loop().run_until_complete(_process({
        "id": event_id, "event_type": "ORDER_PLACED",
        "customer_id": "C3", "payload": {"order_id": "O3"}
    }))
    r = client.get("/api/notifications?customer_id=C3")
    channels = [n["channel"] for n in r.json()]
    # Should not have duplicates
    assert len(channels) == len(set(channels))