# Maveric MCP Mini - Setup Guide

Real-time network tower monitoring with AI-powered analysis.

## Requirements

- **Python 3.12.x
- **Docker & Docker Compose**
- **Groq API Key** → [Get free key](https://console.groq.com/)

## Quick Start

### 1. Clone & Setup
```bash
git clone <repo_url>
cd maveric-mcp-mini
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure API Key
```bash
cp .env.example .env
echo "GROQ_API_KEY=your_key_here" >> .env
```

### 3. Start Database
```bash
docker compose up -d
```

### 4. Test Connection
```bash
python -m src.clients.db_ping
# Expected: "Mongo ping: ✅"
```

## Usage

### 3-Terminal Workflow

**Terminal 1: MCP Server**
```bash
python -m src.mcp_server.server
# Waits silently for connections (normal behavior)
```

**Terminal 2: Generate Data**
```bash
# Quick test (2 minutes)
python -m src.generator.generate_logs --cells 8 --interval 1 --iterations 30

# Production demo (5 minutes)
python -m src.generator.generate_logs --cells 12 --interval 2 --iterations 150
```

**Terminal 3: Get AI Analysis**
```bash
python -m src.clients.summarize_once
```

#### *If you follow this far, the project should run and you shoud have a generated summary. Below is some detailed information for better understanding the commands and overall project*

### Parameters

| Flag | Description | Default |
|------|-------------|----------|
| `--cells` | Tower count | 10 |
| `--interval` | Seconds between updates | 3.0 |
| `--iterations` | Update cycles | 10 |
| `--flip-prob` | Status change rate | 0.30 |

### Environment (.env)

```bash
GROQ_API_KEY=your_key_here
MONGO_URI=mongodb://localhost:27017
MONGO_DB=maveric
```

## Analytics

```bash
jupyter notebook
# Open: enhanced_analytics.ipynb
```

**Features**: Time series, heatmaps, SLA tracking, anomaly detection

## Project Structure

```
src/
├── common/          # Database & models
├── mcp_server/      # FastMCP server + AI
├── generator/       # Log simulation
└── clients/         # Test utilities
```

## Testing & Debug

### Verify System Components
```bash
# Test MongoDB connection
python -m src.clients.db_ping

# Test MCP server tools
python -m src.clients.mcp_fetch

# Check database status
docker compose ps
python -c "from src.common.db import get_logs_collection; print(f'Total logs: {get_logs_collection().count_documents({})}')"

# Test MCP connection
python -c "
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test():
    server = StdioServerParameters(command='python', args=['-m', 'src.mcp_server.server'])
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print(f'Available MCP tools: {[t.name for t in tools.tools]}')

asyncio.run(test())
"

# Check recent data availability
python -c "
from src.common.db import get_logs_collection
from datetime import datetime, timedelta, timezone
coll = get_logs_collection()
since = datetime.now(timezone.utc) - timedelta(minutes=30)
count = coll.count_documents({'ts': {'\$gte': since}})
print(f'Logs in last 30min: {count}')
"
```

### Data Generation Scenarios
```bash
# Quick test (30s)
python -m src.generator.generate_logs --cells 8 --interval 1 --iterations 30

# Demo (5min)
python -m src.generator.generate_logs --cells 12 --interval 2 --iterations 150

# Stress test
python -m src.generator.generate_logs --cells 50 --interval 0.5 --iterations 600

# Custom fetch test
python -c "
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def fetch_custom(limit=10, minutes=30):
    server = StdioServerParameters(command='python', args=['-m', 'src.mcp_server.server'])
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            res = await session.call_tool('fetch_logs', {'limit': limit, 'minutes': minutes})
            if hasattr(res, 'structuredContent'):
                result = res.structuredContent.get('result', [])
                print(f'Found {len(result)} logs in last {minutes} minutes')
                for log in result[:3]:
                    print(f'  Cell {log[\"cell_id\"]}: {log[\"status\"]} at {log[\"ts\"]}') 
            else:
                print('No data found')

asyncio.run(fetch_custom(10, 30))
"
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "No data found" | `python -m src.generator.generate_logs --cells 8 --interval 1 --iterations 20` |
| MongoDB down | `docker compose restart mongo` |
| MCP server hung | Restart Terminal 1: `python -m src.mcp_server.server` |
| Groq API error | Check: `echo $GROQ_API_KEY` |
| "Logs: 0" | Generate fresh data |

### Database Operations
```bash
# MongoDB shell access
docker exec -it maveric-mcp-mini-mongo-1 mongosh maveric

# Inside MongoDB shell:
db.cell_logs.stats()                                    # Collection stats
db.cell_logs.count({ts: {$gte: new Date(Date.now() - 3600000)}})  # Recent logs
db.cell_logs.getIndexes()                              # Check indexes
```


**Expected Output**: AI summary with network health status, actionable insights, and visual analytics dashboard.