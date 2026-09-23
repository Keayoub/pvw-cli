# SPDX-License-Identifier: Apache-2.0

"""
Microsoft Fabric REST Client
=============================

A dedicated, synchronous HTTP client for the Microsoft Fabric platform
(https://learn.microsoft.com/rest/api/fabric/). This client is intentionally
separate from the Purview-specific ``SyncPurviewClient`` / ``Endpoint``
stack: Fabric is a different host, a different authentication audience, and
a different error/response shape.

It backs the ``pvw fabric`` command group, primarily the Purview Unified
Catalog -> Fabric OneLake catalog sync workflow, but is written as a
general-purpose Fabric transport so it can be reused by future commands.

Only the operations needed for the sync workflow are implemented:

- OneLake catalog search (discovery of Fabric items)
- Item read / update (``displayName`` / ``description``)
- Tenant tag listing and bulk creation
- Item tag apply / unapply
- Domain listing, creation, update
- Domain workspace assignment / unassignment / listing

All requests are retried with exponential backoff for transient failures
and honor the ``Retry-After`` header on HTTP 429 responses. Authentication
failures, authorization failures, and API errors are raised as exceptions
rather than being silently swallowed or converted into "success" shaped
dictionaries, so calling code (and tests) can rely on exceptions for control
flow.
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
from typing import Any, Dict, Iterator, List, Optional

import requests
from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError
from azure.identity import ClientSecretCredential, DefaultAzureCredential
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class FabricAuthenticationError(Exception):
    """Raised when the client cannot obtain a Fabric access token."""


class FabricCliNotFoundError(FabricAuthenticationError):
    """Raised when the Azure CLI is not installed or not available."""


class FabricCliAuthenticationError(FabricAuthenticationError):
    """Raised when 'az account get-access-token' fails for the Fabric scope."""


class FabricCredentialsError(FabricAuthenticationError):
    """Raised when no supported Azure credential could authenticate."""


class FabricApiError(Exception):
    """Raised for non-2xx responses from the Fabric REST API.

    Attributes:
        status_code: HTTP status code, if known.
        error_code: Fabric ``errorCode`` from the structured error response, if present.
        message: Human-readable error message.
        is_retriable: Whether Fabric indicated the request can be retried.
        request_id: Fabric ``requestId`` for support/troubleshooting, if present.
        raw: The raw parsed error response body, if any.
    """

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        error_code: Optional[str] = None,
        is_retriable: bool = False,
        request_id: Optional[str] = None,
        raw: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.is_retriable = is_retriable
        self.request_id = request_id
        self.raw = raw or {}

    def __str__(self) -> str:  # pragma: no cover - trivial
        parts = [self.message]
        if self.status_code is not None:
            parts.append(f"(HTTP {self.status_code})")
        if self.error_code:
            parts.append(f"[{self.error_code}]")
        return " ".join(parts)


#: Sentinel default for optional "clearable" parameters, distinguishing
#: "argument not supplied" from an explicit ``None`` (e.g. "clear this field
#: to blank").
_UNSET = object()


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


class FabricConfig:
    """Configuration for :class:`FabricClient`.

    All values default to environment variables so the client can be
    constructed with no arguments, matching the pattern used by other
    ``pvw`` clients (e.g. ``UnifiedCatalogClient``) for compatibility with
    :func:`purviewcli.client.client_cache.get_cached_client`.
    """

    DEFAULT_BASE_URL = "https://api.fabric.microsoft.com/v1"
    DEFAULT_AUTH_SCOPE = "https://api.fabric.microsoft.com/.default"

    def __init__(
        self,
        base_url: Optional[str] = None,
        auth_scope: Optional[str] = None,
    ):
        self.base_url = (base_url or os.environ.get("FABRIC_API_BASE_URL") or self.DEFAULT_BASE_URL).rstrip("/")
        self.auth_scope = auth_scope or os.environ.get("FABRIC_AUTH_SCOPE") or self.DEFAULT_AUTH_SCOPE


# ---------------------------------------------------------------------------
# Azure CLI token acquisition (Fabric scope)
# ---------------------------------------------------------------------------


class _FabricCliCredential:
    """Fetches a Fabric-scoped access token via 'az account get-access-token'."""

    def get_token(self, *scopes: str, **kwargs: Any) -> AccessToken:
        scope = scopes[0] if scopes else ""
        resource = scope.replace("/.default", "")

        result = None
        last_error: Optional[str] = None
        for az_cmd in ("az", "az.cmd"):
            try:
                result = subprocess.run(
                    [az_cmd, "account", "get-access-token", "--resource", resource, "--output", "json"],
                    capture_output=True,
                    text=True,
                    check=False,
                    shell=False,
                )
                if result.returncode == 0:
                    break
                last_error = result.stderr
            except (FileNotFoundError, OSError) as exc:
                last_error = str(exc)
                continue

        if not result or result.returncode != 0:
            raise FabricCliAuthenticationError(
                f"Azure CLI authentication failed for the Fabric API. "
                f"Ensure you are logged in with 'az login' and have access to the target tenant. "
                f"Error: {(last_error or 'Unknown error')[:300]}"
            )

        try:
            token_data = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise FabricCliAuthenticationError(f"Invalid JSON response from Azure CLI: {exc}")

        if "accessToken" not in token_data:
            raise FabricCliAuthenticationError("No access token in Azure CLI response")

        from datetime import datetime

        expires_on_str = str(token_data.get("expiresOn", "0"))
        try:
            expires_on = int(expires_on_str)
        except ValueError:
            try:
                dt = datetime.strptime(expires_on_str.split(".")[0], "%Y-%m-%d %H:%M:%S")
                expires_on = int(dt.timestamp())
            except Exception as exc:
                raise FabricCliAuthenticationError(f"Failed to parse token expiration: {expires_on_str}") from exc

        return AccessToken(token=token_data["accessToken"], expires_on=expires_on)


# ---------------------------------------------------------------------------
# Fabric client
# ---------------------------------------------------------------------------


class FabricClient:
    """Synchronous client for the Microsoft Fabric REST API."""

    #: Maximum page size accepted by the Catalog Search API.
    MAX_CATALOG_PAGE_SIZE = 1000
    #: Item field length / count limits enforced by the Fabric platform.
    ITEM_DESCRIPTION_MAX_LENGTH = 256
    MAX_TAGS_PER_ITEM = 10

    def __init__(self, config: Optional[FabricConfig] = None):
        self.config = config or FabricConfig()
        self._token: Optional[str] = None
        self._credential = None
        self._session = self._create_session()

    # -- session / auth -----------------------------------------------------

    def _create_session(self) -> requests.Session:
        session = requests.Session()
        retry_strategy = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            # POST/PATCH are intentionally excluded: they are used for
            # non-idempotent Fabric mutations (create domain/tag, apply item
            # changes), and retrying them on a transient 5xx could double-
            # apply a write if the original request actually succeeded
            # server-side before the error was returned.
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"],
            respect_retry_after_header=True,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session

    def _get_token(self, force_refresh: bool = False) -> str:
        if self._token and not force_refresh:
            return self._token

        scope = self.config.auth_scope

        # 1. Service principal via environment variables (shared with Purview auth).
        client_id = os.environ.get("AZURE_CLIENT_ID")
        client_secret = os.environ.get("AZURE_CLIENT_SECRET")
        tenant_id = os.environ.get("AZURE_TENANT_ID")

        if client_id and client_secret and tenant_id:
            try:
                self._credential = ClientSecretCredential(
                    tenant_id=tenant_id, client_id=client_id, client_secret=client_secret
                )
                token = self._credential.get_token(scope)
                logger.info("Authenticated to Fabric API using service principal")
                self._token = token.token
                return self._token
            except ClientAuthenticationError as exc:
                raise FabricCredentialsError(
                    f"Service principal authentication to the Fabric API failed: {str(exc)[:300]}"
                ) from exc

        # 2. Azure CLI (az login).
        try:
            self._credential = _FabricCliCredential()
            token = self._credential.get_token(scope)
            logger.info("Authenticated to Fabric API using Azure CLI")
            self._token = token.token
            return self._token
        except FabricCliAuthenticationError as exc:
            logger.debug("Azure CLI Fabric authentication failed, falling back: %s", exc)

        # 3. DefaultAzureCredential (managed identity, VS Code, env, etc.).
        try:
            self._credential = DefaultAzureCredential()
            token = self._credential.get_token(scope)
            logger.info("Authenticated to Fabric API using DefaultAzureCredential")
            self._token = token.token
            return self._token
        except ClientAuthenticationError as exc:
            raise FabricCredentialsError(
                f"Failed to authenticate to the Fabric API. Run 'az login' or configure "
                f"AZURE_CLIENT_ID / AZURE_CLIENT_SECRET / AZURE_TENANT_ID. Error: {str(exc)[:300]}"
            ) from exc

    # -- low-level request ----------------------------------------------------

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
        _retried_after_401: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """Issue a request against the Fabric API and return the parsed JSON body.

        Returns ``None`` for empty (e.g. 200/204 with no content) responses.
        Raises :class:`FabricApiError` for non-2xx responses.
        """
        token = self._get_token()
        url = f"{self.config.base_url}{path}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "purviewcli-fabric/1.0",
        }

        debug = os.environ.get("PURVIEWCLI_DEBUG")
        if debug:
            logger.debug("Fabric request: %s %s params=%s", method, url, params)

        try:
            response = self._session.request(
                method=method.upper(),
                url=url,
                headers=headers,
                params=params,
                json=json_body,
                timeout=60,
            )
        except requests.exceptions.Timeout as exc:
            raise FabricApiError("Fabric API request timed out after 60 seconds", is_retriable=True) from exc
        except requests.exceptions.ConnectionError as exc:
            raise FabricApiError(f"Failed to connect to {self.config.base_url}", is_retriable=True) from exc

        if response.status_code == 401 and not _retried_after_401:
            # Token may have expired mid-run; force a fresh token and retry once.
            self._token = None
            return self._request(method, path, params=params, json_body=json_body, _retried_after_401=True)

        if 200 <= response.status_code < 300:
            if not response.content or not response.content.strip():
                return None
            try:
                return response.json()
            except json.JSONDecodeError:
                return {"raw": response.text}

        self._raise_for_error(response)
        return None  # pragma: no cover - _raise_for_error always raises

    @staticmethod
    def _raise_for_error(response: requests.Response) -> None:
        message = f"HTTP {response.status_code}"
        error_code = None
        is_retriable = response.status_code == 429
        request_id = None
        raw: Dict[str, Any] = {}

        try:
            raw = response.json()
            message = raw.get("message") or message
            error_code = raw.get("errorCode")
            is_retriable = bool(raw.get("isRetriable", is_retriable))
            request_id = raw.get("requestId")
        except json.JSONDecodeError:
            if response.text:
                message = f"{message}: {response.text[:500]}"

        raise FabricApiError(
            message,
            status_code=response.status_code,
            error_code=error_code,
            is_retriable=is_retriable,
            request_id=request_id,
            raw=raw,
        )

    # -- Catalog search (discovery) ------------------------------------------

    def search_catalog_page(
        self,
        search: Optional[str] = None,
        filter: Optional[str] = None,  # noqa: A002 - matches Fabric API field name
        page_size: int = 100,
        continuation_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Query one page of the OneLake catalog search API.

        Returns the raw response: ``{"value": [...], "continuationToken": ...}``.
        """
        page_size = max(1, min(page_size, self.MAX_CATALOG_PAGE_SIZE))
        body: Dict[str, Any] = {"pageSize": page_size}
        if search:
            body["search"] = search
        if filter:
            body["filter"] = filter
        if continuation_token:
            body["continuationToken"] = continuation_token
        return self._request("POST", "/catalog/search", json_body=body) or {"value": []}

    def iter_catalog_entries(
        self,
        search: Optional[str] = None,
        filter: Optional[str] = None,  # noqa: A002
        page_size: int = 100,
    ) -> Iterator[Dict[str, Any]]:
        """Yield every catalog entry across all pages of a search."""
        continuation_token: Optional[str] = None
        while True:
            page = self.search_catalog_page(
                search=search, filter=filter, page_size=page_size, continuation_token=continuation_token
            )
            for entry in page.get("value", []) or []:
                yield entry
            continuation_token = page.get("continuationToken")
            if not continuation_token:
                break

    # -- Items ----------------------------------------------------------------

    def get_item(self, workspace_id: str, item_id: str) -> Dict[str, Any]:
        result = self._request("GET", f"/workspaces/{workspace_id}/items/{item_id}")
        return result or {}

    def update_item(
        self,
        workspace_id: str,
        item_id: str,
        display_name: Any = _UNSET,
        description: Any = _UNSET,
    ) -> Dict[str, Any]:
        # `_UNSET` (rather than `None`) marks "field not supplied", so callers
        # -- notably rollback, which restores `before_state` values that can
        # legitimately be `None` (e.g. "the item originally had no
        # description") -- can explicitly clear a field without that request
        # being mistaken for an omitted argument.
        body: Dict[str, Any] = {}
        if display_name is not _UNSET:
            body["displayName"] = display_name
        if description is not _UNSET:
            body["description"] = description
        if not body:
            raise ValueError("update_item requires at least one of display_name or description")
        result = self._request("PATCH", f"/workspaces/{workspace_id}/items/{item_id}", json_body=body)
        return result or {}

    # -- Tags -------------------------------------------------------------------

    def list_tenant_tags(self) -> List[Dict[str, Any]]:
        """List all tenant-visible tags (readable by any authenticated caller)."""
        tags: List[Dict[str, Any]] = []
        continuation_token: Optional[str] = None
        while True:
            params = {"continuationToken": continuation_token} if continuation_token else None
            page = self._request("GET", "/tags", params=params) or {}
            tags.extend(page.get("value", []) or [])
            continuation_token = page.get("continuationToken")
            if not continuation_token:
                break
        return tags

    def bulk_create_tags(
        self,
        display_names: List[str],
        domain_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Create one or more tenant- or domain-scoped tags.

        Requires Fabric administrator permissions. Raises :class:`FabricApiError`
        with ``error_code == "EntityConflict"`` if a tag with the same display
        name already exists; callers should typically resolve existing tags via
        :meth:`list_tenant_tags` first and only create missing ones.
        """
        if not display_names:
            return []
        body: Dict[str, Any] = {
            "createTagsRequest": [{"displayName": name} for name in display_names],
        }
        if domain_id:
            body["scope"] = {"type": "Domain", "domainId": domain_id}
        result = self._request("POST", "/admin/tags/bulkCreateTags", json_body=body) or {}
        return result.get("value", []) or []

    def apply_tags(self, workspace_id: str, item_id: str, tag_ids: List[str]) -> None:
        if not tag_ids:
            return
        self._request(
            "POST",
            f"/workspaces/{workspace_id}/items/{item_id}/applyTags",
            json_body={"tags": tag_ids},
        )

    def unapply_tags(self, workspace_id: str, item_id: str, tag_ids: List[str]) -> None:
        if not tag_ids:
            return
        self._request(
            "POST",
            f"/workspaces/{workspace_id}/items/{item_id}/unapplyTags",
            json_body={"tags": tag_ids},
        )

    # -- Domains ------------------------------------------------------------

    def list_domains(self) -> List[Dict[str, Any]]:
        """List all Fabric domains. Requires Fabric administrator permissions."""
        result = self._request("GET", "/admin/domains") or {}
        return result.get("domains", result.get("value", [])) or []

    def get_domain(self, domain_id: str) -> Dict[str, Any]:
        result = self._request("GET", f"/admin/domains/{domain_id}")
        return result or {}

    def create_domain(
        self,
        display_name: str,
        description: Optional[str] = None,
        parent_domain_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        body: Dict[str, Any] = {"displayName": display_name}
        if description:
            body["description"] = description
        if parent_domain_id:
            body["parentDomainId"] = parent_domain_id
        result = self._request("POST", "/admin/domains", json_body=body)
        return result or {}

    def update_domain(
        self,
        domain_id: str,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        body: Dict[str, Any] = {}
        if display_name is not None:
            body["displayName"] = display_name
        if description is not None:
            body["description"] = description
        if not body:
            raise ValueError("update_domain requires at least one of display_name or description")
        result = self._request("PATCH", f"/admin/domains/{domain_id}", json_body=body)
        return result or {}

    def list_domain_workspaces(self, domain_id: str) -> List[Dict[str, Any]]:
        workspaces: List[Dict[str, Any]] = []
        continuation_token: Optional[str] = None
        while True:
            params = {"continuationToken": continuation_token} if continuation_token else None
            page = self._request("GET", f"/admin/domains/{domain_id}/workspaces", params=params) or {}
            workspaces.extend(page.get("value", []) or [])
            continuation_token = page.get("continuationToken")
            if not continuation_token:
                break
        return workspaces

    def assign_domain_workspaces(self, domain_id: str, workspace_ids: List[str]) -> None:
        if not workspace_ids:
            return
        self._request(
            "POST",
            f"/admin/domains/{domain_id}/assignWorkspaces",
            json_body={"workspacesIds": workspace_ids},
        )

    def unassign_domain_workspaces(self, domain_id: str, workspace_ids: List[str]) -> None:
        if not workspace_ids:
            return
        self._request(
            "POST",
            f"/admin/domains/{domain_id}/unassignWorkspaces",
            json_body={"workspacesIds": workspace_ids},
        )
