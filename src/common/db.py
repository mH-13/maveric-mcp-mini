from __future__ import annotations
import os
from typing import Optional
from pymongo import MongoClient, ASCENDING
from pymongo.collection import Collection
from datetime import timedelta

def _get_client_uri() -> str:
    return os.getenv("MONGO_URI", "mongodb://localhost:27017")

def get_client() -> MongoClient:
    """
    Create a new MongoClient. In small scripts it's fine to create on demand.
    In long-lived servers, keep one per process.
    """
    return MongoClient(_get_client_uri())

def get_logs_collection(client: Optional[MongoClient] = None) -> Collection:
    """
    Returns the cell_logs collection and ensures indexes exist.
    """
    close_client = False
    if client is None:
        client = get_client()
        close_client = True

    dbname = os.getenv("MONGO_DB", "maveric")
    db = client[dbname]
    coll = db["cell_logs"]

    # Indexes
    coll.create_index([("ts", ASCENDING)], background=True)

    # Optional TTL index if LOG_TTL_DAYS is set
    ttl_days = os.getenv("LOG_TTL_DAYS")
    if ttl_days:
        try:
            seconds = int(float(ttl_days) * 24 * 3600)
            # Mongo requires an index on a single field with expireAfterSeconds
            coll.create_index("ts", expireAfterSeconds=seconds, background=True, name="ts_ttl")
        except Exception:
            # If parsing fails, just skip; user can fix later
            pass

    if close_client:
        client.close()

    return coll

def ping() -> bool:
    """
    Lightweight check the Mongo server is reachable.
    """
    client = get_client()
    try:
        client.admin.command("ping")
        return True
    finally:
        client.close()
