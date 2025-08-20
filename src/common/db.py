from __future__ import annotations
import os
from typing import Optional
from pymongo import MongoClient, ASCENDING
from pymongo.collection import Collection

# Module-level singleton client for reuse
_client: Optional[MongoClient] = None

def _mongo_uri() -> str:
    return os.getenv("MONGO_URI", "mongodb://localhost:27017")

def get_client() -> MongoClient:
    global _client
    if _client is None:
        _client = MongoClient(_mongo_uri())
    return _client

def get_logs_collection() -> Collection:
    client = get_client()
    dbname = os.getenv("MONGO_DB", "maveric")
    db = client[dbname]
    coll = db["cell_logs"]

    # Index for time-based queries
    coll.create_index([("ts", ASCENDING)], background=True)

    # Optional TTL index if LOG_TTL_DAYS is set
    ttl_days = (os.getenv("LOG_TTL_DAYS") or "").strip()
    if ttl_days:
        try:
            seconds = int(float(ttl_days) * 24 * 3600)
            # Single-field TTL index required by Mongo
            coll.create_index("ts", expireAfterSeconds=seconds, name="ts_ttl", background=True)
        except Exception:
            pass  # ignore misconfig; you can fix the env later

    return coll

def ping() -> bool:
    try:
        get_client().admin.command("ping")
        return True
    except Exception:
        return False
