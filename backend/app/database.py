import uuid
import aiosqlite
from typing import List, Dict, Any

class Database:
    def __init__(self, path: str = '/data/15_event_driven_notification_hub.db'):
        self.path = path
        self._conn = None

    async def init(self):
        self._conn = await aiosqlite.connect(self.path)
        self._conn.row_factory = aiosqlite.Row
        await self._conn.execute('PRAGMA journal_mode=WAL')
        await self._conn.executescript('''
            CREATE TABLE IF NOT EXISTS notifications (id TEXT PRIMARY KEY, user_id TEXT NOT NULL, channel TEXT NOT NULL, template_id TEXT NOT NULL, status TEXT DEFAULT 'pending', subject TEXT, body TEXT, created_at TEXT DEFAULT (datetime('now')), sent_at TEXT);
            CREATE TABLE IF NOT EXISTS notification_templates (id TEXT PRIMARY KEY, name TEXT NOT NULL, channel TEXT NOT NULL, subject_template TEXT, body_template TEXT NOT NULL, created_at TEXT DEFAULT (datetime('now')));
        ''')
        await self._conn.commit()

    async def close(self):
        if self._conn:
            await self._conn.close()
