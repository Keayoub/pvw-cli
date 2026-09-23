# SPDX-License-Identifier: Apache-2.0
"""Purview Unified Catalog -> Fabric OneLake catalog sync package.

This package is intentionally independent of Click and of the Purview/Fabric
HTTP clients: it operates on plain, typed, JSON-serializable models so the
matching, planning, execution, checkpointing, and reporting logic can be
unit-tested without any network access or CLI harness.

Modules:
    models: Typed dataclasses for normalized Purview/Fabric state, mapping
        entries, match/plan decisions, and run/checkpoint/report records.
    mapping: Loading and validation of explicit source-to-target mapping
        files and scheduled-run configuration files.
    matching: Deterministic resolution of Purview assets to Fabric items.
    planning: Diffing desired vs. current Fabric state into planned,
        conflict-aware operations (including domain and tag mapping).
    state: Fingerprinting and atomic persistence of checkpoint state.
    reporting: JSON/CSV serialization of assessment and sync results.
    service: Orchestration entry points used by the ``pvw fabric`` CLI.
"""
