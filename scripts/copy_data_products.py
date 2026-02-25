"""
Copy DataProduct entities to a target collection.

Dedicated wrapper around copy_entities_to_collection that:
  - Forces --type-filter DataProduct (skips any non-DataProduct GUID)
  - Defaults to --skip-relationships (DataProduct assets are links, not clones)
  - Exposes only the options that make sense for DataProducts

Reuses all shared logic from copy_entities_to_collection without duplication.

Usage examples:
  # Dry run
  python scripts/copy_data_products.py \
      --guids-file dp_guids.txt \
      --collection-id target-collection \
      --dry-run

  # Real copy
  python scripts/copy_data_products.py \
      --guids-file dp_guids.txt \
      --collection-id target-collection \
      --name-suffix "-v2" \
      --qualified-name-suffix "-v2"

  # Copy and keep links to existing assets (instead of skipping relationships)
  python scripts/copy_data_products.py \
      --guids-file dp_guids.txt \
      --collection-id target-collection \
      --copy-asset-links
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scripts.copy_entities_to_collection import (
    _clone_entity,
    _copy_relationships,
    _extract_entity_object,
    _load_guids,
    apply_skip_flags,
)
from purviewcli.client._entity import Entity
from purviewcli.client._relationship import Relationship

import time
from typing import Optional

DATA_PRODUCT_TYPE = "DataProduct"


def copy_data_products(args: argparse.Namespace) -> int:
    entity_client = Entity()
    relationship_client = Relationship()

    guids = _load_guids(args.guids_file)
    if not guids:
        print("No GUIDs found in input file")
        return 1

    errors = 0
    for source_guid in guids:
        print(f"INFO: Processing {source_guid}")
        try:
            # Always peek first to enforce DataProduct-only filter
            result = entity_client.entityRead({
                "--guid": source_guid,
                "--ignoreRelationships": True,
                "--minExtInfo": True,
            })
            entity_obj = _extract_entity_object(result)
            entity_type = entity_obj.get("typeName", "")

            if entity_type != DATA_PRODUCT_TYPE:
                print(f"SKIP: {source_guid} is '{entity_type}', not a DataProduct")
                continue

            name = entity_obj.get("attributes", {}).get("name", source_guid)
            print(f"INFO: Copying DataProduct '{name}' ({source_guid})")

            new_guid, entity_obj, target_qn = _clone_entity(
                entity_client,
                source_guid,
                args.collection_id,
                args.qualified_name_suffix,
                args.name_suffix,
                args.dry_run,
                copy_classifications=not args.skip_classifications,
                copy_business_metadata=not args.skip_business_metadata,
                copy_labels=not args.skip_labels,
                prefetched_entity=entity_obj,  # reuse the peek, avoid double entityRead
            )

            # Optionally copy relationships (asset links, terms, etc.)
            if args.copy_asset_links:
                source_qn = entity_obj.get("attributes", {}).get("qualifiedName", "")
                _copy_relationships(
                    entity_client,
                    relationship_client,
                    source_guid,
                    new_guid,
                    args.dry_run,
                    limit=1000,
                    direction="BOTH",
                    clone_related=False,          # never clone assets, only re-link
                    collection_id=args.collection_id,
                    qn_suffix=args.qualified_name_suffix,
                    name_suffix=args.name_suffix,
                    copy_classifications=not args.skip_classifications,
                    copy_business_metadata=not args.skip_business_metadata,
                    copy_labels=not args.skip_labels,
                    source_table_qualified_name=source_qn,
                    target_table_qualified_name=target_qn,
                    source_table_name=entity_obj.get("attributes", {}).get("name"),
                    target_table_name=None,
                    source_table_display_name=entity_obj.get("attributes", {}).get("displayName"),
                    target_table_display_name=None,
                )

            print(f"OK: Copied DataProduct {source_guid} -> {new_guid}")

        except Exception as exc:
            errors += 1
            print(f"FAILED: {source_guid} - {exc}")

        if args.throttle_ms > 0:
            time.sleep(args.throttle_ms / 1000.0)

    return 1 if errors else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Copy DataProduct entities to another collection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/copy_data_products.py \\
      --guids-file dp_guids.txt \\
      --collection-id target-collection \\
      --dry-run

  python scripts/copy_data_products.py \\
      --guids-file dp_guids.txt \\
      --collection-id target-collection \\
      --name-suffix "-v2" \\
      --copy-asset-links
""",
    )

    # Required
    parser.add_argument("--guids-file", required=True,
                        help="Text file or CSV with a 'guid' column listing DataProduct GUIDs")
    parser.add_argument("--collection-id", required=True,
                        help="Target collection ID")

    # Naming
    parser.add_argument("--qualified-name-suffix", default="-copy",
                        help="Suffix appended to qualifiedName (default: -copy)")
    parser.add_argument("--name-suffix", default="-copy",
                        help="Suffix appended to name and displayName (default: -copy)")

    # DataProduct-specific
    parser.add_argument("--copy-asset-links", action="store_true",
                        help="Re-link the copied DataProduct to the same assets/terms "
                             "(relationships are re-linked, not cloned)")

    # What to skip
    parser.add_argument("--skip-classifications", action="store_true",
                        help="Do not copy classifications")
    parser.add_argument("--skip-business-metadata", action="store_true",
                        help="Do not copy business metadata")
    parser.add_argument("--skip-labels", action="store_true",
                        help="Do not copy labels")

    # Misc
    parser.add_argument("--throttle-ms", type=int, default=200,
                        help="Delay in ms between entities (default: 200)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview actions without making any changes")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return copy_data_products(args)


if __name__ == "__main__":
    sys.exit(main())
