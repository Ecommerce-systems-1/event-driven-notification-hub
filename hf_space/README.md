---
title: Event-Driven Notification Hub
emoji: 📣
colorFrom: yellow
colorTo: gray
sdk: docker
app_port: 7860
pinned: false
---

# Event-Driven Notification Hub

Publish order events; an async processor fans each one out to EMAIL, SMS, and PUSH notifications with idempotent dedup.

The landing page is an interactive API console — click any endpoint to call the live API.

## API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/api/events` | Publish an event (202) |
| GET | `/api/events` | Recent events |
| GET | `/api/notifications?customer_id=X` | Notifications for a customer |

## Stack

Python 3.11 · FastAPI · SQLite · Pydantic v2 · Next.js 14 (static export) · Tailwind CSS · Docker
