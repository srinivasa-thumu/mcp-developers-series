"""A small stdio MCP client for the Part 6 customer lookup server."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Sequence

from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client

SERVER_DIRECTORY = Path(__file__).resolve().parents[1] / "part-06-first-mcp-server"


def create_server_parameters() -> StdioServerParameters:
    """Launch the existing Part 6 server with the client Python environment."""
    return StdioServerParameters(
        command=sys.executable,
        args=["server.py"],
        cwd=str(SERVER_DIRECTORY),
    )


async def interact(customer_id: int) -> tuple[list[types.Tool], types.CallToolResult]:
    """Connect, initialize, discover tools, and call the customer lookup tool."""
    server_parameters = create_server_parameters()

    # These nested contexts close the MCP session and the server subprocess,
    # even when initialization or a tool request raises an exception.
    async with stdio_client(server_parameters) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            tool_response = await session.list_tools()
            available_tools = tool_response.tools
            tool = next((item for item in available_tools if item.name == "get_customer"), None)
            if tool is None:
                raise RuntimeError("The Part 6 server does not provide get_customer.")

            result = await session.call_tool(
                "get_customer", arguments={"customer_id": customer_id}
            )
            return available_tools, result


def print_result(result: types.CallToolResult) -> None:
    """Display structured customer data or a readable MCP tool error."""
    if result.isError:
        messages = [
            block.text for block in result.content if isinstance(block, types.TextContent)
        ]
        detail = " ".join(messages) if messages else "The server returned a tool error."
        print(f"Tool error: {detail}")
        return

    structured = result.structuredContent
    if structured is not None:
        print("Customer details:")
        print(json.dumps(structured, indent=2))
        return

    text_blocks = [block.text for block in result.content if isinstance(block, types.TextContent)]
    print("\n".join(text_blocks) if text_blocks else "Tool returned no displayable content.")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse a customer ID, defaulting to the demonstration customer John."""
    parser = argparse.ArgumentParser(description="Look up a customer through the Part 6 MCP server.")
    parser.add_argument(
        "customer_id",
        nargs="?",
        type=int,
        default=101,
        help="customer ID to look up (default: 101)",
    )
    args = parser.parse_args(argv)
    if args.customer_id <= 0:
        parser.error("customer_id must be a positive integer")
    return args


async def run(customer_id: int) -> None:
    """Run one complete MCP client interaction and display its results."""
    available_tools, result = await interact(customer_id)
    print("Available MCP tools:")
    for tool in available_tools:
        print(f"- {tool.name}: {tool.description or '(no description provided)'}")
    print(f"\nCalling get_customer(customer_id={customer_id})...")
    print_result(result)


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point with friendly errors for launch and protocol failures."""
    args = parse_args(argv)
    try:
        asyncio.run(run(args.customer_id))
    except (OSError, RuntimeError, TimeoutError) as exc:
        print(f"Could not complete the MCP interaction: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


