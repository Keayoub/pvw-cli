# SPDX-License-Identifier: Apache-2.0
"""Unit tests for purviewcli.client.fabric_client.FabricClient.

These tests mock ``requests.Session.request`` directly (no network, no
``requests_mock`` dependency) and stub token acquisition so we can validate
request construction, pagination, retry/error handling, and payload shapes
in isolation.
"""

import json
import os
import sys
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from purviewcli.client.fabric_client import (
    FabricApiError,
    FabricClient,
    FabricConfig,
    FabricCredentialsError,
)


def _response(status_code=200, json_body=None, text=""):
    resp = MagicMock()
    resp.status_code = status_code
    resp.text = text
    if json_body is not None:
        resp.content = b"{}"
        resp.json.return_value = json_body
    elif text:
        # Simulate a non-JSON error body (e.g. plain-text 500 page).
        resp.content = text.encode()
        resp.json.side_effect = json.JSONDecodeError("Expecting value", text, 0)
    else:
        resp.content = b""
        resp.json.side_effect = json.JSONDecodeError("Expecting value", "", 0)
    return resp


@pytest.fixture
def client():
    c = FabricClient(FabricConfig())
    c._token = "fake-token"  # bypass real authentication
    return c


class TestRequestConstruction:
    def test_get_item_builds_expected_url_and_auth_header(self, client):
        with patch.object(client._session, "request", return_value=_response(200, {"id": "item-1"})) as mock_req:
            result = client.get_item("ws-1", "item-1")

        assert result == {"id": "item-1"}
        call = mock_req.call_args
        assert call.kwargs["method"] == "GET"
        assert call.kwargs["url"] == "https://api.fabric.microsoft.com/v1/workspaces/ws-1/items/item-1"
        assert call.kwargs["headers"]["Authorization"] == "Bearer fake-token"

    def test_update_item_sends_only_provided_fields(self, client):
        with patch.object(client._session, "request", return_value=_response(200, {"id": "item-1"})) as mock_req:
            client.update_item("ws-1", "item-1", display_name="New Name")

        call = mock_req.call_args
        assert call.kwargs["json"] == {"displayName": "New Name"}
        assert call.kwargs["method"] == "PATCH"

    def test_update_item_requires_a_field(self, client):
        with pytest.raises(ValueError):
            client.update_item("ws-1", "item-1")

    def test_update_item_allows_explicit_none_to_clear_a_field(self, client):
        """An explicit `description=None` (e.g. restoring a rollback's
        before_state where the item originally had no description) must be
        sent as a PATCH value, not treated the same as "not supplied"."""
        with patch.object(client._session, "request", return_value=_response(200, {"id": "item-1"})) as mock_req:
            client.update_item("ws-1", "item-1", description=None)

        call = mock_req.call_args
        assert call.kwargs["json"] == {"description": None}


class TestCatalogPagination:
    def test_iter_catalog_entries_follows_continuation_token(self, client):
        page1 = {"value": [{"id": "a"}], "continuationToken": "tok-2"}
        page2 = {"value": [{"id": "b"}], "continuationToken": None}

        responses = [_response(200, page1), _response(200, page2)]
        with patch.object(client._session, "request", side_effect=responses) as mock_req:
            entries = list(client.iter_catalog_entries(search="Sales", page_size=1))

        assert [e["id"] for e in entries] == ["a", "b"]
        assert mock_req.call_count == 2
        first_body = mock_req.call_args_list[0].kwargs["json"]
        second_body = mock_req.call_args_list[1].kwargs["json"]
        assert first_body == {"pageSize": 1, "search": "Sales"}
        assert second_body["continuationToken"] == "tok-2"

    def test_search_catalog_page_caps_page_size(self, client):
        with patch.object(client._session, "request", return_value=_response(200, {"value": []})) as mock_req:
            client.search_catalog_page(page_size=5000)

        assert mock_req.call_args.kwargs["json"]["pageSize"] == FabricClient.MAX_CATALOG_PAGE_SIZE


class TestTags:
    def test_list_tenant_tags_paginates(self, client):
        page1 = {"value": [{"id": "t1", "displayName": "Finance"}], "continuationToken": "tok"}
        page2 = {"value": [{"id": "t2", "displayName": "HR"}]}
        with patch.object(client._session, "request", side_effect=[_response(200, page1), _response(200, page2)]):
            tags = client.list_tenant_tags()
        assert [t["id"] for t in tags] == ["t1", "t2"]

    def test_bulk_create_tags_payload_shape(self, client):
        with patch.object(
            client._session, "request", return_value=_response(200, {"value": [{"id": "t1", "displayName": "Sales"}]})
        ) as mock_req:
            result = client.bulk_create_tags(["Sales"])

        body = mock_req.call_args.kwargs["json"]
        assert body == {"createTagsRequest": [{"displayName": "Sales"}]}
        assert result == [{"id": "t1", "displayName": "Sales"}]

    def test_bulk_create_tags_with_domain_scope(self, client):
        with patch.object(client._session, "request", return_value=_response(200, {"value": []})) as mock_req:
            client.bulk_create_tags(["Sales"], domain_id="dom-1")

        body = mock_req.call_args.kwargs["json"]
        assert body["scope"] == {"type": "Domain", "domainId": "dom-1"}

    def test_bulk_create_tags_noop_for_empty_list(self, client):
        with patch.object(client._session, "request") as mock_req:
            result = client.bulk_create_tags([])
        assert result == []
        mock_req.assert_not_called()

    def test_apply_tags_sends_tag_ids(self, client):
        with patch.object(client._session, "request", return_value=_response(200)) as mock_req:
            client.apply_tags("ws-1", "item-1", ["tag-a", "tag-b"])

        call = mock_req.call_args
        assert call.kwargs["url"].endswith("/workspaces/ws-1/items/item-1/applyTags")
        assert call.kwargs["json"] == {"tags": ["tag-a", "tag-b"]}

    def test_unapply_tags_noop_for_empty_list(self, client):
        with patch.object(client._session, "request") as mock_req:
            client.unapply_tags("ws-1", "item-1", [])
        mock_req.assert_not_called()


class TestDomains:
    def test_create_domain_request_shape(self, client):
        with patch.object(
            client._session, "request", return_value=_response(201, {"id": "dom-1", "displayName": "Finance"})
        ) as mock_req:
            client.create_domain("Finance", description="Financial data")

        call = mock_req.call_args
        # Matches microsoft/fabric-cli's fab_api_domain.create_domain: no `preview`
        # query parameter on admin/domains (that param applied to an older,
        # now-superseded preview revision of this API).
        assert call.kwargs["params"] is None
        assert call.kwargs["json"] == {"displayName": "Finance", "description": "Financial data"}

    def test_list_domain_workspaces_paginates(self, client):
        page1 = {"value": [{"id": "ws-1"}], "continuationToken": "tok"}
        page2 = {"value": [{"id": "ws-2"}]}
        with patch.object(client._session, "request", side_effect=[_response(200, page1), _response(200, page2)]):
            workspaces = client.list_domain_workspaces("dom-1")
        assert [w["id"] for w in workspaces] == ["ws-1", "ws-2"]

    def test_assign_domain_workspaces_payload(self, client):
        with patch.object(client._session, "request", return_value=_response(200)) as mock_req:
            client.assign_domain_workspaces("dom-1", ["ws-1", "ws-2"])
        assert mock_req.call_args.kwargs["json"] == {"workspacesIds": ["ws-1", "ws-2"]}

    def test_unassign_domain_workspaces_noop_for_empty_list(self, client):
        with patch.object(client._session, "request") as mock_req:
            client.unassign_domain_workspaces("dom-1", [])
        mock_req.assert_not_called()


class TestErrorHandling:
    def test_non_2xx_raises_fabric_api_error_with_structured_fields(self, client):
        error_body = {
            "errorCode": "ItemNotFound",
            "message": "The requested item was not found.",
            "isRetriable": False,
            "requestId": "req-123",
        }
        with patch.object(client._session, "request", return_value=_response(404, error_body)):
            with pytest.raises(FabricApiError) as exc_info:
                client.get_item("ws-1", "missing-item")

        err = exc_info.value
        assert err.status_code == 404
        assert err.error_code == "ItemNotFound"
        assert err.request_id == "req-123"
        assert err.is_retriable is False

    def test_malformed_error_body_falls_back_to_status_and_text(self, client):
        with patch.object(client._session, "request", return_value=_response(500, None, text="boom")):
            with pytest.raises(FabricApiError) as exc_info:
                client.get_item("ws-1", "item-1")
        assert exc_info.value.status_code == 500
        assert "boom" in str(exc_info.value)

    def test_empty_success_body_returns_none_shaped_dict(self, client):
        with patch.object(client._session, "request", return_value=_response(200)):
            result = client.update_item("ws-1", "item-1", display_name="X")
        assert result == {}

    def test_401_triggers_single_token_refresh_and_retry(self, client):
        responses = [_response(401, {"message": "expired"}), _response(200, {"id": "item-1"})]
        with patch.object(client, "_get_token", side_effect=["fake-token", "fresh-token"]):
            with patch.object(client._session, "request", side_effect=responses) as mock_req:
                result = client.get_item("ws-1", "item-1")

        assert result == {"id": "item-1"}
        assert mock_req.call_count == 2
        assert mock_req.call_args_list[1].kwargs["headers"]["Authorization"] == "Bearer fresh-token"


    def test_write_methods_are_excluded_from_automatic_retry(self, client):
        """POST/PATCH are non-idempotent Fabric mutations; retrying them on a
        transient 5xx risks double-applying a write that actually succeeded
        server-side, so they must not be in the retry adapter's allowlist."""
        adapter = client._session.get_adapter("https://api.fabric.microsoft.com")
        allowed_methods = adapter.max_retries.allowed_methods
        assert "POST" not in allowed_methods
        assert "PATCH" not in allowed_methods
        assert "GET" in allowed_methods


class TestAuthentication:
    def test_service_principal_env_vars_are_used_when_present(self, monkeypatch):
        monkeypatch.setenv("AZURE_CLIENT_ID", "client-id")
        monkeypatch.setenv("AZURE_CLIENT_SECRET", "secret")
        monkeypatch.setenv("AZURE_TENANT_ID", "tenant-id")

        fake_token = MagicMock()
        fake_token.token = "sp-token"

        with patch("purviewcli.client.fabric_client.ClientSecretCredential") as mock_cred_cls:
            mock_cred_cls.return_value.get_token.return_value = fake_token
            c = FabricClient(FabricConfig())
            token = c._get_token()

        assert token == "sp-token"
        mock_cred_cls.assert_called_once_with(tenant_id="tenant-id", client_id="client-id", client_secret="secret")

    def test_falls_back_to_azure_cli_when_no_service_principal(self, monkeypatch):
        for var in ("AZURE_CLIENT_ID", "AZURE_CLIENT_SECRET", "AZURE_TENANT_ID"):
            monkeypatch.delenv(var, raising=False)

        fake_token = MagicMock()
        fake_token.token = "cli-token"

        with patch("purviewcli.client.fabric_client._FabricCliCredential") as mock_cli_cls:
            mock_cli_cls.return_value.get_token.return_value = fake_token
            c = FabricClient(FabricConfig())
            token = c._get_token()

        assert token == "cli-token"

    def test_raises_credentials_error_when_all_methods_fail(self, monkeypatch):
        for var in ("AZURE_CLIENT_ID", "AZURE_CLIENT_SECRET", "AZURE_TENANT_ID"):
            monkeypatch.delenv(var, raising=False)

        from azure.core.exceptions import ClientAuthenticationError

        from purviewcli.client.fabric_client import FabricCliAuthenticationError

        with patch("purviewcli.client.fabric_client._FabricCliCredential") as mock_cli_cls, patch(
            "purviewcli.client.fabric_client.DefaultAzureCredential"
        ) as mock_default_cls:
            mock_cli_cls.return_value.get_token.side_effect = FabricCliAuthenticationError("no cli")
            mock_default_cls.return_value.get_token.side_effect = ClientAuthenticationError("no default")

            c = FabricClient(FabricConfig())
            with pytest.raises(FabricCredentialsError):
                c._get_token()


class TestConfig:
    def test_defaults(self):
        cfg = FabricConfig()
        assert cfg.base_url == "https://api.fabric.microsoft.com/v1"
        assert cfg.auth_scope == "https://api.fabric.microsoft.com/.default"

    def test_env_overrides(self, monkeypatch):
        monkeypatch.setenv("FABRIC_API_BASE_URL", "https://example.test/v1/")
        monkeypatch.setenv("FABRIC_AUTH_SCOPE", "https://example.test/.default")
        cfg = FabricConfig()
        assert cfg.base_url == "https://example.test/v1"
        assert cfg.auth_scope == "https://example.test/.default"
