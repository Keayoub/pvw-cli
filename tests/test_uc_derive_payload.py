# SPDX-License-Identifier: Apache-2.0
"""Unit tests for _derive_uc_payload_from_entity type and property mapping."""

import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from purviewcli.cli.unified_catalog import _derive_uc_payload_from_entity


def test_azure_sql_table_maps_to_AzureSqlTable():
    entity = {
        "typeName": "azure_sql_table",
        "attributes": {
            "name": "orders",
            "serverEndpoint": "srv.database.windows.net",
            "dbName": "mydb",
            "schemaName": "dbo",
        },
    }
    result = _derive_uc_payload_from_entity(entity)
    assert result["type"] == "AzureSqlTable"
    assert result["name"] == "orders"
    assert result["typeProperties"]["serverEndpoint"] == "srv.database.windows.net"
    assert result["typeProperties"]["databaseName"] == "mydb"
    assert result["typeProperties"]["schemaName"] == "dbo"
    assert result["typeProperties"]["format"] == "Table"


def test_adls_gen2_path_maps_to_ADLSGen2Path():
    entity = {
        "typeName": "adls_gen2_path",
        "attributes": {
            "qualifiedName": "adls://myaccount.dfs.core.windows.net/container/path/file.csv",
            "name": "file.csv",
            "url": "https://myaccount.dfs.core.windows.net",
            "container": "mycontainer",
            "path": "/path/to",
        },
    }
    result = _derive_uc_payload_from_entity(entity)
    assert result["type"] == "ADLSGen2Path"
    assert result["name"] == "file.csv"
    assert result["typeProperties"]["serverEndpoint"] == "https://myaccount.dfs.core.windows.net"
    assert result["typeProperties"]["container"] == "mycontainer"


def test_unknown_type_falls_back_to_General():
    entity = {"typeName": "some_custom_type", "attributes": {"name": "my-asset"}}
    result = _derive_uc_payload_from_entity(entity)
    assert result["type"] == "General"
    assert result["name"] == "my-asset"
    assert result["typeProperties"] == {}


def test_name_extracted_from_qualifiedName_path():
    entity = {
        "typeName": "adls_gen2_path",
        "attributes": {
            "qualifiedName": "https://acc.dfs.core.windows.net/container/folder/file.parquet"
        },
    }
    result = _derive_uc_payload_from_entity(entity)
    assert result["name"] == "file.parquet"


def test_empty_entity_returns_General_defaults():
    result = _derive_uc_payload_from_entity({})
    assert result["type"] == "General"
    assert result["typeProperties"] == {}
