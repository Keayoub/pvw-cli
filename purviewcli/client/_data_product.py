import json
from purviewcli.client._entity import Entity

class DataProduct:
    """Client for managing data products in Microsoft Purview."""
    def __init__(self):
        self.entity_client = Entity()

    def import_from_csv(self, products):
        results = []
        for product in products:
            payload = {
                "typeName": product.get("typeName", "DataProduct"),
                "attributes": {
                    "qualifiedName": product["qualifiedName"],
                    "name": product.get("name", product["qualifiedName"]),
                    "description": product.get("description", "")
                },
                # Add more fields as needed
            }
            # The entity client expects a file, so we serialize to a temp file or pass dict if supported
            # Here, we assume entityCreate can accept a dict for --payloadFile
            result = self.entity_client.entityCreate({"--payloadFile": payload})
            results.append((product["qualifiedName"], result))
        return results

    def create(self, qualified_name, name=None, description=None, type_name="DataProduct"):
        """Create a single data product entity."""
        payload = {
            "typeName": type_name,
            "attributes": {
                "qualifiedName": qualified_name,
                "name": name or qualified_name,
                "description": description or ""
            },
        }
        return self.entity_client.entityCreate({"--payloadFile": payload})

    def list(self, type_name="DataProduct"):
        """List all data products (by typeName)."""
        # This is a simple example; in practice, use search or filter by typeName
        # Here, you would call a search client or entity list method
        # For now, return an empty list as a placeholder
        return []

    def show(self, qualified_name, type_name="DataProduct"):
        """Show a data product by qualifiedName."""
        args = {"--typeName": type_name, "--qualifiedName": qualified_name}
        return self.entity_client.entityReadUniqueAttribute(args)

    def delete(self, qualified_name, type_name="DataProduct"):
        """Delete a data product by qualifiedName."""
        args = {"--typeName": type_name, "--qualifiedName": qualified_name}
        return self.entity_client.entityDeleteUniqueAttribute(args)

    def add_classification(self, qualified_name, classification, type_name="DataProduct"):
        """Add a classification to a data product."""
        args = {
            "--typeName": type_name,
            "--qualifiedName": qualified_name,
            "--payloadFile": {"classifications": [classification]}
        }
        return self.entity_client.entityAddClassificationsByUniqueAttribute(args)

    def remove_classification(self, qualified_name, classification, type_name="DataProduct"):
        """Remove a classification from a data product."""
        args = {
            "--typeName": type_name,
            "--qualifiedName": qualified_name,
            "--classificationName": classification
        }
        return self.entity_client.entityDeleteClassificationByUniqueAttribute(args)

    def add_label(self, qualified_name, label, type_name="DataProduct"):
        """Add a label to a data product."""
        args = {
            "--typeName": type_name,
            "--qualifiedName": qualified_name,
            "--payloadFile": {"labels": [label]}
        }
        return self.entity_client.entityAddLabelsByUniqueAttribute(args)

    def remove_label(self, qualified_name, label, type_name="DataProduct"):
        """Remove a label from a data product."""
        args = {
            "--typeName": type_name,
            "--qualifiedName": qualified_name,
            "--payloadFile": {"labels": [label]}
        }
        return self.entity_client.entityRemoveLabelsByUniqueAttribute(args)

    def link_glossary(self, qualified_name, term, type_name="DataProduct"):
        """Link a glossary term to a data product."""
        # This assumes business metadata or a custom attribute for glossary terms
        # You may need to adjust this to your Purview model
        args = {
            "--typeName": type_name,
            "--qualifiedName": qualified_name,
            "--payloadFile": {"meanings": [term]}
        }
        return self.entity_client.entityPartialUpdateByUniqueAttribute(args)

    def show_lineage(self, qualified_name, type_name="DataProduct"):
        """Show lineage for a data product."""
        args = {"--typeName": type_name, "--qualifiedName": qualified_name}
        # This assumes you have a lineage client or can call entityReadUniqueAttribute and extract lineage
        # For now, just return the entity details
        return self.entity_client.entityReadUniqueAttribute(args)

    def set_status(self, qualified_name, status, type_name="DataProduct"):
        """Set the status of a data product (e.g., active, deprecated)."""
        args = {
            "--typeName": type_name,
            "--qualifiedName": qualified_name,
            "--payloadFile": {"status": status}
        }
        return self.entity_client.entityPartialUpdateByUniqueAttribute(args)
