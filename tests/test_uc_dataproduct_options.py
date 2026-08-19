# SPDX-License-Identifier: Apache-2.0
"""Regression tests for current Data Product enum options."""

from click.testing import CliRunner

from purviewcli.cli.cli import main


def test_dataproduct_create_accepts_current_type():
    result = CliRunner().invoke(
        main,
        [
            "uc", "dataproduct", "create",
            "--name", "Product",
            "--domain-id", "domain-id",
            "--type", "SemanticModel",
            "--help",
        ],
    )

    assert result.exit_code == 0
    assert "SemanticModel" in result.output


def test_dataproduct_create_accepts_yearly_frequency():
    result = CliRunner().invoke(
        main,
        [
            "uc", "dataproduct", "create",
            "--name", "Product",
            "--domain-id", "domain-id",
            "--update-frequency", "Yearly",
            "--help",
        ],
    )

    assert result.exit_code == 0