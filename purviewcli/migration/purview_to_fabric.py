# SPDX-License-Identifier: Apache-2.0
"""Deterministic matching and planning for the Purview UC -> Fabric sync.

This module contains the pure "brain" of the migration: given normalized
Purview and Fabric state (see :mod:`purviewcli.migration.models`), it
produces a :class:`~purviewcli.migration.models.MigrationPlan` describing
every proposed change, with no network access and no side effects. This
keeps matching/planning fully unit-testable and keeps policy decisions
(conflict handling, tag-overflow behavior, description truncation) in one
auditable place.

Retrieving and normalizing live data from ``UnifiedCatalogClient`` and
``FabricClient`` into these plain models is intentionally kept out of this
module; that glue lives in the CLI/service layer (a later step) so it can
evolve independently of this planning logic.
"""

from __future__ import annotations

import re
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from .models import (
    AssetMatch,
    DomainAction,
    DomainPlan,
    FabricCatalogEntry,
    FabricDomain,
    FabricItemState,
    FieldChange,
    ItemDecision,
    ItemPlan,
    ItemTagPlan,
    MatchOutcome,
    MatchSuggestion,
    MigrationMapping,
    MigrationPlan,
    NonPortableSummary,
    PurviewAsset,
    PurviewDomain,
    PurviewGovernanceObject,
    TagDecision,
    WorkspaceDomainAssignmentPlan,
)

#: Fabric tag display names are capped at this length by the platform.
TAG_NAME_MAX_LENGTH = 40
#: Fabric item descriptions are capped at this length by the platform.
DESCRIPTION_MAX_LENGTH = 256
#: Fabric enforces this maximum number of tags per item.
MAX_TAGS_PER_ITEM = 10

_SLUG_RE = re.compile(r"[^a-zA-Z0-9._ -]")


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------


def filter_assets_by_domain(assets: Sequence[PurviewAsset], domain_ids: Sequence[str]) -> List[PurviewAsset]:
    """Restrict assets to the given Purview domain IDs (no filter if empty)."""
    if not domain_ids:
        return list(assets)
    allowed = set(domain_ids)
    return [a for a in assets if a.domain_id in allowed]


def filter_catalog_entries_by_workspace(
    entries: Sequence[FabricCatalogEntry], workspace_ids: Sequence[str]
) -> List[FabricCatalogEntry]:
    """Restrict Fabric catalog entries to the given workspace IDs (no filter if empty)."""
    if not workspace_ids:
        return list(entries)
    allowed = set(workspace_ids)
    return [e for e in entries if e.workspace_id in allowed]


# ---------------------------------------------------------------------------
# Matching
# ---------------------------------------------------------------------------


def extract_embedded_fabric_ref(asset: PurviewAsset) -> Optional[Tuple[str, str]]:
    """Look for an embedded ``(workspaceId, itemId)`` reference on a Purview asset.

    Checks the asset's ``source`` object first (where Fabric-originated
    Purview assets typically carry their origin identifiers), then falls
    back to ``type_properties``, accepting a small set of known key-name
    variants used by different Purview scan/ingestion paths.
    """
    for container in (asset.source, asset.type_properties):
        if not container:
            continue
        workspace_id = (
            container.get("workspaceId")
            or container.get("workspace_id")
            or container.get("fabricWorkspaceId")
        )
        item_id = (
            container.get("itemId")
            or container.get("item_id")
            or container.get("fabricItemId")
        )
        if workspace_id and item_id:
            return str(workspace_id), str(item_id)
    return None


def _find_catalog_entry(
    entries_by_key: Dict[Tuple[str, str], FabricCatalogEntry], workspace_id: str, item_id: str
) -> Optional[FabricCatalogEntry]:
    return entries_by_key.get((workspace_id, item_id))


def _suggest_by_name(
    asset: PurviewAsset, entries: Sequence[FabricCatalogEntry], limit: int = 3
) -> List[MatchSuggestion]:
    """Surface likely-but-unproven candidates for human review only.

    These suggestions never authorize a write (see
    :meth:`AssetMatch.is_writable`); they exist purely to speed up building
    an explicit mapping file.
    """
    target_name = (asset.name or "").strip().lower()
    if not target_name:
        return []
    suggestions: List[MatchSuggestion] = []
    for entry in entries:
        if (entry.display_name or "").strip().lower() == target_name:
            suggestions.append(
                MatchSuggestion(
                    workspace_id=entry.workspace_id,
                    item_id=entry.id,
                    display_name=entry.display_name,
                    reason="exact_name_match",
                )
            )
        if len(suggestions) >= limit:
            break
    return suggestions


def resolve_matches(
    assets: Sequence[PurviewAsset],
    catalog_entries: Sequence[FabricCatalogEntry],
    mapping: Optional[MigrationMapping] = None,
) -> List[AssetMatch]:
    """Resolve each Purview asset to at most one Fabric item.

    Precedence: embedded Fabric IDs first, then an explicit mapping entry.
    Anything else is ``unmatched`` (with non-authoritative name suggestions
    only) -- fuzzy/name-only matching is never sufficient to authorize a
    write, per the approved migration design.
    """
    entries_by_key = {(e.workspace_id, e.id): e for e in catalog_entries}
    mapping_by_source = mapping.by_purview_asset_id() if mapping else {}
    matches: List[AssetMatch] = []

    for asset in assets:
        embedded = extract_embedded_fabric_ref(asset)
        if embedded:
            workspace_id, item_id = embedded
            entry = _find_catalog_entry(entries_by_key, workspace_id, item_id)
            if entry is not None:
                matches.append(
                    AssetMatch(
                        purview_asset_id=asset.id,
                        outcome=MatchOutcome.MATCHED_BY_ID,
                        workspace_id=workspace_id,
                        item_id=item_id,
                    )
                )
            else:
                matches.append(
                    AssetMatch(
                        purview_asset_id=asset.id,
                        outcome=MatchOutcome.TARGET_NOT_FOUND,
                        workspace_id=workspace_id,
                        item_id=item_id,
                        reason=(
                            f"Embedded Fabric reference workspaceId={workspace_id!r} "
                            f"itemId={item_id!r} was not found in the current Fabric catalog scope."
                        ),
                    )
                )
            continue

        mapping_entry = mapping_by_source.get(asset.id)
        if mapping_entry is not None:
            entry = _find_catalog_entry(entries_by_key, mapping_entry.workspace_id, mapping_entry.item_id)
            if entry is not None:
                matches.append(
                    AssetMatch(
                        purview_asset_id=asset.id,
                        outcome=MatchOutcome.MATCHED_BY_MAPPING,
                        workspace_id=mapping_entry.workspace_id,
                        item_id=mapping_entry.item_id,
                    )
                )
            else:
                matches.append(
                    AssetMatch(
                        purview_asset_id=asset.id,
                        outcome=MatchOutcome.TARGET_NOT_FOUND,
                        workspace_id=mapping_entry.workspace_id,
                        item_id=mapping_entry.item_id,
                        reason=(
                            f"Mapping file target workspaceId={mapping_entry.workspace_id!r} "
                            f"itemId={mapping_entry.item_id!r} was not found in the current Fabric catalog scope."
                        ),
                    )
                )
            continue

        matches.append(
            AssetMatch(
                purview_asset_id=asset.id,
                outcome=MatchOutcome.UNMATCHED,
                reason="No embedded Fabric reference and no explicit mapping entry.",
                suggestions=_suggest_by_name(asset, catalog_entries),
            )
        )

    return matches


def validate_mapping_targets_are_unambiguous(
    mapping: MigrationMapping, assets_by_id: Dict[str, PurviewAsset]
) -> List[str]:
    """Return human-readable errors for mapping entries with unresolvable sources.

    Referencing a Purview asset ID that no longer exists is flagged as
    ``invalid_mapping`` material; callers should surface these before
    treating the run as safe to apply.
    """
    errors = []
    for entry in mapping.entries:
        if entry.purview_asset_id not in assets_by_id:
            errors.append(
                f"Mapping entry references unknown Purview asset id {entry.purview_asset_id!r}"
            )
    return errors


# ---------------------------------------------------------------------------
# Item metadata planning
# ---------------------------------------------------------------------------


def plan_item_metadata(
    asset: PurviewAsset,
    match: AssetMatch,
    current_state: FabricItemState,
    overwrite: bool = False,
    truncate_descriptions: bool = False,
) -> ItemPlan:
    """Diff a matched asset's portable metadata against current Fabric state.

    Policy:
      - A blank/empty current value being filled in is never a conflict.
      - A non-blank current value that differs from the desired value is a
        conflict unless ``overwrite`` is set.
      - A description longer than 256 characters is a validation error
        unless ``truncate_descriptions`` is set, in which case it is
        truncated to exactly 256 characters before diffing/conflict checks.
    """
    changes: List[FieldChange] = []
    validation_errors: List[str] = []
    truncated = False
    has_conflict = False

    # -- display name --
    desired_name = asset.name
    current_name = current_state.display_name
    if desired_name and desired_name != current_name:
        if current_name and not overwrite:
            has_conflict = True
        changes.append(FieldChange(field="displayName", current=current_name, desired=desired_name))

    # -- description --
    desired_description = asset.description
    if desired_description is not None and len(desired_description) > DESCRIPTION_MAX_LENGTH:
        if truncate_descriptions:
            desired_description = desired_description[:DESCRIPTION_MAX_LENGTH]
            truncated = True
        else:
            validation_errors.append(
                f"Description exceeds Fabric's {DESCRIPTION_MAX_LENGTH}-character limit "
                f"({len(asset.description)} characters); pass --truncate-descriptions to allow this."
            )
            desired_description = None  # do not propose a change we can't legally apply

    current_description = current_state.description
    if desired_description is not None and desired_description != (current_description or None):
        if current_description and not overwrite:
            has_conflict = True
        changes.append(
            FieldChange(field="description", current=current_description, desired=desired_description)
        )

    if validation_errors:
        decision = ItemDecision.VALIDATION_ERROR
    elif not changes:
        decision = ItemDecision.NO_CHANGE
    elif has_conflict:
        decision = ItemDecision.CONFLICT
    else:
        decision = ItemDecision.READY

    return ItemPlan(
        purview_asset_id=asset.id,
        workspace_id=current_state.workspace_id,
        item_id=current_state.item_id,
        decision=decision,
        changes=changes,
        validation_errors=validation_errors,
        truncated_description=truncated,
    )


# ---------------------------------------------------------------------------
# Governance tag namespacing and planning
# ---------------------------------------------------------------------------


def namespaced_tag_name(object_type: str, name: str) -> str:
    """Derive a deterministic, collision-safe Fabric tag name.

    Format: ``purview:<object_type>:<sanitized name>``, truncated to
    Fabric's 40-character tag-name limit. Sanitization strips characters
    outside a conservative safe set so tag names round-trip cleanly through
    Fabric's admin APIs regardless of the source Purview object's name.
    """
    sanitized = _SLUG_RE.sub("", name or "").strip()
    prefix = f"purview:{object_type}:"
    available = TAG_NAME_MAX_LENGTH - len(prefix)
    return f"{prefix}{sanitized[:available]}"


def plan_governance_tag_names(objects: Sequence[PurviewGovernanceObject]) -> List[str]:
    """Compute the deduplicated set of namespaced tag names for governance objects."""
    seen: Dict[str, None] = {}
    for obj in objects:
        seen[namespaced_tag_name(obj.object_type, obj.name)] = None
    return list(seen.keys())


def plan_item_tags(
    workspace_id: str,
    item_id: str,
    current_state: FabricItemState,
    desired_tag_names: Sequence[str],
) -> ItemTagPlan:
    """Plan governance-tag application for one item, honoring the tag-overflow policy.

    All pre-existing tags are always preserved. If applying every new
    governance tag would push the item over Fabric's 10-tags-per-item
    limit, *none* of the new tags are applied (all-or-nothing) and the item
    is reported as ``tag_overflow`` so a human can prune manually.
    """
    current_names = set(current_state.tag_names())
    desired_names = list(dict.fromkeys(desired_tag_names))  # de-dup, preserve order

    already_present = [t for t in desired_names if t in current_names]
    new_tags = [t for t in desired_names if t not in current_names]

    if not new_tags:
        return ItemTagPlan(
            workspace_id=workspace_id,
            item_id=item_id,
            decision=TagDecision.NO_CHANGE,
            tags_already_present=already_present,
        )

    total_after_apply = len(current_names) + len(new_tags)
    if total_after_apply > MAX_TAGS_PER_ITEM:
        return ItemTagPlan(
            workspace_id=workspace_id,
            item_id=item_id,
            decision=TagDecision.TAG_OVERFLOW,
            tags_already_present=already_present,
            overflow_tags=new_tags,
        )

    return ItemTagPlan(
        workspace_id=workspace_id,
        item_id=item_id,
        decision=TagDecision.READY,
        tags_to_apply=new_tags,
        tags_already_present=already_present,
    )


# ---------------------------------------------------------------------------
# Domain planning
# ---------------------------------------------------------------------------


def index_fabric_domains_by_name(domains: Sequence[FabricDomain]) -> Dict[str, FabricDomain]:
    """Build a case-insensitive display-name index for :func:`plan_domain`."""
    return {d.display_name.strip().lower(): d for d in domains}


def plan_domain(
    purview_domain: PurviewDomain,
    target_workspace_ids: Sequence[str],
    fabric_domains_by_name: Dict[str, FabricDomain],
    workspace_current_domain: Dict[str, str],
) -> DomainPlan:
    """Plan a Purview domain's mapping onto a Fabric domain and workspace assignments.

    Reuses an existing Fabric domain matched by case-insensitive display
    name; otherwise proposes creating one. ``fabric_domains_by_name`` must be
    keyed by lowercase display name -- see :func:`index_fabric_domains_by_name`.
    Because a Fabric workspace can only belong to a single domain, a
    workspace already assigned to a *different* domain is always reported as
    a conflict and never reassigned automatically, regardless of
    ``--overwrite`` (which only governs item metadata).
    """
    desired_name = purview_domain.name
    existing = fabric_domains_by_name.get(desired_name.strip().lower())

    assignments: List[WorkspaceDomainAssignmentPlan] = []
    for workspace_id in target_workspace_ids:
        current_domain_id = workspace_current_domain.get(workspace_id)
        desired_domain_id = existing.id if existing else ""  # resolved post-creation if new

        if existing is not None and current_domain_id == existing.id:
            action = DomainAction.NO_CHANGE
            conflict_reason = None
        elif current_domain_id and (existing is None or current_domain_id != existing.id):
            action = DomainAction.WORKSPACE_CONFLICT
            conflict_reason = (
                f"Workspace {workspace_id!r} is already assigned to Fabric domain "
                f"{current_domain_id!r}; a workspace may only belong to one domain."
            )
        else:
            action = DomainAction.ASSIGN_WORKSPACE
            conflict_reason = None

        assignments.append(
            WorkspaceDomainAssignmentPlan(
                workspace_id=workspace_id,
                current_domain_id=current_domain_id,
                desired_domain_id=desired_domain_id,
                action=action,
                conflict_reason=conflict_reason,
            )
        )

    domain_action = DomainAction.REUSE_DOMAIN if existing else DomainAction.CREATE_DOMAIN
    if not any(a.action == DomainAction.ASSIGN_WORKSPACE for a in assignments) and existing:
        # Nothing to do for this domain if every target workspace is already correct.
        if all(a.action == DomainAction.NO_CHANGE for a in assignments):
            domain_action = DomainAction.NO_CHANGE

    return DomainPlan(
        purview_domain_id=purview_domain.id,
        fabric_domain_name=desired_name,
        fabric_domain_id=existing.id if existing else None,
        action=domain_action,
        workspace_assignments=assignments,
    )


# ---------------------------------------------------------------------------
# Non-portable metadata summary
# ---------------------------------------------------------------------------


def build_non_portable_summary(
    domains: Sequence[PurviewDomain],
    governance_objects: Sequence[PurviewGovernanceObject],
    owners: Sequence[Dict[str, str]] = (),
    relationships: Sequence[Dict[str, str]] = (),
) -> NonPortableSummary:
    """Collect Purview metadata with no native Fabric representation for audit reporting.

    Terms/data products/CDEs *do* get a portable representation (namespaced
    tags, see :func:`plan_item_tags`), but their full schema/hierarchy is
    still summarized here since only the tag name survives onto Fabric.
    """
    summary = NonPortableSummary()
    summary.domains = [d.to_dict() for d in domains]
    summary.terms = [g.to_dict() for g in governance_objects if g.object_type == "term"]
    summary.data_products = [g.to_dict() for g in governance_objects if g.object_type == "data_product"]
    summary.cdes = [g.to_dict() for g in governance_objects if g.object_type == "cde"]
    summary.owners = list(owners)
    summary.relationships = list(relationships)
    return summary
