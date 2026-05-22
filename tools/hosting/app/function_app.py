# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import asyncio
import json
import logging

import azure.functions as func

from pvw_mcp_server.server import mcp  # FastMCP instance — all Purview tools registered

logger = logging.getLogger("purview-mcp-functions")

_fastmcp_base = mcp.http_app()


class _FastMCPBridge:
    """ASGI adapter for Azure Functions that fixes two compatibility issues:

    1. **Path prefix** – Azure Functions forwards the full URL path
       (e.g. ``/api/mcp``), but FastMCP's Starlette app mounts its endpoint
       at ``/mcp``.  We strip the leading ``/api`` before forwarding.

    2. **Lifespan** – ``AsgiMiddleware`` never emits ASGI lifespan events, so
       FastMCP's ``StreamableHTTPSessionManager`` never initialises its
       ``anyio`` task group and raises ``RuntimeError`` on the first request.
       We emit ``lifespan.startup`` in a background asyncio task and wait for
       ``lifespan.startup.complete`` before forwarding any HTTP request.
    """

    def __init__(self, app) -> None:
        self._app = app
        self._startup_done = asyncio.Event()
        self._lifespan_task: asyncio.Task | None = None

    async def _run_lifespan(self) -> None:
        queue: asyncio.Queue = asyncio.Queue()
        await queue.put({"type": "lifespan.startup"})

        async def receive():
            return await queue.get()

        async def send(message: dict) -> None:
            if message.get("type") == "lifespan.startup.complete":
                self._startup_done.set()

        try:
            await self._app({"type": "lifespan", "asgi": {"version": "3.0"}}, receive, send)
        except Exception:
            logger.warning("FastMCP lifespan startup failed", exc_info=True)
            self._startup_done.set()

    async def __call__(self, scope, receive, send) -> None:
        if scope.get("type") == "http":
            path: str = scope.get("path", "")
            if path.startswith("/api"):
                overrides: dict = {"path": path[4:] or "/"}
                raw = scope.get("raw_path", b"")
                if isinstance(raw, (bytes, bytearray)) and raw.startswith(b"/api"):
                    overrides["raw_path"] = raw[4:] or b"/"
                scope = {**scope, **overrides}

        if scope.get("type") == "http" and not self._startup_done.is_set():
            if self._lifespan_task is None or self._lifespan_task.done():
                self._lifespan_task = asyncio.create_task(self._run_lifespan())
            await asyncio.wait_for(asyncio.shield(self._startup_done.wait()), timeout=15.0)

        await self._app(scope, receive, send)


_mcp_asgi = func.AsgiMiddleware(_FastMCPBridge(_fastmcp_base))

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


# ── /api/mcp  (all MCP traffic → FastMCP via ASGI bridge) ────────────────────

@app.route(route="mcp/{*rest}", methods=["GET", "POST", "DELETE"])
async def mcp_handler(req: func.HttpRequest) -> func.HttpResponse:
    """Forward all MCP traffic to the FastMCP streamable-HTTP app.

    FastMCP handles ``initialize``, ``tools/list``, ``tools/call`` and the full
    MCP protocol automatically for all registered Purview tools.
    """
    try:
        return await _mcp_asgi.handle_async(req)
    except Exception:
        logger.exception("MCP ASGI bridge failed for %s %s", req.method, req.url)
        return func.HttpResponse(
            '{"error":"internal server error"}',
            status_code=500,
            headers={"Content-Type": "application/json"},
        )


# ── /api/health ────────────────────────────────────────────────────────────────

@app.route(route="health", methods=["GET"])
async def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """Liveness probe — returns 200 if the Function is running."""
    from pvw_mcp_server.__version__ import __version__ as _ver
    tools = await mcp.list_tools()
    return func.HttpResponse(
        json.dumps({"status": "ok", "version": _ver, "tools": len(tools)}),
        status_code=200,
        headers={"Content-Type": "application/json"},
    )
