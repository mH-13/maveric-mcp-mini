# Maveric MCP Mini

Real-time network tower monitoring system using Model Context Protocol (MCP) for intelligent log processing and AI-powered analysis.

## Architecture

```
┌─────────────────┐  MCP Protocol  ┌─────────────────┐  MongoDB Query ┌─────────────────┐
│                 │  (stdio/JSON)  │                 │  (PyMongo)     │                 │
│  Log Generator  │──────────────▶│   MCP Server    │──────────────▶│    MongoDB      │
│                 │                │                 │                │                 │
│ • Simulates     │                │ Tools:          │                │ • Time-series   │
│   cell towers   │                │ • write_logs    │                │   log storage   │
│ • ON/OFF status │                │ • fetch_logs    │                │ • Automatic     │
│ • Batch writes  │                │ • summarize     │                │   indexing      │
└─────────────────┘                └─────────────────┘                └─────────────────┘
                                                 │
                                                 │ API Call
                                                 ▼
                                        ┌─────────────────┐
                                        │   Groq LLM      │
                                        │                 │
                                        │ • Natural lang  │
                                        │   summaries     │
                                        │ • Anomaly det   │
                                        └─────────────────┘
```



## Data Flow

1. **Log Generation**: Simulates cell tower status changes (ON/OFF)
2. **MCP Communication**: Generator calls MCP server tools via stdio protocol
3. **Data Storage**: MCP server writes logs to MongoDB with automatic indexing
4. **Analysis**: Fetch logs and generate AI summaries using Groq LLM
5. **Visualization**: Jupyter notebooks provide analytics dashboards

## Project Structure

```
maveric-mcp-mini/
├── src/
│   ├── common/              # Shared utilities
│   │   ├── db.py            # MongoDB connection & indexing
│   │   └── models.py        # Pydantic data models
│   ├── mcp_server/          # MCP server implementation
│   │   ├── server.py        # FastMCP server with tools
│   │   └── summarizers/     # AI summarization
│   ├── generator/           # Log simulation
│   └── clients/             # Client utilities
├─ enhanced_analytics.ipynb  # Advanced analytics dashboard
├─ simple_analytics.ipynb    # Basic analytics (no pandas)
├─ docker-compose.yml        # MongoDB setup
└─ requirements.txt          # Dependencies
```

## Core Components

### MCP Server
- **FastMCP** framework for tool exposure
- **Tools**: `write_logs`, `fetch_logs`, `summarize_recent`
- **Transport**: stdio protocol for client communication

### Data Models
```python
class CellLog(BaseModel):
    cell_id: int                    # Tower identifier
    status: Literal["ON", "OFF"]    # Current status
    ts: datetime                    # Timestamp (UTC)
    run_id: int                     # Batch identifier
    cluster: Optional[str]          # Geographic cluster
```

### Database
- **MongoDB** for time-series log storage
- **Automatic indexing** on timestamp fields
- **TTL support** for log expiration

## Key Features

- **Real-time Simulation**: Configurable cell tower behavior
- **MCP Protocol**: Modern tool-calling interface  
- **AI Analysis**: Groq LLM for natural language summaries
- **Visual Analytics**: Jupyter dashboards with SLA tracking
- **Scalable Storage**: MongoDB with automatic indexing


See [DEV.md](DEV.md) for complete setup guide.

## License

MIT License - see LICENSE file for details.