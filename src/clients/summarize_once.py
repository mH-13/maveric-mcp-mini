import asyncio, os
from dotenv import load_dotenv
load_dotenv()

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main(minutes: int = 10):
    server = StdioServerParameters(command="python", args=["-m", "src.mcp_server.server"])

    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            res = await session.call_tool(name="summarize_recent", arguments={"minutes": minutes})

            # Try common response shape
            try:
                stats = res.result.get("stats")
                summary = res.result.get("summary")
            except Exception:
                # Fallback for other shapes
                stats = str(res)
                summary = ""

            print("\n=== STATS ===\n", stats)
            print("\n=== SUMMARY ===\n", summary)

if __name__ == "__main__":
    # Allow overriding minutes via env if you want (optional)
    mins = int(os.getenv("SUMMARY_MINUTES", "10"))
    asyncio.run(main(mins))
