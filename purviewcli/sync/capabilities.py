# SPDX-License-Identifier: Apache-2.0
"""Single source of truth for the Purview UC -> Fabric OneLake catalog sync
feature-status table.

Both ``pvw fabric sync capabilities`` (see :mod:`purviewcli.cli.fabric`) and
``docs/purview-to-fabric-onelake-sync.md`` describe the same information; this
module is the structured data behind the CLI rendering, so the CLI can never
silently drift from what's actually implemented in ``purviewcli/sync/``. The
docs page remains hand-maintained prose/links, but its status table should be
kept identical to this module's contents (checked implicitly by
``tests/test_fabric_capabilities.py``'s docs-in-sync assertions where
practical, and by manual review otherwise).

When a capability's status changes (e.g. a new Purview/Fabric API makes a
``PLANNED`` row possible), update the entry here first, then mirror the change
into the docs page and, if newly ``SUPPORTED``, implement it in
``purviewcli/sync/`` following the existing additive/opt-in pattern.
"""

from __future__ import annotations

import dataclasses
from enum import Enum
from typing import List


class CapabilityStatus(str, Enum):
    """Status legend shared with ``docs/purview-to-fabric-onelake-sync.md``."""

    SUPPORTED = "supported"
    PARTIAL = "partial"
    PLANNED = "planned"
    NOT_SUPPORTED = "not_supported"

    @property
    def label(self) -> str:
        return {
            CapabilityStatus.SUPPORTED: "Supported",
            CapabilityStatus.PARTIAL: "Partial",
            CapabilityStatus.PLANNED: "Planned / TBD",
            CapabilityStatus.NOT_SUPPORTED: "Not supported",
        }[self]

    @property
    def symbol(self) -> str:
        return {
            CapabilityStatus.SUPPORTED: "[OK]",
            CapabilityStatus.PARTIAL: "[!]",
            CapabilityStatus.PLANNED: "[!]",
            CapabilityStatus.NOT_SUPPORTED: "[X]",
        }[self]


@dataclasses.dataclass(frozen=True)
class SyncCapability:
    """One row of the Purview -> Fabric sync status board."""

    purview_capability: str
    fabric_target: str
    status: CapabilityStatus
    notes: str
    command_flag: str = "(always on)"

    def to_dict(self) -> dict:
        return {
            "purview_capability": self.purview_capability,
            "fabric_target": self.fabric_target,
            "status": self.status.value,
            "status_label": self.status.label,
            "notes": self.notes,
            "command_flag": self.command_flag,
        }


CAPABILITIES: List[SyncCapability] = [
    SyncCapability(
        purview_capability="Data asset display name / description",
        fabric_target="Item `displayName` / `description`",
        status=CapabilityStatus.SUPPORTED,
        notes="Always on; additive-only, dry-run by default.",
    ),
    SyncCapability(
        purview_capability="Governance domain",
        fabric_target="Fabric domain + workspace assignment",
        status=CapabilityStatus.SUPPORTED,
        notes="Matched/created by name; always on.",
    ),
    SyncCapability(
        purview_capability="Glossary term name",
        fabric_target="Namespaced tag `purview:glossary:<name>`",
        status=CapabilityStatus.PARTIAL,
        notes="Only the name is portable -- no hierarchy, definitions, or relationships.",
    ),
    SyncCapability(
        purview_capability="Data product name",
        fabric_target="Namespaced tag `purview:dataproduct:<name>`",
        status=CapabilityStatus.PARTIAL,
        notes="Name only; Fabric has no first-class \"data product\" object yet.",
    ),
    SyncCapability(
        purview_capability="Critical Data Element (CDE) name",
        fabric_target="Namespaced tag `purview:cde:<name>`",
        status=CapabilityStatus.PARTIAL,
        notes="Name only.",
    ),
    SyncCapability(
        purview_capability="Data Map classifications (e.g. MICROSOFT.PERSONAL.EMAIL)",
        fabric_target="Namespaced tag `purview:classification:<name>`",
        status=CapabilityStatus.SUPPORTED,
        notes="Requires a resolvable Data Map link + known type mapping.",
        command_flag="--sync-classifications",
    ),
    SyncCapability(
        purview_capability="Data Map labels (free-text)",
        fabric_target="Namespaced tag `purview:label:<name>`",
        status=CapabilityStatus.SUPPORTED,
        notes="Same source/limitations as classifications.",
        command_flag="--sync-classifications",
    ),
    SyncCapability(
        purview_capability="Sensitivity label (MIP)",
        fabric_target="Item `sensitivityLabel.id` + admin `bulkSetLabels`/`bulkRemoveLabels`",
        status=CapabilityStatus.PLANNED,
        notes=(
            "Fabric side is now fully ready (verified 2026-09-22): Get/List/Create Item "
            "return `sensitivityLabel.id`, Create accepts `sensitivityLabelSettings`, and "
            "admin bulk set/remove label APIs exist. Still blocked on the PURVIEW read "
            "side -- no confirmed per-asset API returns an asset's applied MIP label ID "
            "(only tenant-wide aggregate reports)."
        ),
        command_flag="(not available)",
    ),
    SyncCapability(
        purview_capability="Data quality rules / scores",
        fabric_target="(no Fabric OneLake catalog field identified)",
        status=CapabilityStatus.PLANNED,
        notes="Watch Fabric's data-quality feature area for a documented per-item API.",
        command_flag="(not available)",
    ),
    SyncCapability(
        purview_capability="Lineage",
        fabric_target="(no confirmed mapping)",
        status=CapabilityStatus.PLANNED,
        notes=(
            "Fabric's lineage model differs structurally from Purview's Atlas "
            "process/relationship graph; needs its own design once a compatible "
            "ingestion API ships."
        ),
        command_flag="(not available)",
    ),
    SyncCapability(
        purview_capability="Data Products as first-class Fabric objects",
        fabric_target="(no Fabric object exists)",
        status=CapabilityStatus.NOT_SUPPORTED,
        notes="Fabric has no native \"data product\" concept beyond tags today.",
        command_flag="(not available)",
    ),
    SyncCapability(
        purview_capability="RBAC -> ABAC access policies",
        fabric_target="(no confirmed Fabric equivalent)",
        status=CapabilityStatus.NOT_SUPPORTED,
        notes="No matching Fabric item/workspace attribute-based policy API today.",
        command_flag="(not available)",
    ),
    SyncCapability(
        purview_capability="Custom / managed attributes",
        fabric_target="(no confirmed Fabric field)",
        status=CapabilityStatus.PLANNED,
        notes=(
            "Present in Purview UC domain responses (`managedAttributes`); no "
            "confirmed arbitrary-property field on Fabric items yet."
        ),
        command_flag="(not available)",
    ),
    SyncCapability(
        purview_capability="Full glossary hierarchy (parent/child terms, relationships)",
        fabric_target="(no Fabric equivalent)",
        status=CapabilityStatus.NOT_SUPPORTED,
        notes="Only the term's name is portable as a tag; no structured term/hierarchy object.",
        command_flag="(not available)",
    ),
]


def get_capabilities() -> List[SyncCapability]:
    """Return the full, ordered capability list (a fresh list each call)."""
    return list(CAPABILITIES)
