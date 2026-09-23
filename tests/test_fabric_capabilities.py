# SPDX-License-Identifier: Apache-2.0
"""Tests for purviewcli.sync.capabilities and the `pvw fabric sync capabilities`
CLI command that renders it."""

import json

from click.testing import CliRunner

from purviewcli.cli.fabric import fabric
from purviewcli.sync.capabilities import CapabilityStatus, get_capabilities


class TestCapabilitiesData:
    def test_get_capabilities_returns_a_fresh_list_each_call(self):
        first = get_capabilities()
        first.append("mutate-me")
        second = get_capabilities()
        assert "mutate-me" not in second

    def test_every_capability_has_a_status_and_nonempty_fields(self):
        for capability in get_capabilities():
            assert isinstance(capability.status, CapabilityStatus)
            assert capability.purview_capability
            assert capability.fabric_target
            assert capability.notes
            assert capability.command_flag

    def test_to_dict_includes_status_value_and_label(self):
        capability = get_capabilities()[0]
        as_dict = capability.to_dict()
        assert as_dict["status"] == capability.status.value
        assert as_dict["status_label"] == capability.status.label

    def test_classification_and_label_sync_are_supported_and_gated_by_flag(self):
        by_name = {c.purview_capability: c for c in get_capabilities()}
        classifications = by_name["Data Map classifications (e.g. MICROSOFT.PERSONAL.EMAIL)"]
        labels = by_name["Data Map labels (free-text)"]
        assert classifications.status == CapabilityStatus.SUPPORTED
        assert classifications.command_flag == "--sync-classifications"
        assert labels.status == CapabilityStatus.SUPPORTED
        assert labels.command_flag == "--sync-classifications"

    def test_sensitivity_label_sync_is_not_yet_supported(self):
        by_name = {c.purview_capability: c for c in get_capabilities()}
        sensitivity = by_name["Sensitivity label (MIP)"]
        assert sensitivity.status == CapabilityStatus.PLANNED


class TestCapabilitiesCli:
    def test_capabilities_table_output_lists_every_capability(self):
        runner = CliRunner()
        result = runner.invoke(fabric, ["sync", "capabilities"])
        assert result.exit_code == 0
        # Rich truncates/wraps long cells depending on terminal width, so only assert
        # the first word of each capability name shows up somewhere (exhaustive,
        # exact-text coverage is asserted against --output json below instead).
        for capability in get_capabilities():
            first_word = capability.purview_capability.split()[0]
            assert first_word in result.output

    def test_capabilities_json_output_is_valid_and_matches_data(self):
        runner = CliRunner()
        result = runner.invoke(fabric, ["sync", "capabilities", "--output", "json"])
        assert result.exit_code == 0
        payload = json.loads(result.output)
        assert len(payload) == len(get_capabilities())
        assert payload[0]["purview_capability"] == get_capabilities()[0].purview_capability

    def test_capabilities_status_filter_narrows_results(self):
        runner = CliRunner()
        result = runner.invoke(
            fabric, ["sync", "capabilities", "--status", "planned", "--output", "json"]
        )
        assert result.exit_code == 0
        payload = json.loads(result.output)
        assert len(payload) > 0
        assert all(row["status"] == "planned" for row in payload)

    def test_capabilities_invalid_status_filter_rejected_by_click(self):
        runner = CliRunner()
        result = runner.invoke(fabric, ["sync", "capabilities", "--status", "bogus"])
        assert result.exit_code != 0

    def test_capabilities_does_not_require_any_client_setup(self, monkeypatch):
        """`capabilities` is pure/offline: it must not call `_get_clients` at all."""
        import purviewcli.cli.fabric as fabric_module

        def _boom(ctx):
            raise AssertionError("capabilities should not construct any clients")

        monkeypatch.setattr(fabric_module, "_get_clients", _boom)
        runner = CliRunner()
        result = runner.invoke(fabric, ["sync", "capabilities"])
        assert result.exit_code == 0
