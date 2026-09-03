# Controlling NeoScaffold from other agents (MCP + OpenAPI)

NeoScaffold v1.0.0 is designed to be driven by other agents. Two layers make
that possible:

1. **OpenAPI spec** — the machine-readable contract for the HTTP API, served at
   `GET /v1/openapi.json` (a static copy lives at [`openapi.json`](./openapi.json)).
2. **MCP interface** — a Model Context Protocol *tools* server whose tools are
   derived directly from that OpenAPI spec, so anything in the spec (with an
   `operationId`) becomes an agent-callable tool.

## Tools

The tool surface is derived from the OpenAPI operations. Inspect it live at
`GET /v1/mcp/tools`. Current tools:

| Tool (`operationId`) | Does |
| --- | --- |
| `buildGraph` | Natural language -> validated prompt-graph |
| `runPrompt` | Execute a prompt-graph |
| `listExtensions` | List node/rule contracts |
| `getInfo` | Queue/exec info |
| `getAgentEvents` | Recent subagent activity (visibility) |
| `importWorkflow` | Import a LiteGraph or prompt-graph workflow |
| `exportWorkflow` | Export a prompt-graph as portable JSON |
| `suggestFix` | Run error + prompt-graph → accept-ready patch |
| `getMetrics` | Prometheus metrics |
| `getHealth` | Liveness + counts |
| `getOpenApi` | The OpenAPI document |
| `listMcpTools` | This tool list |

## Running the MCP server

The MCP server speaks JSON-RPC over stdio and proxies tool calls to a running
NeoScaffold HTTP server. Start NeoScaffold, then run:

```bash
cd server
NEOSCAFFOLD_URL=http://localhost:6166 python mcp_server.py
```

### Configure in an MCP client

Register it as a stdio server (example shape used by common MCP clients):

```json
{
  "mcpServers": {
    "neoscaffold": {
      "command": "python",
      "args": ["/absolute/path/to/server/mcp_server.py"],
      "env": { "NEOSCAFFOLD_URL": "http://localhost:6166" }
    }
  }
}
```

### Protocol

`mcp_server.py` implements the MCP JSON-RPC subset a tools server needs:
`initialize`, `notifications/initialized`, `ping`, `tools/list`, and
`tools/call`. It is dependency-free (stdlib `urllib`); the protocol and
OpenAPI→tools logic live in `server/server/harness/mcp.py` and
`server/server/harness/openapi_mcp.py` and are unit-tested.

## Example session

```jsonc
--> {"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}
<-- {"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2024-11-05","serverInfo":{"name":"neoscaffold","version":"1.0.0"}, ...}}

--> {"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"buildGraph","arguments":{"prompt":"concatenate \"a\" and \"b\" then log it"}}}
<-- {"jsonrpc":"2.0","id":2,"result":{"content":[{"type":"text","text":"{\"prompt\": {\"1\": {\"type\": \"StringJoin\", ...}}}"}],"isError":false}}
```
