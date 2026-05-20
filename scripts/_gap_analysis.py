"""
Gap analysis: endpoints.py definitions vs client _*.py implementations.
Prints:
  1. Ops defined in ENDPOINTS but never referenced in client files
  2. Client files referencing op keys that don't exist in ENDPOINTS
  3. Summary of "advanced / fictional" ops (labeled 'new for 100% coverage')
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from purviewcli.client.endpoints import ENDPOINTS

LEGACY = {"search", "scan", "share"}
active_groups = {k: v for k, v in ENDPOINTS.items() if k not in LEGACY}

# ── Collect ENDPOINTS[group][op] references from all client _*.py files ──────
client_dir = Path("purviewcli/client")
all_refs = {}   # group -> {op, ...}
for f in client_dir.glob("_*.py"):
    src = f.read_text(encoding="utf-8")
    # matches ENDPOINTS["entity"]["get"]  or  ENDPOINTS['entity']['get']
    for group, op in re.findall(
        r'ENDPOINTS\[["\'](\w+)["\']\]\[["\'](\w+)["\']\]', src
    ):
        all_refs.setdefault(group, set()).add(op)

# ── 1. Defined but never called in any client file ───────────────────────────
print("\n" + "=" * 70)
print("  OPS IN endpoints.py  →  NOT REFERENCED IN ANY CLIENT FILE")
print("=" * 70)
total_unused = 0
for group in sorted(active_groups):
    ops = active_groups[group]
    used = all_refs.get(group, set())
    missing = [op for op in ops if op not in used]
    if missing:
        print(f"\n  [{group}]  ({len(missing)} of {len(ops)} unused)")
        for op in missing:
            print(f"      {op:<45}  {ops[op]}")
        total_unused += len(missing)

total_defined = sum(len(v) for v in active_groups.values())
print(f"\n  → {total_unused} / {total_defined} ops defined but never called in client")

# ── 2. Client references that don't exist in ENDPOINTS ───────────────────────
print("\n" + "=" * 70)
print("  CLIENT FILES REFERENCING ENDPOINT KEYS THAT DON'T EXIST")
print("=" * 70)
phantom = 0
for group in sorted(all_refs):
    defined = set(ENDPOINTS.get(group, {}).keys())
    bad = [op for op in all_refs[group] if op not in defined]
    if bad:
        print(f"\n  [{group}] bad refs: {bad}")
        phantom += len(bad)
if phantom == 0:
    print("  None found.")
else:
    print(f"\n  → {phantom} phantom references")

# ── 3. "Advanced / fictional" ops (added for coverage but likely not real) ───
advanced_pattern = re.compile(
    r"# Advanced .+? \(new for 100% coverage\).*?(?=\n\s*#|\Z)", re.DOTALL
)
src_ep = Path("purviewcli/client/endpoints.py").read_text(encoding="utf-8")
# find op names defined under "Advanced ... new for 100% coverage" comments
fake_ops = {}  # group -> [op, ...]
for match in re.finditer(
    r"# Advanced[^\n]+ \(new for 100% coverage\)\n((?:\s+\"[\w]+\":[^\n]+\n)+)",
    src_ep,
):
    block = match.group(1)
    ops_found = re.findall(r'"([\w]+)":', block)
    # find which group they belong to by looking back
    before = src_ep[: match.start()]
    grp_match = re.findall(r'"(\w+)":\s*\{', before)
    group = grp_match[-1] if grp_match else "?"
    fake_ops.setdefault(group, []).extend(ops_found)

print("\n" + "=" * 70)
print("  'NEW FOR 100% COVERAGE' OPS — likely NOT in real Purview API")
print("=" * 70)
total_fake = 0
for group, ops in sorted(fake_ops.items()):
    print(f"\n  [{group}]")
    for op in ops:
        path = active_groups.get(group, {}).get(op, "???")
        in_client = op in all_refs.get(group, set())
        tag = "  [client: YES]" if in_client else "  [client: NO]"
        print(f"      {op:<45}  {path}{tag}")
    total_fake += len(ops)

print(f"\n  → {total_fake} ops flagged as potentially fictional")
print()
