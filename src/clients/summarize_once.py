import asyncio, os
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import json 

# Load environment variables
load_dotenv()

def save_summary_to_file(summary: str, stats: str, filename: str = "summary_report.txt"):
    """
    Save the summarized stats and output to a human-readable text file.
    """
    with open(filename, "w") as f:
        f.write(f"Summary Report:\n")
        f.write("=" * 50 + "\n")
        f.write("=== STATS ===\n")
        f.write(f"{stats}\n")
        f.write("=" * 50 + "\n")
        f.write("=== SUMMARY ===\n")
        f.write(f"{summary}\n")
        f.write("=" * 50 + "\n")
    print(f"Summary saved to {filename}")

def save_summary_to_json(summary: str, stats: str, filename: str = "summary_report.json"):
    """
    Save the summarized stats and output to a JSON file.
    """
    data = {
        "stats": stats,
        "summary": summary
    }

    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Summary saved to {filename}")


async def main(minutes: int = 10):
    server = StdioServerParameters(command="python", args=["-m", "src.mcp_server.server"])

    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            res = await session.call_tool(name="summarize_recent", arguments={"minutes": minutes})

            # Handle new MCP response structure
            try:
                if hasattr(res, 'structuredContent') and res.structuredContent:
                    result = res.structuredContent.get('result', {})
                    stats = result.get("stats", "No stats available")
                    summary = result.get("summary", "No summary available")
                else:
                    # Fallback
                    stats = str(res)
                    summary = ""
            except Exception as e:
                stats = f"Error parsing response: {e}"
                summary = ""

            print("\n=== STATS ===\n", stats)
            print("\n=== SUMMARY ===\n", summary)

            # Save the output to text and JSON files
            save_summary_to_file(summary, stats, filename="summarized_report.txt")
            save_summary_to_json(summary, stats, filename="summarized_report.json")


if __name__ == "__main__":
    # Allow overriding minutes via env if you want (optional)
    mins = int(os.getenv("SUMMARY_MINUTES", "10"))
    asyncio.run(main(mins))
