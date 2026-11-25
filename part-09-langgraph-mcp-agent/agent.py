"""Customer assistant that uses the existing Part 6 MCP tool through Part 8."""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path
from typing import Sequence

from langchain.messages import HumanMessage, SystemMessage
from langchain.mcp import MCPAdapter
from langchain_ollama import ChatOllama
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition


PART_08_DIRECTORY = Path(__file__).resolve().parents[1] / "part-08-langchain-mcp-integration"
if not PART_08_DIRECTORY.is_dir():
    raise RuntimeError(f"Part 8 integration was not found: {PART_08_DIRECTORY}")
sys.path.insert(0, str(PART_08_DIRECTORY))
try:
    # Reuse Part 8's stdio transport. It runs Part 6 with its own locked
    # environment, keeping the MCP SDK 1.x dependency isolated there.
    from app import create_mcp_client
finally:
    sys.path.pop(0)


SYSTEM_PROMPT = """You are a customer assistant. Answer clearly and briefly.
Use get_customer whenever a user asks about a customer by ID or asks if an ID
exists. Never guess customer records. Base customer answers on the tool result.
If the tool says a customer was not found, explain that plainly. Answer general
questions without calling the customer lookup tool. Describe only the customer
lookup capability; do not claim access to accounts or other banking systems."""


def build_graph(model: ChatOllama, tools: list):
    """Build an agent/tool loop using MCP-discovered LangChain tools."""
    if not any(tool.name == "get_customer" for tool in tools):
        raise RuntimeError("The Part 6 MCP server did not advertise get_customer.")

    model_with_tools = model.bind_tools(tools)

    async def agent_node(state: MessagesState) -> dict:
        response = await model_with_tools.ainvoke(state["messages"])
        return {"messages": [response]}

    graph = StateGraph(MessagesState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode(tools))
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", tools_condition, {"tools": "tools", END: END})
    graph.add_edge("tools", "agent")
    return graph.compile()


def message_text(message: object) -> str:
    content = getattr(message, "content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = [
            str(block.get("text", "")) if isinstance(block, dict) else str(block)
            for block in content
        ]
        return "\n".join(part for part in parts if part).strip()
    return str(content)


async def answer(graph, prompt: str, show_tool_calls: bool = False) -> str:
    result = await graph.ainvoke(
        {"messages": [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=prompt)]},
        config={"recursion_limit": 10},
    )
    messages = result["messages"]
    if show_tool_calls:
        for message in messages:
            for call in getattr(message, "tool_calls", []):
                print(f"[tool call] {call['name']}({call['args']})", file=sys.stderr)
    return message_text(messages[-1]) if messages else "I couldn't produce a response."


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default=os.getenv("OLLAMA_MODEL", "qwen3:4b"))
    parser.add_argument("--message", help="Handle one message and exit.")
    parser.add_argument(
        "--show-tool-calls", action="store_true",
        help="Print the tool calls selected by the model.",
    )
    return parser.parse_args(argv)


async def run(args: argparse.Namespace) -> int:
    try:
        async with MCPAdapter(create_mcp_client()) as adapter:
            tools = await adapter.list_tools()
            model = ChatOllama(model=args.model, temperature=0)
            graph = build_graph(model, tools)
            if args.message:
                print(await answer(graph, args.message, args.show_tool_calls))
                return 0

            print(f"Customer Assistant ({args.model}). Type 'exit' to quit.")
            while True:
                try:
                    prompt = input("You: ").strip()
                except (EOFError, KeyboardInterrupt):
                    print()
                    break
                if prompt.lower() in {"exit", "quit"}:
                    break
                if not prompt:
                    continue
                try:
                    response = await answer(graph, prompt, args.show_tool_calls)
                    print(f"Assistant: {response}")
                except Exception as exc:
                    print(f"Assistant: I couldn't complete that request ({exc}).")
        return 0
    except Exception as exc:
        print(f"Could not start the customer assistant: {exc}", file=sys.stderr)
        return 1


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        return asyncio.run(run(args))
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
