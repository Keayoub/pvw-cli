import pytest
from purviewcli.client._search import Search

@pytest.fixture
def search_client():
    return Search()

def test_basic_query(search_client):
    args = {"--keywords": "customer", "--limit": 5}
    search_client.searchQuery(args)
    assert search_client.method == "POST"
    assert "keywords" in search_client.payload

def test_advanced_query_with_filter(search_client):
    args = {
        "--keywords": "sales",
        "--classification": "PII",
        "--objectType": "Tables",
        "--limit": 10
    }
    search_client.searchQuery(args)
    # The filter will be an 'and' structure with two conditions
    filt = search_client.payload["filter"]
    if "and" in filt:
        fields = [cond["condition"]["field"] for cond in filt["and"]]
        assert "objectType" in fields
        assert "classification" in fields
    else:
        assert filt["field"] == "objectType" or filt["field"] == "classification"


def test_autocomplete(search_client):
    args = {"--keywords": "ord", "--limit": 3}
    search_client.searchAutoComplete(args)
    assert search_client.method == "POST"
    assert search_client.endpoint.endswith("autocomplete")


def test_suggest(search_client):
    args = {"--keywords": "prod", "--limit": 2}
    search_client.searchSuggest(args)
    assert search_client.method == "POST"
    assert search_client.endpoint.endswith("suggest")


def test_faceted_search(search_client):
    args = {"--keywords": "finance", "--facetFields": "objectType,classification", "--limit": 5}
    search_client.searchFaceted(args)
    assert "facets" in search_client.payload


def test_browse(search_client):
    args = {"--entityType": "Tables", "--path": "/root/finance", "--limit": 2}
    search_client.searchBrowse(args)
    assert search_client.method == "POST"
    assert search_client.endpoint.endswith("browse")


def test_time_based_search(search_client):
    args = {"--keywords": "audit", "--createdAfter": "2024-01-01", "--limit": 1}
    search_client.searchByTime(args)
    assert search_client.method == "POST"
    assert "filter" in search_client.payload


def test_entity_type_search(search_client):
    args = {"--entityTypes": "Files,Tables", "--limit": 2}
    search_client.searchByEntityType(args)
    assert search_client.method == "POST"
    assert "objectType" in search_client.payload