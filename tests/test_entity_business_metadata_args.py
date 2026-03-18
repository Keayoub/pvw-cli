import os
import sys
import json

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from purviewcli.client._entity import Entity


def test_resolve_business_metadata_name_accepts_legacy_aliases():
    entity = Entity()

    assert entity._resolve_business_metadata_name({"--businessMetadataName": "group1"}) == "group1"
    assert entity._resolve_business_metadata_name({"--bmName": "group1"}) == "group1"
    assert entity._resolve_business_metadata_name({"--bm-name": "group1"}) == "group1"
    assert entity._resolve_business_metadata_name({"bm_name": "group1"}) == "group1"


def test_resolve_business_metadata_name_reads_first_payload_key(tmp_path):
    entity = Entity()
    payload_file = tmp_path / "group.json"
    payload_file.write_text(json.dumps({"group1": {"attr1": "value1"}}), encoding="utf-8")

    assert (
        entity._resolve_business_metadata_name({"--payloadFile": str(payload_file)}, allow_payload=True)
        == "group1"
    )


def test_resolve_business_metadata_attributes_accepts_single_attr_aliases():
    entity = Entity()

    assert entity._resolve_business_metadata_attributes({"--attributes": ["attr1"]}) == ["attr1"]
    assert entity._resolve_business_metadata_attributes({"--attr-name": "attr1"}) == ["attr1"]
    assert entity._resolve_business_metadata_attributes({"attr_name": "attr1"}) == ["attr1"]


def test_resolve_business_metadata_name_requires_value():
    entity = Entity()

    with pytest.raises(ValueError, match="Business metadata name is required"):
        entity._resolve_business_metadata_name({})


def test_delete_business_metadata_accepts_legacy_group_alias(monkeypatch):
    monkeypatch.setattr("purviewcli.client.endpoint.get_data", lambda http_dict: http_dict)
    entity = Entity()

    result = entity.entityDeleteBusinessMetadata({"--guid": ["entity-guid-123"], "--bmName": "group1"})

    assert result is not None
    assert result["method"] == "DELETE"
    assert result["endpoint"].endswith("/entity/guid/entity-guid-123/businessmetadata")
    assert result["params"]["businessMetadataName"] == "group1"


def test_create_business_metadata_preserves_inline_payload(monkeypatch):
    monkeypatch.setattr("purviewcli.client.endpoint.get_data", lambda http_dict: http_dict)
    entity = Entity()

    result = entity.entityCreateBusinessMetadata(
        {
            "--guid": ["entity-guid-123"],
            "--payloadFile": {"group1": {"attr1": "value1"}},
        }
    )

    assert result is not None
    assert result["method"] == "POST"
    assert result["endpoint"].endswith("/entity/guid/entity-guid-123/businessmetadata")
    assert result["payload"] == {"group1": {"attr1": "value1"}}


def test_delete_business_metadata_attributes_accepts_legacy_group_and_attr_aliases(monkeypatch):
    monkeypatch.setattr("purviewcli.client.endpoint.get_data", lambda http_dict: http_dict)
    entity = Entity()

    result = entity.entityDeleteBusinessMetadataAttributes(
        {
            "--guid": ["entity-guid-123"],
            "--bmName": "group1",
            "--attr-name": "attr1",
        }
    )

    assert result is not None
    assert result["method"] == "DELETE"
    assert result["endpoint"].endswith("/entity/guid/entity-guid-123/businessmetadata/group1")
    assert result["params"]["businessMetadataAttributes"] == ["attr1"]


def test_create_business_metadata_attributes_accepts_legacy_group_alias(monkeypatch):
    monkeypatch.setattr("purviewcli.client.endpoint.get_data", lambda http_dict: http_dict)
    entity = Entity()

    result = entity.entityCreateBusinessMetadataAttributes(
        {
            "--guid": ["entity-guid-123"],
            "--bmName": "group1",
            "--payloadFile": {"attr1": "value1"},
        }
    )

    assert result is not None
    assert result["method"] == "POST"
    assert result["endpoint"].endswith("/entity/guid/entity-guid-123/businessmetadata/group1")
    assert result["payload"] == {"attr1": "value1"}