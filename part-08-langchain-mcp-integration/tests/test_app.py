"""Integration tests for LangChain MCPAdapter and the existing Part 6 server."""
import asyncio

from fastmcp import Client
from langchain_core.tools import BaseTool
from langchain.mcp import MCPAdapter

from app import SERVER_SCRIPT, create_mcp_client, run_demo, tool_error_message


def test_part6_server_and_transport_configuration() -> None:
    """The stdio transport targets the unchanged Part 6 server."""
    assert SERVER_SCRIPT.is_file()
    assert SERVER_SCRIPT.parent.name == "part-06-first-mcp-server"
    assert isinstance(create_mcp_client(), Client)


def test_discovery_schema_invocations_and_cleanup() -> None:
    """Verify discovery, adapted calls, server errors, and adapter cleanup."""
    async def exercise() -> tuple[list[BaseTool], object, object, object]:
        async with MCPAdapter(create_mcp_client()) as adapter:
            tools = await adapter.list_tools()
            tool = next(item for item in tools if item.name == "get_customer")
            schema = tool.args_schema if isinstance(tool.args_schema, dict) else (
                tool.args_schema.model_json_schema()
            )
            assert schema["properties"]["customer_id"]["type"] == "integer"
            john = await tool.ainvoke({"customer_id": 101})
            sarah = await tool.ainvoke({"customer_id": 102})
            unknown = await tool.ainvoke({"customer_id": 999})
            return tools, john, sarah, unknown

    tools, john, sarah, unknown = asyncio.run(exercise())
    assert any(tool.name == "get_customer" for tool in tools)
    assert "John" in str(john) and "john@example.com" in str(john)
    assert "Sarah" in str(sarah) and "sarah@example.com" in str(sarah)
    assert "Customer with ID 999 was not found." in (tool_error_message(unknown) or "")


def test_demo_displays_all_scenarios(capfd) -> None:
    """Check discovery and displayed success/error results from the runnable demo."""
    asyncio.run(run_demo())
    output = capfd.readouterr().out
    assert "get_customer(customer_id: integer)" in output
    assert '"name": "John"' in output and '"name": "Sarah"' in output
    assert "Customer lookup error: Customer with ID 999 was not found." in output
