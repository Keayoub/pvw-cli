"""
Copy Purview entities to a target collection by creating new entities
and reapplying classifications, business metadata, labels, and relationships.
"""

import argparse
import csv
import json
import os
import sys
import tempfile
import time
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

from purviewcli.client._entity import Entity
from purviewcli.client._relationship import Relationship


def _load_guids(path: str) -> List[str]:
    if path.lower().endswith(".csv"):
        with open(path, newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames:
                raise ValueError("CSV file has no headers")
            fieldnames = {name.strip() for name in reader.fieldnames if name}
            guid_key = None
            for candidate in ("guid", "entityGuid", "entity_guid", "entity_id"):
                if candidate in fieldnames:
                    guid_key = candidate
                    break
            if not guid_key:
                raise ValueError("CSV must contain a 'guid' column")
            return [row[guid_key].strip() for row in reader if row.get(guid_key)]

    with open(path, "r", encoding="utf-8") as handle:
        return [line.strip() for line in handle if line.strip()]


def _write_payload(payload: Dict[str, Any]) -> str:
    temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
    try:
        json.dump(payload, temp_file, indent=2)
        temp_file.flush()
    finally:
        temp_file.close()
    return temp_file.name


def _cleanup_temp(path: Optional[str]) -> None:
    if path and os.path.exists(path):
        os.remove(path)


def _extract_entity_object(result: Dict[str, Any]) -> Dict[str, Any]:
    if "entity" in result and isinstance(result["entity"], dict):
        return result["entity"]
    return result


def _build_new_entity_payload(
    entity_obj: Dict[str, Any],
    qn_suffix: str,
    name_suffix: str,
    qn_prefix_map: Optional[Dict[str, str]] = None,
    use_suffix_if_no_map: bool = True,
    name_prefix_map: Optional[Dict[str, str]] = None,
    map_name_suffix_if_no_map: bool = True,
) -> Tuple[Dict[str, Any], str]:
    type_name = entity_obj.get("typeName")
    attributes = dict(entity_obj.get("attributes", {}))

    qualified_name = attributes.get("qualifiedName")
    if not qualified_name:
        raise ValueError("Source entity is missing attributes.qualifiedName")

    mapped_qualified_name = None
    if qn_prefix_map:
        for old_prefix, new_prefix in qn_prefix_map.items():
            if qualified_name.startswith(old_prefix):
                mapped_qualified_name = f"{new_prefix}{qualified_name[len(old_prefix):]}"
                break

    if mapped_qualified_name:
        attributes["qualifiedName"] = mapped_qualified_name
    elif use_suffix_if_no_map:
        attributes["qualifiedName"] = f"{qualified_name}{qn_suffix}"
    else:
        attributes["qualifiedName"] = qualified_name
    if "name" in attributes and attributes["name"]:
        original_name = attributes["name"]
        mapped_name = None
        if name_prefix_map:
            for old_prefix, new_prefix in name_prefix_map.items():
                if original_name.startswith(old_prefix):
                    mapped_name = f"{new_prefix}{original_name[len(old_prefix):]}"
                    break
        if mapped_name:
            attributes["name"] = mapped_name
        elif map_name_suffix_if_no_map:
            attributes["name"] = f"{original_name}{name_suffix}"

    if "displayName" in attributes and attributes["displayName"]:
        original_display = attributes["displayName"]
        mapped_display = None
        if name_prefix_map:
            for old_prefix, new_prefix in name_prefix_map.items():
                if original_display.startswith(old_prefix):
                    mapped_display = f"{new_prefix}{original_display[len(old_prefix):]}"
                    break
        if mapped_display:
            attributes["displayName"] = mapped_display
        elif map_name_suffix_if_no_map:
            attributes["displayName"] = f"{original_display}{name_suffix}"

    payload_entity = {
        "typeName": type_name,
        "attributes": attributes,
        "status": entity_obj.get("status", "ACTIVE"),
    }

    return {"entity": payload_entity}, attributes["qualifiedName"]


def _extract_created_guid(result: Dict[str, Any]) -> Optional[str]:
    if isinstance(result, dict):
        if "guid" in result:
            return str(result["guid"])
        guid_assignments = result.get("guidAssignments")
        if isinstance(guid_assignments, dict) and guid_assignments:
            return str(next(iter(guid_assignments.values())))
        entity = result.get("entity")
        if isinstance(entity, dict) and entity.get("guid"):
            return str(entity["guid"])
        mutated = result.get("mutatedEntities")
        if isinstance(mutated, dict):
            for _key, entries in mutated.items():
                if isinstance(entries, list) and entries:
                    first = entries[0]
                    if isinstance(first, dict) and first.get("guid"):
                        return str(first["guid"])
    return None


def _maybe_get(result: Dict[str, Any], *keys: str) -> Optional[Any]:
    for key in keys:
        if key in result and result[key] is not None:
            return result[key]
    return None


def _copy_classifications(entity_client: Entity, source_guid: str, target_guid: str, dry_run: bool) -> None:
    data = entity_client.entityReadClassifications({"--guid": source_guid})
    classifications = _maybe_get(data, "classifications")
    if not classifications:
        return

    payload = {"classifications": classifications}
    if dry_run:
        print(f"DRY RUN: Would add {len(classifications)} classifications to {target_guid}")
        return

    payload_file = _write_payload(payload)
    try:
        entity_client.entityAddClassifications({"--guid": [target_guid], "--payloadFile": payload_file})
    finally:
        _cleanup_temp(payload_file)


def _copy_labels(entity_obj: Dict[str, Any], entity_client: Entity, target_guid: str, dry_run: bool) -> None:
    labels = _maybe_get(entity_obj, "labels")
    if not labels:
        return

    payload = {"labels": labels}
    if dry_run:
        print(f"DRY RUN: Would set {len(labels)} labels to {target_guid}")
        return

    payload_file = _write_payload(payload)
    try:
        entity_client.entitySetLabels({"--guid": [target_guid], "--payloadFile": payload_file})
    finally:
        _cleanup_temp(payload_file)


def _copy_business_metadata(entity_obj: Dict[str, Any], entity_client: Entity, target_guid: str, dry_run: bool) -> None:
    business_metadata = _maybe_get(entity_obj, "businessMetadata", "businessAttributes")
    if not business_metadata:
        return

    payload = {"businessMetadata": business_metadata}
    if dry_run:
        print(f"DRY RUN: Would add business metadata to {target_guid}")
        return

    payload_file = _write_payload(payload)
    try:
        entity_client.entityAddOrUpdateBusinessMetadata({
            "--guid": [target_guid],
            "--payloadFile": payload_file,
            "--isOverwrite": True,
        })
    finally:
        _cleanup_temp(payload_file)


def _extract_relationships(result: Dict[str, Any]) -> List[Dict[str, Any]]:
    for key in ("relationships", "value", "results"):
        value = result.get(key)
        if isinstance(value, list):
            return value
    return []


def _clone_entity(
    entity_client: Entity,
    source_guid: str,
    collection_id: str,
    qn_suffix: str,
    name_suffix: str,
    dry_run: bool,
    copy_classifications: bool,
    copy_business_metadata: bool,
    copy_labels: bool,
    qn_prefix_map: Optional[Dict[str, str]] = None,
    use_suffix_if_no_map: bool = True,
    name_prefix_map: Optional[Dict[str, str]] = None,
    map_name_suffix_if_no_map: bool = True,
) -> Tuple[str, Dict[str, Any], str]:
    result = entity_client.entityRead({
        "--guid": source_guid,
        "--ignoreRelationships": True,
        "--minExtInfo": True,
    })
    entity_obj = _extract_entity_object(result)

    payload, target_qualified_name = _build_new_entity_payload(
        entity_obj,
        qn_suffix,
        name_suffix,
        qn_prefix_map=qn_prefix_map,
        use_suffix_if_no_map=use_suffix_if_no_map,
        name_prefix_map=name_prefix_map,
        map_name_suffix_if_no_map=map_name_suffix_if_no_map,
    )
    if dry_run:
        print(f"DRY RUN: Would create new entity for {source_guid}")
        new_guid = f"dry-run-{source_guid}"
    else:
        payload_file = _write_payload(payload)
        try:
            create_result = entity_client.entityCreate({"--payloadFile": payload_file})
        finally:
            _cleanup_temp(payload_file)
        new_guid = _extract_created_guid(create_result)

    if not new_guid:
        raise RuntimeError("Could not determine new entity GUID from create response")

    _move_to_collection(entity_client, new_guid, collection_id, dry_run)

    if copy_classifications:
        _copy_classifications(entity_client, source_guid, new_guid, dry_run)
    if copy_business_metadata:
        _copy_business_metadata(entity_obj, entity_client, new_guid, dry_run)
    if copy_labels:
        _copy_labels(entity_obj, entity_client, new_guid, dry_run)

    return new_guid, entity_obj, target_qualified_name


def _copy_relationships(
    entity_client: Entity,
    relationship_client: Relationship,
    source_guid: str,
    target_guid: str,
    dry_run: bool,
    limit: int,
    direction: str,
    clone_related: bool,
    collection_id: str,
    qn_suffix: str,
    name_suffix: str,
    copy_classifications: bool,
    copy_business_metadata: bool,
    copy_labels: bool,
    source_table_qualified_name: str,
    target_table_qualified_name: str,
    source_table_name: Optional[str],
    target_table_name: Optional[str],
    source_table_display_name: Optional[str],
    target_table_display_name: Optional[str],
) -> None:
    seen: Set[Tuple[str, str, str]] = set()
    related_map: Dict[str, str] = {}
    offset = 0

    while True:
        args = {
            "--entityGuid": source_guid,
            "--direction": direction,
            "--status": "ACTIVE",
            "--limit": limit,
            "--offset": offset,
        }
        data = relationship_client.relationshipReadByEntity(args)
        relationships = _extract_relationships(data)
        if not relationships:
            break

        payload_relationships = []
        for rel in relationships:
            type_name = rel.get("typeName")
            end1 = rel.get("end1")
            end2 = rel.get("end2")
            if not (type_name and isinstance(end1, dict) and isinstance(end2, dict)):
                continue

            end1_guid = end1.get("guid")
            end2_guid = end2.get("guid")
            if not (end1_guid and end2_guid):
                continue

            if end1_guid != source_guid and end2_guid != source_guid:
                continue

            related_guid = end2_guid if end1_guid == source_guid else end1_guid
            if clone_related:
                if related_guid not in related_map:
                    qn_prefix_map = {
                        source_table_qualified_name: target_table_qualified_name,
                    }
                    name_prefix_map = {}
                    if source_table_name and target_table_name:
                        name_prefix_map[source_table_name] = target_table_name
                    if source_table_display_name and target_table_display_name:
                        name_prefix_map[source_table_display_name] = target_table_display_name
                    related_new_guid, _, _ = _clone_entity(
                        entity_client,
                        related_guid,
                        collection_id,
                        qn_suffix,
                        name_suffix,
                        dry_run,
                        copy_classifications,
                        copy_business_metadata,
                        copy_labels,
                        qn_prefix_map=qn_prefix_map,
                        use_suffix_if_no_map=True,
                        name_prefix_map=name_prefix_map if name_prefix_map else None,
                        map_name_suffix_if_no_map=True,
                    )
                    related_map[related_guid] = related_new_guid
                related_guid = related_map[related_guid]

            if end1_guid == source_guid:
                end1 = {**end1, "guid": target_guid}
            else:
                end1 = {**end1, "guid": related_guid}

            if end2_guid == source_guid:
                end2 = {**end2, "guid": target_guid}
            else:
                end2 = {**end2, "guid": related_guid}

            signature = (type_name, end1["guid"], end2["guid"])
            if signature in seen:
                continue
            seen.add(signature)

            payload_relationships.append({
                "typeName": type_name,
                "end1": end1,
                "end2": end2,
                "attributes": rel.get("attributes", {}),
            })

        if payload_relationships:
            if dry_run:
                print(f"DRY RUN: Would create {len(payload_relationships)} relationships for {target_guid}")
            else:
                payload_file = _write_payload({"relationships": payload_relationships})
                try:
                    relationship_client.relationshipCreateBulk({"--payloadFile": payload_file})
                finally:
                    _cleanup_temp(payload_file)

        if len(relationships) < limit:
            break

        offset += limit


def _move_to_collection(entity_client: Entity, target_guid: str, collection_id: str, dry_run: bool) -> None:
    payload = {
        "entityGuids": [target_guid],
        "collectionId": collection_id,
    }
    if dry_run:
        print(f"DRY RUN: Would move {target_guid} to collection {collection_id}")
        return

    payload_file = _write_payload(payload)
    try:
        entity_client.entityMoveToCollection({"--payloadFile": payload_file})
    finally:
        _cleanup_temp(payload_file)


def copy_entities(args: argparse.Namespace) -> int:
    entity_client = Entity()
    relationship_client = Relationship()

    guids = _load_guids(args.guids_file)
    if not guids:
        print("No GUIDs found in input file")
        return 1

    errors = 0
    for source_guid in guids:
        print(f"INFO: Copying entity {source_guid}")
        try:
            new_guid, entity_obj, target_table_qualified_name = _clone_entity(
                entity_client,
                source_guid,
                args.collection_id,
                args.qualified_name_suffix,
                args.name_suffix,
                args.dry_run,
                args.copy_classifications,
                args.copy_business_metadata,
                args.copy_labels,
            )
            source_table_qualified_name = entity_obj.get("attributes", {}).get("qualifiedName")
            if not source_table_qualified_name:
                raise RuntimeError("Source entity missing qualifiedName")

            if args.from_table_qn and args.to_table_qn:
                source_table_qualified_name = args.from_table_qn
                target_table_qualified_name = args.to_table_qn

            source_table_name = entity_obj.get("attributes", {}).get("name")
            target_table_name = None
            if source_table_name:
                if args.from_table_name and args.to_table_name:
                    if source_table_name.startswith(args.from_table_name):
                        target_table_name = f"{args.to_table_name}{source_table_name[len(args.from_table_name):]}"
                if not target_table_name:
                    target_table_name = f"{source_table_name}{args.name_suffix}"

            source_table_display_name = entity_obj.get("attributes", {}).get("displayName")
            target_table_display_name = None
            if source_table_display_name:
                if args.from_table_display_name and args.to_table_display_name:
                    if source_table_display_name.startswith(args.from_table_display_name):
                        target_table_display_name = (
                            f"{args.to_table_display_name}{source_table_display_name[len(args.from_table_display_name):]}"
                        )
                if not target_table_display_name:
                    target_table_display_name = f"{source_table_display_name}{args.name_suffix}"

            if args.copy_relationships:
                _copy_relationships(
                    entity_client,
                    relationship_client,
                    source_guid,
                    new_guid,
                    args.dry_run,
                    args.relationship_limit,
                    args.relationship_direction,
                    args.clone_related,
                    args.collection_id,
                    args.qualified_name_suffix,
                    args.name_suffix,
                    args.copy_classifications,
                    args.copy_business_metadata,
                    args.copy_labels,
                    source_table_qualified_name,
                    target_table_qualified_name,
                    source_table_name,
                    target_table_name,
                    source_table_display_name,
                    target_table_display_name,
                )

            print(f"OK: Copied {source_guid} -> {new_guid}")
        except Exception as exc:
            errors += 1
            print(f"FAILED: {source_guid} - {exc}")

        if args.throttle_ms > 0:
            time.sleep(args.throttle_ms / 1000.0)

    return 1 if errors else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Copy entities to another collection using Purview CLI client",
    )
    parser.add_argument("--guids-file", required=True, help="Text file or CSV with a guid column")
    parser.add_argument("--collection-id", required=True, help="Target collection ID (collection name)")
    parser.add_argument("--qualified-name-suffix", default="-copy", help="Suffix for new qualifiedName")
    parser.add_argument("--name-suffix", default="-copy", help="Suffix for name/displayName")
    parser.add_argument("--from-table-qn", help="Override source table qualifiedName for mapping")
    parser.add_argument("--to-table-qn", help="Override target table qualifiedName for mapping")
    parser.add_argument("--from-table-name", help="Override source table name for mapping")
    parser.add_argument("--to-table-name", help="Override target table name for mapping")
    parser.add_argument("--from-table-display-name", help="Override source table displayName for mapping")
    parser.add_argument("--to-table-display-name", help="Override target table displayName for mapping")
    parser.add_argument("--relationship-limit", type=int, default=1000, help="Max relationships to copy per entity")
    parser.add_argument(
        "--relationship-direction",
        default="BOTH",
        choices=["BOTH", "IN", "OUT"],
        help="Relationship direction to copy",
    )
    parser.add_argument("--throttle-ms", type=int, default=200, help="Delay between entities (ms)")
    parser.add_argument("--dry-run", action="store_true", help="Preview actions without changes")

    parser.add_argument("--copy-classifications", action="store_true", default=True, help="Copy classifications")
    parser.add_argument("--copy-business-metadata", action="store_true", default=True, help="Copy business metadata")
    parser.add_argument("--copy-labels", action="store_true", default=True, help="Copy labels")
    parser.add_argument("--copy-relationships", action="store_true", default=True, help="Copy relationships")
    parser.add_argument("--clone-related", action="store_true", default=True, help="Clone related entities")
    parser.add_argument("--link-related", action="store_true", help="Keep relationships to existing entities")

    parser.add_argument("--skip-classifications", action="store_true", help="Skip classifications")
    parser.add_argument("--skip-business-metadata", action="store_true", help="Skip business metadata")
    parser.add_argument("--skip-labels", action="store_true", help="Skip labels")
    parser.add_argument("--skip-relationships", action="store_true", help="Skip relationships")

    return parser


def apply_skip_flags(args: argparse.Namespace) -> None:
    if args.skip_classifications:
        args.copy_classifications = False
    if args.skip_business_metadata:
        args.copy_business_metadata = False
    if args.skip_labels:
        args.copy_labels = False
    if args.skip_relationships:
        args.copy_relationships = False
    if args.link_related:
        args.clone_related = False


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    apply_skip_flags(args)
    return copy_entities(args)


if __name__ == "__main__":
    sys.exit(main())
