# SPDX-License-Identifier: Apache-2.0
"""Adapter/orchestration layer wiring UnifiedCatalogClient and FabricClient
into the pure matching/planning/execution engine.

Everything in :mod:`purviewcli.sync.purview_to_fabric` and
:mod:`purviewcli.sync.execution` is deliberately free of network I/O so
it can be unit-tested without a live tenant. This module is the (thin,
best-effort) glue that normalizes real API responses into the typed models
those pure functions consume, and is where any tenant-specific field-naming
differences should be adjusted if your Purview/Fabric responses vary from
what's assumed here.

Fabric response shapes verified live against a real tenant (2026-09-18):
    - ``GET /v1/tags``: ``{"value": [{"id", "displayName", "scope"}]}``.
    - ``GET /v1/admin/domains``: ``{"domains": [{"id", "displayName",
      "description", "parentDomainId"}]}`` -- **not** a ``value``-keyed
      envelope.
    - ``POST /v1/catalog/search``: ``{"value": [...], "continuationToken"}``,
      where each entry nests its workspace under
      ``hierarchy.workspace.{id,displayName}`` -- **not** flat
      ``workspaceId``/``workspaceDisplayName`` fields as originally assumed
      (fixed in :func:`normalize_catalog_entries`, which now checks the flat
      fields first as a defensive fallback, then falls back to the nested
      shape).
    - ``GET /v1/workspaces/{ws}/items/{id}``: flat ``id``/``type``/
      ``displayName``/``description``/``workspaceId``; a ``tags`` array
      (``[{"id","displayName"}]``) is present only when the item has at
      least one tag applied and is omitted entirely otherwise (confirmed via
      a live ``applyTags``/``unapplyTags`` round-trip).
    - ``POST /v1/workspaces/{ws}/items/{id}/applyTags`` and
      ``.../unapplyTags``: body is ``{"tags": [<tag-id-string>, ...]}`` --
      plain GUID strings, not ``{"id": ...}`` objects.

Purview response shapes verified live against a real tenant (2026-09-18):
    - ``pvw uc domain list`` (``GET .../governanceDomains``): matches the
      field names already assumed below (``id``/``name``/``description``/
      ``type``/``status``/``managedAttributes``).
    - Classic Atlas ``GET /entity/guid/{guid}`` (and, by the same endpoint
      family, ``GET /entity/uniqueAttribute/type/{typeName}``): the
      ``entity`` sub-object's ``classifications`` field is a list of
      ``{"typeName", "attributes", "entityGuid", "entityStatus", ...}``, and
      ``labels`` is a plain list of strings (``["some-label"]``). This is
      the source :func:`fetch_entity_metadata` reads from.
    - The newer Unified Catalog Data Asset API (``list_data_assets``/
      ``get_data_asset``, preview ``2026-03-20-preview``) does **not** expose
      classifications, labels, tags, or a sensitivity label on the asset
      object at all -- confirmed live even with
      ``includeExtendedProperties=true`` on ``get_data_asset``. This is why
      classification/label sync (see :func:`enrich_assets_with_entity_metadata`)
      reads from the classic Entity API instead of the UC wrapper.
    - Creating a UC data asset linked to a Data Map entity requires
      ``source.type`` to be exactly ``"DataMap"`` (or ``"PurviewDataMap"``);
      any other value (e.g. the asset's own UC ``type``) is rejected with
      ``DataCatalogInvalidEntity``.
    - Purview's per-asset *sensitivity label* (MIP) has **no confirmed read
      API** in this codebase -- only tenant-wide aggregate reporting
      endpoints exist (``sensitivityLabel/labelSummary``,
      ``sensitivityLabel/labelInsights``). Sensitivity-label sync is
      therefore out of scope for now; see
      ``docs/fabric-sync-feature-parity.md``.
"""


from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional, Sequence

from .execution import (
    FabricMutationClient,
    apply_operations,
    apply_rollback,
    build_planned_operations,
    build_rollback_operations,
)
from .models import (
    FabricCatalogEntry,
    FabricDomain,
    FabricItemState,
    FabricTag,
    SyncMapping,
    SyncPlan,
    PurviewAsset,
    PurviewDomain,
    PurviewGovernanceObject,
    RollbackResult,
    RunCheckpoint,
    SyncRunResult,
)
from .purview_to_fabric import (
    build_non_portable_summary,
    filter_assets_by_domain,
    filter_catalog_entries_by_workspace,
    index_fabric_domains_by_name,
    plan_asset_metadata_tag_names,
    plan_domain,
    plan_governance_tag_names,
    plan_item_metadata,
    plan_item_tags,
    resolve_matches,
    validate_mapping_targets_are_unambiguous,
)
from .state import CheckpointStore, new_run_id

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Mapping file I/O
# ---------------------------------------------------------------------------


def load_mapping_file(path: Optional[str]) -> Optional[SyncMapping]:
    """Load and validate an explicit Purview-asset-to-Fabric-item mapping file."""
    if not path:
        return None
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    return SyncMapping.from_dict(data)


# ---------------------------------------------------------------------------
# Normalizing Purview Unified Catalog responses
# ---------------------------------------------------------------------------


def _as_list(response: Any) -> List[Dict[str, Any]]:
    """Unwrap a UC ``{"value": [...]}`` envelope, or pass through a bare list."""
    if isinstance(response, dict):
        return list(response.get("value", []) or [])
    if isinstance(response, list):
        return list(response)
    return []


def normalize_purview_domains(raw_domains: Sequence[Dict[str, Any]]) -> List[PurviewDomain]:
    """Normalize ``get_governance_domains`` results into :class:`PurviewDomain`."""
    domains = []
    for raw in raw_domains:
        domains.append(
            PurviewDomain(
                id=raw.get("id", ""),
                name=raw.get("name", ""),
                description=raw.get("description"),
                parent_id=raw.get("parentId"),
                type=raw.get("type", ""),
            )
        )
    return domains


def normalize_purview_assets(raw_assets: Sequence[Dict[str, Any]]) -> List[PurviewAsset]:
    """Normalize ``list_data_assets``/``get_data_asset`` results into :class:`PurviewAsset`.

    NOTE: field names below (``domainId``, ``typeProperties``, ``termIds``,
    ``dataProductIds``, ``criticalDataElementIds``, ``contacts``) follow the
    Unified Catalog naming convention used elsewhere in this client but have
    not been verified against a live tenant response; adjust here if your
    tenant's payload differs.
    """
    assets = []
    for raw in raw_assets:
        owners = [
            c.get("id", "") for c in (raw.get("contacts", {}).get("owner", []) or []) if isinstance(c, dict)
        ] if isinstance(raw.get("contacts"), dict) else []
        assets.append(
            PurviewAsset(
                id=raw.get("id", ""),
                name=raw.get("name", ""),
                description=raw.get("description"),
                type=raw.get("type", raw.get("dataAssetType", "")),
                source=raw.get("source", {}) or {},
                type_properties=raw.get("typeProperties", {}) or {},
                domain_id=raw.get("domainId"),
                term_ids=list(raw.get("termIds", []) or []),
                data_product_ids=list(raw.get("dataProductIds", []) or []),
                cde_ids=list(raw.get("criticalDataElementIds", []) or []),
                owners=owners,
            )
        )
    return assets


def normalize_governance_objects(
    raw_terms: Sequence[Dict[str, Any]],
    raw_data_products: Sequence[Dict[str, Any]],
    raw_cdes: Sequence[Dict[str, Any]],
) -> List[PurviewGovernanceObject]:
    """Normalize terms/data products/CDEs into a single typed list for tag planning."""
    objects: List[PurviewGovernanceObject] = []
    for raw in raw_terms:
        objects.append(
            PurviewGovernanceObject(
                id=raw.get("id", ""), name=raw.get("name", ""), object_type="term", domain_id=raw.get("domainId")
            )
        )
    for raw in raw_data_products:
        objects.append(
            PurviewGovernanceObject(
                id=raw.get("id", ""),
                name=raw.get("name", ""),
                object_type="data_product",
                domain_id=raw.get("domainId"),
            )
        )
    for raw in raw_cdes:
        objects.append(
            PurviewGovernanceObject(
                id=raw.get("id", ""), name=raw.get("name", ""), object_type="cde", domain_id=raw.get("domainId")
            )
        )
    return objects


# Maps a Unified Catalog asset ``type`` to the classic Atlas ``typeName``
# needed for ``entityReadUniqueAttribute``. Only unambiguous, well-known
# mappings are included; UC types that fold multiple Data Map types into one
# bucket (e.g. ``"General"`` covers Fabric lakehouses, warehouses, and
# datasets -- see ``_DM_TYPE_TO_UC`` in ``cli/unified_catalog.py``) are
# deliberately omitted so classification/label lookup is skipped rather than
# guessed for those assets.
_UC_TYPE_TO_ENTITY_TYPENAME: Dict[str, str] = {
    "ADLSGen2Path": "azure_datalake_gen2_path",
    "AzureSqlTable": "azure_sql_table",
}


def resolve_entity_type_name(uc_type: str) -> Optional[str]:
    """Best-effort reverse mapping from a UC asset ``type`` to an Atlas ``typeName``."""
    return _UC_TYPE_TO_ENTITY_TYPENAME.get(uc_type)


def fetch_entity_metadata(entity_client: Any, type_name: str, qualified_name: str):
    """Fetch one Data Map entity's classification/label names, best-effort.

    Uses ``entityReadUniqueAttribute`` (typeName + qualifiedName lookup) --
    the classic Atlas API, which is the only confirmed source of
    classifications/labels (see the module docstring). Any failure (entity
    not found, no Data Map linkage, transient error) is swallowed and
    reported as "nothing found" rather than failing the whole sync, since
    this is an enrichment step, not a hard requirement.

    Returns a ``(classification_names, label_names)`` tuple of ``List[str]``.
    """
    try:
        response = entity_client.entityReadUniqueAttribute(
            {"--typeName": type_name, "--qualifiedName": qualified_name}
        )
    except Exception:
        logger.debug(
            "entityReadUniqueAttribute failed for typeName=%s qualifiedName=%s",
            type_name,
            qualified_name,
            exc_info=True,
        )
        return [], []

    entity = response.get("entity", {}) if isinstance(response, dict) else {}
    classification_names = [
        c.get("typeName", "") for c in (entity.get("classifications", []) or []) if c.get("typeName")
    ]
    label_names = list(entity.get("labels", []) or [])
    return classification_names, label_names


def enrich_assets_with_entity_metadata(
    entity_client: Any, assets: Sequence[PurviewAsset]
) -> List[PurviewAsset]:
    """Populate each asset's ``classification_names``/``label_names`` from Data Map.

    Only assets whose ``source.qualifiedName`` is present *and* whose UC
    ``type`` has a known Atlas ``typeName`` mapping (see
    :func:`resolve_entity_type_name`) are looked up; all others are returned
    unchanged (empty classification/label lists), since there is no reliable
    way to resolve their underlying Data Map entity without guessing.
    """
    import dataclasses as _dataclasses

    enriched: List[PurviewAsset] = []
    for asset in assets:
        qualified_name = asset.source.get("qualifiedName") if isinstance(asset.source, dict) else None
        type_name = resolve_entity_type_name(asset.type)
        if qualified_name and type_name:
            classification_names, label_names = fetch_entity_metadata(entity_client, type_name, qualified_name)
        else:
            classification_names, label_names = [], []
        enriched.append(
            _dataclasses.replace(asset, classification_names=classification_names, label_names=label_names)
        )
    return enriched


def fetch_purview_state(
    uc_client: Any,
    domain_ids: Sequence[str] = (),
    entity_client: Any = None,
    sync_classifications: bool = False,
) -> Dict[str, List[Any]]:
    """Retrieve and normalize the full Purview UC state needed for an assessment.

    ``uc_client`` is expected to be a
    :class:`purviewcli.client._unified_catalog.UnifiedCatalogClient` (or a
    compatible test double). If ``domain_ids`` is given, data assets are
    fetched per-domain; otherwise all assets are fetched unfiltered.

    When ``sync_classifications`` is true, ``entity_client`` (a
    :class:`purviewcli.client._entity.Entity` or compatible test double) is
    used to enrich each asset with classification/label names via
    :func:`enrich_assets_with_entity_metadata`. Off by default: it costs one
    extra API call per asset and depends on Data Map linkage that not every
    UC asset has.
    """
    raw_domains = _as_list(uc_client.get_governance_domains({}))
    domains = normalize_purview_domains(raw_domains)
    if domain_ids:
        domains = [d for d in domains if d.id in set(domain_ids)]

    raw_assets: List[Dict[str, Any]] = []
    if domain_ids:
        for domain_id in domain_ids:
            raw_assets.extend(_as_list(uc_client.list_data_assets({"--domain-id": domain_id})))
    else:
        raw_assets.extend(_as_list(uc_client.list_data_assets({})))
    assets = normalize_purview_assets(raw_assets)
    if domain_ids:
        assets = filter_assets_by_domain(assets, domain_ids)
    if sync_classifications and entity_client is not None:
        assets = enrich_assets_with_entity_metadata(entity_client, assets)

    raw_terms = _as_list(uc_client.get_terms({}))
    raw_data_products = _as_list(uc_client.get_data_products({}))
    raw_cdes = _as_list(uc_client.get_critical_data_elements({}))
    governance_objects = normalize_governance_objects(raw_terms, raw_data_products, raw_cdes)

    return {
        "domains": domains,
        "assets": assets,
        "governance_objects": governance_objects,
    }


# ---------------------------------------------------------------------------
# Normalizing Fabric responses
# ---------------------------------------------------------------------------


def normalize_catalog_entries(raw_entries: Sequence[Dict[str, Any]]) -> List[FabricCatalogEntry]:
    """Normalize raw ``catalog/search`` entries into :class:`FabricCatalogEntry`.

    Verified live against ``POST /v1/catalog/search``: the workspace is nested
    under ``hierarchy.workspace.{id,displayName}``, not flat ``workspaceId``/
    ``workspaceDisplayName`` fields. The flat fields are still checked first as
    a defensive fallback in case a future/older API version or a different
    catalog entry ``type`` returns a flatter shape.
    """
    entries = []
    for raw in raw_entries:
        workspace = (raw.get("hierarchy") or {}).get("workspace") or {}
        entries.append(
            FabricCatalogEntry(
                id=raw.get("id", ""),
                type=raw.get("type", ""),
                display_name=raw.get("displayName", ""),
                description=raw.get("description"),
                workspace_id=raw.get("workspaceId") or workspace.get("id", ""),
                workspace_display_name=raw.get("workspaceDisplayName") or workspace.get("displayName", ""),
            )
        )
    return entries


def normalize_fabric_domains(raw_domains: Sequence[Dict[str, Any]]) -> List[FabricDomain]:
    domains = []
    for raw in raw_domains:
        domains.append(
            FabricDomain(
                id=raw.get("id", ""),
                display_name=raw.get("displayName", ""),
                description=raw.get("description"),
                parent_domain_id=raw.get("parentDomainId"),
            )
        )
    return domains


def fetch_fabric_catalog(fabric_client: Any, workspace_ids: Sequence[str] = ()) -> List[FabricCatalogEntry]:
    """Retrieve the full OneLake catalog, optionally scoped to given workspaces."""
    raw_entries = list(fabric_client.iter_catalog_entries())
    entries = normalize_catalog_entries(raw_entries)
    if workspace_ids:
        entries = filter_catalog_entries_by_workspace(entries, workspace_ids)
    return entries


def fetch_fabric_item_state(fabric_client: Any, workspace_id: str, item_id: str) -> FabricItemState:
    """Fetch the current display name/description/tags for one Fabric item."""
    raw = fabric_client.get_item(workspace_id, item_id)
    raw_tags = raw.get("tags", []) or []
    tags = [FabricTag(id=t.get("id", ""), display_name=t.get("displayName", "")) for t in raw_tags]
    return FabricItemState(
        workspace_id=workspace_id,
        item_id=item_id,
        display_name=raw.get("displayName", ""),
        description=raw.get("description"),
        tags=tags,
    )


def fetch_fabric_domains_and_workspace_assignments(
    fabric_client: Any,
) -> tuple:
    """Return ``(domains, workspace_id -> current domain id)`` for domain planning."""
    raw_domains = fabric_client.list_domains()
    domains = normalize_fabric_domains(raw_domains)
    workspace_current_domain: Dict[str, str] = {}
    for domain in domains:
        for workspace in fabric_client.list_domain_workspaces(domain.id):
            ws_id = workspace.get("id")
            if ws_id:
                workspace_current_domain[ws_id] = domain.id
    return domains, workspace_current_domain


# ---------------------------------------------------------------------------
# Building a full SyncPlan
# ---------------------------------------------------------------------------


def build_sync_plan(
    run_id: str,
    purview_assets: Sequence[PurviewAsset],
    purview_domains: Sequence[PurviewDomain],
    governance_objects: Sequence[PurviewGovernanceObject],
    catalog_entries: Sequence[FabricCatalogEntry],
    fabric_domains: Sequence[FabricDomain],
    workspace_current_domain: Dict[str, str],
    fabric_client: Any,
    mapping: Optional[SyncMapping] = None,
    target_workspace_ids: Sequence[str] = (),
    overwrite: bool = False,
    truncate_descriptions: bool = False,
    sync_classifications: bool = False,
) -> SyncPlan:
    """Run the full matching/planning pipeline and assemble a :class:`SyncPlan`.

    ``fabric_client`` is used only for read calls needed mid-planning
    (fetching each matched item's current state); no writes happen here.

    When ``sync_classifications`` is true, each asset's
    ``classification_names``/``label_names`` (populated ahead of time by
    ``fetch_purview_state(..., sync_classifications=True)``) are folded into
    that asset's desired tag list alongside its governance-object tags, via
    :func:`~.purview_to_fabric.plan_asset_metadata_tag_names`. Reuses the
    existing tag-sync pipeline (``plan_item_tags``/``APPLY_ITEM_TAGS``)
    unchanged -- classifications/labels are just another source of tag
    names, additive-only like glossary-term tags.
    """
    from datetime import datetime, timezone

    matches = resolve_matches(purview_assets, catalog_entries, mapping)
    assets_by_id = {a.id: a for a in purview_assets}

    item_plans = []
    tag_plans = []
    governance_by_domain: Dict[str, List[PurviewGovernanceObject]] = {}
    for obj in governance_objects:
        if obj.domain_id:
            governance_by_domain.setdefault(obj.domain_id, []).append(obj)

    for match in matches:
        if not match.is_writable():
            continue
        asset = assets_by_id.get(match.purview_asset_id)
        if asset is None:
            continue
        current_state = fetch_fabric_item_state(fabric_client, match.workspace_id, match.item_id)
        item_plans.append(
            plan_item_metadata(asset, match, current_state, overwrite=overwrite, truncate_descriptions=truncate_descriptions)
        )
        relevant_objects = governance_by_domain.get(asset.domain_id, []) if asset.domain_id else []
        desired_tags = plan_governance_tag_names(relevant_objects)
        if sync_classifications:
            desired_tags = list(dict.fromkeys(desired_tags + plan_asset_metadata_tag_names(asset)))
        if desired_tags:
            tag_plans.append(plan_item_tags(match.workspace_id, match.item_id, current_state, desired_tags))

    fabric_domains_by_name = index_fabric_domains_by_name(fabric_domains)
    domain_plans = [
        plan_domain(domain, target_workspace_ids, fabric_domains_by_name, workspace_current_domain)
        for domain in purview_domains
    ]

    non_portable = build_non_portable_summary(purview_domains, governance_objects)

    return SyncPlan(
        run_id=run_id,
        generated_at=datetime.now(timezone.utc).isoformat(),
        matches=matches,
        item_plans=item_plans,
        domain_plans=domain_plans,
        tag_plans=tag_plans,
        non_portable=non_portable,
    )


# ---------------------------------------------------------------------------
# Applying a plan (resolving tag names to IDs, then delegating to execution.py)
# ---------------------------------------------------------------------------


def resolve_tag_names_to_ids(fabric_client: Any, tag_names: Sequence[str]) -> Dict[str, str]:
    """Return ``{tag display name: tag id}`` for every existing tenant tag."""
    existing = fabric_client.list_tenant_tags()
    return {t.get("displayName", ""): t.get("id", "") for t in existing if t.get("displayName")}


def sync_plan(
    fabric_client: FabricMutationClient,
    plan: SyncPlan,
    checkpoint_store: CheckpointStore,
    run_id: str,
    dry_run: bool = True,
) -> SyncRunResult:
    """Build operations for a plan and apply them, resolving tag names to IDs first."""
    desired_tag_names = sorted({tag for tp in plan.tag_plans for tag in tp.tags_to_apply})
    existing_tags_by_name = resolve_tag_names_to_ids(fabric_client, desired_tag_names) if not dry_run else {}

    operations = build_planned_operations(
        plan.item_plans,
        plan.domain_plans,
        plan.tag_plans,
        desired_governance_tag_names=desired_tag_names,
        existing_tenant_tag_names=list(existing_tags_by_name.keys()),
    )

    checkpoint = checkpoint_store.load_or_create(run_id)
    return apply_operations(
        fabric_client,
        operations,
        checkpoint_store,
        checkpoint,
        dry_run=dry_run,
        existing_tag_ids_by_name=existing_tags_by_name,
    )


def rollback_run(
    fabric_client: FabricMutationClient,
    checkpoint_store: CheckpointStore,
    dry_run: bool = True,
) -> RollbackResult:
    """Roll back a completed run using only its checkpoint file."""
    checkpoint = checkpoint_store.load()
    if checkpoint is None:
        return RollbackResult(run_id="", dry_run=dry_run, results=[])
    reverse_operations = build_rollback_operations(checkpoint)
    result = apply_rollback(fabric_client, reverse_operations, dry_run=dry_run)
    result.run_id = checkpoint.run_id
    return result
