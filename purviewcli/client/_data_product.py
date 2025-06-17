import json
import tempfile
import os
import csv
from purviewcli.client._entity import Entity

class DataProduct:
    """Client for managing data products in Microsoft Purview."""
    
    def __init__(self):
        self.entity_client = Entity()

    def import_from_csv(self, products):
        with open("import_from_csv_debug.log", "a") as logf:
            logf.write(f"products type: {type(products)}\n")
            if products:
                logf.write(f"first product type: {type(products[0])}\n")
                logf.write(f"first product: {products[0]}\n")
        if not isinstance(products, list):
            raise TypeError(f"Expected a list, got: {type(products)} with value: {products}")
        if not products or not isinstance(products[0], dict):
            raise TypeError(
                f"Expected a list of dicts, got: {type(products[0])} with value: {products[0]}"
            )
        required_fields = ["qualifiedName"]
        entities = []
        for product in products:
            # Validate required fields
            for field in required_fields:
                if not product.get(field):
                    raise ValueError(f"Missing required field '{field}' in row: {product}")
            # Always use typeName DataSet (Purview default)
            attributes = {k: v for k, v in product.items() if k != "typeName"}
            entity = {
                "typeName": "DataSet",
                "attributes": attributes
            }
            entities.append(entity)
        # Write the bulk payload to a temp file (always as {"entities": [...]})
        bulk_payload = {"entities": entities}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmpf:
            json.dump(bulk_payload, tmpf, indent=2)
            tmpf.flush()
            payload_file = tmpf.name
        try:
            result = self.entity_client.entityCreateBulk({"--payloadFile": payload_file})
            return [(e["attributes"]["qualifiedName"], result) for e in entities]
        finally:
            os.remove(payload_file)

    def import_from_csv_file(self, csv_file_path, dry_run=False):
        """Load data products from a CSV file and import them. If dry_run is True, return the parsed products only."""
        with open(csv_file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            products = list(reader)
        if dry_run:
            return products
        return self.import_from_csv(products)

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
        # Write payload to temp file since entity client expects a file path
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmpf:
            json.dump(payload, tmpf, indent=2)
            tmpf.flush()
            payload_file = tmpf.name
        
        try:
            return self.entity_client.entityCreate({"--payloadFile": payload_file})
        finally:
            os.remove(payload_file)

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
