# MCP for Developers

A hands-on LinkedIn learning series that introduces the Model Context Protocol step by step for developers. Each part builds one concept at a time, with small examples that can be run and inspected locally.

## Learning path

- **Part 6 — Build Your First MCP Server Using Python:** a local FastMCP server exposes one customer lookup tool over stdio. See [part-06-first-mcp-server](part-06-first-mcp-server/README.md).

Earlier and later parts will be added as the series is published. The examples focus on MCP fundamentals and introduce larger application frameworks only in the later parts where they belong.

## Repository layout

```text
mcp-developers-series/
├── part-06-first-mcp-server/
│   ├── server.py
│   ├── pyproject.toml
│   ├── uv.lock
│   ├── README.md
│   └── tests/
│       └── test_server.py
├── .gitignore
└── README.md
```

## Requirements

- Python 3.12
- [uv](https://docs.astral.sh/uv/)
- MCP Inspector (launched by the SDK's `mcp dev` command; Node.js/npm is needed when launching it separately)

Each part has its own setup instructions. Start at the part README you want to run.


