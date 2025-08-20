from __future__ import annotations
import os
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List

from dotenv import load_dotenv
load_dotenv()

from mcp.server.fastmcp import FastMCP
from src.common.db import get_logs_collection
from src.common.models import CellLog
from src.mcp_server.summarizers.groq_llm import summarize_logs_and_tower_info

@dataclass
class AppCtx:
    pass

mcp = FastMCP(os.getenv("MCP_SERVER_NAME", "MavericCellMCP"))

@mcp.tool(title="Write cell logs")
def write_logs(batch: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Insert a batch of cell logs. Each item must fit CellLog schema.
    """
    coll = get_logs_collection()
    docs = [CellLog.model_validate(item).model_dump(mode="python") for item in batch]
    if not docs:
        return {"inserted": 0}
    res = coll.insert_many(docs)
    return {"inserted": len(res.inserted_ids)}

@mcp.tool(title="Fetch recent logs")
def fetch_logs(limit: int = 20, minutes: int = 5) -> List[Dict[str, Any]]:
    """
    Return recent logs since now - minutes, newest first.
    """
    coll = get_logs_collection()
    since = datetime.now(timezone.utc) - timedelta(minutes=minutes)
    cur = coll.find({"ts": {"$gte": since}}).sort("ts", -1).limit(limit)
    out: List[Dict[str, Any]] = []
    for d in cur:
        d["_id"] = str(d["_id"])
        out.append(d)
    return out

@mcp.tool(title="Summarize recent activity")
def summarize_recent(minutes: int = 10) -> Dict[str, Any]:
    """
    Aggregate simple stats for the last N minutes and produce an LLM summary via Groq.
    """
    coll = get_logs_collection()
    since = datetime.now(timezone.utc) - timedelta(minutes=minutes)
    cur = coll.find({"ts": {"$gte": since}})

    logs = []
    total = on = off = 0
    per_cell: Dict[int, Dict[str, int]] = {}

    # Collect logs and aggregate basic counts
    for d in cur:
        logs.append(d)
        total += 1
        s = d["status"]
        on += (s == "ON")
        off += (s == "OFF")
        cid = int(d["cell_id"])
        per_cell.setdefault(cid, {"ON": 0, "OFF": 0})
        per_cell[cid][s] += 1

    # Basic statistics for the window
    lines = [f"Window: last {minutes} min", f"Total events: {total}", f"ON: {on}, OFF: {off}", "Per-cell:"]
    for cid in sorted(per_cell):
        lines.append(f"  cell {cid}: ON={per_cell[cid]['ON']} OFF={per_cell[cid]['OFF']}")
    stats_text = "\n".join(lines)

    # Call Groq to generate natural language summary from stats
    summary = summarize_logs_and_tower_info(logs)  # Clean, natural language summary

    return {"stats": stats_text, "summary": summary}

if __name__ == "__main__":
    mcp.run(transport="stdio")
