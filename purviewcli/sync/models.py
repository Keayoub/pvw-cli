# SPDX-License-Identifier: Apache-2.0
"""Typed models for the Purview Unified Catalog -> Fabric OneLake catalog sync.

All enums subclass ``str`` so instances serialize directly with
``json.dumps`` and compare equal to their plain string value (e.g.
``MatchOutcome.MATCHED_BY_ID == "matched_by_id"``). All records are plain
dataclasses with ``to_dict``/``from_dict`` helpers so they can be persisted
to JSON checkpoint/report files and reloaded without a custom codec.
"""

from __future__ import annotations

import dataclasses
from enum import Enum
from typing import Any, Dict, List, Optional


def _to_dict(obj: Any) -> Any:
    """Recursively convert dataclasses (and containers of them) to plain dicts."""
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return {k: _to_dict(v) for k, v in dataclasses.asdict(obj).items()}
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, list):
        return [_to_dict(v) for v in obj]
    if isinstance(obj, dict):
        return {k: _to_dict(v) for k, v in obj.items()}
    return obj


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class MatchOutcome(str, Enum):
    """How (or whether) a Purview UC asset was resolved to a Fabric item."""

    MATCHED_BY_ID = "matched_by_id"
    MATCHED_BY_MAPPING = "matched_by_mapping"
    UNMATCHED = "unmatched"
    INVALID_MAPPING = "invalid_mapping"
    TARGET_NOT_FOUND = "target_not_found"


class ItemDecision(str, Enum):
    """The plan decision for a matched item's portable metadata."""

    NO_CHANGE = "no_change"
    READY = "ready"
    CONFLICT = "conflict"
    VALIDATION_ERROR = "validation_error"


class TagDecision(str, Enum):
    """The plan decision for governance-tag synchronization on an item."""

    NO_CHANGE = "no_change"
    READY = "ready"
    TAG_OVERFLOW = "tag_overflow"


class DomainAction(str, Enum):
    """The plan action for a Purview domain -> Fabric domain mapping."""

    NO_CHANGE = "no_change"
    CREATE_DOMAIN = "create_domain"
    REUSE_DOMAIN = "reuse_domain"
    ASSIGN_WORKSPACE = "assign_workspace"
    WORKSPACE_CONFLICT = "workspace_conflict"


class OperationType(str, Enum):
    """The kind of mutation a :class:`PlannedOperation` represents."""

    UPDATE_ITEM = "update_item"
    CREATE_DOMAIN = "create_domain"
    ASSIGN_WORKSPACE_DOMAIN = "assign_workspace_domain"
    UNASSIGN_WORKSPACE_DOMAIN = "unassign_workspace_domain"
    CREATE_TAG = "create_tag"
    APPLY_ITEM_TAGS = "apply_item_tags"
    UNAPPLY_ITEM_TAGS = "unapply_item_tags"


class OperationStatus(str, Enum):
    """The outcome of attempting to apply (or roll back) an operation."""

    APPLIED = "applied"
    SKIPPED_NO_CHANGE = "skipped_no_change"
    SKIPPED_DRY_RUN = "skipped_dry_run"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


# ---------------------------------------------------------------------------
# Normalized source (Purview) models
# ---------------------------------------------------------------------------


@dataclasses.dataclass
class PurviewAsset:
    """A normalized Purview Unified Catalog data asset."""

    id: str
    name: str
    description: Optional[str] = None
    type: str = ""
    source: Dict[str, Any] = dataclasses.field(default_factory=dict)
    type_properties: Dict[str, Any] = dataclasses.field(default_factory=dict)
    domain_id: Optional[str] = None
    term_ids: List[str] = dataclasses.field(default_factory=list)
    data_product_ids: List[str] = dataclasses.field(default_factory=list)
    cde_ids: List[str] = dataclasses.field(default_factory=list)
    owners: List[str] = dataclasses.field(default_factory=list)
    # Populated only when the caller opts into classification/label sync (see
    # ``service.enrich_assets_with_entity_metadata``); empty by default so
    # existing construction sites are unaffected. Sourced from the classic
    # Atlas Entity API, *not* the Unified Catalog data-asset API, which does
    # not expose classifications/labels (live-verified: absent even with
    # ``includeExtendedProperties=true``).
    classification_names: List[str] = dataclasses.field(default_factory=list)
    label_names: List[str] = dataclasses.field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return _to_dict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PurviewAsset":
        known = {f.name for f in dataclasses.fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in known})


@dataclasses.dataclass
class PurviewDomain:
    id: str
    name: str
    description: Optional[str] = None
    parent_id: Optional[str] = None
    type: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return _to_dict(self)


@dataclasses.dataclass
class PurviewGovernanceObject:
    """A Purview glossary term, data product, or critical data element.

    These map onto namespaced Fabric tags rather than native Fabric objects;
    ``object_type`` distinguishes the three cases (``term``, ``data_product``,
    ``cde``) for reporting and tag-namespace derivation.
    """

    id: str
    name: str
    object_type: str
    domain_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return _to_dict(self)


# ---------------------------------------------------------------------------
# Normalized destination (Fabric) models
# ---------------------------------------------------------------------------


@dataclasses.dataclass
class FabricCatalogEntry:
    """A single entry returned by the OneLake Catalog Search API."""

    id: str
    type: str
    display_name: str
    description: Optional[str]
    workspace_id: str
    workspace_display_name: str

    def to_dict(self) -> Dict[str, Any]:
        return _to_dict(self)


@dataclasses.dataclass
class FabricTag:
    id: str
    display_name: str

    def to_dict(self) -> Dict[str, Any]:
        return _to_dict(self)


@dataclasses.dataclass
class FabricItemState:
    """Current state of a Fabric item relevant to the sync (from Get Item)."""

    workspace_id: str
    item_id: str
    display_name: str
    description: Optional[str] = None
    tags: List[FabricTag] = dataclasses.field(default_factory=list)

    def tag_names(self) -> List[str]:
        return [t.display_name for t in self.tags]

    def to_dict(self) -> Dict[str, Any]:
        return _to_dict(self)


@dataclasses.dataclass
class FabricDomain:
    id: str
    display_name: str
    description: Optional[str] = None
    parent_domain_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return _to_dict(self)


# ---------------------------------------------------------------------------
# Explicit mapping (source -> target) models
# ---------------------------------------------------------------------------


@dataclasses.dataclass
class MappingEntry:
    purview_asset_id: str
    workspace_id: str
    item_id: str
    note: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return _to_dict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MappingEntry":
        return cls(
            purview_asset_id=data["purviewAssetId"],
            workspace_id=data["workspaceId"],
            item_id=data["itemId"],
            note=data.get("note"),
        )


class MappingValidationError(ValueError):
    """Raised when a mapping file contains duplicate or malformed bindings."""


@dataclasses.dataclass
class SyncMapping:
    """A validated set of explicit Purview-asset-to-Fabric-item bindings."""

    entries: List[MappingEntry] = dataclasses.field(default_factory=list)

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        seen_sources: Dict[str, int] = {}
        seen_targets: Dict[str, int] = {}
        for entry in self.entries:
            if not entry.purview_asset_id or not entry.workspace_id or not entry.item_id:
                raise MappingValidationError(
                    "Mapping entries require purviewAssetId, workspaceId, and itemId"
                )
            seen_sources[entry.purview_asset_id] = seen_sources.get(entry.purview_asset_id, 0) + 1
            target_key = f"{entry.workspace_id}::{entry.item_id}"
            seen_targets[target_key] = seen_targets.get(target_key, 0) + 1

        duplicate_sources = [k for k, v in seen_sources.items() if v > 1]
        if duplicate_sources:
            raise MappingValidationError(
                f"Duplicate purviewAssetId binding(s) in mapping file: {sorted(duplicate_sources)}"
            )
        duplicate_targets = [k for k, v in seen_targets.items() if v > 1]
        if duplicate_targets:
            raise MappingValidationError(
                f"Duplicate Fabric target binding(s) in mapping file: {sorted(duplicate_targets)}"
            )

    def by_purview_asset_id(self) -> Dict[str, MappingEntry]:
        return {e.purview_asset_id: e for e in self.entries}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SyncMapping":
        raw_entries = data.get("mappings", data.get("entries", []))
        return cls(entries=[MappingEntry.from_dict(e) for e in raw_entries])


# ---------------------------------------------------------------------------
# Matching results
# ---------------------------------------------------------------------------


@dataclasses.dataclass
class MatchSuggestion:
    """A non-authoritative candidate match surfaced for human review only."""

    workspace_id: str
    item_id: str
    display_name: str
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        return _to_dict(self)


@dataclasses.dataclass
class AssetMatch:
    purview_asset_id: str
    outcome: MatchOutcome
    workspace_id: Optional[str] = None
    item_id: Optional[str] = None
    reason: Optional[str] = None
    suggestions: List[MatchSuggestion] = dataclasses.field(default_factory=list)

    def is_writable(self) -> bool:
        """Only ID-derived or explicitly mapped matches ever authorize writes."""
        return self.outcome in (MatchOutcome.MATCHED_BY_ID, MatchOutcome.MATCHED_BY_MAPPING)

    def to_dict(self) -> Dict[str, Any]:
        return _to_dict(self)


# ---------------------------------------------------------------------------
# Planning results
# ---------------------------------------------------------------------------


@dataclasses.dataclass
class FieldChange:
    field: str
    current: Optional[str]
    desired: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        return _to_dict(self)


@dataclasses.dataclass
class ItemPlan:
    purview_asset_id: str
    workspace_id: str
    item_id: str
    decision: ItemDecision
    changes: List[FieldChange] = dataclasses.field(default_factory=list)
    validation_errors: List[str] = dataclasses.field(default_factory=list)
    truncated_description: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return _to_dict(self)


@dataclasses.dataclass
class WorkspaceDomainAssignmentPlan:
    workspace_id: str
    current_domain_id: Optional[str]
    desired_domain_id: str
    action: DomainAction
    conflict_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return _to_dict(self)


@dataclasses.dataclass
class DomainPlan:
    purview_domain_id: str
    fabric_domain_name: str
    fabric_domain_id: Optional[str] = None
    action: DomainAction = DomainAction.NO_CHANGE
    workspace_assignments: List[WorkspaceDomainAssignmentPlan] = dataclasses.field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return _to_dict(self)


@dataclasses.dataclass
class ItemTagPlan:
    workspace_id: str
    item_id: str
    decision: TagDecision
    tags_to_apply: List[str] = dataclasses.field(default_factory=list)
    tags_already_present: List[str] = dataclasses.field(default_factory=list)
    overflow_tags: List[str] = dataclasses.field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return _to_dict(self)


@dataclasses.dataclass
class NonPortableSummary:
    """Purview governance metadata that has no native Fabric representation.

    Populated for reporting/audit purposes only; nothing here is written to
    Fabric. Terms, data products, and CDEs map to namespaced tags (tracked
    separately via :class:`ItemTagPlan`) but their full object schema,
    hierarchy, ownership, and relationships still land here.
    """

    domains: List[Dict[str, Any]] = dataclasses.field(default_factory=list)
    terms: List[Dict[str, Any]] = dataclasses.field(default_factory=list)
    data_products: List[Dict[str, Any]] = dataclasses.field(default_factory=list)
    cdes: List[Dict[str, Any]] = dataclasses.field(default_factory=list)
    owners: List[Dict[str, Any]] = dataclasses.field(default_factory=list)
    relationships: List[Dict[str, Any]] = dataclasses.field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return _to_dict(self)


@dataclasses.dataclass
class SyncPlan:
    """The complete, human- and machine-readable output of an assessment."""

    run_id: str
    generated_at: str
    matches: List[AssetMatch] = dataclasses.field(default_factory=list)
    item_plans: List[ItemPlan] = dataclasses.field(default_factory=list)
    domain_plans: List[DomainPlan] = dataclasses.field(default_factory=list)
    tag_plans: List[ItemTagPlan] = dataclasses.field(default_factory=list)
    non_portable: NonPortableSummary = dataclasses.field(default_factory=NonPortableSummary)
    #: Human-readable errors for mapping-file entries referencing an unknown
    #: Purview asset id (stale/mistyped mappings); see
    #: :func:`~.purview_to_fabric.validate_mapping_targets_are_unambiguous`.
    #: Non-empty here means the mapping file needs correction before apply.
    mapping_errors: List[str] = dataclasses.field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return _to_dict(self)


# ---------------------------------------------------------------------------
# Execution (apply) models
# ---------------------------------------------------------------------------


@dataclasses.dataclass
class PlannedOperation:
    """One atomic, checkpointable mutation derived from a :class:`SyncPlan`."""

    operation_id: str
    operation_type: OperationType
    fingerprint: str
    purview_source_id: Optional[str] = None
    target: Dict[str, str] = dataclasses.field(default_factory=dict)
    payload: Dict[str, Any] = dataclasses.field(default_factory=dict)
    before_state: Dict[str, Any] = dataclasses.field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return _to_dict(self)


@dataclasses.dataclass
class OperationResult:
    operation_id: str
    operation_type: OperationType
    status: OperationStatus
    message: Optional[str] = None
    target: Dict[str, str] = dataclasses.field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return _to_dict(self)


@dataclasses.dataclass
class CheckpointRecord:
    """A durable record of one successfully applied operation."""

    operation_id: str
    operation_type: OperationType
    run_id: str
    applied_at: str
    fingerprint: str
    target: Dict[str, str] = dataclasses.field(default_factory=dict)
    before_state: Dict[str, Any] = dataclasses.field(default_factory=dict)
    after_state: Dict[str, Any] = dataclasses.field(default_factory=dict)
    purview_source_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return _to_dict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CheckpointRecord":
        return cls(
            operation_id=data["operation_id"],
            operation_type=OperationType(data["operation_type"]),
            run_id=data["run_id"],
            applied_at=data["applied_at"],
            fingerprint=data["fingerprint"],
            target=data.get("target", {}),
            before_state=data.get("before_state", {}),
            after_state=data.get("after_state", {}),
            purview_source_id=data.get("purview_source_id"),
        )


@dataclasses.dataclass
class RunCheckpoint:
    """The full checkpoint state for one sync run, keyed by run_id."""

    run_id: str
    created_at: str
    updated_at: str
    records: List[CheckpointRecord] = dataclasses.field(default_factory=list)

    def record_by_operation_id(self) -> Dict[str, CheckpointRecord]:
        return {r.operation_id: r for r in self.records}

    def to_dict(self) -> Dict[str, Any]:
        return _to_dict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RunCheckpoint":
        return cls(
            run_id=data["run_id"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            records=[CheckpointRecord.from_dict(r) for r in data.get("records", [])],
        )


@dataclasses.dataclass
class SyncRunResult:
    run_id: str
    dry_run: bool
    results: List[OperationResult] = dataclasses.field(default_factory=list)

    @property
    def failures(self) -> List[OperationResult]:
        return [r for r in self.results if r.status == OperationStatus.FAILED]

    @property
    def succeeded_count(self) -> int:
        return sum(1 for r in self.results if r.status == OperationStatus.APPLIED)

    @property
    def failed_count(self) -> int:
        return len(self.failures)

    def to_dict(self) -> Dict[str, Any]:
        return _to_dict(self)


@dataclasses.dataclass
class RollbackResult:
    run_id: str
    dry_run: bool
    results: List[OperationResult] = dataclasses.field(default_factory=list)

    @property
    def failures(self) -> List[OperationResult]:
        return [r for r in self.results if r.status == OperationStatus.FAILED]

    def to_dict(self) -> Dict[str, Any]:
        return _to_dict(self)
