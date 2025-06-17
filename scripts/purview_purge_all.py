"""
Script to remove all sample data from a Microsoft Purview instance for a clean slate.
Deletes collections, entities, data products, domains, glossary terms, etc.
"""
import sys
from purviewcli.client._collections import Collections
from purviewcli.client._entity import Entity
from purviewcli.client._data_product import DataProduct
from purviewcli.client._glossary import Glossary
# from purviewcli.client._domain import Domain  # Uncomment if available

def main():
    print("Purging all sample data...")
    # Remove data products
    data_product_client = DataProduct()
    try:
        dps = data_product_client.list()
        for dp in dps:
            qn = dp.get("qualifiedName")
            if qn:
                data_product_client.delete(qn)
                print(f"Deleted data product: {qn}")
    except Exception as e:
        print(f"Error deleting data products: {e}")

    # Remove entities
    entity_client = Entity()
    try:
        # This assumes a list() method or similar; adjust as needed
        entities = []  # entity_client.list()  # Implement if available
        for ent in entities:
            qn = ent.get("qualifiedName")
            if qn:
                entity_client.entityDeleteUniqueAttribute({"--qualifiedName": qn})
                print(f"Deleted entity: {qn}")
    except Exception as e:
        print(f"Error deleting entities: {e}")

    # Remove glossary terms
    glossary_client = Glossary()
    try:
        terms = glossary_client.list_terms() if hasattr(glossary_client, 'list_terms') else []
        for t in terms:
            name = t.get("name")
            if name:
                glossary_client.delete_term(name)
                print(f"Deleted term: {name}")
    except Exception as e:
        print(f"Error deleting glossary terms: {e}")

    # Remove collections
    collections_client = Collections()
    try:
        cols = collections_client.list() if hasattr(collections_client, 'list') else []
        for c in cols:
            name = c.get("name")
            if name:
                collections_client.delete(name)
                print(f"Deleted collection: {name}")
    except Exception as e:
        print(f"Error deleting collections: {e}")

    # Remove domains (if supported)
    # domain_client = Domain()
    # try:
    #     domains = domain_client.list() if hasattr(domain_client, 'list') else []
    #     for d in domains:
    #         name = d.get("name")
    #         if name:
    #             domain_client.delete(name)
    #             print(f"Deleted domain: {name}")
    # except Exception as e:
    #     print(f"Error deleting domains: {e}")

    print("Purge complete.")

if __name__ == "__main__":
    main()
