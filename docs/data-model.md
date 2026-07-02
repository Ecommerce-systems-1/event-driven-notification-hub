# Data Model — Event-Driven Notification Hub

```sql
CREATE TABLE IF NOT EXISTS notifications (id TEXT PRIMARY KEY, user_id TEXT NOT NULL, channel TEXT NOT NULL, template_id TEXT NOT NULL, status TEXT DEFAULT 'pending', subject TEXT, body TEXT, created_at TEXT DEFAULT (datetime('now')), sent_at TEXT);
```
