"""Tests for pvw entity bulk-read with repeated GUID flags."""
import os
import sys

from click.testing import CliRunner

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from purviewcli.cli.cli import main

RUNNER = CliRunner()


def _invoke(*args, **kwargs):
    return RUNNER.invoke(main, list(args), catch_exceptions=False, **kwargs)


class TestEntityBulkReadCommand:
    def test_bulk_read_multiple_guids_with_mock(self):
        result = _invoke(
            "--mock",
            "entity",
            "bulk-read",
            "--guid",
            "ea3412c3-7387-4bc1-9923-11f6f6f60000",
            "--guid",
            "2d21eba5-b08b-4571-b31d-7bf6f6f60000",
        )
        assert result.exit_code == 0, result.output
        assert "entity bulk-read command" in result.output
        assert "ea3412c3-7387-4bc1-9923-11f6f6f60000" in result.output
        assert "2d21eba5-b08b-4571-b31d-7bf6f6f60000" in result.output
