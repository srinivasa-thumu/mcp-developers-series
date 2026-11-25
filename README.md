# MCP for Developers

A hands-on learning series that introduces the Model Context Protocol step by step.

## Learning path

- **Part 6 — Build Your First MCP Server Using Python** — a local FastMCP server exposes a customer lookup tool over stdio. See [Part 6](part-06-first-mcp-server/README.md).
- **Part 7 — Build Your First MCP Client Using Python** — a Python MCP client starts Part 6 over stdio, discovers its tool, and calls it. See [Part 7](part-07-first-mcp-client/README.md).
- **Part 8 — Integrate MCP with LangChain** — LangChain's MCPAdapter discovers and adapts the Part 6 tool. See [Part 8](part-08-langchain-mcp-integration/README.md).
- **Part 9 — Build an MCP-powered AI Agent using LangGraph** — an Ollama-powered assistant uses LangGraph to decide when to call the existing Part 6 customer tool. See [Part 9](part-09-langgraph-mcp-agent/README.md).

See the [project roadmap](ROADMAP.md) for milestone status.

## Host, Client, and Server

- **MCP Host:** the user-facing application that may use clients, tools, and an LLM.
- **MCP Client:** establishes a session with an MCP server, discovers capabilities, and sends requests.
- **MCP Server:** exposes tools, resources, or prompts through MCP.

Part 7 is a standalone MCP client, not an LLM-powered host. Part 8 demonstrates LangChain consuming an existing server tool without adding a model or agent.

## Repository layout

```text
mcp-developers-series/
├── part-06-first-mcp-server/
├── part-07-first-mcp-client/
├── part-08-langchain-mcp-integration/
├── part-09-langgraph-mcp-agent/
├── ROADMAP.md
└── README.md
```

Requirements: Python 3.12 and [uv](https://docs.astral.sh/uv/). Each part has its own setup instructions.
