# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Literal

Transport = Literal["stdio", "sse", "streamable-http"]


def _as_int(value: str | None, default: int, name: str) -> int:
    if value is None:
        return default
    try:
        return int(value.strip())
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer, got: {value!r}") from exc


@dataclass(frozen=True)
class PurviewMCPConfig:
    # --- Purview client settings ---
    account_name: str
    tenant_id: str | None
    azure_region: str | None
    max_retries: int
    timeout: int
    batch_size: int

    # --- MCP server / transport settings ---
    transport: Transport
    host: str
    port: int

    @classmethod
    def from_env(cls) -> "PurviewMCPConfig":
        account_name = os.getenv("PURVIEW_ACCOUNT_NAME", "").strip()
        if not account_name:
            raise ValueError("PURVIEW_ACCOUNT_NAME is required.")

        transport_raw = os.getenv("PURVIEW_MCP_TRANSPORT", "stdio").strip().lower()
        # Accept "http" as an alias for "streamable-http"
        if transport_raw == "http":
            transport_raw = "streamable-http"
        if transport_raw not in {"stdio", "sse", "streamable-http"}:
            raise ValueError(
                "PURVIEW_MCP_TRANSPORT must be one of: stdio, sse, streamable-http, http"
            )
        typed_transport: Transport = transport_raw  # type: ignore[assignment]

        return cls(
            account_name=account_name,
            tenant_id=os.getenv("AZURE_TENANT_ID") or None,
            azure_region=os.getenv("AZURE_REGION") or None,
            max_retries=_as_int(os.getenv("PURVIEW_MAX_RETRIES"), 3, "PURVIEW_MAX_RETRIES"),
            timeout=_as_int(os.getenv("PURVIEW_TIMEOUT"), 30, "PURVIEW_TIMEOUT"),
            batch_size=_as_int(os.getenv("PURVIEW_BATCH_SIZE"), 100, "PURVIEW_BATCH_SIZE"),
            transport=typed_transport,
            host=os.getenv("PURVIEW_MCP_HOST", "127.0.0.1").strip(),
            port=_as_int(os.getenv("PURVIEW_MCP_PORT"), 8000, "PURVIEW_MCP_PORT"),
        )
