"""Graph routing tests independent of Ollama and the running MCP server."""

import asyncio

from langchain.messages import AIMessage, ToolMessage
from langchain.tools import tool

from agent import answer, build_graph


class FakeModel:
    def __init__(self, response_factory):
        self.response_factory = response_factory

    def bind_tools(self, tools):
        assert any(item.name == "get_customer" for item in tools)
        return self

    async def ainvoke(self, messages):
        return self.response_factory(messages)


@tool
def get_customer(customer_id: int) -> str:
    """Look up a sample customer by ID."""
    customers = {
        101: "John, john@example.com, Hyderabad",
        102: "Sarah, sarah@example.com, Bangalore",
    }
    if customer_id not in customers:
        return f"Error executing tool get_customer: Customer with ID {customer_id} was not found."
    return customers[customer_id]


def test_tool_result_is_routed_back_to_agent_and_used() -> None:
    def response(messages):
        if not any(isinstance(item, ToolMessage) for item in messages):
            return AIMessage(content="", tool_calls=[{
                "name": "get_customer", "args": {"customer_id": 101}, "id": "lookup-101"
            }])
        assert "John" in str(messages[-1].content)
        return AIMessage(content="Customer 101 is John in Hyderabad.")

    graph = build_graph(FakeModel(response), [get_customer])
    final = asyncio.run(answer(graph, "Get customer 101 details."))
    assert final == "Customer 101 is John in Hyderabad."


def test_customer_102_lookup_uses_the_tool_result() -> None:
    def response(messages):
        if not any(isinstance(item, ToolMessage) for item in messages):
            return AIMessage(content="", tool_calls=[{
                "name": "get_customer", "args": {"customer_id": 102}, "id": "lookup-102"
            }])
        assert "Sarah" in str(messages[-1].content)
        return AIMessage(content="Customer 102 is Sarah in Bangalore.")

    graph = build_graph(FakeModel(response), [get_customer])
    final = asyncio.run(answer(graph, "Find customer 102."))
    assert final == "Customer 102 is Sarah in Bangalore."


def test_general_question_ends_without_a_tool_call() -> None:
    calls = []

    def response(messages):
        calls.append(messages)
        return AIMessage(content="I can look up customers by ID.")

    graph = build_graph(FakeModel(response), [get_customer])
    final = asyncio.run(answer(graph, "What can you help me with?"))
    assert final == "I can look up customers by ID."
    assert len(calls) == 1
    assert not any(isinstance(item, ToolMessage) for item in calls[0])


def test_unknown_customer_tool_result_reaches_agent() -> None:
    def response(messages):
        if not any(isinstance(item, ToolMessage) for item in messages):
            return AIMessage(content="", tool_calls=[{
                "name": "get_customer", "args": {"customer_id": 999}, "id": "lookup-999"
            }])
        assert "not found" in str(messages[-1].content).lower()
        return AIMessage(content="Customer 999 was not found.")

    graph = build_graph(FakeModel(response), [get_customer])
    final = asyncio.run(answer(graph, "Do we have a customer with ID 999?"))
    assert final == "Customer 999 was not found."
