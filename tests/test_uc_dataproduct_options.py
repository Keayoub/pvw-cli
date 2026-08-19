# SPDX-License-Identifier: Apache-2.0
"""Regression tests for current Data Product enum options."""

from click.testing import CliRunner

from purviewcli.cli.cli import main
from purviewcli.cli.unified_catalog import DATA_PRODUCT_TYPES


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


def test_dataproduct_types_match_tenant_confirmed_values():
    assert DATA_PRODUCT_TYPES == [
        "Dataset",
        "MasterDataAndReferenceData",
        "BusinessSystemOrApplication",
        "ModelTypes",
        "DashboardsOrReports",
        "Operational",
        "MLAITrainingDataSet",
        "MLAITestingDataSet",
        "TransactionalDataset",
        "AnalyticsModel",
        "SemanticModel",
    ]