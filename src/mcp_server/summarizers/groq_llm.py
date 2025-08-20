from __future__ import annotations
import os
from groq import Groq

def summarize_logs_and_tower_info(logs: list) -> str:
    """
    Uses Groq API to produce a natural language summary of logs, including
    tower (cell) information and any notable events (e.g., status changes).
    """
    # Group by cell_id for better readability
    towers_info = {}
    for log in logs:
        cid = log["cell_id"]
        if cid not in towers_info:
            towers_info[cid] = {"on": 0, "off": 0, "last_status": "", "cluster": log["cluster"]}
        
        status = log["status"]
        towers_info[cid][status] += 1
        towers_info[cid]["last_status"] = status
    
    # Prepare the log summary and tower info
    summary = "Tower Status Summary:\n"
    for cid, info in towers_info.items():
        summary += f"\n- **Tower {cid}** (Cluster: {info['cluster'] or 'N/A'}):\n"
        summary += f"  - ON: {info['on']} times\n"
        summary += f"  - OFF: {info['off']} times\n"
        summary += f"  - Last Status: {info['last_status']}\n"
    
    # Generate natural language text using Groq model
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "[LLM unavailable] GROQ_API_KEY not set"
    
    model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    prompt = (
        "You are an SRE assistant. Provide a concise natural language summary of the following log data.\n"
        "In your summary, include the ON/OFF events and last known status for each tower (cell_id).\n"
        f"LOGS:\n{summary}\n\n"
        "Return your summary as bullet points, highlighting any anomalies, especially extended downtimes or frequent flips."
    )
    
    client = Groq(api_key=api_key)
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=500,
    )
    
    return resp.choices[0].message.content.strip()
