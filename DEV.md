# Development Guide

Complete setup and development guide for the Maveric MCP Mini project.

## Prerequisites

- Python 3.9+
- Docker & Docker Compose
- Groq API key ([Get one here](https://console.groq.com/))

## Initial Setup

### 1. Environment Setup
```bash
git clone <repo_url>
cd maveric-mcp-mini
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configuration
```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

### 3. Start Infrastructure
```bash
docker compose up -d
```

### 4. Verify Setup
```bash
# Test MongoDB connection
python -m src.clients.db_ping

# Should output: "MongoDB connection: OK"
```

## Running the System

### Basic Workflow

**Terminal 1: Start MCP Server**
```bash
python -m src.mcp_server.server
```

**Terminal 2: Generate Data**
```bash
# Basic data generation (12 cells, 30 iterations)
python -m src.generator.generate_logs --cells 12 --interval 2 --iterations 30

# Extended data generation (5 minutes of data)
python -m src.generator.generate_logs --cells 12 --interval 2 --iterations 150

# High-frequency data (1 second intervals)
python -m src.generator.generate_logs --cells 20 --interval 1 --iterations 100
```

**Terminal 3: Get AI Summary**
```bash
python -m src.clients.summarize_once
```

### Generator Parameters

| Parameter | Description | Default | Example |
|-----------|-------------|---------|---------|
| `--cells` | Number of cell towers | 10 | `--cells 20` |
| `--interval` | Seconds between updates | 3.0 | `--interval 1.5` |
| `--iterations` | Number of update cycles | 10 | `--iterations 100` |
| `--flip-prob` | Status change probability | 0.30 | `--flip-prob 0.25` |

### Environment Variables

```bash
# MongoDB Configuration
MONGO_URI=mongodb://localhost:27017
MONGO_DB=maveric
LOG_TTL_DAYS=30                    # Optional: Auto-delete old logs

# Groq LLM Configuration  
GROQ_API_KEY=your_key_here
GROQ_MODEL=llama-3.1-8b-instant

# MCP Server Configuration
MCP_SERVER_NAME=MavericCellMCP
```

## Data Analysis

### Jupyter Notebooks

**Enhanced Analytics**
- Original visualizations
- Time series plots
- Status heatmaps
- Basic statistics
- Color-coded visualizations
- SLA compliance tracking
- Anomaly detection
- Performance insights

### Running Analytics
```bash
# Start Jupyter
jupyter notebook

# Or use Jupyter Lab
jupyter lab

# Open enhanced_analytics.ipynb or simple_analytics.ipynb
```

## Development Commands

### Database Operations
```bash
# Check database status
docker compose ps

# View MongoDB logs
docker compose logs mongo

# Access MongoDB shell
docker exec -it maveric-mcp-mini-mongo-1 mongosh maveric

# Check collection stats
db.cell_logs.stats()

# Count recent logs
db.cell_logs.count({ts: {$gte: new Date(Date.now() - 3600000)}})
```

### MCP Server Testing
```bash
# Test MCP tools directly
python -m src.clients.mcp_fetch

# Test with specific parameters
python -c "
import asyncio
from src.clients.mcp_fetch import main
asyncio.run(main(limit=50, minutes=30))
"
```

### Data Generation Scenarios

**Testing Scenario**
```bash
# Quick test data (30 seconds)
python -m src.generator.generate_logs --cells 8 --interval 1 --iterations 30
```

**Demo Scenario**
```bash
# 5 minutes of realistic data
python -m src.generator.generate_logs --cells 12 --interval 2 --iterations 150 --flip-prob 0.3
```

**Stress Test Scenario**
```bash
# High-frequency data generation
python -m src.generator.generate_logs --cells 50 --interval 0.5 --iterations 600 --flip-prob 0.2
```

## Troubleshooting

### Common Issues

**"No data found in last X minutes"**
```bash
# Solution: Generate fresh data
python -m src.generator.generate_logs --cells 12 --interval 1 --iterations 30
```

**MongoDB Connection Failed**
```bash
# Check if MongoDB is running
docker compose ps mongo

# Restart MongoDB
docker compose restart mongo

# Check logs
docker compose logs mongo
```

**MCP Server Not Responding**
```bash
# Check if server is running in Terminal 1
# Restart server if needed
python -m src.mcp_server.server
```

**Groq API Errors**
```bash
# Verify API key is set
echo $GROQ_API_KEY

# Check .env file
cat .env | grep GROQ_API_KEY
```

### Debug Commands

**Check Data Availability**
```bash
# Quick data check
python -c "
from src.common.db import get_logs_collection
from datetime import datetime, timedelta, timezone
coll = get_logs_collection()
since = datetime.now(timezone.utc) - timedelta(hours=1)
count = coll.count_documents({'ts': {'$gte': since}})
print(f'Logs in last hour: {count}')
"
```

**Test MCP Connection**
```bash
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
            print(f'Available tools: {[t.name for t in tools.tools]}')

asyncio.run(test())
"
```

## Development Workflow

### 1. Start Development Environment
```bash
# Terminal 1: Infrastructure
docker compose up -d

# Terminal 2: MCP Server (keep running)
python -m src.mcp_server.server

# Terminal 3: Development commands
```

### 2. Generate Test Data
```bash
# Generate sample data for testing
python -m src.generator.generate_logs --cells 12 --interval 1 --iterations 60
```

### 3. Test Analytics
```bash
# Open Jupyter and run notebooks
jupyter notebook
# Open simple_analytics.ipynb for enhanced visualizations
```

### 4. Verify AI Summaries
```bash
# Get AI-powered summary
python -m src.clients.summarize_once
```

## Performance Tuning

### MongoDB Optimization
```bash
# Check indexes
db.cell_logs.getIndexes()

# Query performance
db.cell_logs.explain().find({ts: {$gte: new Date(Date.now() - 3600000)}})
```

### Data Generation Optimization
```bash
# Larger batches for better performance
python -m src.generator.generate_logs --cells 50 --interval 0.5 --iterations 1200
```

Keep only:
- `README.md` (project overview)
- `DEV.md` (this development guide)
- `simple_analytics.ipynb` (analytics)
- `enhanced_analytics.ipynb` (Better analytics)