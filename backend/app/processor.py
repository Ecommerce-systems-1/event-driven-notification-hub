import asyncio, json, logging
from datetime import datetime
from app.database import load_rules, insert_notification
from app.templates import render_template

logger = logging.getLogger(__name__)

async def run_processor(bus) -> None:
    logger.info("Event processor started")
    while True:
        try:
            event = await bus.consume()
            await _process(event)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Processor error: {e}")

async def _process(event: dict) -> None:
    rules = load_rules(event["event_type"])
    payload = event.get("payload", {})
    if isinstance(payload, str):
        payload = json.loads(payload)
    payload["customer_id"] = event["customer_id"]
    now = datetime.utcnow().isoformat()
    for rule in rules:
        body = render_template(rule["template_id"], payload)
        insert_notification(
            event["id"], rule["channel"], event["customer_id"],
            rule["template_id"], body, now
        )
    logger.info(f"Processed {event['event_type']} → {len(rules)} notifications")