# SPDX-License-Identifier: Apache-2.0
"""Checkpoint persistence, fingerprinting, and run-id generation.

This module is responsible for the durability half of the sync
workflow: turning a desired-state payload into a stable fingerprint,
generating stable run IDs, and reading/writing checkpoint files atomically
so a crashed or interrupted run can resume without redoing (or losing track
of) already-applied operations.

Nothing here talks to Purview or Fabric; it operates purely on the
dataclasses defined in :mod:`purviewcli.sync.models`.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from .models import CheckpointRecord, RunCheckpoint


def new_run_id() -> str:
    """Generate a stable, sortable, collision-resistant run identifier.

    Format: ``run-<UTC compact timestamp>-<8 hex chars>``, e.g.
    ``run-20240115T142530Z-a1b2c3d4``. The timestamp prefix keeps runs
    listed in chronological order; the suffix avoids collisions for runs
    started within the same second.
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"run-{timestamp}-{uuid.uuid4().hex[:8]}"


def _canonical_json(payload: Dict[str, Any]) -> str:
    """Serialize a payload deterministically for fingerprinting.

    Keys are sorted and separators are compact so semantically identical
    payloads always produce byte-identical JSON regardless of dict
    insertion order.
    """
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def compute_fingerprint(payload: Dict[str, Any]) -> str:
    """Compute a stable SHA-256 fingerprint of a desired-state payload.

    Two payloads produce the same fingerprint if and only if they are
    semantically identical (same keys/values, regardless of ordering). Used
    to decide whether a previously-applied operation still matches the
    currently-planned desired state (safe to skip) or whether the source
    data changed since the last run (must be reapplied).
    """
    canonical = _canonical_json(payload)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def atomic_write(path: str, content: str) -> None:
    """Write ``content`` to ``path`` atomically.

    Writes to a temporary file in the same directory then uses
    ``os.replace`` (atomic on POSIX and Windows for same-volume renames) so
    a crash mid-write never leaves a truncated/corrupt checkpoint file in
    place of a good one.
    """
    directory = os.path.dirname(os.path.abspath(path)) or "."
    os.makedirs(directory, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(prefix=".tmp-", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_path, path)
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise


class CheckpointStore:
    """Loads, mutates, and atomically persists a single run's checkpoint file."""

    def __init__(self, path: str):
        self.path = path

    def exists(self) -> bool:
        return os.path.isfile(self.path)

    def load(self) -> Optional[RunCheckpoint]:
        """Load the checkpoint file, or return ``None`` if it does not exist yet."""
        if not self.exists():
            return None
        with open(self.path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        return RunCheckpoint.from_dict(data)

    def load_or_create(self, run_id: str) -> RunCheckpoint:
        """Load an existing checkpoint for ``run_id``, or start a fresh one.

        Raises :class:`ValueError` if the checkpoint file exists but belongs
        to a different run, since resuming under the wrong run ID would
        silently corrupt rollback attribution.
        """
        existing = self.load()
        if existing is not None:
            if existing.run_id != run_id:
                raise ValueError(
                    f"Checkpoint file {self.path!r} belongs to run {existing.run_id!r}, "
                    f"not {run_id!r}. Use a different --checkpoint-file or --run-id."
                )
            return existing
        now = datetime.now(timezone.utc).isoformat()
        return RunCheckpoint(run_id=run_id, created_at=now, updated_at=now, records=[])

    def save(self, checkpoint: RunCheckpoint) -> None:
        checkpoint.updated_at = datetime.now(timezone.utc).isoformat()
        atomic_write(self.path, json.dumps(checkpoint.to_dict(), indent=2, sort_keys=True))

    def record_operation(self, checkpoint: RunCheckpoint, record: CheckpointRecord) -> None:
        """Append (or replace) a checkpoint record and persist immediately.

        Persisting after every single successful operation (rather than
        batching at the end of a run) is what makes partial-failure
        resilience possible: if the process dies mid-run, everything applied
        so far is already durable on disk.
        """
        existing_by_id = {r.operation_id: i for i, r in enumerate(checkpoint.records)}
        if record.operation_id in existing_by_id:
            checkpoint.records[existing_by_id[record.operation_id]] = record
        else:
            checkpoint.records.append(record)
        self.save(checkpoint)

    @staticmethod
    def has_applied(checkpoint: RunCheckpoint, operation_id: str, fingerprint: str) -> bool:
        """Return ``True`` if ``operation_id`` was already applied with this fingerprint.

        A matching operation ID with a *different* fingerprint means the
        underlying desired state changed since the last run (e.g. the
        Purview description was edited) and must be re-planned/reapplied,
        so this only returns ``True`` on an exact fingerprint match.
        """
        for record in checkpoint.records:
            if record.operation_id == operation_id:
                return record.fingerprint == fingerprint
        return False
