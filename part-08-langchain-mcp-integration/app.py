"""Discover and invoke Part 6 MCP tools through LangChain's MCPAdapter."""
from __future__ import annotations

import asyncio
import json
import shutil
import sys
from pathlib import Path
from typing import Any

from fastmcp import Client
from fastmcp.client.transports import StdioTransport
from langchain_core.tools import BaseTool, ToolException
from langchain.mcp import MCPAdapter

SERVER_DIRECTORY = Path(__file__).resolve().parents[1] / "part-06-first-mcp-server"
SERVER_SCRIPT = SERVER_DIRECTORY / "server.py"


def create_mcp_client() -> Client:
    """Run Part 6 with its own locked dependencies through a stdio transport."""
    transport = StdioTransport(
        command=shutil.which("uv") or "uv",
        args=["run", "--directory", str(SERVER_DIRECTORY), "python", "server.py"],
        cwd=str(SERVER_DIRECTORY),
    )
    # Part 6 uses MCP SDK 1.x and the legacy initialize/list-tools protocol.
    return Client(transport, mode="legacy")


def describe_tool(tool: BaseTool) -> str:
    """Display the server-derived schema and tool description."""
    schema = tool.args_schema if isinstance(tool.args_schema, dict) else (
        tool.args_schema.model_json_schema() if tool.args_schema else {}
    )
    arguments = ", ".join(
        f"{name}: {field.get('type', 'unknown')}"
        for name, field in schema.get("properties", {}).items()
    )
    return f"{tool.name}({arguments}): {tool.description or '(no description provided)'}"


def tool_error_message(result: Any) -> str | None:
    """Return an MCP execution error found in an invocation result or exception."""
    mcp_result = getattr(result, "result", result)
    content = getattr(mcp_result, "content", mcp_result if isinstance(mcp_result, list) else [])
    texts: list[str] = []
    for item in content:
        value = item.get("text") if isinstance(item, dict) else getattr(item, "text", None)
        if isinstance(value, str):
            texts.append(value)
    for value in texts:
        if value.startswith("Error executing tool "):
            return value.partition(": ")[2] or value
    if isinstance(result, ToolException):
        return str(result)
    return None


def display_result(customer_id: int, result: Any) -> None:
    """Print structured customer data or a server-reported error."""
    error = tool_error_message(result)
    if error:
        print(f"Customer lookup error: {error}")
        return

    print(f"Customer {customer_id}:")
    content = getattr(result, "content", result)
    if isinstance(content, list):
        texts = [
            item.get("text") if isinstance(item, dict) else getattr(item, "text", None)
            for item in content
        ]
        texts = [text for text in texts if isinstance(text, str)]
        if len(texts) == 1:
            try:
                print(json.dumps(json.loads(texts[0]), indent=2))
                return
            except json.JSONDecodeError:
                print(texts[0])
                return
    print(json.dumps(result, indent=2) if isinstance(result, (dict, list)) else result)


async def run_demo() -> None:
    """Discover and invoke the actual Part 6 tool for IDs 101, 102, and 999."""
    if not SERVER_SCRIPT.is_file():
        raise FileNotFoundError(f"Part 6 server was not found: {SERVER_SCRIPT}")

    async with MCPAdapter(create_mcp_client()) as adapter:
        tools = await adapter.list_tools()
        print("Available LangChain tools adapted from MCP:")
        for tool in tools:
            print(f"- {describe_tool(tool)}")

        customer_tool = next((tool for tool in tools if tool.name == "get_customer"), None)
        if customer_tool is None:
            raise RuntimeError("The Part 6 MCP server did not advertise get_customer.")

        for customer_id in (101, 102, 999):
            print(f"\nInvoking discovered get_customer with customer_id={customer_id}...")
            try:
                result = await customer_tool.ainvoke({"customer_id": customer_id})
            except ToolException as exc:
                display_result(customer_id, exc)
            else:
                display_result(customer_id, result)


def main() -> int:
    """Run the demo and report connection failures clearly."""
    try:
        asyncio.run(run_demo())
    except (OSError, RuntimeError, TimeoutError) as exc:
        print(f"Could not complete the LangChain MCP demo: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
