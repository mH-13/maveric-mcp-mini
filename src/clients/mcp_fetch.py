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

            # Different SDK versions return structured results slightly differently.
            # Most expose a .result dict:
            try:
                print(res.result)  # may be a list of docs
            except AttributeError:
                # Fallback: print raw object
                print(res)

if __name__ == "__main__":
    asyncio.run(main())
