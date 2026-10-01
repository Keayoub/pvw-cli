# SPDX-License-Identifier: Apache-2.0
"""Tests for the reusable Purview export-validation scenario."""

import json
from pathlib import Path

import pytest

from purviewcli.export.scenario import apply_scenario, load_scenario

SAMPLE = (
    Path(__file__).parents[1]
    / "samples"
    / "json"
    / "fabric_sync"
    / "purview_validation_scenario.json"
)


class FakeUC:
    def __init__(self):
        self.domains = []
        self.terms = []
        self.cdes = []
        self.products = []
        self.assets = []
        self.relationships = []

    def get_governance_domains(self, args):
        return {"value": self.domains}

    def create_governance_domain(self, args):
        row = {"id": "domain-1", **args["--payload"]}
        self.domains.append(row)
        return row

    def get_terms(self, args):
        return {"value": self.terms}

    def create_term(self, args):
        row = {
            "id": f"term-{len(self.terms) + 1}",
            "name": args["--name"][0],
            "description": args["--description"][0],
            "domain": args["--governance-domain-id"][0],
            "status": args["--status"][0],
        }
        self.terms.append(row)
        return row

    def get_critical_data_elements(self, args):
        return {"value": self.cdes}

    def create_critical_data_element(self, args):
        row = {
            "id": f"cde-{len(self.cdes) + 1}",
            "name": args["--name"][0],
            "description": args["--description"][0],
            "domain": args["--governance-domain-id"][0],
            "status": args["--status"][0],
            "dataType": args["--data-type"][0],
        }
        self.cdes.append(row)
        return row

    def get_data_products(self, args):
        return {"value": self.products}

    def create_data_product(self, args):
        row = {
            "id": "product-1",
            "name": args["--name"][0],
            "description": args["--description"][0],
            "domain": args["--governance-domain-id"][0],
            "status": args["--status"][0],
            "type": args["--type"][0],
            "businessUse": args["--business-use"][0],
        }
        self.products.append(row)
        return row

    def list_data_assets(self, args):
        return {"value": self.assets}

    def create_data_asset(self, args):
        payload = args["--payload"]
        row = {
            "id": f"asset-{len(self.assets) + 1}",
            **payload,
            "source": {
                **payload["source"],
                "fqn": (
                    "pvw-cli-validation/sales-orders@kaydemopurview"
                    if not self.assets
                    else "pvw-cli-validation/sales-customers@kaydemopurview"
                ),
            },
        }
        self.assets.append(row)
        return row

    def create_data_asset_relationship(self, args):
        self.relationships.append((args["--asset-id"], args["--payload"]))
        return args["--payload"]

    def list_data_asset_relationships(self, args):
        return {
            "value": [
                payload
                for asset_id, payload in self.relationships
                if asset_id == args["--asset-id"] and payload["entityType"] == args["--entity-type"]
            ]
        }


class FakeEntity:
    def __init__(self):
        self.created = []

    def entityCreate(self, args):
        self.created.append(args)
        index = len(self.created)
        return {"guidAssignments": {f"-{index}": f"entity-{index}"}}


def test_sample_scenario_is_complete():
    scenario = load_scenario(SAMPLE)
    assert len(scenario["terms"]) == 2
    assert len(scenario["criticalDataElements"]) == 2
    assert len(scenario["dataProducts"]) == 1
    assert len(scenario["assets"]) == 2


def test_dry_run_plans_complete_scenario_without_writes(tmp_path):
    uc = FakeUC()
    entity = FakeEntity()
    result = apply_scenario(uc, entity, SAMPLE, tmp_path / "state.json")
    assert result["dryRun"] is True
    assert len(result["actions"]) == 13
    assert {action["action"] for action in result["actions"]} == {"create"}
    assert not uc.domains
    assert not entity.created
    assert not (tmp_path / "state.json").exists()


def test_apply_is_idempotent_with_state_file(tmp_path):
    uc = FakeUC()
    entity = FakeEntity()
    state = tmp_path / "state.json"
    first = apply_scenario(uc, entity, SAMPLE, state, apply=True)
    assert first["stateWritten"] is True
    assert len(uc.domains) == 1
    assert len(uc.terms) == 2
    assert len(uc.cdes) == 2
    assert len(uc.products) == 1
    assert len(uc.assets) == 2
    assert len(entity.created) == 2
    assert len(uc.relationships) == 5

    second = apply_scenario(uc, entity, SAMPLE, state, apply=True)
    assert all(action["action"] == "reuse" for action in second["actions"])
    assert len(entity.created) == 2
    assert len(uc.relationships) == 5


def test_existing_drift_blocks_without_updates(tmp_path):
    uc = FakeUC()
    uc.domains.append(
        {
            "id": "domain-1",
            "name": "PVW CLI Validation Sales",
            "description": "Different",
            "type": "FunctionalUnit",
            "status": "Draft",
        }
    )
    with pytest.raises(ValueError, match="existing object differs"):
        apply_scenario(uc, FakeEntity(), SAMPLE, tmp_path / "state.json", apply=True)


def test_state_is_bound_to_exact_scenario(tmp_path):
    state = tmp_path / "state.json"
    apply_scenario(FakeUC(), FakeEntity(), SAMPLE, state, apply=True)
    changed = tmp_path / "changed.json"
    payload = json.loads(SAMPLE.read_text(encoding="utf-8"))
    payload["scenarioId"] = "another-scenario"
    changed.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="different scenario version"):
        apply_scenario(FakeUC(), FakeEntity(), changed, state)
