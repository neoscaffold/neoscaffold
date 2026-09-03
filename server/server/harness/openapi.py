"""Machine-readable OpenAPI 3.1 contract for the NeoScaffold HTTP API.

The spec is the single source of truth for what other agents can control. The
MCP interface (``openapi_mcp``) derives its tool definitions from this document,
so adding an operation here (with an ``operationId``) makes it available to
external agents automatically.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

OPENAPI_VERSION = "3.1.0"


def build_openapi_spec(server: Optional[Any] = None) -> Dict[str, Any]:
    """Return the OpenAPI document describing the NeoScaffold API."""
    version = "1.0.0"
    if server is not None:
        version = str(getattr(server, "VERSION", version) or version)

    prompt_graph_schema = {
        "type": "object",
        "additionalProperties": {
            "type": "object",
            "required": ["type"],
            "properties": {
                "type": {"type": "string", "description": "Registered node type name."},
                "name": {"type": "string", "description": "Display nickname."},
                "inputs": {
                    "type": "object",
                    "description": (
                        "Input name -> literal value, or {\"originId\": <nodeId>} "
                        "to wire an edge from another node's output."
                    ),
                    "additionalProperties": True,
                },
            },
        },
        "description": "A NeoScaffold prompt-graph: node_id -> node spec.",
    }

    return {
        "openapi": OPENAPI_VERSION,
        "info": {
            "title": "NeoScaffold API",
            "version": version,
            "description": (
                "HTTP API for NeoScaffold, a visual agent-graph builder. Designed "
                "to be controllable by other agents; see /v1/mcp/tools for the MCP "
                "tool surface derived from this spec."
            ),
        },
        "servers": [{"url": "/", "description": "NeoScaffold server"}],
        "paths": {
            "/v1/agent/build-graph": {
                "post": {
                    "operationId": "buildGraph",
                    "summary": "Build a validated prompt-graph from natural language.",
                    "description": (
                        "Turns a plain-language intent into an executable, "
                        "parse-validated NeoScaffold prompt-graph. Offline and "
                        "deterministic by default."
                    ),
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["prompt"],
                                    "properties": {
                                        "prompt": {
                                            "type": "string",
                                            "description": "Natural-language description of the workflow.",
                                        }
                                    },
                                }
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "A built graph plus plan and provenance.",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "prompt": {"$ref": "#/components/schemas/PromptGraph"},
                                            "layout": {"type": "object"},
                                            "plan": {"type": "array", "items": {"type": "string"}},
                                            "warnings": {"type": "array", "items": {"type": "string"}},
                                            "repairs": {"type": "array", "items": {"type": "string"}},
                                            "source": {"type": "string"},
                                        },
                                    }
                                }
                            },
                        },
                        "400": {"description": "Invalid request."},
                        "422": {"description": "Prompt could not be parsed into a graph."},
                    },
                }
            },
            "/prompt": {
                "post": {
                    "operationId": "runPrompt",
                    "summary": "Execute a prompt-graph.",
                    "description": (
                        "Queues a prompt-graph for execution. Results stream over "
                        "the WebSocket channel; the HTTP response is an acknowledgement."
                    ),
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["prompt", "promptId"],
                                    "properties": {
                                        "prompt": {"$ref": "#/components/schemas/PromptGraph"},
                                        "promptId": {"type": "string"},
                                        "workflow": {"type": "object"},
                                        "executionMode": {
                                            "type": "string",
                                            "enum": ["sequential", "parallel"],
                                        },
                                    },
                                }
                            }
                        },
                    },
                    "responses": {
                        "200": {"description": "Execution acknowledgement."},
                        "400": {"description": "Missing or invalid prompt."},
                    },
                }
            },
            "/extensions": {
                "get": {
                    "operationId": "listExtensions",
                    "summary": "List loaded extensions and their node/rule contracts.",
                    "responses": {"200": {"description": "Extension registry."}},
                }
            },
            "/info": {
                "get": {
                    "operationId": "getInfo",
                    "summary": "Queue/exec info.",
                    "responses": {"200": {"description": "Execution info."}},
                }
            },
            "/v1/agent/events": {
                "get": {
                    "operationId": "getAgentEvents",
                    "summary": "Recent agent/subagent activity events.",
                    "description": (
                        "Returns recent subagent spans (graph builds, prompt nodes, "
                        "sub-graph builders) so users and agents can see inside the swarm."
                    ),
                    "parameters": [
                        {
                            "name": "limit",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "integer", "minimum": 1, "maximum": 1000},
                            "description": "Maximum number of events to return (newest last).",
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "A list of agent events.",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "events": {
                                                "type": "array",
                                                "items": {"$ref": "#/components/schemas/AgentEvent"},
                                            }
                                        },
                                    }
                                }
                            },
                        }
                    },
                }
            },
            "/v1/metrics": {
                "get": {
                    "operationId": "getMetrics",
                    "summary": "Prometheus metrics (PromQL-compatible).",
                    "responses": {
                        "200": {
                            "description": "Prometheus text exposition.",
                            "content": {"text/plain": {"schema": {"type": "string"}}},
                        }
                    },
                }
            },
            "/v1/healthz": {
                "get": {
                    "operationId": "getHealth",
                    "summary": "Liveness + loaded node/extension counts.",
                    "responses": {"200": {"description": "Health status."}},
                }
            },
            "/v1/openapi.json": {
                "get": {
                    "operationId": "getOpenApi",
                    "summary": "This OpenAPI document.",
                    "responses": {"200": {"description": "OpenAPI spec."}},
                }
            },
            "/v1/mcp/tools": {
                "get": {
                    "operationId": "listMcpTools",
                    "summary": "MCP tool definitions derived from this OpenAPI spec.",
                    "responses": {"200": {"description": "MCP tools."}},
                }
            },
        },
        "components": {
            "schemas": {
                "PromptGraph": prompt_graph_schema,
                "AgentEvent": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "parent_id": {"type": ["string", "null"]},
                        "kind": {"type": "string"},
                        "name": {"type": "string"},
                        "status": {
                            "type": "string",
                            "enum": ["started", "running", "succeeded", "failed"],
                        },
                        "started_at": {"type": "number"},
                        "ended_at": {"type": ["number", "null"]},
                        "detail": {"type": "object"},
                    },
                },
            }
        },
    }
