import asyncio
from dotenv import load_dotenv
load_dotenv()

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    # Run the server as a module so imports resolve (src/ layout)
    server = StdioServerParameters(command="python", args=["-m", "src.mcp_server.server"])

    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            res = await session.call_tool(name="fetch_logs", arguments={"limit": 5, "minutes": 10})

            # Handle MCP response structure
            try:
                if hasattr(res, 'structuredContent') and res.structuredContent:
                    result = res.structuredContent.get('result', [])
                    print(f"Found {len(result)} recent logs:")
                    for log in result:
                        print(f"  Cell {log['cell_id']}: {log['status']} at {log['ts']}")
                else:
                    print("No structured result found")
                    print(res)
            except Exception as e:
                print(f"Error parsing response: {e}")
                print(res)

if __name__ == "__main__":
    asyncio.run(main())
