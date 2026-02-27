"""
Unit tests for schema-level classification commands:
  - entity read-schema-classifications
  - entity add-schema-classification
  - entity remove-schema-classification

Uses Click CliRunner + unittest.mock — no real Purview API calls.
"""

import json
import pytest
from unittest.mock import MagicMock, patch, call
from click.testing import CliRunner

from purviewcli.cli.cli import main


# ---------------------------------------------------------------------------
# Shared test fixtures
# ---------------------------------------------------------------------------

TABLE_GUID = "table-aaaa-1111-bbbb-2222"
COL_NAS_GUID = "col-nas-1111-2222-3333"
COL_NOM_GUID = "col-nom-4444-5555-6666"
COL_EMAIL_GUID = "col-email-7777-8888-9999"

PARENT_ENTITY_RESPONSE = {
    "entity": {
        "guid": TABLE_GUID,
        "typeName": "azure_sql_table",
        "attributes": {"name": "Personne", "qualifiedName": "mssql://server/db/dbo/Personne"},
        "relationshipAttributes": {
            "columns": [
                {"guid": COL_NAS_GUID, "displayText": "NAS"},
                {"guid": COL_NOM_GUID, "displayText": "Nom"},
                {"guid": COL_EMAIL_GUID, "displayText": "Email"},
            ]
        },
    }
}

CLASSIF_NAS = {
    "list": [
        {"typeName": "Canada Social Insurance Number"},
        {"typeName": "Disponibilité élevé"},
    ]
}
CLASSIF_NOM = {"list": []}
CLASSIF_EMAIL = {"list": [{"typeName": "Intégrité élevé"}]}

RUNNER = CliRunner()


def invoke(*args):
    """Convenience: invoke the CLI with a list of string args."""
    return RUNNER.invoke(main, list(args), catch_exceptions=False)


def invoke_mock(*extra):
    """Invoke with --mock flag."""
    return RUNNER.invoke(main, ["--mock", "entity"] + list(extra), catch_exceptions=False)


# ===========================================================================
# read-schema-classifications
# ===========================================================================


class TestReadSchemaClassifications:
    @patch("purviewcli.cli.entity.Entity")
    def test_table_output(self, mock_entity_cls):
        """Returns a rich table with all columns and their classifications."""
        mock_client = MagicMock()
        mock_entity_cls.return_value = mock_client
        mock_client.entityRead.return_value = PARENT_ENTITY_RESPONSE
        mock_client.entityReadClassifications.side_effect = [
            CLASSIF_NAS,
            CLASSIF_NOM,
            CLASSIF_EMAIL,
        ]

        result = invoke("entity", "read-schema-classifications", "--guid", TABLE_GUID)

        assert result.exit_code == 0, result.output
        assert "NAS" in result.output
        assert "Canada Social Insurance Number" in result.output
        assert "Disponibilité élevé" in result.output
        assert "Email" in result.output
        assert "Intégrité élevé" in result.output
        # Column with no classifications still appears
        assert "Nom" in result.output
        assert "3/3" not in result.output  # Only 2 of 3 columns have classifs
        assert "2/3" in result.output

    @patch("purviewcli.cli.entity.Entity")
    def test_json_output(self, mock_entity_cls):
        """--output json returns valid parseable JSON."""
        mock_client = MagicMock()
        mock_entity_cls.return_value = mock_client
        mock_client.entityRead.return_value = PARENT_ENTITY_RESPONSE
        mock_client.entityReadClassifications.side_effect = [
            CLASSIF_NAS,
            CLASSIF_NOM,
            CLASSIF_EMAIL,
        ]

        result = invoke("entity", "read-schema-classifications", "--guid", TABLE_GUID, "--output", "json")

        assert result.exit_code == 0, result.output
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert len(data) == 3
        col_names = {r["column"] for r in data}
        assert "NAS" in col_names
        nas = next(r for r in data if r["column"] == "NAS")
        assert "Canada Social Insurance Number" in nas["classifications"]

    @patch("purviewcli.cli.entity.Entity")
    def test_entity_not_found(self, mock_entity_cls):
        """Handles None response from entityRead gracefully."""
        mock_client = MagicMock()
        mock_entity_cls.return_value = mock_client
        mock_client.entityRead.return_value = None

        result = invoke("entity", "read-schema-classifications", "--guid", TABLE_GUID)

        assert result.exit_code == 0
        assert "not found" in result.output.lower() or "[X]" in result.output

    @patch("purviewcli.cli.entity.Entity")
    def test_no_columns(self, mock_entity_cls):
        """Reports when entity has no columns."""
        mock_client = MagicMock()
        mock_entity_cls.return_value = mock_client
        mock_client.entityRead.return_value = {
            "entity": {"guid": TABLE_GUID, "typeName": "azure_sql_table",
                        "attributes": {}, "relationshipAttributes": {}}
        }

        result = invoke("entity", "read-schema-classifications", "--guid", TABLE_GUID)

        assert result.exit_code == 0
        assert "No columns" in result.output

    @patch("purviewcli.cli.entity.Entity")
    def test_fallback_referred_entities(self, mock_entity_cls):
        """Falls back to referredEntities when relationshipAttributes has no columns."""
        mock_client = MagicMock()
        mock_entity_cls.return_value = mock_client
        mock_client.entityRead.return_value = {
            "entity": {
                "guid": TABLE_GUID,
                "typeName": "azure_sql_table",
                "attributes": {},
                "relationshipAttributes": {},
            },
            "referredEntities": {
                COL_NAS_GUID: {
                    "typeName": "azure_sql_column",
                    "attributes": {"name": "NAS"},
                }
            },
        }
        mock_client.entityReadClassifications.return_value = CLASSIF_NAS

        result = invoke("entity", "read-schema-classifications", "--guid", TABLE_GUID)

        assert result.exit_code == 0
        assert "NAS" in result.output

    def test_mock_mode(self):
        """--mock flag bypasses API calls."""
        result = invoke_mock("read-schema-classifications", "--guid", TABLE_GUID)
        assert result.exit_code == 0
        assert "MOCK" in result.output
        assert "[OK]" in result.output


# ===========================================================================
# add-schema-classification
# ===========================================================================


class TestAddSchemaClassification:
    # --- Validation errors --------------------------------------------------

    def test_error_no_guid_no_column_guid(self):
        result = invoke(
            "entity", "add-schema-classification",
            "--classification-name", "Canada Social Insurance Number",
        )
        assert result.exit_code != 0 or "[X]" in result.output or "Missing" in result.output

    def test_error_guid_without_column_name_or_all_columns(self):
        result = invoke(
            "entity", "add-schema-classification",
            "--guid", TABLE_GUID,
            "--classification-name", "Canada Social Insurance Number",
        )
        assert result.exit_code == 0
        assert "[X]" in result.output
        assert "--column-name" in result.output or "--all-columns" in result.output

    def test_error_column_guid_mixed_with_guid(self):
        result = invoke(
            "entity", "add-schema-classification",
            "--guid", TABLE_GUID,
            "--column-guid", COL_NAS_GUID,
            "--classification-name", "Test",
        )
        assert result.exit_code == 0
        assert "[X]" in result.output
        assert "exclusive" in result.output

    # --- Direct mode (--column-guid) ----------------------------------------

    @patch("purviewcli.cli.entity.Entity")
    def test_direct_column_guid(self, mock_entity_cls):
        """Adds classification directly to a column GUID."""
        mock_client = MagicMock()
        mock_entity_cls.return_value = mock_client
        mock_client.entityCreateClassifications.return_value = None

        result = invoke(
            "entity", "add-schema-classification",
            "--column-guid", COL_NAS_GUID,
            "--classification-name", "Canada Social Insurance Number",
        )

        assert result.exit_code == 0
        mock_client.entityCreateClassifications.assert_called_once()
        call_args = mock_client.entityCreateClassifications.call_args[0][0]
        assert call_args["--guid"] == [COL_NAS_GUID]
        payload = call_args["--payloadFile"]
        assert any(p["typeName"] == "Canada Social Insurance Number" for p in payload)
        assert "OK" in result.output

    # --- By column name -----------------------------------------------------

    @patch("purviewcli.cli.entity.Entity")
    def test_by_column_name(self, mock_entity_cls):
        """Resolves column by name and adds classification."""
        mock_client = MagicMock()
        mock_entity_cls.return_value = mock_client
        mock_client.entityRead.return_value = PARENT_ENTITY_RESPONSE
        mock_client.entityCreateClassifications.return_value = None

        result = invoke(
            "entity", "add-schema-classification",
            "--guid", TABLE_GUID,
            "--column-name", "NAS",
            "--classification-name", "Canada Social Insurance Number",
        )

        assert result.exit_code == 0
        mock_client.entityCreateClassifications.assert_called_once()
        call_args = mock_client.entityCreateClassifications.call_args[0][0]
        assert call_args["--guid"] == [COL_NAS_GUID]
        assert "OK" in result.output

    @patch("purviewcli.cli.entity.Entity")
    def test_column_name_case_insensitive(self, mock_entity_cls):
        """Column name match is case-insensitive."""
        mock_client = MagicMock()
        mock_entity_cls.return_value = mock_client
        mock_client.entityRead.return_value = PARENT_ENTITY_RESPONSE
        mock_client.entityCreateClassifications.return_value = None

        result = invoke(
            "entity", "add-schema-classification",
            "--guid", TABLE_GUID,
            "--column-name", "nas",  # lowercase
            "--classification-name", "Test",
        )

        assert result.exit_code == 0
        assert "[X]" not in result.output
        call_args = mock_client.entityCreateClassifications.call_args[0][0]
        assert call_args["--guid"] == [COL_NAS_GUID]

    @patch("purviewcli.cli.entity.Entity")
    def test_column_name_not_found(self, mock_entity_cls):
        """Reports error and lists available columns when name not found."""
        mock_client = MagicMock()
        mock_entity_cls.return_value = mock_client
        mock_client.entityRead.return_value = PARENT_ENTITY_RESPONSE

        result = invoke(
            "entity", "add-schema-classification",
            "--guid", TABLE_GUID,
            "--column-name", "DoesNotExist",
            "--classification-name", "Test",
        )

        assert result.exit_code == 0
        assert "[X]" in result.output
        assert "Available columns" in result.output
        mock_client.entityCreateClassifications.assert_not_called()

    # --- All columns --------------------------------------------------------

    @patch("purviewcli.cli.entity.Entity")
    def test_all_columns(self, mock_entity_cls):
        """Applies classification to every column of the table."""
        mock_client = MagicMock()
        mock_entity_cls.return_value = mock_client
        mock_client.entityRead.return_value = PARENT_ENTITY_RESPONSE
        mock_client.entityCreateClassifications.return_value = None

        result = invoke(
            "entity", "add-schema-classification",
            "--guid", TABLE_GUID,
            "--all-columns",
            "--classification-name", "Disponibilité élevé",
        )

        assert result.exit_code == 0
        assert mock_client.entityCreateClassifications.call_count == 3
        assert "3/3" in result.output

    # --- Multiple classifications at once -----------------------------------

    @patch("purviewcli.cli.entity.Entity")
    def test_multiple_classification_names(self, mock_entity_cls):
        """Repeating --classification-name sends all types in a single payload."""
        mock_client = MagicMock()
        mock_entity_cls.return_value = mock_client
        mock_client.entityCreateClassifications.return_value = None

        result = invoke(
            "entity", "add-schema-classification",
            "--column-guid", COL_NAS_GUID,
            "--classification-name", "Canada Social Insurance Number",
            "--classification-name", "Disponibilité élevé",
        )

        assert result.exit_code == 0
        call_args = mock_client.entityCreateClassifications.call_args[0][0]
        types_sent = {p["typeName"] for p in call_args["--payloadFile"]}
        assert "Canada Social Insurance Number" in types_sent
        assert "Disponibilité élevé" in types_sent

    # --- Dry-run ------------------------------------------------------------

    @patch("purviewcli.cli.entity.Entity")
    def test_dry_run(self, mock_entity_cls):
        """Dry-run mode: table lookup occurs but no creation API call."""
        mock_client = MagicMock()
        mock_entity_cls.return_value = mock_client
        mock_client.entityRead.return_value = PARENT_ENTITY_RESPONSE

        result = invoke(
            "entity", "add-schema-classification",
            "--guid", TABLE_GUID,
            "--all-columns",
            "--classification-name", "Test",
            "--dry-run",
        )

        assert result.exit_code == 0
        assert "DRY-RUN" in result.output
        mock_client.entityCreateClassifications.assert_not_called()

    # --- JSON output --------------------------------------------------------

    @patch("purviewcli.cli.entity.Entity")
    def test_json_output(self, mock_entity_cls):
        """--output json returns parseable JSON report."""
        mock_client = MagicMock()
        mock_entity_cls.return_value = mock_client
        mock_client.entityCreateClassifications.return_value = None

        result = invoke(
            "entity", "add-schema-classification",
            "--column-guid", COL_NAS_GUID,
            "--classification-name", "Test",
            "--output", "json",
        )

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert data[0]["status"] == "ok"

    # --- API error handling -------------------------------------------------

    @patch("purviewcli.cli.entity.Entity")
    def test_api_error_reported(self, mock_entity_cls):
        """API errors per column are captured and shown, not raised."""
        mock_client = MagicMock()
        mock_entity_cls.return_value = mock_client
        mock_client.entityCreateClassifications.side_effect = Exception("403 Forbidden")

        result = invoke(
            "entity", "add-schema-classification",
            "--column-guid", COL_NAS_GUID,
            "--classification-name", "Test",
        )

        assert result.exit_code == 0
        assert "error" in result.output.lower() or "403" in result.output

    # --- Mock mode ----------------------------------------------------------

    def test_mock_mode(self):
        result = invoke_mock(
            "add-schema-classification",
            "--guid", TABLE_GUID,
            "--column-name", "NAS",
            "--classification-name", "Test",
        )
        assert result.exit_code == 0
        assert "MOCK" in result.output
        assert "[OK]" in result.output


# ===========================================================================
# remove-schema-classification
# ===========================================================================


class TestRemoveSchemaClassification:
    # --- Validation errors --------------------------------------------------

    def test_error_no_guid_no_column_guid(self):
        result = invoke(
            "entity", "remove-schema-classification",
            "--classification-name", "Test",
        )
        assert result.exit_code != 0 or "[X]" in result.output or "Missing" in result.output

    def test_error_guid_without_column_name_or_all_columns(self):
        result = invoke(
            "entity", "remove-schema-classification",
            "--guid", TABLE_GUID,
            "--classification-name", "Test",
        )
        assert result.exit_code == 0
        assert "[X]" in result.output

    def test_error_column_guid_mixed_with_guid(self):
        result = invoke(
            "entity", "remove-schema-classification",
            "--guid", TABLE_GUID,
            "--column-guid", COL_NAS_GUID,
            "--classification-name", "Test",
        )
        assert result.exit_code == 0
        assert "[X]" in result.output
        assert "exclusive" in result.output

    # --- Direct mode --------------------------------------------------------

    @patch("purviewcli.cli.entity.Entity")
    def test_direct_column_guid_removes(self, mock_entity_cls):
        """Removes a classification from a column by direct GUID."""
        mock_client = MagicMock()
        mock_entity_cls.return_value = mock_client
        mock_client.entityReadClassifications.return_value = {
            "list": [{"typeName": "Canada Social Insurance Number"}]
        }
        mock_client.entityDeleteClassification.return_value = None

        result = invoke(
            "entity", "remove-schema-classification",
            "--column-guid", COL_NAS_GUID,
            "--classification-name", "Canada Social Insurance Number",
        )

        assert result.exit_code == 0
        mock_client.entityDeleteClassification.assert_called_once()
        call_args = mock_client.entityDeleteClassification.call_args[0][0]
        assert call_args["--guid"] == [COL_NAS_GUID]
        assert call_args["--classificationName"] == "Canada Social Insurance Number"
        assert "OK" in result.output

    # --- Graceful skip when classification not present ----------------------

    @patch("purviewcli.cli.entity.Entity")
    def test_skips_classification_not_present(self, mock_entity_cls):
        """Skips gracefully when the classification doesn't exist on the column."""
        mock_client = MagicMock()
        mock_entity_cls.return_value = mock_client
        mock_client.entityReadClassifications.return_value = {"list": []}
        # No classifications present — delete should NOT be called

        result = invoke(
            "entity", "remove-schema-classification",
            "--column-guid", COL_NAS_GUID,
            "--classification-name", "Canada Social Insurance Number",
        )

        assert result.exit_code == 0
        mock_client.entityDeleteClassification.assert_not_called()
        assert "skipped" in result.output

    # --- By column name -----------------------------------------------------

    @patch("purviewcli.cli.entity.Entity")
    def test_by_column_name(self, mock_entity_cls):
        """Resolves column by name then removes."""
        mock_client = MagicMock()
        mock_entity_cls.return_value = mock_client
        mock_client.entityRead.return_value = PARENT_ENTITY_RESPONSE
        mock_client.entityReadClassifications.return_value = {
            "list": [{"typeName": "Disponibilité élevé"}]
        }
        mock_client.entityDeleteClassification.return_value = None

        result = invoke(
            "entity", "remove-schema-classification",
            "--guid", TABLE_GUID,
            "--column-name", "NAS",
            "--classification-name", "Disponibilité élevé",
        )

        assert result.exit_code == 0
        call_args = mock_client.entityDeleteClassification.call_args[0][0]
        assert call_args["--guid"] == [COL_NAS_GUID]
        assert "OK" in result.output

    # --- All columns --------------------------------------------------------

    @patch("purviewcli.cli.entity.Entity")
    def test_all_columns(self, mock_entity_cls):
        """Iterates over all columns, removing where the classification is present."""
        mock_client = MagicMock()
        mock_entity_cls.return_value = mock_client
        mock_client.entityRead.return_value = PARENT_ENTITY_RESPONSE
        # NAS and Email have it; Nom does not
        mock_client.entityReadClassifications.side_effect = [
            {"list": [{"typeName": "Disponibilité élevé"}]},   # NAS
            {"list": []},                                        # Nom
            {"list": [{"typeName": "Disponibilité élevé"}]},   # Email
        ]
        mock_client.entityDeleteClassification.return_value = None

        result = invoke(
            "entity", "remove-schema-classification",
            "--guid", TABLE_GUID,
            "--all-columns",
            "--classification-name", "Disponibilité élevé",
        )

        assert result.exit_code == 0
        # Delete called only for the 2 columns that had the classification
        assert mock_client.entityDeleteClassification.call_count == 2

    # --- Multiple classifications at once -----------------------------------

    @patch("purviewcli.cli.entity.Entity")
    def test_multiple_classification_names(self, mock_entity_cls):
        """Removes multiple classifications from a single column."""
        mock_client = MagicMock()
        mock_entity_cls.return_value = mock_client
        mock_client.entityReadClassifications.return_value = {
            "list": [
                {"typeName": "Canada Social Insurance Number"},
                {"typeName": "Disponibilité élevé"},
            ]
        }
        mock_client.entityDeleteClassification.return_value = None

        result = invoke(
            "entity", "remove-schema-classification",
            "--column-guid", COL_NAS_GUID,
            "--classification-name", "Canada Social Insurance Number",
            "--classification-name", "Disponibilité élevé",
        )

        assert result.exit_code == 0
        assert mock_client.entityDeleteClassification.call_count == 2

    # --- Dry-run ------------------------------------------------------------

    @patch("purviewcli.cli.entity.Entity")
    def test_dry_run(self, mock_entity_cls):
        """Dry-run: no delete calls made."""
        mock_client = MagicMock()
        mock_entity_cls.return_value = mock_client
        mock_client.entityRead.return_value = PARENT_ENTITY_RESPONSE

        result = invoke(
            "entity", "remove-schema-classification",
            "--guid", TABLE_GUID,
            "--all-columns",
            "--classification-name", "Test",
            "--dry-run",
        )

        assert result.exit_code == 0
        assert "DRY-RUN" in result.output
        mock_client.entityDeleteClassification.assert_not_called()
        mock_client.entityReadClassifications.assert_not_called()

    # --- JSON output --------------------------------------------------------

    @patch("purviewcli.cli.entity.Entity")
    def test_json_output(self, mock_entity_cls):
        """--output json returns parseable JSON report."""
        mock_client = MagicMock()
        mock_entity_cls.return_value = mock_client
        mock_client.entityReadClassifications.return_value = {
            "list": [{"typeName": "Test"}]
        }
        mock_client.entityDeleteClassification.return_value = None

        result = invoke(
            "entity", "remove-schema-classification",
            "--column-guid", COL_NAS_GUID,
            "--classification-name", "Test",
            "--output", "json",
        )

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert data[0]["column_guid"] == COL_NAS_GUID

    # --- API error handling -------------------------------------------------

    @patch("purviewcli.cli.entity.Entity")
    def test_api_delete_error_captured(self, mock_entity_cls):
        """Delete API error is captured per classification, not raised."""
        mock_client = MagicMock()
        mock_entity_cls.return_value = mock_client
        mock_client.entityReadClassifications.return_value = {
            "list": [{"typeName": "Test"}]
        }
        mock_client.entityDeleteClassification.side_effect = Exception("500 Server Error")

        result = invoke(
            "entity", "remove-schema-classification",
            "--column-guid", COL_NAS_GUID,
            "--classification-name", "Test",
        )

        assert result.exit_code == 0
        assert "error" in result.output.lower() or "500" in result.output

    # --- Mock mode ----------------------------------------------------------

    def test_mock_mode(self):
        result = invoke_mock(
            "remove-schema-classification",
            "--guid", TABLE_GUID,
            "--all-columns",
            "--classification-name", "Test",
        )
        assert result.exit_code == 0
        assert "MOCK" in result.output
        assert "[OK]" in result.output
