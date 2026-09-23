# SPDX-License-Identifier: Apache-2.0
"""Tests for purviewcli.sync.purview_to_fabric (matching + planning)."""

import pytest

from purviewcli.sync.models import (
    DomainAction,
    FabricCatalogEntry,
    FabricDomain,
    FabricItemState,
    FabricTag,
    ItemDecision,
    MappingEntry,
    MatchOutcome,
    SyncMapping,
    PurviewAsset,
    PurviewDomain,
    PurviewGovernanceObject,
    TagDecision,
)
from purviewcli.sync.purview_to_fabric import (
    DESCRIPTION_MAX_LENGTH,
    build_non_portable_summary,
    extract_embedded_fabric_ref,
    filter_assets_by_domain,
    filter_catalog_entries_by_workspace,
    index_fabric_domains_by_name,
    namespaced_tag_name,
    plan_asset_metadata_tag_names,
    plan_domain,
    plan_governance_tag_names,
    plan_item_metadata,
    plan_item_tags,
    resolve_matches,
    validate_mapping_targets_are_unambiguous,
)


def _catalog_entry(workspace_id="ws1", item_id="it1", name="Sales Lakehouse"):
    return FabricCatalogEntry(
        id=item_id,
        type="Lakehouse",
        display_name=name,
        description=None,
        workspace_id=workspace_id,
        workspace_display_name="Sales Workspace",
    )


def _item_state(workspace_id="ws1", item_id="it1", display_name="Sales Lakehouse", description=None, tags=()):
    return FabricItemState(
        workspace_id=workspace_id,
        item_id=item_id,
        display_name=display_name,
        description=description,
        tags=[FabricTag(id=f"tag-{t}", display_name=t) for t in tags],
    )


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------


class TestFilters:
    def test_filter_assets_by_domain_noop_when_empty(self):
        assets = [PurviewAsset(id="a1", name="A", domain_id="d1")]
        assert filter_assets_by_domain(assets, []) == assets

    def test_filter_assets_by_domain_restricts(self):
        assets = [
            PurviewAsset(id="a1", name="A", domain_id="d1"),
            PurviewAsset(id="a2", name="B", domain_id="d2"),
        ]
        result = filter_assets_by_domain(assets, ["d1"])
        assert [a.id for a in result] == ["a1"]

    def test_filter_catalog_entries_by_workspace_restricts(self):
        entries = [_catalog_entry(workspace_id="ws1"), _catalog_entry(workspace_id="ws2", item_id="it2")]
        result = filter_catalog_entries_by_workspace(entries, ["ws2"])
        assert [e.workspace_id for e in result] == ["ws2"]


# ---------------------------------------------------------------------------
# Matching
# ---------------------------------------------------------------------------


class TestEmbeddedRefExtraction:
    def test_extracts_from_source(self):
        asset = PurviewAsset(id="a1", name="A", source={"workspaceId": "ws1", "itemId": "it1"})
        assert extract_embedded_fabric_ref(asset) == ("ws1", "it1")

    def test_extracts_from_type_properties_fallback(self):
        asset = PurviewAsset(id="a1", name="A", type_properties={"workspace_id": "ws1", "item_id": "it1"})
        assert extract_embedded_fabric_ref(asset) == ("ws1", "it1")

    def test_returns_none_when_absent(self):
        asset = PurviewAsset(id="a1", name="A")
        assert extract_embedded_fabric_ref(asset) is None

    def test_returns_none_when_partial(self):
        asset = PurviewAsset(id="a1", name="A", source={"workspaceId": "ws1"})
        assert extract_embedded_fabric_ref(asset) is None


class TestResolveMatches:
    def test_matched_by_embedded_id(self):
        asset = PurviewAsset(id="a1", name="A", source={"workspaceId": "ws1", "itemId": "it1"})
        matches = resolve_matches([asset], [_catalog_entry()])
        assert matches[0].outcome == MatchOutcome.MATCHED_BY_ID
        assert matches[0].is_writable()

    def test_embedded_id_target_not_found(self):
        asset = PurviewAsset(id="a1", name="A", source={"workspaceId": "ws1", "itemId": "missing"})
        matches = resolve_matches([asset], [_catalog_entry()])
        assert matches[0].outcome == MatchOutcome.TARGET_NOT_FOUND
        assert not matches[0].is_writable()

    def test_matched_by_explicit_mapping(self):
        asset = PurviewAsset(id="a1", name="A")
        mapping = SyncMapping(entries=[MappingEntry(purview_asset_id="a1", workspace_id="ws1", item_id="it1")])
        matches = resolve_matches([asset], [_catalog_entry()], mapping=mapping)
        assert matches[0].outcome == MatchOutcome.MATCHED_BY_MAPPING
        assert matches[0].is_writable()

    def test_mapping_target_not_found(self):
        asset = PurviewAsset(id="a1", name="A")
        mapping = SyncMapping(
            entries=[MappingEntry(purview_asset_id="a1", workspace_id="ws1", item_id="does-not-exist")]
        )
        matches = resolve_matches([asset], [_catalog_entry()], mapping=mapping)
        assert matches[0].outcome == MatchOutcome.TARGET_NOT_FOUND

    def test_embedded_id_takes_precedence_over_mapping(self):
        asset = PurviewAsset(id="a1", name="A", source={"workspaceId": "ws1", "itemId": "it1"})
        mapping = SyncMapping(
            entries=[MappingEntry(purview_asset_id="a1", workspace_id="ws2", item_id="it2")]
        )
        entries = [_catalog_entry(workspace_id="ws1", item_id="it1"), _catalog_entry(workspace_id="ws2", item_id="it2")]
        matches = resolve_matches([asset], entries, mapping=mapping)
        assert matches[0].outcome == MatchOutcome.MATCHED_BY_ID
        assert matches[0].workspace_id == "ws1"

    def test_unmatched_with_name_suggestion_is_not_writable(self):
        asset = PurviewAsset(id="a1", name="Sales Lakehouse")
        matches = resolve_matches([asset], [_catalog_entry()])
        assert matches[0].outcome == MatchOutcome.UNMATCHED
        assert not matches[0].is_writable()
        assert len(matches[0].suggestions) == 1
        assert matches[0].suggestions[0].reason == "exact_name_match"

    def test_unmatched_without_any_candidate(self):
        asset = PurviewAsset(id="a1", name="Nothing Like This")
        matches = resolve_matches([asset], [_catalog_entry()])
        assert matches[0].outcome == MatchOutcome.UNMATCHED
        assert matches[0].suggestions == []


class TestMappingValidation:
    def test_flags_unknown_source_asset(self):
        mapping = SyncMapping(entries=[MappingEntry(purview_asset_id="ghost", workspace_id="ws1", item_id="it1")])
        errors = validate_mapping_targets_are_unambiguous(mapping, assets_by_id={})
        assert len(errors) == 1
        assert "ghost" in errors[0]

    def test_no_errors_for_known_source(self):
        asset = PurviewAsset(id="a1", name="A")
        mapping = SyncMapping(entries=[MappingEntry(purview_asset_id="a1", workspace_id="ws1", item_id="it1")])
        errors = validate_mapping_targets_are_unambiguous(mapping, assets_by_id={"a1": asset})
        assert errors == []


# ---------------------------------------------------------------------------
# Item metadata planning
# ---------------------------------------------------------------------------


class TestPlanItemMetadata:
    def _match(self):
        return None  # match object unused by plan_item_metadata besides typing; kept for signature symmetry

    def test_no_change_when_identical(self):
        asset = PurviewAsset(id="a1", name="Sales Lakehouse", description="desc")
        current = _item_state(display_name="Sales Lakehouse", description="desc")
        plan = plan_item_metadata(asset, self._match(), current)
        assert plan.decision == ItemDecision.NO_CHANGE
        assert plan.changes == []

    def test_ready_when_filling_blank_description(self):
        asset = PurviewAsset(id="a1", name="Sales Lakehouse", description="new desc")
        current = _item_state(display_name="Sales Lakehouse", description=None)
        plan = plan_item_metadata(asset, self._match(), current)
        assert plan.decision == ItemDecision.READY
        assert plan.changes[0].field == "description"

    def test_conflict_when_overwriting_existing_description_without_flag(self):
        asset = PurviewAsset(id="a1", name="Sales Lakehouse", description="new desc")
        current = _item_state(display_name="Sales Lakehouse", description="old desc")
        plan = plan_item_metadata(asset, self._match(), current, overwrite=False)
        assert plan.decision == ItemDecision.CONFLICT

    def test_overwrite_resolves_conflict(self):
        asset = PurviewAsset(id="a1", name="Sales Lakehouse", description="new desc")
        current = _item_state(display_name="Sales Lakehouse", description="old desc")
        plan = plan_item_metadata(asset, self._match(), current, overwrite=True)
        assert plan.decision == ItemDecision.READY

    def test_conflict_when_renaming_without_overwrite(self):
        asset = PurviewAsset(id="a1", name="New Name")
        current = _item_state(display_name="Old Name")
        plan = plan_item_metadata(asset, self._match(), current, overwrite=False)
        assert plan.decision == ItemDecision.CONFLICT
        assert plan.changes[0].field == "displayName"

    def test_validation_error_on_long_description_without_truncate_flag(self):
        long_description = "x" * (DESCRIPTION_MAX_LENGTH + 10)
        asset = PurviewAsset(id="a1", name="Sales Lakehouse", description=long_description)
        current = _item_state(display_name="Sales Lakehouse")
        plan = plan_item_metadata(asset, self._match(), current, truncate_descriptions=False)
        assert plan.decision == ItemDecision.VALIDATION_ERROR
        assert plan.validation_errors

    def test_truncate_flag_allows_long_description(self):
        long_description = "x" * (DESCRIPTION_MAX_LENGTH + 10)
        asset = PurviewAsset(id="a1", name="Sales Lakehouse", description=long_description)
        current = _item_state(display_name="Sales Lakehouse")
        plan = plan_item_metadata(asset, self._match(), current, truncate_descriptions=True)
        assert plan.decision == ItemDecision.READY
        assert plan.truncated_description is True
        assert len(plan.changes[0].desired) == DESCRIPTION_MAX_LENGTH


# ---------------------------------------------------------------------------
# Governance tag namespacing + item tag planning
# ---------------------------------------------------------------------------


class TestNamespacedTagName:
    def test_basic_namespacing(self):
        assert namespaced_tag_name("term", "Customer ID") == "purview:term:Customer ID"

    def test_truncated_to_max_length(self):
        name = namespaced_tag_name("data_product", "x" * 100)
        assert len(name) == 40

    def test_truncated_names_get_a_collision_resistant_suffix(self):
        # Two distinct long names sharing a common prefix must not collapse
        # onto the same truncated Fabric tag name.
        name_a = namespaced_tag_name("term", "Customer Segmentation Model For Retail Division A")
        name_b = namespaced_tag_name("term", "Customer Segmentation Model For Retail Division B")
        assert len(name_a) == 40
        assert len(name_b) == 40
        assert name_a != name_b

    def test_strips_unsafe_characters(self):
        name = namespaced_tag_name("cde", "Weird/Name*?")
        assert "/" not in name and "*" not in name and "?" not in name

    def test_plan_governance_tag_names_dedupes(self):
        objects = [
            PurviewGovernanceObject(id="t1", name="Customer ID", object_type="term"),
            PurviewGovernanceObject(id="t2", name="Customer ID", object_type="term"),
        ]
        names = plan_governance_tag_names(objects)
        assert names == ["purview:term:Customer ID"]

    def test_plan_asset_metadata_tag_names_namespaces_and_dedupes(self):
        asset = PurviewAsset(
            id="a1",
            name="A",
            classification_names=["MICROSOFT.PERSONAL.EMAIL", "MICROSOFT.PERSONAL.EMAIL"],
            label_names=["pvw-test-label"],
        )
        names = plan_asset_metadata_tag_names(asset)
        assert names == ["purview:classification:MICROSOF-2a0099bb", "purview:label:pvw-test-label"]

    def test_plan_asset_metadata_tag_names_empty_when_no_metadata(self):
        asset = PurviewAsset(id="a1", name="A")
        assert plan_asset_metadata_tag_names(asset) == []


class TestPlanItemTags:
    def test_no_change_when_all_tags_already_present(self):
        current = _item_state(tags=["purview:term:A"])
        plan = plan_item_tags("ws1", "it1", current, ["purview:term:A"])
        assert plan.decision == TagDecision.NO_CHANGE
        assert plan.tags_already_present == ["purview:term:A"]

    def test_ready_applies_only_new_tags(self):
        current = _item_state(tags=["existing-tag"])
        plan = plan_item_tags("ws1", "it1", current, ["purview:term:A", "purview:term:B"])
        assert plan.decision == TagDecision.READY
        assert set(plan.tags_to_apply) == {"purview:term:A", "purview:term:B"}

    def test_preserves_existing_non_governance_tags(self):
        current = _item_state(tags=["custom-tag"])
        plan = plan_item_tags("ws1", "it1", current, ["purview:term:A"])
        assert "custom-tag" not in plan.tags_to_apply
        assert "custom-tag" not in plan.overflow_tags

    def test_overflow_skips_all_new_tags(self):
        current = _item_state(tags=[f"existing-{i}" for i in range(9)])
        plan = plan_item_tags("ws1", "it1", current, ["purview:term:A", "purview:term:B"])
        assert plan.decision == TagDecision.TAG_OVERFLOW
        assert plan.tags_to_apply == []
        assert set(plan.overflow_tags) == {"purview:term:A", "purview:term:B"}

    def test_exactly_at_limit_is_not_overflow(self):
        current = _item_state(tags=[f"existing-{i}" for i in range(8)])
        plan = plan_item_tags("ws1", "it1", current, ["purview:term:A", "purview:term:B"])
        assert plan.decision == TagDecision.READY


# ---------------------------------------------------------------------------
# Domain planning
# ---------------------------------------------------------------------------


class TestPlanDomain:
    def test_creates_domain_and_assigns_workspace_when_none_exists(self):
        purview_domain = PurviewDomain(id="d1", name="Finance")
        plan = plan_domain(purview_domain, ["ws1"], fabric_domains_by_name={}, workspace_current_domain={})
        assert plan.action == DomainAction.CREATE_DOMAIN
        assert plan.workspace_assignments[0].action == DomainAction.ASSIGN_WORKSPACE

    def test_reuses_existing_domain_by_case_insensitive_name(self):
        purview_domain = PurviewDomain(id="d1", name="Finance")
        fabric_domain = FabricDomain(id="fd1", display_name="finance")
        plan = plan_domain(
            purview_domain,
            ["ws1"],
            fabric_domains_by_name=index_fabric_domains_by_name([fabric_domain]),
            workspace_current_domain={},
        )
        assert plan.action == DomainAction.REUSE_DOMAIN
        assert plan.fabric_domain_id == "fd1"
        assert plan.workspace_assignments[0].action == DomainAction.ASSIGN_WORKSPACE

    def test_no_change_when_workspace_already_correctly_assigned(self):
        purview_domain = PurviewDomain(id="d1", name="Finance")
        fabric_domain = FabricDomain(id="fd1", display_name="Finance")
        plan = plan_domain(
            purview_domain,
            ["ws1"],
            fabric_domains_by_name=index_fabric_domains_by_name([fabric_domain]),
            workspace_current_domain={"ws1": "fd1"},
        )
        assert plan.action == DomainAction.NO_CHANGE
        assert plan.workspace_assignments[0].action == DomainAction.NO_CHANGE

    def test_conflict_when_workspace_assigned_elsewhere(self):
        purview_domain = PurviewDomain(id="d1", name="Finance")
        fabric_domain = FabricDomain(id="fd1", display_name="Finance")
        plan = plan_domain(
            purview_domain,
            ["ws1"],
            fabric_domains_by_name=index_fabric_domains_by_name([fabric_domain]),
            workspace_current_domain={"ws1": "fd-other"},
        )
        assignment = plan.workspace_assignments[0]
        assert assignment.action == DomainAction.WORKSPACE_CONFLICT
        assert assignment.conflict_reason is not None


# ---------------------------------------------------------------------------
# Non-portable summary
# ---------------------------------------------------------------------------


class TestBuildNonPortableSummary:
    def test_buckets_governance_objects_by_type(self):
        domains = [PurviewDomain(id="d1", name="Finance")]
        objects = [
            PurviewGovernanceObject(id="t1", name="Term A", object_type="term"),
            PurviewGovernanceObject(id="p1", name="Product A", object_type="data_product"),
            PurviewGovernanceObject(id="c1", name="CDE A", object_type="cde"),
        ]
        summary = build_non_portable_summary(domains, objects, owners=[{"name": "Alice"}])
        assert len(summary.domains) == 1
        assert len(summary.terms) == 1
        assert len(summary.data_products) == 1
        assert len(summary.cdes) == 1
        assert summary.owners == [{"name": "Alice"}]
