# Maveric MCP Mini

Simulate **cell/tower ON/OFF** logs, ingest them via an **MCP server** into **MongoDB**, and summarize recent activity using an **LLM on Groq**.

## Why this exists
- **MCP** standardizes how clients call tools (e.g., `write_logs`, `summarize_recent`) without bespoke glue.
- **MongoDB** gives simple, flexible NoSQL storage with time-based queries.
- **Groq** provides fast, cost-effective inference (e.g., `llama-3.1-8b-instant`).

## Architecture

[Generator] → (MCP tool call) → [MCP Server] → [MongoDB]
└─> [Groq LLM] for summaries
