"""Tests for GUID-based entity bulk updates from CSV."""
import json
import os
import sys
from unittest.mock import patch

from click.testing import CliRunner

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from purviewcli.cli.cli import main


def test_bulk_update_csv_prefers_guid_and_maps_classification():
    csv_content = (
        "typeName,guid,qualifiedName,name,userDescription,classification\n"
        '"DataSet","5b80b2ea-db05-4404-b964-50f6f6f60000",'
        '"mssql://server/database/schema/table","table",'
        '"Updated description","Sensible"\n'
    )

    with CliRunner().isolated_filesystem():
        with open("update.csv", "w", encoding="utf-8", newline="") as csv_file:
            csv_file.write(csv_content)

        captured_payloads = []

        def capture_bulk_call(args):
            with open(args["--payloadFile"], encoding="utf-8") as payload_file:
                captured_payloads.append(json.load(payload_file))
            return {"mutatedEntities": {}}

        with patch(
            "purviewcli.client._entity.Entity.entityCreateBulk", side_effect=capture_bulk_call
        ):
            result = CliRunner().invoke(
                main,
                ("entity", "bulk-update-csv", "--csv-file", "update.csv"),
                catch_exceptions=False,
            )

    assert result.exit_code == 0, result.output
    assert captured_payloads == [
        {
            "entities": [
                {
                    "guid": "5b80b2ea-db05-4404-b964-50f6f6f60000",
                    "typeName": "DataSet",
                    "attributes": {
                        "name": "table",
                        "userDescription": "Updated description",
                    },
                    "classifications": [{"typeName": "Sensible"}],
                }
            ]
        }
    ]