import asyncio, random, argparse, sys
from datetime import datetime, timezone
from dotenv import load_dotenv
load_dotenv()

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run(cell_count: int, interval_sec: float, iterations: int, flip_prob: float):
    # Launch the MCP server as a module (works with src/ layout)
    # Suppress server debug output by redirecting stderr to devnull
    server = StdioServerParameters(
        command="python", 
        args=["-m", "src.mcp_server.server"],
        env={"PYTHONUNBUFFERED": "1"}
    )

    # Track current ON/OFF state per cell
    states = {i: "OFF" for i in range(1, cell_count + 1)}
    run_id = 0

    print(f"Starting log generation: {cell_count} cells, {iterations} iterations")
    
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            for _ in range(iterations):
                run_id += 1
                # Flip ~flip_prob of cells
                for cid in range(1, cell_count + 1):
                    if random.random() < flip_prob:
                        states[cid] = "ON" if states[cid] == "OFF" else "OFF"

                now = datetime.now(timezone.utc).isoformat()
                batch = [
                    {"cell_id": cid, "status": states[cid], "ts": now, "run_id": run_id}
                    for cid in range(1, cell_count + 1)
                ]

                res = await session.call_tool(name="write_logs", arguments={"batch": batch})
                # Clean output - just show progress
                try:
                    # Handle new MCP response structure
                    if hasattr(res, 'structuredContent') and res.structuredContent:
                        inserted = res.structuredContent.get('result', {}).get('inserted', 0)
                    else:
                        inserted = len(batch)  # fallback
                    print(f"Run {run_id:3d}: {inserted} logs inserted", flush=True)
                except Exception as e:
                    print(f"Run {run_id:3d}: {len(batch)} logs (status unknown)", flush=True)

                await asyncio.sleep(interval_sec)
            
            print(f"\nCompleted: {iterations} iterations, {iterations * cell_count} total logs")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Generate cell ON/OFF logs via MCP.")
    ap.add_argument("--cells", type=int, default=10, help="number of cells")
    ap.add_argument("--interval", type=float, default=3.0, help="seconds between ticks")
    ap.add_argument("--iterations", type=int, default=10, help="number of ticks to generate")
    ap.add_argument("--flip-prob", type=float, default=0.30, help="probability each cell flips per tick")
    args = ap.parse_args()

    asyncio.run(run(args.cells, args.interval, args.iterations, args.flip_prob))
