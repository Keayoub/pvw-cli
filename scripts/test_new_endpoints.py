"""
API Coverage Report — Purview CLI
==================================
Answers three questions in a single pass:

  1. DEFINED     — How many operations exist in endpoints.py per service group?
  2. CLI COVERAGE — Does a matching CLI file exist, and how many @click.command
                    entries are wired up for that group?
  3. LIVE CHECK  — For a curated probe list, is the endpoint currently deployed
                   and returning a known HTTP status?

Usage:
    python scripts/test_new_endpoints.py
    python scripts/test_new_endpoints.py --update-readme   # patches README.md

Deployment heuristic (per HTTP status):
  200/201/202  → LIVE      route works
  400          → DEPLOYED  route exists; request shape / params may need updating
  401/403      → DEPLOYED  route exists; auth / permission gap
  404          → MISSING   route not found at this path or api-version
  405          → DEPLOYED  route exists; wrong HTTP method
"""

import sys
import os
import re
import glob
import json
import argparse
from datetime import date

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from purviewcli.client.sync_client import SyncPurviewClient, SyncPurviewConfig
from purviewcli.client.endpoints import ENDPOINTS
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()

REPO_ROOT  = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CLI_DIR    = os.path.join(REPO_ROOT, 'purviewcli', 'cli')
README_PATH = os.path.join(REPO_ROOT, 'README.md')

# ── Service group → CLI file(s) that implement it ────────────────────────────
GROUP_CLI_MAP: dict[str, list[str]] = {
    "entity":                ["entity.py"],
    "glossary":              ["glossary.py"],
    "types":                 ["types.py"],
    "lineage":               ["lineage.py"],
    "relationship":          ["relationship.py"],
    "discovery":             ["search.py"],
    "account":               ["account.py"],
    "collections":           ["collections.py"],
    "scanning":              ["scan.py"],
    "workflow":              ["workflow.py"],
    "devops_policies":       ["policystore.py"],
    "self_service_policies": ["policystore.py"],
    "metadata_policies":     ["policystore.py"],
    "sharing":               ["share.py"],
    "unified_catalog":       ["unified_catalog.py", "domain.py"],
    "data_quality":          ["quality.py"],
    "management":            ["management.py"],
    # aliases / legacy — skip from coverage count
    "search": [],
    "scan":   [],
    "share":  [],
}

# ── Curated live probes ───────────────────────────────────────────────────────
# (label, endpoint_path, method, extra_params, payload)
LIVE_PROBES: list[tuple[str, str, str, dict, dict | None]] = [
    ("unified_catalog – terms query",
     "/datagovernance/catalog/terms/query",          "POST", {},                                    {"size": 1}),
    ("unified_catalog – data products query",
     "/datagovernance/catalog/dataproducts/query",   "POST", {},                                    {"size": 1}),
    ("unified_catalog – objectives query",
     "/datagovernance/catalog/objectives/query",     "POST", {},                                    {"size": 1}),
    ("unified_catalog – policies query",
     "/datagovernance/catalog/policies/query",       "POST", {},                                    {"size": 1}),
    ("unified_catalog – CDE query",
     "/datagovernance/catalog/criticalDataElements/query", "POST", {},                              {"size": 1}),
    ("unified_catalog – customMetadata",
     "/datagovernance/catalog/customMetadata",       "GET",  {},                                    None),
    ("unified_catalog – business domains",
     "/datagovernance/catalog/businessdomains",      "GET",  {},                                    None),
    ("data_quality – business-domains",
     "/datagovernance/quality/business-domains",     "GET",  {"api-version": "2026-01-12-preview"}, None),
    ("health – summary",
     "/datagovernance/health/summary",               "GET",  {"api-version": "2024-02-01-preview"}, None),
    ("health – actions/query",
     "/datagovernance/health/actions/query",         "POST", {"api-version": "2024-02-01-preview"}, {}),
    ("discovery – search",
     "/datamap/api/search/query",                    "POST", {},                                    {"keywords": "*", "limit": 1}),
    ("account – get",
     "/account",                                     "GET",  {"api-version": "2019-11-01-preview"}, None),
]


# ─────────────────────────────────────────────────────────────────────────────
# Static analysis helpers
# ─────────────────────────────────────────────────────────────────────────────

def count_click_commands(cli_files: list[str]) -> int:
    """Count @click.command decorators across a list of CLI filenames."""
    total = 0
    for fname in cli_files:
        fpath = os.path.join(CLI_DIR, fname)
        if not os.path.exists(fpath):
            continue
        try:
            text = open(fpath, encoding='utf-8', errors='ignore').read()
            total += len(re.findall(r'@\w+\.command|@click\.command', text))
        except OSError:
            pass
    return total


def cli_files_exist(cli_files: list[str]) -> bool:
    return bool(cli_files) and any(
        os.path.exists(os.path.join(CLI_DIR, f)) for f in cli_files
    )


def build_static_coverage() -> list[dict]:
    """Build per-group coverage from the ENDPOINTS dict and CLI directory."""
    rows = []
    for group, ops in ENDPOINTS.items():
        cli_files = GROUP_CLI_MAP.get(group, [])
        if not cli_files:           # alias / legacy group — exclude
            continue
        defined  = len(ops)
        has_cli  = cli_files_exist(cli_files)
        commands = count_click_commands(cli_files) if has_cli else 0
        rows.append({
            "group":    group,
            "defined":  defined,
            "has_cli":  has_cli,
            "commands": commands,
            "cli_files": cli_files,
        })
    return rows


# ─────────────────────────────────────────────────────────────────────────────
# Live probe helpers
# ─────────────────────────────────────────────────────────────────────────────

def deployment_verdict(status: int) -> tuple[str, str]:
    if status in (200, 201, 202):
        return "LIVE    ✓", "bold green"
    if status in (400, 401, 403, 405):
        return "DEPLOYED~", "yellow"
    if status == 404:
        return "MISSING ✗", "bold red"
    return f"? ({status})", "dim"


def probe_endpoint(
    client,
    label: str,
    endpoint: str,
    method: str,
    extra_params: dict,
    payload: dict | None,
) -> dict:
    status = 0
    error_body = ""
    item_count = None
    try:
        result = client.make_request(
            method=method,
            endpoint=endpoint,
            params=extra_params,
            json=payload,
        )
        status = result.get("status_code", 0)
        data   = result.get("data", {})
        if status in (200, 201, 202) and isinstance(data, dict) and "value" in data:
            item_count = len(data["value"])
        if status not in (200, 201, 202) and data:
            raw = json.dumps(data) if isinstance(data, (dict, list)) else str(data)
            error_body = raw[:300]
    except Exception as exc:
        error_body = str(exc)[:200]

    verdict, style = deployment_verdict(status)
    return {
        "label":      label,
        "method":     method,
        "endpoint":   endpoint,
        "status":     status,
        "verdict":    verdict,
        "style":      style,
        "item_count": item_count,
        "error_body": error_body,
    }


# ─────────────────────────────────────────────────────────────────────────────
# README patch
# ─────────────────────────────────────────────────────────────────────────────

_MARKER_START = "<!-- API_COVERAGE_START -->"
_MARKER_END   = "<!-- API_COVERAGE_END -->"


def build_coverage_markdown(static: list[dict], probes: list[dict]) -> str:
    today = date.today().isoformat()

    total_groups   = len(static)
    covered_groups = sum(1 for r in static if r["has_cli"])
    total_ops      = sum(r["defined"]  for r in static)
    total_cmds     = sum(r["commands"] for r in static)
    pct_groups = int(covered_groups / total_groups * 100) if total_groups else 0
    pct_cmds   = min(int(total_cmds / total_ops * 100), 100) if total_ops else 0

    live_count     = sum(1 for p in probes if "✓" in p["verdict"])
    deployed_count = sum(1 for p in probes if p["verdict"].startswith("DEPLOYED"))
    missing_count  = sum(1 for p in probes if "✗" in p["verdict"])

    lines = [
        _MARKER_START,
        "",
        f"## 📊 API Coverage  *(auto-updated {today})*",
        "",
        "### Static Coverage — Defined vs Implemented",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Service groups defined in `endpoints.py` | **{total_groups}** |",
        f"| Groups with a CLI file | **{covered_groups} / {total_groups}** ({pct_groups}%) |",
        f"| Total operations defined | **{total_ops}** |",
        f"| Total CLI commands wired | **{total_cmds}** (~{pct_cmds}% op-level) |",
        "",
        "| Group | Defined ops | CLI file(s) | Commands |",
        "|-------|-------------|-------------|----------|",
    ]
    for r in sorted(static, key=lambda x: x["group"]):
        cli_str = ", ".join(f"`{f}`" for f in r["cli_files"]) or "—"
        check   = "✅" if r["has_cli"] else "❌"
        lines.append(
            f"| `{r['group']}` | {r['defined']} | {check} {cli_str} | {r['commands']} |"
        )

    lines += [
        "",
        "### Live Probe Results",
        "",
        f"| Endpoint | Method | Status | Result |",
        f"|----------|--------|--------|--------|",
    ]
    for p in probes:
        icon = "✅" if "✓" in p["verdict"] else ("⚠️" if "~" in p["verdict"] else "❌")
        note = f"{p['item_count']} items" if p["item_count"] is not None else (p["error_body"][:80] if p["error_body"] else "")
        lines.append(
            f"| `{p['endpoint']}` | `{p['method']}` | {p['status']} | {icon} {p['verdict'].strip()} — {note} |"
        )

    lines += [
        "",
        f"> Live probe summary: **{live_count} live**, "
        f"**{deployed_count} deployed (needs payload/auth fix)**, "
        f"**{missing_count} missing/404**",
        "",
        _MARKER_END,
    ]
    return "\n".join(lines)


def patch_readme(coverage_md: str) -> bool:
    """Insert or replace the coverage block in README.md. Returns True if changed."""
    if not os.path.exists(README_PATH):
        return False
    text = open(README_PATH, encoding='utf-8').read()
    block = f"\n{coverage_md}\n"
    if _MARKER_START in text and _MARKER_END in text:
        new_text = re.sub(
            re.escape(_MARKER_START) + r'.*?' + re.escape(_MARKER_END),
            coverage_md,
            text,
            flags=re.DOTALL,
        )
    else:
        # Insert before the first ## section after the title
        insert_after = re.search(r'\n## ', text)
        pos = insert_after.start() if insert_after else len(text)
        new_text = text[:pos] + "\n" + block + text[pos:]
    if new_text == text:
        return False
    open(README_PATH, 'w', encoding='utf-8').write(new_text)
    return True


# ─────────────────────────────────────────────────────────────────────────────
# Display helpers
# ─────────────────────────────────────────────────────────────────────────────

def print_static_table(static: list[dict]) -> None:
    t = Table(title="Static Coverage — Defined vs Implemented",
              box=box.ROUNDED, show_header=True, header_style="bold white")
    t.add_column("Group",    style="cyan",  no_wrap=True)
    t.add_column("Defined",  justify="right", width=8)
    t.add_column("CLI?",     justify="center", width=6)
    t.add_column("Commands", justify="right", width=9)
    t.add_column("CLI file(s)", style="dim")

    for r in sorted(static, key=lambda x: x["group"]):
        cli_str = ", ".join(r["cli_files"]) or "—"
        check   = "[green]✓[/green]" if r["has_cli"] else "[red]✗[/red]"
        t.add_row(r["group"], str(r["defined"]), check, str(r["commands"]), cli_str)

    console.print(t)

    total_groups   = len(static)
    covered_groups = sum(1 for r in static if r["has_cli"])
    total_ops      = sum(r["defined"]  for r in static)
    total_cmds     = sum(r["commands"] for r in static)
    pct_g = int(covered_groups / total_groups * 100) if total_groups else 0
    pct_c = min(int(total_cmds / total_ops * 100), 100) if total_ops else 0

    console.print(f"\n  Groups covered : [bold]{covered_groups}/{total_groups}[/bold] ({pct_g}%)")
    console.print(f"  Operations def.: [bold]{total_ops}[/bold]  |  CLI commands: [bold]{total_cmds}[/bold] (~{pct_c}% op-level)\n")


def print_probe_table(probes: list[dict]) -> None:
    t = Table(title="Live Probe Results",
              box=box.ROUNDED, show_header=True, header_style="bold white")
    t.add_column("#",        style="dim",   width=3)
    t.add_column("Label",    style="cyan",  min_width=30)
    t.add_column("Method",   width=7)
    t.add_column("Status",   justify="right", width=7)
    t.add_column("Verdict",  width=12)
    t.add_column("Notes")

    for i, p in enumerate(probes, 1):
        note = ""
        if p["item_count"] is not None:
            note = f"[green]{p['item_count']} items[/green]"
        elif p["error_body"]:
            note = f"[dim]{p['error_body'][:80]}[/dim]"
        t.add_row(
            str(i),
            p["label"],
            p["method"],
            str(p["status"]) if p["status"] else "—",
            f"[{p['style']}]{p['verdict']}[/{p['style']}]",
            note,
        )
    console.print(t)

    live    = sum(1 for p in probes if "✓" in p["verdict"])
    dep     = sum(1 for p in probes if "~" in p["verdict"])
    missing = sum(1 for p in probes if "✗" in p["verdict"])
    console.print(
        f"\n  Live: [bold green]{live}[/bold green]  "
        f"Deployed (needs fix): [bold yellow]{dep}[/bold yellow]  "
        f"Missing/404: [bold red]{missing}[/bold red]\n"
    )

    gaps = [p for p in probes if "✗" in p["verdict"]]
    if gaps:
        console.print("[bold red]Endpoints not found (possible API changes or version drift):[/bold red]")
        for p in gaps:
            console.print(f"  [red]• {p['method']} {p['endpoint']}[/red]")
        console.print()

    needs_fix = [p for p in probes if "~" in p["verdict"]]
    if needs_fix:
        console.print("[bold yellow]Deployed but returning non-2xx (payload/auth/params likely stale):[/bold yellow]")
        for p in needs_fix:
            console.print(f"  [yellow]• {p['method']} {p['endpoint']}[/yellow]  [dim]{p['error_body'][:120]}[/dim]")
        console.print()


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Purview CLI — API coverage report")
    parser.add_argument("--update-readme", action="store_true",
                        help="Patch README.md with the coverage table")
    parser.add_argument("--no-probe", action="store_true",
                        help="Skip live endpoint probing (static analysis only)")
    args = parser.parse_args()

    console.rule("[bold cyan]Purview CLI — API Coverage Report[/bold cyan]")

    # ── 1. Static analysis ────────────────────────────────────────────────
    console.print("\n[bold]Step 1 — Static analysis[/bold]")
    static = build_static_coverage()
    print_static_table(static)

    # ── 2. Live probes ────────────────────────────────────────────────────
    probes: list[dict] = []
    if not args.no_probe:
        console.print("[bold]Step 2 — Live endpoint probes[/bold]")
        account_name = os.getenv("PURVIEW_NAME", "kaydemopurview")
        config  = SyncPurviewConfig(account_name=account_name, azure_region="public")
        client  = SyncPurviewClient(config)
        console.print(f"  Account: [green]{config.account_name}[/green]\n")

        for label, ep, method, params, payload in LIVE_PROBES:
            console.print(f"  [dim]probing {method} {ep} …[/dim]", end="\r")
            result = probe_endpoint(client, label, ep, method, params, payload)
            probes.append(result)

        console.print(" " * 80, end="\r")   # clear spinner line
        print_probe_table(probes)
    else:
        console.print("[dim]  (live probing skipped)[/dim]\n")

    # ── 3. README update ─────────────────────────────────────────────────
    if args.update_readme:
        console.print("[bold]Step 3 — Updating README.md[/bold]")
        coverage_md = build_coverage_markdown(static, probes)
        changed = patch_readme(coverage_md)
        if changed:
            console.print("  [green]✓ README.md patched — coverage section updated.[/green]")
        else:
            console.print("  [dim]README.md already up to date.[/dim]")
    else:
        console.print("[dim]Tip: run with --update-readme to persist this table to README.md[/dim]")


if __name__ == "__main__":
    main()


