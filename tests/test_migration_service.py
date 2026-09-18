# SPDX-License-Identifier: Apache-2.0
"""Tests for purviewcli.migration.service (adapter/orchestration layer)."""

import json
import os
import tempfile

import pytest

from purviewcli.migration.models import (
    FabricDomain,
    MigrationMapping,
    OperationStatus,
    PurviewAsset,
    PurviewDomain,
    PurviewGovernanceObject,
)
from purviewcli.migration.service import (
    build_migration_plan,
    fetch_fabric_catalog,
    fetch_fabric_domains_and_workspace_assignments,
    fetch_fabric_item_state,
    fetch_purview_state,
    load_mapping_file,
    normalize_catalog_entries,
    normalize_fabric_domains,
    normalize_governance_objects,
    normalize_purview_assets,
    normalize_purview_domains,
    resolve_tag_names_to_ids,
    rollback_run,
    sync_plan,
)
from purviewcli.migration.state import CheckpointStore


# ---------------------------------------------------------------------------
# Fakes
# ---------------------------------------------------------------------------


class FakeUcClient:
    def __init__(self, domains=(), assets=(), terms=(), data_products=(), cdes=()):
        self._domains = list(domains)
        self._assets = list(assets)
        self._terms = list(terms)
        self._data_products = list(data_products)
        self._cdes = list(cdes)
        self.list_data_assets_calls = []

    def get_governance_domains(self, args):
        return {"value": self._domains}

    def list_data_assets(self, args):
        self.list_data_assets_calls.append(args)
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
        self.created_domains = []
        self.assigned = []
        self.unassigned = []
        self.unapplied_tags = []
        self._next_domain_id = 100

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
        domain_id = f"fd-{self._next_domain_id}"
        self._next_domain_id += 1
        self.created_domains.append(display_name)
        return {"id": domain_id, "displayName": display_name}

    def assign_domain_workspaces(self, domain_id, workspace_ids):
        self.assigned.append((domain_id, workspace_ids))

    def unassign_domain_workspaces(self, domain_id, workspace_ids):
        self.unassigned.append((domain_id, workspace_ids))


# ---------------------------------------------------------------------------
# Normalization
# ---------------------------------------------------------------------------


class TestNormalization:
    def test_normalize_purview_domains(self):
        raw = [{"id": "d1", "name": "Sales", "description": "desc", "parentId": None, "type": "BusinessUnit"}]
        domains = normalize_purview_domains(raw)
        assert domains == [PurviewDomain(id="d1", name="Sales", description="desc", parent_id=None, type="BusinessUnit")]

    def test_normalize_purview_assets_basic_fields(self):
        raw = [
            {
                "id": "a1",
                "name": "Customer Table",
                "description": "desc",
                "type": "Table",
                "domainId": "d1",
                "termIds": ["t1"],
                "dataProductIds": ["dp1"],
                "criticalDataElementIds": ["c1"],
            }
        ]
        assets = normalize_purview_assets(raw)
        assert len(assets) == 1
        asset = assets[0]
        assert asset.id == "a1"
        assert asset.domain_id == "d1"
        assert asset.term_ids == ["t1"]
        assert asset.data_product_ids == ["dp1"]
        assert asset.cde_ids == ["c1"]

    def test_normalize_purview_assets_missing_optional_fields_default_safely(self):
        assets = normalize_purview_assets([{"id": "a1", "name": "X"}])
        assert assets[0].term_ids == []
        assert assets[0].owners == []
        assert assets[0].domain_id is None

    def test_normalize_governance_objects_tags_object_type(self):
        objects = normalize_governance_objects(
            raw_terms=[{"id": "t1", "name": "PII"}],
            raw_data_products=[{"id": "dp1", "name": "Customer 360"}],
            raw_cdes=[{"id": "c1", "name": "SSN"}],
        )
        by_type = {o.object_type: o for o in objects}
        assert by_type["term"].name == "PII"
        assert by_type["data_product"].name == "Customer 360"
        assert by_type["cde"].name == "SSN"

    def test_normalize_catalog_entries(self):
        raw = [
            {
                "id": "item1",
                "type": "Lakehouse",
                "displayName": "Sales LH",
                "description": None,
                "workspaceId": "ws1",
                "workspaceDisplayName": "Sales WS",
            }
        ]
        entries = normalize_catalog_entries(raw)
        assert entries[0].workspace_id == "ws1"
        assert entries[0].display_name == "Sales LH"

    def test_normalize_catalog_entries_nested_hierarchy_workspace(self):
        # Verified live against POST /v1/catalog/search: the real Fabric API
        # nests workspace info under hierarchy.workspace, not flat
        # workspaceId/workspaceDisplayName fields.
        raw = [
            {
                "id": "item1",
                "type": "PowerBIApp",
                "displayName": "Sales LH",
                "description": None,
                "catalogEntryType": "App",
                "hierarchy": {"workspace": {"id": "ws1", "displayName": "Sales WS"}},
            }
        ]
        entries = normalize_catalog_entries(raw)
        assert entries[0].workspace_id == "ws1"
        assert entries[0].workspace_display_name == "Sales WS"
        assert entries[0].display_name == "Sales LH"

    def test_normalize_fabric_domains(self):
        raw = [{"id": "fd1", "displayName": "Finance", "description": None, "parentDomainId": None}]
        domains = normalize_fabric_domains(raw)
        assert domains == [FabricDomain(id="fd1", display_name="Finance", description=None, parent_domain_id=None)]


# ---------------------------------------------------------------------------
# Fetch helpers
# ---------------------------------------------------------------------------


class TestFetchHelpers:
    def test_fetch_purview_state_unfiltered(self):
        uc = FakeUcClient(
            domains=[{"id": "d1", "name": "Sales"}],
            assets=[{"id": "a1", "name": "X", "domainId": "d1"}],
            terms=[{"id": "t1", "name": "PII"}],
        )
        state = fetch_purview_state(uc)
        assert len(state["domains"]) == 1
        assert len(state["assets"]) == 1
        assert len(state["governance_objects"]) == 1
        assert uc.list_data_assets_calls == [{}]

    def test_fetch_purview_state_filters_by_domain(self):
        uc = FakeUcClient(
            domains=[{"id": "d1", "name": "Sales"}, {"id": "d2", "name": "HR"}],
            assets=[{"id": "a1", "name": "X", "domainId": "d1"}, {"id": "a2", "name": "Y", "domainId": "d2"}],
        )
        state = fetch_purview_state(uc, domain_ids=["d1"])
        assert [d.id for d in state["domains"]] == ["d1"]
        assert [a.id for a in state["assets"]] == ["a1"]
        assert uc.list_data_assets_calls == [{"--domain-id": "d1"}]

    def test_fetch_fabric_catalog_filters_by_workspace(self):
        client = FakeFabricClient(
            catalog_entries=[
                {"id": "i1", "type": "Lakehouse", "displayName": "A", "workspaceId": "ws1", "workspaceDisplayName": "WS1"},
                {"id": "i2", "type": "Lakehouse", "displayName": "B", "workspaceId": "ws2", "workspaceDisplayName": "WS2"},
            ]
        )
        entries = fetch_fabric_catalog(client, workspace_ids=["ws1"])
        assert [e.id for e in entries] == ["i1"]

    def test_fetch_fabric_item_state_normalizes_tags(self):
        client = FakeFabricClient(
            items={("ws1", "it1"): {"displayName": "A", "description": "d", "tags": [{"id": "t1", "displayName": "purview:term:PII"}]}}
        )
        state = fetch_fabric_item_state(client, "ws1", "it1")
        assert state.tag_names() == ["purview:term:PII"]

    def test_fetch_fabric_domains_and_workspace_assignments(self):
        client = FakeFabricClient(
            domains=[{"id": "fd1", "displayName": "Finance"}],
            domain_workspaces={"fd1": [{"id": "ws1"}, {"id": "ws2"}]},
        )
        domains, assignments = fetch_fabric_domains_and_workspace_assignments(client)
        assert [d.id for d in domains] == ["fd1"]
        assert assignments == {"ws1": "fd1", "ws2": "fd1"}

    def test_resolve_tag_names_to_ids(self):
        client = FakeFabricClient(tenant_tags=[{"id": "t1", "displayName": "purview:term:PII"}])
        resolved = resolve_tag_names_to_ids(client, ["purview:term:PII"])
        assert resolved == {"purview:term:PII": "t1"}


# ---------------------------------------------------------------------------
# Mapping file I/O
# ---------------------------------------------------------------------------


class TestMappingFile:
    def test_load_mapping_file_none_path_returns_none(self):
        assert load_mapping_file(None) is None

    def test_load_mapping_file_roundtrip(self):
        payload = {"mappings": [{"purviewAssetId": "a1", "workspaceId": "ws1", "itemId": "it1"}]}
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = os.path.join(tmp_dir, "mapping.json")
            with open(path, "w", encoding="utf-8") as handle:
                json.dump(payload, handle)
            mapping = load_mapping_file(path)
        assert isinstance(mapping, MigrationMapping)
        assert mapping.entries[0].purview_asset_id == "a1"


# ---------------------------------------------------------------------------
# End-to-end plan + apply + rollback
# ---------------------------------------------------------------------------


class TestBuildMigrationPlanAndApply:
    def _asset(self):
        return PurviewAsset(id="a1", name="Customer Table", description="A customer table.", domain_id="d1")

    def _catalog_entry_embedding_ref(self):
        # extract_embedded_fabric_ref looks for a `fabric_ref` shaped source; simplest writable
        # path for this test is an explicit mapping instead of embedded-ref detection.
        from purviewcli.migration.models import FabricCatalogEntry

        return FabricCatalogEntry(
            id="it1", type="Lakehouse", display_name="", description=None, workspace_id="ws1", workspace_display_name="WS1"
        )

    def test_build_plan_matches_via_mapping_and_diffs_metadata(self):
        asset = self._asset()
        entry = self._catalog_entry_embedding_ref()
        mapping = MigrationMapping.from_dict(
            {"mappings": [{"purviewAssetId": "a1", "workspaceId": "ws1", "itemId": "it1"}]}
        )
        fabric_client = FakeFabricClient(items={("ws1", "it1"): {"displayName": "", "description": None, "tags": []}})

        plan = build_migration_plan(
            run_id="run-1",
            purview_assets=[asset],
            purview_domains=[],
            governance_objects=[],
            catalog_entries=[entry],
            fabric_domains=[],
            workspace_current_domain={},
            fabric_client=fabric_client,
            mapping=mapping,
        )
        assert len(plan.matches) == 1
        assert plan.matches[0].outcome.value == "matched_by_mapping"
        assert len(plan.item_plans) == 1
        assert plan.item_plans[0].decision.value == "ready"

    def test_sync_plan_dry_run_makes_no_calls(self):
        asset = self._asset()
        entry = self._catalog_entry_embedding_ref()
        mapping = MigrationMapping.from_dict(
            {"mappings": [{"purviewAssetId": "a1", "workspaceId": "ws1", "itemId": "it1"}]}
        )
        fabric_client = FakeFabricClient(items={("ws1", "it1"): {"displayName": "", "description": None, "tags": []}})
        plan = build_migration_plan(
            run_id="run-1",
            purview_assets=[asset],
            purview_domains=[],
            governance_objects=[],
            catalog_entries=[entry],
            fabric_domains=[],
            workspace_current_domain={},
            fabric_client=fabric_client,
            mapping=mapping,
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            store = CheckpointStore(os.path.join(tmp_dir, "checkpoint.json"))
            result = sync_plan(fabric_client, plan, store, "run-1", dry_run=True)
        assert result.dry_run is True
        assert fabric_client.updated_items == []

    def test_sync_plan_apply_updates_item(self):
        asset = self._asset()
        entry = self._catalog_entry_embedding_ref()
        mapping = MigrationMapping.from_dict(
            {"mappings": [{"purviewAssetId": "a1", "workspaceId": "ws1", "itemId": "it1"}]}
        )
        fabric_client = FakeFabricClient(items={("ws1", "it1"): {"displayName": "", "description": None, "tags": []}})
        plan = build_migration_plan(
            run_id="run-1",
            purview_assets=[asset],
            purview_domains=[],
            governance_objects=[],
            catalog_entries=[entry],
            fabric_domains=[],
            workspace_current_domain={},
            fabric_client=fabric_client,
            mapping=mapping,
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            checkpoint_path = os.path.join(tmp_dir, "checkpoint.json")
            store = CheckpointStore(checkpoint_path)
            result = sync_plan(fabric_client, plan, store, "run-1", dry_run=False)
            assert result.succeeded_count == 1
            assert fabric_client.updated_items == [("ws1", "it1", "Customer Table", "A customer table.")]

            # Rollback restores the pre-apply (blank) state.
            rollback_result = rollback_run(fabric_client, store, dry_run=False)
            assert rollback_result.run_id == "run-1"
            assert len(rollback_result.results) == 1
            assert rollback_result.results[0].status == OperationStatus.ROLLED_BACK
            assert fabric_client.updated_items[-1] == ("ws1", "it1", "", None)

    def test_rollback_with_no_checkpoint_returns_empty_result(self):
        fabric_client = FakeFabricClient()
        with tempfile.TemporaryDirectory() as tmp_dir:
            store = CheckpointStore(os.path.join(tmp_dir, "checkpoint.json"))
            result = rollback_run(fabric_client, store, dry_run=True)
        assert result.run_id == ""
        assert result.results == []
