# SPDX-License-Identifier: Apache-2.0
"""Standalone Unified Catalog export tests; no network or Fabric tenant."""

import json
import hashlib

import pytest
from click.testing import CliRunner

from purviewcli.cli.unified_catalog import uc
from purviewcli.cli.fabric import fabric
from purviewcli.export.catalog import export_catalog
from purviewcli.export.decisions import load_reviewed_snapshot


class FakeUC:
    def __init__(self):
        self.calls = []

    def get_governance_domains(self, args):
        return {"value": [{"id": "d1", "name": "Sales", "description": "Sales domain"}]}

    def list_data_assets(self, args):
        self.calls.append(args)
        return {
            "value": [
                {
                    "id": "a1",
                    "name": "Orders",
                    "domainId": "d1",
                    "termIds": ["t1"],
                    "dataProductIds": ["p1"],
                    "criticalDataElementIds": ["c1"],
                }
            ]
        }

    def get_terms(self, args):
        return {
            "value": [{"id": "t1", "name": "Order", "description": "An order", "domainId": "d1"}]
        }

    def get_data_products(self, args):
        return {
            "value": [
                {"id": "p1", "name": "Sales data", "description": "Curated", "domainId": "d1"}
            ]
        }

    def get_critical_data_elements(self, args):
        return {"value": [{"id": "c1", "name": "Order ID", "domainId": "d1"}]}


def test_export_writes_related_portable_json(tmp_path):
    client = FakeUC()
    path = tmp_path / "snapshot"
    manifest = export_catalog(client, path)
    assert client.calls == [{"--skip": 0, "--top": 100}]
    assert set(p.name for p in path.iterdir()) == {
        "assets.json",
        "domains.json",
        "terms.json",
        "data_products.json",
        "cdes.json",
        "manifest.json",
        "decisions.example.json",
    }
    assert manifest["schemaVersion"] == 1
    assert manifest["lineageIncluded"] is False
    assert manifest["files"]["assets.json"] == 1
    asset = json.loads((path / "assets.json").read_text(encoding="utf-8"))[0]
    term = json.loads((path / "terms.json").read_text(encoding="utf-8"))[0]
    assert asset["term_ids"] == [term["id"]]
    assert asset["domain_id"] == "d1"
    assert term["description"] == "An order"


def test_export_refuses_existing_destination(tmp_path):
    path = tmp_path / "snapshot"
    path.mkdir()
    with pytest.raises(FileExistsError):
        export_catalog(FakeUC(), path)


def test_export_aborts_on_unfollowed_continuation_without_partial_files(tmp_path):
    class TruncatedUC(FakeUC):
        def get_terms(self, args):
            return {"value": [], "nextLink": "more"}

    path = tmp_path / "snapshot"
    with pytest.raises(ValueError, match="continuation"):
        export_catalog(TruncatedUC(), path)
    assert not path.exists()


@pytest.mark.parametrize(
    "method",
    [
        "get_governance_domains",
        "get_terms",
        "get_data_products",
        "get_critical_data_elements",
    ],
)
def test_export_aborts_on_incomplete_business_object_page(tmp_path, method):
    class IncompleteUC(FakeUC):
        pass

    original = getattr(FakeUC, method)

    def incomplete(self, args):
        response = original(self, args)
        return {**response, "totalCount": len(response["value"]) + 1}

    setattr(IncompleteUC, method, incomplete)
    path = tmp_path / "snapshot"
    with pytest.raises(ValueError, match="totalCount mismatch"):
        export_catalog(IncompleteUC(), path)
    assert not path.exists()


def test_export_aborts_on_changed_asset_total_count(tmp_path):
    class ChangingUC(FakeUC):
        def list_data_assets(self, args):
            if args["--skip"] == 0:
                return {
                    "value": [{"id": f"asset-{i}", "name": str(i)} for i in range(100)],
                    "totalCount": 101,
                }
            return {"value": [{"id": "asset-100", "name": "100"}], "totalCount": 102}

    path = tmp_path / "snapshot"
    with pytest.raises(ValueError, match="changed between pages"):
        export_catalog(ChangingUC(), path)
    assert not path.exists()


def test_export_aborts_on_missing_domain_id(tmp_path):
    class InvalidUC(FakeUC):
        def get_governance_domains(self, args):
            return {"value": [{"name": "Sales"}]}

    with pytest.raises(ValueError, match="domains"):
        export_catalog(InvalidUC(), tmp_path / "snapshot")
    assert not (tmp_path / "snapshot").exists()


def test_export_aborts_when_asset_pagination_repeats(tmp_path):
    class RepeatingUC(FakeUC):
        def list_data_assets(self, args):
            return {"value": [{"id": "same", "name": "Asset"}] * 100}

    with pytest.raises(ValueError, match="duplicate ID"):
        export_catalog(RepeatingUC(), tmp_path / "snapshot")
    assert not (tmp_path / "snapshot").exists()


def test_export_reads_all_asset_pages(tmp_path):
    class PagedUC(FakeUC):
        def list_data_assets(self, args):
            self.calls.append(args)
            start = args["--skip"]
            if start == 0:
                return {"value": [{"id": f"asset-{i}", "name": str(i)} for i in range(100)]}
            return {"value": [{"id": "asset-100", "name": "100"}]}

    client = PagedUC()
    export_catalog(client, tmp_path / "snapshot")
    assert [call["--skip"] for call in client.calls] == [0, 100]
    assert (
        len(json.loads((tmp_path / "snapshot" / "assets.json").read_text(encoding="utf-8"))) == 101
    )


def test_cli_requires_no_fabric_client(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "purviewcli.client.client_cache.get_cached_client",
        lambda cls, profile: FakeUC(),
    )
    output = tmp_path / "snapshot"
    result = CliRunner().invoke(uc, ["export", "--output-dir", str(output)])
    assert result.exit_code == 0, result.output
    assert (output / "manifest.json").exists()
    assert "OK Purview export saved" in result.output


def reviewed_export(tmp_path):
    folder = tmp_path / "snapshot"
    export_catalog(FakeUC(), folder)
    decisions = tmp_path / "decisions.json"
    reviewed = json.loads((folder / "decisions.example.json").read_text(encoding="utf-8"))
    reviewed.update(
        {
            "selectedAssetIds": ["a1"],
            "descriptions": {"a1": "Approved description"},
            "mappings": [
                {
                    "purviewAssetId": "a1",
                    "workspaceId": "ws1",
                    "itemId": "i1",
                    "expectedFabricType": "Lakehouse",
                }
            ],
        }
    )
    decisions.write_text(json.dumps(reviewed), encoding="utf-8")
    return folder, decisions


def test_reviewed_snapshot_uses_decisions_and_rejects_modified_export(tmp_path):
    folder, decisions = reviewed_export(tmp_path)
    checked = CliRunner().invoke(
        uc, ["validate-export", "--snapshot-dir", str(folder), "--decisions-file", str(decisions)]
    )
    assert checked.exit_code == 0, checked.output
    state, mapping = load_reviewed_snapshot(folder, decisions)
    assert state["assets"][0].description == "Approved description"
    assert state["assets"][0].source == {}
    assert state["domains"] == []
    assert mapping.entries[0].item_id == "i1"
    (folder / "assets.json").write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError, match="checksum"):
        load_reviewed_snapshot(folder, decisions)


def test_reviewed_snapshot_requires_explicit_selected_mapping(tmp_path):
    folder, decisions = reviewed_export(tmp_path)
    reviewed = json.loads(decisions.read_text(encoding="utf-8"))
    reviewed["mappings"] = []
    decisions.write_text(json.dumps(reviewed), encoding="utf-8")
    with pytest.raises(ValueError, match="Every selected asset"):
        load_reviewed_snapshot(folder, decisions)
    result = CliRunner().invoke(
        uc, ["validate-export", "--snapshot-dir", str(folder), "--decisions-file", str(decisions)]
    )
    assert result.exit_code != 0
    assert "Every selected asset" in result.output


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("purviewAssetId", ["a1"]),
        ("workspaceId", {"id": "ws1"}),
        ("itemId", 42),
        ("expectedFabricType", ["Lakehouse"]),
    ],
)
def test_reviewed_snapshot_rejects_malformed_mapping_fields(tmp_path, field, value):
    folder, decisions = reviewed_export(tmp_path)
    reviewed = json.loads(decisions.read_text(encoding="utf-8"))
    reviewed["mappings"][0][field] = value
    decisions.write_text(json.dumps(reviewed), encoding="utf-8")
    with pytest.raises(ValueError, match=field):
        load_reviewed_snapshot(folder, decisions)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("term_ids", [{"id": "t1"}], "unresolved term_ids"),
        ("type", ["Lakehouse"], "type must be a string"),
    ],
)
def test_reviewed_snapshot_rejects_malformed_asset_fields(tmp_path, field, value, message):
    folder, decisions = reviewed_export(tmp_path)
    path = folder / "assets.json"
    assets = json.loads(path.read_text(encoding="utf-8"))
    assets[0][field] = value
    path.write_text(json.dumps(assets), encoding="utf-8")
    manifest_path = folder / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["sha256"]["assets.json"] = hashlib.sha256(path.read_bytes()).hexdigest()
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    reviewed = json.loads(decisions.read_text(encoding="utf-8"))
    reviewed["snapshotSha256"] = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    decisions.write_text(json.dumps(reviewed), encoding="utf-8")
    with pytest.raises(ValueError, match=message):
        load_reviewed_snapshot(folder, decisions)


def _rewrite_manifest(folder, decisions, **changes):
    manifest_path = folder / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for key, value in changes.items():
        if key == "assets_count":
            manifest["files"]["assets.json"] = value
        else:
            manifest[key] = value
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    reviewed = json.loads(decisions.read_text(encoding="utf-8"))
    reviewed["snapshotSha256"] = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    decisions.write_text(json.dumps(reviewed), encoding="utf-8")


def test_reviewed_snapshot_rejects_boolean_manifest_schema_version(tmp_path):
    folder, decisions = reviewed_export(tmp_path)
    _rewrite_manifest(folder, decisions, schemaVersion=True)
    with pytest.raises(ValueError, match="Unsupported or unverified snapshot manifest"):
        load_reviewed_snapshot(folder, decisions)


def test_reviewed_snapshot_rejects_boolean_manifest_count(tmp_path):
    folder, decisions = reviewed_export(tmp_path)
    _rewrite_manifest(folder, decisions, assets_count=True)
    with pytest.raises(ValueError, match="manifest count mismatch"):
        load_reviewed_snapshot(folder, decisions)


def test_reviewed_snapshot_rejects_boolean_decisions_schema_version(tmp_path):
    folder, decisions = reviewed_export(tmp_path)
    reviewed = json.loads(decisions.read_text(encoding="utf-8"))
    reviewed["schemaVersion"] = True
    decisions.write_text(json.dumps(reviewed), encoding="utf-8")
    with pytest.raises(ValueError, match="snapshot version"):
        load_reviewed_snapshot(folder, decisions)


def test_reviewed_snapshot_rejects_broken_term_reference(tmp_path):
    folder, decisions = reviewed_export(tmp_path)
    terms = folder / "terms.json"
    terms.write_text("[]", encoding="utf-8")
    manifest_path = folder / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["sha256"]["terms.json"] = hashlib.sha256(terms.read_bytes()).hexdigest()
    manifest["files"]["terms.json"] = 0
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    reviewed = json.loads(decisions.read_text(encoding="utf-8"))
    reviewed["snapshotSha256"] = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    decisions.write_text(json.dumps(reviewed), encoding="utf-8")
    with pytest.raises(ValueError, match="unresolved term_ids"):
        load_reviewed_snapshot(folder, decisions)


class FakeFabric:
    def __init__(self):
        self.updated_items = []
        self.created_tags = []
        self.applied_tags = []

    def iter_catalog_entries(self):
        return iter(
            [
                {
                    "id": "i1",
                    "type": "Lakehouse",
                    "displayName": "",
                    "workspaceId": "ws1",
                    "workspaceDisplayName": "WS1",
                }
            ]
        )

    def list_domains(self):
        raise AssertionError("Reviewed snapshot must not read Fabric admin domains")

    def get_item(self, workspace_id, item_id):
        return {
            "id": item_id,
            "workspaceId": workspace_id,
            "type": "Lakehouse",
            "displayName": "",
            "description": None,
            "tags": [],
        }

    def list_tenant_tags(self):
        return []

    def update_item(self, workspace_id, item_id, display_name=None, description=None):
        self.updated_items.append((workspace_id, item_id, display_name, description))
        return {}

    def bulk_create_tags(self, names):
        self.created_tags.extend(names)
        return [{"id": f"tag-{name}", "displayName": name} for name in names]

    def apply_tags(self, workspace_id, item_id, tag_ids):
        self.applied_tags.append((workspace_id, item_id, tag_ids))


def test_snapshot_assess_no_purview_reads_and_dry_run_apply(tmp_path, monkeypatch):
    folder, decisions = reviewed_export(tmp_path)
    client = FakeFabric()

    def get_client(cls, profile):
        assert cls.__name__ == "FabricClient"
        return client

    monkeypatch.setattr("purviewcli.client.client_cache.get_cached_client", get_client)
    monkeypatch.setattr(
        "purviewcli.cli.fabric._get_clients", lambda ctx: pytest.fail("Purview read")
    )
    args = ["--snapshot-dir", str(folder), "--decisions-file", str(decisions), "--output", "json"]
    assessed = CliRunner().invoke(fabric, ["sync", "assess", *args], obj={"profile": "default"})
    assert assessed.exit_code == 0, assessed.output
    plan = json.loads(assessed.output)
    assert plan["domain_plans"] == []
    assert plan["item_plans"][0]["changes"][1]["desired"] == "Approved description"
    applied = CliRunner().invoke(
        fabric,
        ["sync", "apply", *args, "--checkpoint-file", str(tmp_path / "checkpoint.json")],
        obj={"profile": "default"},
    )
    assert applied.exit_code == 0, applied.output
    assert json.loads(applied.output)["syncResult"]["dry_run"] is True
    assert client.updated_items == []
    written = CliRunner().invoke(
        fabric,
        ["sync", "apply", *args, "--checkpoint-file", str(tmp_path / "checkpoint.json"), "--apply"],
        obj={"profile": "default"},
    )
    assert written.exit_code == 0, written.output
    assert client.updated_items == [("ws1", "i1", "Orders", "Approved description")]
    assert client.applied_tags


def test_snapshot_assess_plans_from_the_verified_item_response(tmp_path, monkeypatch):
    folder, decisions = reviewed_export(tmp_path)
    client = FakeFabric()
    reads = []

    def get_item(workspace_id, item_id):
        reads.append((workspace_id, item_id))
        if len(reads) > 1:
            raise AssertionError("Planner must not re-read an unverified item response")
        return {
            "id": item_id,
            "workspaceId": workspace_id,
            "type": "Lakehouse",
            "displayName": "",
            "description": None,
            "tags": [],
        }

    client.get_item = get_item
    monkeypatch.setattr(
        "purviewcli.client.client_cache.get_cached_client", lambda cls, profile: client
    )
    result = CliRunner().invoke(
        fabric,
        [
            "sync",
            "assess",
            "--snapshot-dir",
            str(folder),
            "--decisions-file",
            str(decisions),
            "--output",
            "json",
        ],
        obj={"profile": "default"},
    )
    assert result.exit_code == 0, result.output
    assert reads == [("ws1", "i1")]
    assert (
        json.loads(result.output)["item_plans"][0]["changes"][1]["desired"]
        == "Approved description"
    )


def test_snapshot_import_rejects_classification_flag(tmp_path, monkeypatch):
    folder, decisions = reviewed_export(tmp_path)
    monkeypatch.setattr(
        "purviewcli.client.client_cache.get_cached_client", lambda cls, profile: FakeFabric()
    )
    result = CliRunner().invoke(
        fabric,
        [
            "sync",
            "assess",
            "--snapshot-dir",
            str(folder),
            "--decisions-file",
            str(decisions),
            "--sync-classifications",
        ],
    )
    assert result.exit_code != 0
    assert "not supported for snapshot imports" in result.output


def test_run_config_accepts_snapshot_and_decisions(tmp_path, monkeypatch):
    folder, decisions = reviewed_export(tmp_path)
    monkeypatch.setattr(
        "purviewcli.client.client_cache.get_cached_client",
        lambda cls, profile: FakeFabric(),
    )
    monkeypatch.setattr(
        "purviewcli.cli.fabric._get_clients", lambda ctx: pytest.fail("Purview read")
    )
    config = tmp_path / "run.json"
    config.write_text(
        json.dumps(
            {
                "snapshot_dir": str(folder),
                "decisions_file": str(decisions),
                "checkpoint_file": str(tmp_path / "checkpoint.json"),
                "output": "json",
            }
        ),
        encoding="utf-8",
    )
    result = CliRunner().invoke(
        fabric, ["sync", "run", "--config", str(config)], obj={"profile": "default"}
    )
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["syncResult"]["dry_run"] is True


def test_snapshot_assess_fails_on_missing_target(tmp_path, monkeypatch):
    folder, decisions = reviewed_export(tmp_path)
    client = FakeFabric()
    client.iter_catalog_entries = lambda: iter([])
    monkeypatch.setattr(
        "purviewcli.client.client_cache.get_cached_client", lambda cls, profile: client
    )
    result = CliRunner().invoke(
        fabric,
        ["sync", "assess", "--snapshot-dir", str(folder), "--decisions-file", str(decisions)],
        obj={"profile": "default"},
    )
    assert result.exit_code != 0
    assert "not present in the current catalog scope" in result.output


def test_snapshot_apply_blocks_all_writes_on_metadata_conflict(tmp_path, monkeypatch):
    folder, decisions = reviewed_export(tmp_path)
    client = FakeFabric()
    client.get_item = lambda workspace_id, item_id: {
        "id": item_id,
        "workspaceId": workspace_id,
        "type": "Lakehouse",
        "displayName": "Another name",
        "description": None,
        "tags": [],
    }
    monkeypatch.setattr(
        "purviewcli.client.client_cache.get_cached_client", lambda cls, profile: client
    )
    result = CliRunner().invoke(
        fabric,
        [
            "sync",
            "apply",
            "--snapshot-dir",
            str(folder),
            "--decisions-file",
            str(decisions),
            "--checkpoint-file",
            str(tmp_path / "checkpoint.json"),
            "--apply",
        ],
        obj={"profile": "default"},
    )
    assert result.exit_code == 1
    assert client.updated_items == []
    assert client.created_tags == []
    assert client.applied_tags == []


def test_prepare_offers_typed_candidates_without_approving_anything(tmp_path, monkeypatch):
    folder, _ = reviewed_export(tmp_path)
    client = FakeFabric()
    client.iter_catalog_entries = lambda: iter(
        [
            {
                "id": "i1",
                "type": "Lakehouse",
                "catalogEntryType": "FabricItem",
                "displayName": "Orders",
                "workspaceId": "ws1",
                "workspaceDisplayName": "Sales",
            },
            {
                "id": "i2",
                "type": "SemanticModel",
                "catalogEntryType": "FabricItem",
                "displayName": "Orders",
                "workspaceId": "ws2",
                "workspaceDisplayName": "Analytics",
            },
            {
                "id": "ws3",
                "type": "Workspace",
                "catalogEntryType": "Workspace",
                "displayName": "Orders",
            },
        ]
    )
    monkeypatch.setattr(
        "purviewcli.client.client_cache.get_cached_client", lambda cls, profile: client
    )
    monkeypatch.setattr(
        "purviewcli.cli.fabric._get_clients", lambda ctx: pytest.fail("Purview read")
    )
    output = tmp_path / "draft.json"
    result = CliRunner().invoke(
        fabric,
        [
            "sync",
            "prepare",
            "--snapshot-dir",
            str(folder),
            "--output-file",
            str(output),
        ],
        obj={"profile": "default"},
    )
    assert result.exit_code == 0, result.output
    draft = json.loads(output.read_text(encoding="utf-8"))
    assert draft["selectedAssetIds"] == []
    assert draft["mappings"] == []
    assert draft["candidates"][0]["reviewStatus"] == "multiple_candidates"
    assert {(c["workspaceId"], c["fabricType"]) for c in draft["candidates"][0]["suggestions"]} == {
        ("ws1", "Lakehouse"),
        ("ws2", "SemanticModel"),
    }
    assert {
        c["proposedMapping"]["expectedFabricType"] for c in draft["candidates"][0]["suggestions"]
    } == {"Lakehouse", "SemanticModel"}
    assert draft["candidates"][0]["suggestions"][0]["proposedMapping"] == {
        "purviewAssetId": "a1",
        "workspaceId": "ws1",
        "itemId": "i1",
        "expectedFabricType": "Lakehouse",
    }
    again = CliRunner().invoke(
        fabric,
        [
            "sync",
            "prepare",
            "--snapshot-dir",
            str(folder),
            "--output-file",
            str(output),
        ],
        obj={"profile": "default"},
    )
    assert again.exit_code != 0


def test_single_candidate_can_be_explicitly_approved(tmp_path, monkeypatch):
    folder, _ = reviewed_export(tmp_path)
    client = FakeFabric()
    client.iter_catalog_entries = lambda: iter(
        [
            {
                "id": "i1",
                "type": "Lakehouse",
                "catalogEntryType": "FabricItem",
                "displayName": "Orders",
                "workspaceId": "ws1",
                "workspaceDisplayName": "Sales",
            }
        ]
    )
    monkeypatch.setattr(
        "purviewcli.client.client_cache.get_cached_client", lambda cls, profile: client
    )
    output = tmp_path / "draft.json"
    result = CliRunner().invoke(
        fabric,
        ["sync", "prepare", "--snapshot-dir", str(folder), "--output-file", str(output)],
        obj={"profile": "default"},
    )
    assert result.exit_code == 0, result.output
    draft = json.loads(output.read_text(encoding="utf-8"))
    assert draft["candidates"][0]["reviewStatus"] == "single_candidate"
    assert draft["selectedAssetIds"] == []
    assert draft["mappings"] == []
    unapproved = CliRunner().invoke(
        uc, ["validate-export", "--snapshot-dir", str(folder), "--decisions-file", str(output)]
    )
    assert unapproved.exit_code != 0
    draft["selectedAssetIds"] = ["a1"]
    draft["mappings"] = [draft["candidates"][0]["suggestions"][0]["proposedMapping"]]
    output.write_text(json.dumps(draft), encoding="utf-8")
    approved = CliRunner().invoke(
        uc, ["validate-export", "--snapshot-dir", str(folder), "--decisions-file", str(output)]
    )
    assert approved.exit_code == 0, approved.output


def test_prepare_reports_no_candidate_without_selecting_asset(tmp_path, monkeypatch):
    folder, _ = reviewed_export(tmp_path)
    monkeypatch.setattr(
        "purviewcli.client.client_cache.get_cached_client",
        lambda cls, profile: FakeFabric(),
    )
    output = tmp_path / "draft.json"
    result = CliRunner().invoke(
        fabric,
        ["sync", "prepare", "--snapshot-dir", str(folder), "--output-file", str(output)],
        obj={"profile": "default"},
    )
    assert result.exit_code == 0, result.output
    draft = json.loads(output.read_text(encoding="utf-8"))
    assert draft["candidates"][0]["reviewStatus"] == "no_candidate"
    assert draft["candidates"][0]["suggestions"] == []
    assert draft["selectedAssetIds"] == []
    assert draft["mappings"] == []


def test_existing_semantic_model_is_assessed_without_recreation(tmp_path, monkeypatch):
    folder, decisions = reviewed_export(tmp_path)
    reviewed = json.loads(decisions.read_text(encoding="utf-8"))
    reviewed["mappings"][0]["expectedFabricType"] = "SemanticModel"
    decisions.write_text(json.dumps(reviewed), encoding="utf-8")
    client = FakeFabric()
    client.iter_catalog_entries = lambda: iter(
        [
            {
                "id": "i1",
                "type": "SemanticModel",
                "catalogEntryType": "FabricItem",
                "displayName": "Orders",
                "workspaceId": "ws1",
                "workspaceDisplayName": "WS1",
            }
        ]
    )
    client.get_item = lambda workspace_id, item_id: {
        "id": item_id,
        "workspaceId": workspace_id,
        "type": "SemanticModel",
        "displayName": "Orders",
        "description": None,
        "tags": [],
    }
    monkeypatch.setattr(
        "purviewcli.client.client_cache.get_cached_client", lambda cls, profile: client
    )
    result = CliRunner().invoke(
        fabric,
        [
            "sync",
            "assess",
            "--snapshot-dir",
            str(folder),
            "--decisions-file",
            str(decisions),
            "--output",
            "json",
        ],
        obj={"profile": "default"},
    )
    assert result.exit_code == 0, result.output
    plan = json.loads(result.output)
    assert plan["item_plans"][0]["changes"][0]["field"] == "description"
    assert plan["item_plans"][0]["changes"][0]["desired"] == "Approved description"
    assert client.updated_items == []


@pytest.mark.parametrize("where", ["decision", "catalog", "item", "identity"])
def test_type_mismatch_blocks_reviewed_apply(tmp_path, monkeypatch, where):
    folder, decisions = reviewed_export(tmp_path)
    client = FakeFabric()
    if where == "decision":
        raw = json.loads(decisions.read_text(encoding="utf-8"))
        raw["mappings"][0]["expectedFabricType"] = "SemanticModel"
        decisions.write_text(json.dumps(raw), encoding="utf-8")
    if where == "catalog":
        client.iter_catalog_entries = lambda: iter(
            [
                {
                    "id": "i1",
                    "type": "SemanticModel",
                    "catalogEntryType": "FabricItem",
                    "displayName": "Orders",
                    "workspaceId": "ws1",
                    "workspaceDisplayName": "Sales",
                }
            ]
        )
    if where == "item":
        client.get_item = lambda workspace_id, item_id: {
            "id": item_id,
            "workspaceId": workspace_id,
            "type": "SemanticModel",
            "displayName": "",
            "description": None,
            "tags": [],
        }
    if where == "identity":
        client.get_item = lambda workspace_id, item_id: {
            "id": "different-item",
            "workspaceId": workspace_id,
            "type": "Lakehouse",
            "displayName": "",
            "description": None,
            "tags": [],
        }
    monkeypatch.setattr(
        "purviewcli.client.client_cache.get_cached_client", lambda cls, profile: client
    )
    result = CliRunner().invoke(
        fabric,
        [
            "sync",
            "apply",
            "--snapshot-dir",
            str(folder),
            "--decisions-file",
            str(decisions),
            "--checkpoint-file",
            str(tmp_path / "checkpoint.json"),
            "--apply",
        ],
        obj={"profile": "default"},
    )
    assert result.exit_code != 0
    assert "mismatch" in result.output
    assert client.updated_items == []
    assert client.applied_tags == []


def test_known_source_type_cannot_be_mapped_to_other_type(tmp_path):
    folder, decisions = reviewed_export(tmp_path)
    asset_file = folder / "assets.json"
    records = json.loads(asset_file.read_text(encoding="utf-8"))
    records[0]["type"] = "SemanticModel"
    asset_file.write_text(json.dumps(records), encoding="utf-8")
    manifest_file = folder / "manifest.json"
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    manifest["sha256"]["assets.json"] = hashlib.sha256(asset_file.read_bytes()).hexdigest()
    manifest_file.write_text(json.dumps(manifest), encoding="utf-8")
    raw = json.loads(decisions.read_text(encoding="utf-8"))
    raw["snapshotSha256"] = hashlib.sha256(manifest_file.read_bytes()).hexdigest()
    decisions.write_text(json.dumps(raw), encoding="utf-8")
    with pytest.raises(ValueError, match="conflicts with Purview type"):
        load_reviewed_snapshot(folder, decisions)
