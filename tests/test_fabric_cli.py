# SPDX-License-Identifier: Apache-2.0
"""CLI-level tests for `pvw fabric sync` (assess/apply/run/rollback).

These tests exercise Click option parsing, dry-run gating, exit codes, and
report writing by monkeypatching the client-construction seam
(``purviewcli.cli.fabric._get_clients``) with lightweight fakes -- no real
network calls are made.
"""

import json
import os
import tempfile
from unittest.mock import MagicMock

import pytest
from click.testing import CliRunner

from purviewcli.cli.fabric import fabric


def test_sync_help_warns_against_production_use():
    result = CliRunner().invoke(fabric, ["sync", "--help"])
    assert result.exit_code == 0
    assert "Experimental. Do not use sync operations in production." in result.output


def test_operational_command_warns_before_assessment(monkeypatch):
    import purviewcli.cli.fabric as fabric_module

    def fail(*args, **kwargs):
        raise RuntimeError("assessment reached")

    monkeypatch.setattr(fabric_module, "_run_assessment", fail)
    result = CliRunner().invoke(fabric, ["sync", "assess"])
    assert "WARNING: Fabric sync is experimental. Do not use it in production." in result.output
    assert isinstance(result.exception, RuntimeError)


def test_json_assessment_does_not_emit_warning(monkeypatch):
    import purviewcli.cli.fabric as fabric_module

    def fail(*args, **kwargs):
        raise RuntimeError("assessment reached")

    monkeypatch.setattr(fabric_module, "_run_assessment", fail)
    result = CliRunner().invoke(fabric, ["sync", "assess", "--output", "json"])
    assert "WARNING" not in result.output
    assert isinstance(result.exception, RuntimeError)


# ---------------------------------------------------------------------------
# Fakes (mirrors tests/test_sync_service.py's fakes)
# ---------------------------------------------------------------------------


class FakeUcClient:
    def __init__(self, domains=(), assets=(), terms=(), data_products=(), cdes=()):
        self._domains = list(domains)
        self._assets = list(assets)
        self._terms = list(terms)
        self._data_products = list(data_products)
        self._cdes = list(cdes)

    def get_governance_domains(self, args):
        return {"value": self._domains}

    def list_data_assets(self, args):
        domain_id = args.get("--domain-id")
        if domain_id:
            return {"value": [a for a in self._assets if a.get("domainId") == domain_id]}
        return {"value": self._assets}

    def get_terms(self, args):
        return {"value": self._terms}

    def get_data_products(self, args):
        return {"value": self._data_products}

    def get_critical_data_elements(self, args):
        return {"value": self._cdes}


class FakeFabricClient:
    def __init__(self, catalog_entries=(), items=None, domains=(), domain_workspaces=None, tenant_tags=()):
        self._catalog_entries = list(catalog_entries)
        self._items = items or {}
        self._domains = list(domains)
        self._domain_workspaces = domain_workspaces or {}
        self._tenant_tags = list(tenant_tags)
        self.updated_items = []
        self.created_tags = []
        self.applied_tags = []
        self.unapplied_tags = []
        self.created_domains = []
        self.assigned = []
        self.unassigned = []

    def iter_catalog_entries(self):
        return iter(self._catalog_entries)

    def get_item(self, workspace_id, item_id):
        return self._items.get((workspace_id, item_id), {})

    def list_domains(self):
        return self._domains

    def list_domain_workspaces(self, domain_id):
        return self._domain_workspaces.get(domain_id, [])

    def list_tenant_tags(self):
        return self._tenant_tags

    def update_item(self, workspace_id, item_id, display_name=None, description=None):
        self.updated_items.append((workspace_id, item_id, display_name, description))
        return {}

    def bulk_create_tags(self, display_names):
        result = [{"id": f"tagid-{n}", "displayName": n} for n in display_names]
        self.created_tags.extend(display_names)
        return result

    def apply_tags(self, workspace_id, item_id, tag_ids):
        self.applied_tags.append((workspace_id, item_id, tag_ids))

    def unapply_tags(self, workspace_id, item_id, tag_ids):
        self.unapplied_tags.append((workspace_id, item_id, tag_ids))

    def create_domain(self, display_name, description=None):
        return {"id": "fd-1", "displayName": display_name}

    def assign_domain_workspaces(self, domain_id, workspace_ids):
        self.assigned.append((domain_id, workspace_ids))

    def unassign_domain_workspaces(self, domain_id, workspace_ids):
        self.unassigned.append((domain_id, workspace_ids))


def _one_matched_asset_scenario(display_name="", description=None):
    """A single Purview asset explicitly mapped to one Fabric item."""
    uc_client = FakeUcClient(assets=[{"id": "a1", "name": "Customer Table", "description": "A table."}])
    fabric_client = FakeFabricClient(
        catalog_entries=[
            {
                "id": "it1",
                "type": "Lakehouse",
                "displayName": display_name,
                "description": description,
                "workspaceId": "ws1",
                "workspaceDisplayName": "WS1",
            }
        ],
        items={("ws1", "it1"): {"displayName": display_name, "description": description, "tags": []}},
    )
    return uc_client, fabric_client


def _mapping_file(tmp_path):
    path = os.path.join(tmp_path, "mapping.json")
    with open(path, "w", encoding="utf-8") as handle:
        json.dump({"mappings": [{"purviewAssetId": "a1", "workspaceId": "ws1", "itemId": "it1"}]}, handle)
    return path


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def tmp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d


def _patch_clients(monkeypatch, uc_client, fabric_client, entity_client=None):
    if entity_client is None:
        entity_client = MagicMock()
    monkeypatch.setattr("purviewcli.cli.fabric._get_clients", lambda ctx: (uc_client, fabric_client, entity_client))


# ---------------------------------------------------------------------------
# assess
# ---------------------------------------------------------------------------


class TestAssess:
    def test_assess_ready_item_exits_zero_and_renders_table(self, runner, monkeypatch, tmp_dir):
        uc_client, fabric_client = _one_matched_asset_scenario()
        _patch_clients(monkeypatch, uc_client, fabric_client)
        mapping_path = _mapping_file(tmp_dir)

        result = runner.invoke(fabric, ["sync", "assess", "--mapping-file", mapping_path], obj={"profile": "default"})
        assert result.exit_code == 0, result.output
        assert "Assessment summary" in result.output
        assert fabric_client.updated_items == []  # assess never writes

    def test_assess_writes_json_and_csv_reports(self, runner, monkeypatch, tmp_dir):
        uc_client, fabric_client = _one_matched_asset_scenario()
        _patch_clients(monkeypatch, uc_client, fabric_client)
        mapping_path = _mapping_file(tmp_dir)
        report_path = os.path.join(tmp_dir, "report.json")
        csv_path = os.path.join(tmp_dir, "report.csv")

        result = runner.invoke(
            fabric,
            ["sync", "assess", "--mapping-file", mapping_path, "--report-file", report_path, "--csv-report-file", csv_path],
            obj={"profile": "default"},
        )
        assert result.exit_code == 0, result.output
        assert os.path.isfile(report_path)
        assert os.path.isfile(csv_path)
        with open(report_path, "r", encoding="utf-8") as handle:
            document = json.load(handle)
        assert "plan" in document
        assert document["plan"]["item_plans"][0]["decision"] == "ready"

    def test_assess_output_json_prints_plan(self, runner, monkeypatch, tmp_dir):
        uc_client, fabric_client = _one_matched_asset_scenario()
        _patch_clients(monkeypatch, uc_client, fabric_client)
        mapping_path = _mapping_file(tmp_dir)

        result = runner.invoke(
            fabric, ["sync", "assess", "--mapping-file", mapping_path, "--output", "json"], obj={"profile": "default"}
        )
        assert result.exit_code == 0, result.output
        payload = json.loads(result.output)
        assert payload["item_plans"][0]["decision"] == "ready"

    def test_assess_conflict_exits_nonzero(self, runner, monkeypatch, tmp_dir):
        # Fabric item already has a *different* display name -> conflict without --overwrite.
        uc_client, fabric_client = _one_matched_asset_scenario(display_name="Existing Name")
        _patch_clients(monkeypatch, uc_client, fabric_client)
        mapping_path = _mapping_file(tmp_dir)

        result = runner.invoke(fabric, ["sync", "assess", "--mapping-file", mapping_path], obj={"profile": "default"})
        assert result.exit_code == 1, result.output


# ---------------------------------------------------------------------------
# sync
# ---------------------------------------------------------------------------


class TestSync:
    def test_sync_defaults_to_dry_run(self, runner, monkeypatch, tmp_dir):
        uc_client, fabric_client = _one_matched_asset_scenario()
        _patch_clients(monkeypatch, uc_client, fabric_client)
        mapping_path = _mapping_file(tmp_dir)
        checkpoint_path = os.path.join(tmp_dir, "checkpoint.json")

        result = runner.invoke(
            fabric,
            ["sync", "apply", "--mapping-file", mapping_path, "--checkpoint-file", checkpoint_path],
            obj={"profile": "default"},
        )
        assert result.exit_code == 0, result.output
        assert "DRY RUN" in result.output
        assert fabric_client.updated_items == []
        assert not os.path.isfile(checkpoint_path)

    def test_sync_apply_writes_and_checkpoints(self, runner, monkeypatch, tmp_dir):
        uc_client, fabric_client = _one_matched_asset_scenario()
        _patch_clients(monkeypatch, uc_client, fabric_client)
        mapping_path = _mapping_file(tmp_dir)
        checkpoint_path = os.path.join(tmp_dir, "checkpoint.json")

        result = runner.invoke(
            fabric,
            ["sync", "apply", "--mapping-file", mapping_path, "--checkpoint-file", checkpoint_path, "--apply"],
            obj={"profile": "default"},
        )
        assert result.exit_code == 0, result.output
        assert "APPLIED" in result.output
        assert fabric_client.updated_items == [("ws1", "it1", "Customer Table", "A table.")]
        assert os.path.isfile(checkpoint_path)

    def test_sync_second_apply_is_idempotent_via_checkpoint(self, runner, monkeypatch, tmp_dir):
        uc_client, fabric_client = _one_matched_asset_scenario()
        _patch_clients(monkeypatch, uc_client, fabric_client)
        mapping_path = _mapping_file(tmp_dir)
        checkpoint_path = os.path.join(tmp_dir, "checkpoint.json")
        args = ["sync", "apply", "--mapping-file", mapping_path, "--checkpoint-file", checkpoint_path, "--apply"]

        runner.invoke(fabric, args, obj={"profile": "default"})
        assert len(fabric_client.updated_items) == 1

        result = runner.invoke(fabric, args, obj={"profile": "default"})
        assert result.exit_code == 0, result.output
        assert len(fabric_client.updated_items) == 1  # not reapplied


# ---------------------------------------------------------------------------
# run --config
# ---------------------------------------------------------------------------


class TestRunConfig:
    def test_run_config_delegates_to_sync(self, runner, monkeypatch, tmp_dir):
        uc_client, fabric_client = _one_matched_asset_scenario()
        _patch_clients(monkeypatch, uc_client, fabric_client)
        mapping_path = _mapping_file(tmp_dir)
        checkpoint_path = os.path.join(tmp_dir, "checkpoint.json")
        config_path = os.path.join(tmp_dir, "config.json")
        with open(config_path, "w", encoding="utf-8") as handle:
            json.dump(
                {"mapping_file": mapping_path, "checkpoint_file": checkpoint_path, "apply": True},
                handle,
            )

        result = runner.invoke(fabric, ["sync", "run", "--config", config_path], obj={"profile": "default"})
        assert result.exit_code == 0, result.output
        assert fabric_client.updated_items == [("ws1", "it1", "Customer Table", "A table.")]


# ---------------------------------------------------------------------------
# rollback
# ---------------------------------------------------------------------------


class TestRollback:
    def _apply_then_get_checkpoint(self, runner, monkeypatch, tmp_dir):
        uc_client, fabric_client = _one_matched_asset_scenario()
        _patch_clients(monkeypatch, uc_client, fabric_client)
        mapping_path = _mapping_file(tmp_dir)
        checkpoint_path = os.path.join(tmp_dir, "checkpoint.json")
        runner.invoke(
            fabric,
            ["sync", "apply", "--mapping-file", mapping_path, "--checkpoint-file", checkpoint_path, "--apply"],
            obj={"profile": "default"},
        )
        return fabric_client, checkpoint_path

    def test_rollback_previews_by_default(self, runner, monkeypatch, tmp_dir):
        fabric_client, checkpoint_path = self._apply_then_get_checkpoint(runner, monkeypatch, tmp_dir)
        applied_count = len(fabric_client.updated_items)

        result = runner.invoke(fabric, ["sync", "rollback", "--checkpoint-file", checkpoint_path], obj={"profile": "default"})
        assert result.exit_code == 0, result.output
        assert "PREVIEW" in result.output
        assert len(fabric_client.updated_items) == applied_count  # no new writes

    def test_rollback_apply_restores_prior_state(self, runner, monkeypatch, tmp_dir):
        fabric_client, checkpoint_path = self._apply_then_get_checkpoint(runner, monkeypatch, tmp_dir)

        result = runner.invoke(
            fabric, ["sync", "rollback", "--checkpoint-file", checkpoint_path, "--apply"], obj={"profile": "default"}
        )
        assert result.exit_code == 0, result.output
        assert "ROLLED BACK" in result.output
        assert fabric_client.updated_items[-1] == ("ws1", "it1", "", None)
