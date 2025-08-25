from __future__ import annotations
import os
from groq import Groq

def summarize_logs_and_tower_info(logs: list) -> str:
    """
    Uses Groq API to produce a clean, actionable summary of tower status.
    """
    if not logs:
        return "No recent tower activity to analyze."
    
    # Analyze tower data
    towers_info = {}
    for log in logs:
        cid = log["cell_id"]
        if cid not in towers_info:
            towers_info[cid] = {"on": 0, "off": 0, "last_status": ""}
        
        status = log["status"]
        towers_info[cid][status.lower()] = towers_info[cid].get(status.lower(), 0) + 1
        towers_info[cid]["last_status"] = status
    
    # Calculate metrics
    total_towers = len(towers_info)
    online_towers = sum(1 for info in towers_info.values() if info["last_status"] == "ON")
    offline_towers = total_towers - online_towers
    
    # Identify issues
    critical_towers = []
    unstable_towers = []
    
    for cid, info in towers_info.items():
        on_count = info.get('on', 0)
        off_count = info.get('off', 0)
        total_events = on_count + off_count
        
        # Critical: Currently offline
        if info["last_status"] == "OFF":
            critical_towers.append(cid)
        
        # Unstable: High flip rate (>50% of events are status changes)
        if total_events > 10 and off_count > on_count * 1.5:
            unstable_towers.append(cid)
    
    # Generate structured summary
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "[LLM unavailable] GROQ_API_KEY not set"
    
    model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    
    # Create structured data for LLM
    data_summary = f"""NETWORK STATUS OVERVIEW:
- Total Towers: {total_towers}
- Online: {online_towers} ({online_towers/total_towers*100:.1f}%)
- Offline: {offline_towers} ({offline_towers/total_towers*100:.1f}%)
- Critical (Offline): {critical_towers}
- Unstable (High downtime): {unstable_towers}

TOWER DETAILS:
"""
    
    for cid in sorted(towers_info.keys()):
        info = towers_info[cid]
        on_count = info.get('on', 0)
        off_count = info.get('off', 0)
        status = info["last_status"]
        uptime = on_count / (on_count + off_count) * 100 if (on_count + off_count) > 0 else 0
        data_summary += f"Tower {cid}: {status} (Uptime: {uptime:.1f}%, Events: {on_count + off_count})\n"
    
    prompt = f"""You are a network operations assistant. Create a clear, actionable summary from this tower monitoring data.

Format your response EXACTLY like this:

🟢 NETWORK HEALTH: [Overall status - Good/Warning/Critical]

📊 QUICK STATS:
• [Key metric 1]
• [Key metric 2] 
• [Key metric 3]

🚨 IMMEDIATE ACTIONS:
• [Action item 1 if any issues]
• [Action item 2 if any issues]
(Or "None required" if all good)

⚠️ MONITORING FOCUS:
• [Tower(s) to watch]
• [Reason why]

DATA:
{data_summary}

Keep it concise and actionable. Focus on what operators need to know and do."""
    
    try:
        client = Groq(api_key=api_key)
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=400,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        # Fallback summary when Groq API fails
        status = "Critical" if offline_towers > 0 else "Warning" if unstable_towers else "Good"
        
        fallback = f"""🟢 NETWORK HEALTH: {status}

📊 QUICK STATS:
• Total Towers: {total_towers}
• Online: {online_towers} ({online_towers/total_towers*100:.1f}%)
• Offline: {offline_towers} towers

🚨 IMMEDIATE ACTIONS:
"""
        
        if critical_towers:
            fallback += f"• Investigate offline towers: {', '.join(map(str, critical_towers))}\n"
        if unstable_towers:
            fallback += f"• Check unstable towers: {', '.join(map(str, unstable_towers))}\n"
        if not critical_towers and not unstable_towers:
            fallback += "• None required\n"
            
        fallback += f"\n⚠️ MONITORING FOCUS:\n"
        if critical_towers or unstable_towers:
            focus_towers = list(set(critical_towers + unstable_towers))
            fallback += f"• Towers {', '.join(map(str, focus_towers))}\n• High downtime or currently offline\n"
        else:
            fallback += "• All towers operating normally\n• Continue routine monitoring\n"
            
        fallback += f"\n[Note: AI analysis unavailable - {str(e)[:50]}...]"
        return fallback
