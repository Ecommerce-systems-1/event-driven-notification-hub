import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os, logging
from app.database import init_db
from app.event_bus import EventBus, bus as _bus_singleton
from app.processor import run_processor
from app.routers import events, notifications
import app.event_bus as event_bus_module

logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    b = EventBus()
    event_bus_module.bus = b
    task = asyncio.create_task(run_processor(b))
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

app = FastAPI(title="Event-Driven Notification Hub", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(events.router)
app.include_router(notifications.router)

@app.get("/health")
def health():
    return {"status": "ok"}

static_dir = "/app/frontend/out"
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")