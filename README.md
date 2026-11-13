# MCP for Developers

A hands-on learning series that introduces the Model Context Protocol step by step. Each part builds one concept at a time with small examples that can be run and inspected locally.

## Learning path

- **Part 6 — Build Your First MCP Server Using Python** — a local FastMCP server exposes a customer lookup tool over stdio. See [Part 6](part-06-first-mcp-server/README.md).
- **Part 7 — Build Your First MCP Client Using Python** — a standalone Python MCP client starts the existing Part 6 server over stdio, discovers its tool, and calls it. See [Part 7](part-07-first-mcp-client/README.md).
- **Part 8 — Integrate MCP with LangChain** — next milestone; connect MCP capabilities to a LangChain application.

See the [project roadmap](ROADMAP.md) for milestone status.

## Host, Client, and Server

- **MCP Host:** the user-facing application that brings together the user experience and may use one or more MCP clients, tools, and an LLM.
- **MCP Client:** the protocol component that establishes a session with an MCP server, discovers its capabilities, and sends requests.
- **MCP Server:** the program that exposes tools, resources, or prompts through the MCP protocol.

Part 7 is a simple standalone MCP Client for learning. It is not an LLM-powered Host application.

## Repository layout

```text
mcp-developers-series/
├── part-06-first-mcp-server/
│   ├── server.py
│   ├── pyproject.toml
│   ├── uv.lock
│   ├── README.md
│   └── tests/
├── part-07-first-mcp-client/
│   ├── client.py
│   ├── pyproject.toml
│   ├── uv.lock
│   ├── README.md
│   └── tests/
├── ROADMAP.md
├── .gitignore
└── README.md
```

## Requirements

- Python 3.12
- [uv](https://docs.astral.sh/uv/)
- MCP Inspector for the Part 6 guided server walkthrough (optional)

Each part has its own setup instructions. Start at the part README you want to run.
