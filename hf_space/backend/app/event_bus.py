import asyncio

class EventBus:
    def __init__(self):
        self._queue: asyncio.Queue = asyncio.Queue()

    async def publish(self, event: dict) -> None:
        await self._queue.put(event)

    async def consume(self) -> dict:
        return await self._queue.get()

    def pending(self) -> int:
        return self._queue.qsize()

# Global singleton — initialized in main.py lifespan
bus: EventBus = None  # type: ignore