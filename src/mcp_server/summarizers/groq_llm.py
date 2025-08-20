from __future__ import annotations
import os
from groq import Groq

def summarize_with_groq(stats_text: str) -> str:
    """
    Uses Groq chat API to produce a short SRE-style summary from stats text.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "[LLM unavailable] GROQ_API_KEY not set"

    model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    prompt = (
        "You are an SRE assistant. Given ON/OFF telemetry stats, write a concise ops summary.\n"
        "If there are anomalies (frequent flips, extended OFF durations, affected cells), call them out.\n\n"
        f"STATS:\n{stats_text}\n\n"
        "Return 4–7 bullet points."
    )

    client = Groq(api_key=api_key)
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=500,
    )
    return resp.choices[0].message.content.strip()
