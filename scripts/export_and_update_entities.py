#!/usr/bin/env python
"""Export entities from Purview using the repo Search client, write a CSV suitable for bulk_update_csv,
update a column (description) and invoke the CLI bulk_update_csv command (dry-run by default).

Usage:
    python scripts\\export_and_update_entities.py --keywords "*" --limit 5 --out samples\\csv\\exported_entities.csv --update-description "Bulk updated description" --execute

By default the script runs in dry-run mode and will not call the API to update entities unless --execute is provided.
"""
import argparse
import csv
import json
import subprocess
import sys
from purviewcli.client._search import Search


def fetch_entities(keywords, limit):
    search = Search()
    args = {"--keywords": keywords, "--limit": limit}
    result = search.searchQuery(args)
    # searchQuery returns a dict with 'value' list
    items = result.get("value", []) if isinstance(result, dict) else []
    return items


def _derive_name_from_qn(qn: str) -> str:
    # simple heuristics: take last path segment or last token after '/' or ':' or '@' or '#'
    if not qn:
        return ""
    for sep in ["/", "#", ":", "@"]:
        if sep in qn:
            parts = [p for p in qn.split(sep) if p]
            if parts:
                return parts[-1]
    return qn


def write_type_qn_csv(items, out_path, description_value=None, fill_required=False):
    # Columns when fill_required=False: typeName,qualifiedName,description
    # Columns when fill_required=True: typeName,qualifiedName,name,description
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if fill_required:
            writer.writerow(["typeName", "qualifiedName", "name", "description"])
        else:
            writer.writerow(["typeName", "qualifiedName", "description"])

        for it in items:
            t = it.get("entityType") or it.get("typeName") or it.get("objectType") or ""
            qn = it.get("qualifiedName") or it.get("attributes", {}).get("qualifiedName")
            if not qn:
                continue
            desc = description_value if description_value is not None else it.get("description", "")
            if fill_required:
                name = _derive_name_from_qn(qn)
                writer.writerow([t, qn, name, desc])
            else:
                writer.writerow([t, qn, desc])


def run_cli_bulk(csv_path, execute=False):
    cmd = [sys.executable, "-m", "purviewcli.__main__", "entity", "bulk-update-csv", "--csv-file", csv_path, "--batch-size", "2"]
    if not execute:
        cmd.append("--dry-run")

    print("Running:", " ".join(cmd))
    proc = subprocess.run(cmd, shell=False)
    return proc.returncode


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--keywords", default="*", help="Search keywords")
    p.add_argument("--limit", type=int, default=5, help="Number of entities to fetch")
    p.add_argument("--out", default="samples/csv/exported_entities.csv", help="Output CSV path")
    p.add_argument("--update-description", default=None, help="Description to set on each exported entity")
    p.add_argument("--execute", action="store_true", help="Actually run the CLI to perform updates (default: dry-run)")
    p.add_argument("--fill-required", action="store_true", help="Auto-fill common required attributes (e.g., name) derived from qualifiedName")
    args = p.parse_args()

    items = fetch_entities(args.keywords, args.limit)
    print(f"Fetched {len(items)} search hits")
    write_type_qn_csv(items, args.out, description_value=args.update_description, fill_required=args.fill_required)
    print(f"Wrote CSV to {args.out}")

    rc = run_cli_bulk(args.out, execute=args.execute)
    if rc != 0:
        print(f"CLI returned non-zero exit code: {rc}")


if __name__ == "__main__":
    main()
