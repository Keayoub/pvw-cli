# SPDX-License-Identifier: Apache-2.0
"""Idempotent Purview test-data scenarios for export validation."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

SCHEMA_VERSION = 1


def _rows(response: Any, label: str) -> List[Dict[str, Any]]:
    if isinstance(response, list):
        rows = response
    elif isinstance(response, dict):
        rows = response.get("value", [])
    else:
        raise ValueError(f"{label}: expected a list response")
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise ValueError(f"{label}: expected a list of objects")
    return rows


def load_scenario(path: Path) -> Dict[str, Any]:
    path = Path(path)
    with path.open(encoding="utf-8") as handle:
        scenario = json.load(handle)
    if not isinstance(scenario, dict):
        raise ValueError("Scenario must be a JSON object")
    if (
        isinstance(scenario.get("schemaVersion"), bool)
        or scenario.get("schemaVersion") != SCHEMA_VERSION
    ):
        raise ValueError("Unsupported scenario schemaVersion")
    required = {
        "schemaVersion",
        "scenarioId",
        "domain",
        "terms",
        "criticalDataElements",
        "dataProducts",
        "assets",
    }
    if set(scenario) != required:
        raise ValueError(f"Scenario keys must be exactly: {', '.join(sorted(required))}")
    if not isinstance(scenario["scenarioId"], str) or not scenario["scenarioId"].strip():
        raise ValueError("scenarioId must be a nonempty string")
    domain = scenario["domain"]
    if not isinstance(domain, dict):
        raise ValueError("domain must be an object")
    collections = ("terms", "criticalDataElements", "dataProducts", "assets")
    if any(not isinstance(scenario[name], list) for name in collections):
        raise ValueError("terms, criticalDataElements, dataProducts and assets must be arrays")

    keyed = [domain] + [row for name in collections for row in scenario[name]]
    keys = []
    for row in keyed:
        if not isinstance(row, dict):
            raise ValueError("Scenario resources must be objects")
        for field in ("key", "name", "description"):
            if not isinstance(row.get(field), str) or not row[field].strip():
                raise ValueError(f"Scenario resource {field} must be a nonempty string")
        keys.append(row["key"])
    if len(set(keys)) != len(keys):
        raise ValueError("Scenario resource keys must be unique")
    known_keys = set(keys)
    for asset in scenario["assets"]:
        for field in ("termKeys", "criticalDataElementKeys", "dataProductKeys"):
            refs = asset.get(field)
            if not isinstance(refs, list) or any(
                not isinstance(ref, str) or ref not in known_keys for ref in refs
            ):
                raise ValueError(f"Asset {asset['key']}: invalid {field}")
        if asset["criticalDataElementKeys"]:
            raise ValueError(
                f"Asset {asset['key']}: direct CDE relationships are not supported by the UC API"
            )
        if not isinstance(asset.get("qualifiedName"), str) or not asset["qualifiedName"].strip():
            raise ValueError(f"Asset {asset['key']}: qualifiedName must be a nonempty string")
    return scenario


def _same(row: Dict[str, Any], desired: Dict[str, Any], fields: Tuple[str, ...]) -> bool:
    def value(item: Dict[str, Any], field: str) -> Any:
        if field == "domain":
            return item.get("domain", item.get("domainId"))
        return item.get(field)

    return all(value(row, field) == desired.get(field) for field in fields)


def _find_by_name(rows: List[Dict[str, Any]], name: str) -> List[Dict[str, Any]]:
    return [
        row
        for row in rows
        if isinstance(row.get("name"), str) and row["name"].strip().casefold() == name.casefold()
    ]


def _resolve_existing(
    kind: str,
    desired: Dict[str, Any],
    rows: List[Dict[str, Any]],
    fields: Tuple[str, ...],
) -> Tuple[str, Dict[str, Any] | None]:
    matches = _find_by_name(rows, desired["name"])
    if len(matches) > 1:
        raise ValueError(f"{kind} {desired['name']!r}: multiple existing objects")
    if not matches:
        return "create", None
    if not _same(matches[0], desired, fields):
        raise ValueError(f"{kind} {desired['name']!r}: existing object differs from scenario")
    return "reuse", matches[0]


def _scenario_digest(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _created_or_refetched(
    response: Any,
    list_method: Any,
    list_args: Dict[str, Any],
    label: str,
    name: str,
) -> Dict[str, Any]:
    if isinstance(response, dict) and response.get("status") == "error":
        raise ValueError(f"{label} {name!r}: {response.get('message', 'create failed')}")
    if isinstance(response, dict) and response.get("id"):
        return response
    matches = _find_by_name(_rows(list_method(list_args), label), name)
    if len(matches) != 1 or not matches[0].get("id"):
        raise ValueError(f"{label} {name!r}: create response did not resolve a unique ID")
    return matches[0]


def _save_state(state_file: Path, state: Dict[str, Any]) -> None:
    state["updatedAt"] = datetime.now(timezone.utc).isoformat()
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def _require_success(response: Any, label: str) -> None:
    if isinstance(response, dict) and response.get("status") == "error":
        raise ValueError(f"{label}: {response.get('message', 'request failed')}")


def apply_scenario(
    uc_client: Any,
    entity_client: Any,
    scenario_file: Path,
    state_file: Path,
    apply: bool = False,
) -> Dict[str, Any]:
    """Plan or create a validation scenario; existing differing objects block."""
    scenario = load_scenario(scenario_file)
    state_file = Path(state_file)
    if state_file.exists():
        with state_file.open(encoding="utf-8") as handle:
            state = json.load(handle)
        if state.get("scenarioSha256") != _scenario_digest(scenario_file):
            raise ValueError("State file belongs to a different scenario version")
    else:
        state = {
            "schemaVersion": SCHEMA_VERSION,
            "scenarioId": scenario["scenarioId"],
            "scenarioSha256": _scenario_digest(scenario_file),
            "resources": {},
            "relationships": [],
        }

    actions: List[Dict[str, Any]] = []
    resources: Dict[str, Dict[str, Any]] = state["resources"]
    domain_spec = scenario["domain"]
    domain_desired = {
        "name": domain_spec["name"],
        "description": domain_spec["description"],
        "type": domain_spec.get("type", "FunctionalUnit"),
        "status": domain_spec.get("status", "Draft"),
    }
    domain_action, domain = _resolve_existing(
        "domain",
        domain_desired,
        _rows(uc_client.get_governance_domains({}), "domains"),
        ("name", "description", "type", "status"),
    )
    actions.append({"kind": "domain", "key": domain_spec["key"], "action": domain_action})
    if domain_action == "create" and apply:
        domain = _created_or_refetched(
            uc_client.create_governance_domain({"--payload": domain_desired}),
            uc_client.get_governance_domains,
            {},
            "domain",
            domain_desired["name"],
        )
    if domain:
        resources[domain_spec["key"]] = {
            "kind": "domain",
            "id": domain["id"],
            "name": domain["name"],
        }
        if apply:
            _save_state(state_file, state)
    if not apply and domain_action == "create":
        for kind, collection in (
            ("term", "terms"),
            ("cde", "criticalDataElements"),
            ("data_product", "dataProducts"),
            ("asset", "assets"),
        ):
            actions.extend(
                {"kind": kind, "key": spec["key"], "action": "create"}
                for spec in scenario[collection]
            )
        for asset_spec in scenario["assets"]:
            for field in ("termKeys", "dataProductKeys"):
                actions.extend(
                    {
                        "kind": "relationship",
                        "key": f"{asset_spec['key']}->{target_key}",
                        "action": "create",
                    }
                    for target_key in asset_spec[field]
                )
        return {"dryRun": True, "actions": actions, "stateWritten": False}

    domain_id = resources[domain_spec["key"]]["id"]
    specs = (
        (
            "term",
            "terms",
            uc_client.get_terms,
            uc_client.create_term,
            ("name", "description", "domain", "status"),
        ),
        (
            "cde",
            "criticalDataElements",
            uc_client.get_critical_data_elements,
            uc_client.create_critical_data_element,
            ("name", "description", "domain", "status", "dataType"),
        ),
        (
            "data_product",
            "dataProducts",
            uc_client.get_data_products,
            uc_client.create_data_product,
            ("name", "description", "domain", "status", "type", "businessUse"),
        ),
    )
    for kind, collection, list_method, create_method, fields in specs:
        rows = _rows(list_method({"--governance-domain-id": [domain_id]}), collection)
        for spec in scenario[collection]:
            desired = {
                "name": spec["name"],
                "description": spec["description"],
                "domain": domain_id,
                "status": spec.get("status", "Draft"),
            }
            args: Dict[str, Any] = {
                "--name": [spec["name"]],
                "--description": [spec["description"]],
                "--governance-domain-id": [domain_id],
                "--status": [desired["status"]],
            }
            if kind == "cde":
                desired["dataType"] = spec.get("dataType", "String")
                args["--data-type"] = [desired["dataType"]]
            elif kind == "data_product":
                desired["type"] = spec.get("type", "Dataset")
                desired["businessUse"] = spec.get("businessUse", "")
                args["--type"] = [desired["type"]]
                args["--business-use"] = [desired["businessUse"]]
            owner_ids = spec.get("ownerIds", [])
            if not isinstance(owner_ids, list) or any(
                not isinstance(owner_id, str) or not owner_id.strip() for owner_id in owner_ids
            ):
                raise ValueError(f"{kind} {spec['key']}: ownerIds must be nonempty strings")
            if owner_ids:
                args["--owner-id"] = owner_ids
            action, row = _resolve_existing(kind, desired, rows, fields)
            actions.append({"kind": kind, "key": spec["key"], "action": action})
            if action == "create" and apply:
                row = _created_or_refetched(
                    create_method(args),
                    list_method,
                    {"--governance-domain-id": [domain_id]},
                    kind,
                    spec["name"],
                )
            if row:
                resources[spec["key"]] = {"kind": kind, "id": row["id"], "name": row["name"]}
                if apply:
                    _save_state(state_file, state)

    asset_rows = _rows(uc_client.list_data_assets({"--skip": 0, "--top": 100}), "assets")
    for spec in scenario["assets"]:
        matches = _find_by_name(asset_rows, spec["name"])
        if len(matches) > 1:
            raise ValueError(f"asset {spec['name']!r}: multiple existing objects")
        asset = matches[0] if matches else None
        if asset and (
            asset.get("description") != spec["description"]
            or (
                asset.get("source", {}).get("fqn")
                or asset.get("source", {}).get("assetAttributes", {}).get("qualifiedName")
            )
            != spec["qualifiedName"]
        ):
            raise ValueError(f"asset {spec['name']!r}: existing object differs from scenario")
        action = "reuse" if asset else "create"
        actions.append({"kind": "asset", "key": spec["key"], "action": action})
        if not asset and apply:
            entity_response = entity_client.entityCreate(
                {
                    "--payload": {
                        "entity": {
                            "typeName": spec.get("dataMapType", "DataSet"),
                            "attributes": {
                                "qualifiedName": spec["qualifiedName"],
                                "name": spec["name"],
                                "description": spec["description"],
                            },
                        }
                    },
                    "--collectionId": spec.get("collectionId", ""),
                }
            )
            assignments = entity_response.get("guidAssignments", {})
            if len(assignments) != 1:
                raise ValueError(f"Asset {spec['key']}: Data Map create returned no unique GUID")
            entity_id = next(iter(assignments.values()))
            asset = uc_client.create_data_asset(
                {
                    "--payload": {
                        "name": spec["name"],
                        "description": spec["description"],
                        "source": {"type": "DataMap", "assetId": entity_id},
                        "type": "General",
                        "typeProperties": {},
                    }
                }
            )
            asset = _created_or_refetched(
                asset,
                uc_client.list_data_assets,
                {"--skip": 0, "--top": 100},
                "asset",
                spec["name"],
            )
        if asset:
            resources[spec["key"]] = {
                "kind": "asset",
                "id": asset["id"],
                "name": asset["name"],
                "dataMapId": asset.get("source", {}).get("assetId"),
            }
            if apply:
                _save_state(state_file, state)

    if not apply:
        recorded = {
            (rel.get("assetKey"), rel.get("targetKey"), rel.get("entityType"))
            for rel in state["relationships"]
        }
        for asset_spec in scenario["assets"]:
            for field, entity_type in (
                ("termKeys", "Term"),
                ("dataProductKeys", "DataProduct"),
            ):
                actions.extend(
                    {
                        "kind": "relationship",
                        "key": f"{asset_spec['key']}->{target_key}",
                        "action": (
                            "reuse"
                            if (asset_spec["key"], target_key, entity_type) in recorded
                            else "create"
                        ),
                    }
                    for target_key in asset_spec[field]
                )
        return {"dryRun": True, "actions": actions, "stateWritten": False}

    if apply:
        _save_state(state_file, state)
        relation_fields = (
            ("termKeys", "Term"),
            ("dataProductKeys", "DataProduct"),
        )
        for asset_spec in scenario["assets"]:
            asset_id = resources[asset_spec["key"]]["id"]
            for field, entity_type in relation_fields:
                live_relationships = _rows(
                    uc_client.list_data_asset_relationships(
                        {"--asset-id": asset_id, "--entity-type": entity_type}
                    ),
                    f"{entity_type} relationships for {asset_spec['key']}",
                )
                existing_target_ids = {
                    rel.get("entityId") or rel.get("id")
                    for rel in live_relationships
                    if isinstance(rel, dict)
                }
                for target_key in asset_spec[field]:
                    target_id = resources[target_key]["id"]
                    if target_id in existing_target_ids:
                        actions.append(
                            {
                                "kind": "relationship",
                                "key": f"{asset_spec['key']}->{target_key}",
                                "action": "reuse",
                            }
                        )
                        continue
                    response = uc_client.create_data_asset_relationship(
                        {
                            "--asset-id": asset_id,
                            "--payload": {
                                "entityId": target_id,
                                "entityType": entity_type,
                                "relationshipType": "Related",
                                "description": f"Created by scenario {scenario['scenarioId']}",
                            },
                        }
                    )
                    _require_success(response, f"Relationship {asset_spec['key']}->{target_key}")
                    state["relationships"].append(
                        {
                            "assetKey": asset_spec["key"],
                            "targetKey": target_key,
                            "entityType": entity_type,
                        }
                    )
                    actions.append(
                        {
                            "kind": "relationship",
                            "key": f"{asset_spec['key']}->{target_key}",
                            "action": "create",
                        }
                    )
                    existing_target_ids.add(target_id)
                    _save_state(state_file, state)
    return {"dryRun": not apply, "actions": actions, "stateWritten": apply}
