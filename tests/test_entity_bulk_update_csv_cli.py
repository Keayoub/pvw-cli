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

        captured_update_payloads = []
        captured_classification_payloads = []

        def capture_update_call(args):
            with open(args["--payloadFile"], encoding="utf-8") as payload_file:
                captured_update_payloads.append(json.load(payload_file))
            return {"mutatedEntities": {}}

        def capture_classification_call(args):
            captured_classification_payloads.append(args)
            return {"guid": args["--guid"][0]}

        with (
            patch(
                "purviewcli.client._entity.Entity.entityCreateBulk",
                side_effect=capture_update_call,
            ),
            patch(
                "purviewcli.client._entity.Entity.entityCreateClassifications",
                side_effect=capture_classification_call,
            ),
        ):
            result = CliRunner().invoke(
                main,
                ("entity", "bulk-update-csv", "--csv-file", "update.csv"),
                catch_exceptions=False,
            )

    assert result.exit_code == 0, result.output
    assert captured_update_payloads == [
        {
            "entities": [
                {
                    "guid": "5b80b2ea-db05-4404-b964-50f6f6f60000",
                    "typeName": "DataSet",
                    "attributes": {
                        "name": "table",
                        "qualifiedName": "mssql://server/database/schema/table",
                        "userDescription": "Updated description",
                    },
                    "classifications": [{"typeName": "Sensible"}],
                }
            ]
        }
    ]
    assert captured_classification_payloads == [
        {
            "--guid": ["5b80b2ea-db05-4404-b964-50f6f6f60000"],
            "--payloadFile": [{"typeName": "Sensible"}],
        }
    ]


def test_bulk_update_csv_handles_classifications_plural_and_json_array():
    csv_content = (
        'typeName,guid,qualifiedName,name,userDescription,classifications\n'
        '"DataSet","5b80b2ea-db05-4404-b964-50f6f6f60000","mssql://server/db/schema/tab1","tab1","desc1","[""Sensible""]"\n'
        '"mssql_column","5b80b2ea-db05-4404-b964-50f6f6f60001","mssql://server/db/schema/tab2#col","col","desc2","Sensible"\n'
    )

    with CliRunner().isolated_filesystem():
        with open("update.csv", "w", encoding="utf-8", newline="") as csv_file:
            csv_file.write(csv_content)

        captured_update_payloads = []
        captured_classification_payloads = []

        def capture_update_call(args):
            with open(args["--payloadFile"], encoding="utf-8") as payload_file:
                captured_update_payloads.append(json.load(payload_file))
            return {"mutatedEntities": {}}

        def capture_classification_call(args):
            captured_classification_payloads.append(args)
            return {"guid": args["--guid"][0]}

        with (
            patch(
                "purviewcli.client._entity.Entity.entityCreateBulk",
                side_effect=capture_update_call,
            ),
            patch(
                "purviewcli.client._entity.Entity.entityCreateClassifications",
                side_effect=capture_classification_call,
            ),
        ):
            result = CliRunner().invoke(
                main,
                ("entity", "bulk-update-csv", "--csv-file", "update.csv"),
                catch_exceptions=False,
            )

    assert result.exit_code == 0, result.output
    assert captured_update_payloads == [
        {
            "entities": [
                {
                    "guid": "5b80b2ea-db05-4404-b964-50f6f6f60000",
                    "typeName": "DataSet",
                    "attributes": {
                        "name": "tab1",
                        "qualifiedName": "mssql://server/db/schema/tab1",
                        "userDescription": "desc1",
                    },
                    "classifications": [{"typeName": "Sensible"}],
                },
                {
                    "guid": "5b80b2ea-db05-4404-b964-50f6f6f60001",
                    "typeName": "DataSet",
                    "attributes": {
                        "name": "col",
                        "qualifiedName": "mssql://server/db/schema/tab2#col",
                        "userDescription": "desc2",
                    },
                    "classifications": [{"typeName": "Sensible"}],
                },
            ]
        }
    ]
    assert captured_classification_payloads == [
        {
            "--guid": ["5b80b2ea-db05-4404-b964-50f6f6f60000"],
            "--payloadFile": [{"typeName": "Sensible"}],
        },
        {
            "--guid": ["5b80b2ea-db05-4404-b964-50f6f6f60001"],
            "--payloadFile": [{"typeName": "Sensible"}],
        },
    ]