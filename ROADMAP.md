# Project Roadmap

| Part | Milestone | Status |
| --- | --- | --- |
| 6 | Build Your First MCP Server Using Python | Complete |
| 7 | Build Your First MCP Client Using Python | Complete |
| 8 | Integrate MCP with LangChain | Complete |
| 9 | Build an MCP-powered AI Agent using LangGraph | Complete |
| 10 | Expose Multiple Tools from an MCP Server | Planned |

Part 7 was verified with the existing Part 6 server over stdio, including tool discovery, customer IDs 101 and 102, an unknown ID, and clean async shutdown.

Part 8 is complete after integration tests verify LangChain MCPAdapter discovery, schema adaptation, calls for IDs 101 and 102, unknown-ID handling, and adapter cleanup. See [Part 8](part-08-langchain-mcp-integration/README.md).

Part 9 adds a LangGraph agent/tool loop and reuses Part 8's MCP connection. Live Qwen3 scenarios and all Parts 6–9 test suites passed. See [Part 9](part-09-langgraph-mcp-agent/README.md).
