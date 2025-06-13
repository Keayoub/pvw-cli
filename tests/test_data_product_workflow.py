import pytest
from purviewcli.client._data_product import DataProduct
from purviewcli.client._glossary import Glossary
from purviewcli.client._entity import Entity

@pytest.mark.order(1)
def test_create_glossary_and_terms():
    glossary_client = Glossary()
    glossary = glossary_client.create_glossary({"name": "Business Glossary", "shortDescription": "Test glossary"})
    assert "guid" in glossary
    term1 = glossary_client.create_term({"glossaryGuid": glossary["guid"], "name": "Customer", "shortDescription": "A customer entity"})
    term2 = glossary_client.create_term({"glossaryGuid": glossary["guid"], "name": "Order", "shortDescription": "An order entity"})
    assert "guid" in term1 and "guid" in term2

@pytest.mark.order(2)
def test_create_collections():
    entity_client = Entity()
    # Example: create a collection entity (adjust typeName as needed)
    collection = entity_client.entityCreate({"--payloadFile": {
        "typeName": "Collection",
        "attributes": {
            "qualifiedName": "collection1",
            "name": "Collection 1",
            "description": "Test collection"
        }
    }})
    assert "guid" in collection

@pytest.mark.order(3)
def test_create_data_classification():
    entity_client = Entity()
    # Example: create a classification (adjust as needed for your model)
    classification = entity_client.entityAddClassification({
        "--payloadFile": {
            "classifications": ["PII"]
        }
    })
    assert classification is not None

@pytest.mark.order(4)
def test_create_data_product_and_manage():
    data_product_client = DataProduct()
    qualified_name = "product.test.1"
    # Create data product
    result = data_product_client.create(qualified_name, name="Test Product", description="A test data product")
    assert "guid" in result or result is not None
    # Add classification
    result2 = data_product_client.add_classification(qualified_name, "PII")
    assert result2 is not None
    # Add label
    result3 = data_product_client.add_label(qualified_name, "gold")
    assert result3 is not None
    # Link glossary term
    result4 = data_product_client.link_glossary(qualified_name, "Customer")
    assert result4 is not None
    # Set status
    result5 = data_product_client.set_status(qualified_name, "active")
    assert result5 is not None
    # Show lineage
    lineage = data_product_client.show_lineage(qualified_name)
    assert lineage is not None
    # Delete data product
    result6 = data_product_client.delete(qualified_name)
    assert result6 is not None
