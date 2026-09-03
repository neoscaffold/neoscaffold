"""Derive MCP tool definitions from an OpenAPI spec.

An MCP tools server needs, per tool: a name, a description, and a JSON-Schema
``inputSchema``. This module converts each OpenAPI operation (with an
``operationId``) into exactly that, and can resolve a tool call back into a
concrete HTTP request (method, path, query, body). Keeping this pure makes the
MCP interface unit-testable without a running server.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

_BODY_METHODS = {"post", "put", "patch", "delete"}


class OpenApiToolset:
    """Turns an OpenAPI document into MCP tools and resolves calls to requests."""

    def __init__(self, spec: Dict[str, Any]):
        self.spec = spec
        self._operations = self._index_operations(spec)

    def _index_operations(self, spec: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        operations: Dict[str, Dict[str, Any]] = {}
        for path, path_item in (spec.get("paths") or {}).items():
            for method, operation in path_item.items():
                if not isinstance(operation, dict):
                    continue
                operation_id = operation.get("operationId")
                if not operation_id:
                    continue
                operations[operation_id] = {
                    "method": method.lower(),
                    "path": path,
                    "operation": operation,
                }
        return operations

    def _body_schema(self, operation: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        content = (operation.get("requestBody") or {}).get("content") or {}
        json_body = content.get("application/json") or {}
        return json_body.get("schema")

    def _input_schema(self, operation: Dict[str, Any]) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}
        required: List[str] = []

        for param in operation.get("parameters") or []:
            name = param.get("name")
            if not name:
                continue
            schema = dict(param.get("schema") or {"type": "string"})
            if param.get("description"):
                schema.setdefault("description", param["description"])
            properties[name] = schema
            if param.get("required"):
                required.append(name)

        body_schema = self._body_schema(operation)
        if isinstance(body_schema, dict):
            for prop_name, prop_schema in (body_schema.get("properties") or {}).items():
                properties[prop_name] = prop_schema
            for req in body_schema.get("required") or []:
                if req not in required:
                    required.append(req)

        schema: Dict[str, Any] = {"type": "object", "properties": properties}
        if required:
            schema["required"] = required
        return schema

    def tools(self) -> List[Dict[str, Any]]:
        """Return MCP tool definitions (name, description, inputSchema)."""
        tools: List[Dict[str, Any]] = []
        for operation_id, entry in self._operations.items():
            operation = entry["operation"]
            description = operation.get("description") or operation.get("summary") or operation_id
            tools.append(
                {
                    "name": operation_id,
                    "description": description,
                    "inputSchema": self._input_schema(operation),
                }
            )
        tools.sort(key=lambda t: t["name"])
        return tools

    def has_tool(self, name: str) -> bool:
        return name in self._operations

    def resolve(
        self, name: str, arguments: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, str, Dict[str, Any], Optional[Dict[str, Any]]]:
        """Resolve a tool call into ``(method, path, query, body)``.

        Path parameters are substituted into the path, query parameters become
        the query dict, and any remaining request-body properties become the
        JSON body (for body-bearing methods).
        """
        if name not in self._operations:
            raise KeyError(f"unknown tool '{name}'")
        arguments = dict(arguments or {})
        entry = self._operations[name]
        operation = entry["operation"]
        method = entry["method"]
        path = entry["path"]

        consumed = set()
        query: Dict[str, Any] = {}
        for param in operation.get("parameters") or []:
            pname = param.get("name")
            if pname is None or pname not in arguments:
                continue
            location = param.get("in")
            if location == "path":
                path = path.replace("{" + pname + "}", str(arguments[pname]))
                consumed.add(pname)
            elif location == "query":
                query[pname] = arguments[pname]
                consumed.add(pname)

        body: Optional[Dict[str, Any]] = None
        if method in _BODY_METHODS:
            body_schema = self._body_schema(operation) or {}
            body_props = set((body_schema.get("properties") or {}).keys())
            if body_props:
                body = {k: v for k, v in arguments.items() if k in body_props}
            else:
                body = {k: v for k, v in arguments.items() if k not in consumed}

        return method, path, query, body
