"""
Entity Management Client for Microsoft Purview Data Map API
Based on official API: https://learn.microsoft.com/en-us/rest/api/purview/datamapdataplane/entity
API Version: 2023-09-01

Complete implementation of all Entity operations from the official specification:
- CRUD Operations (Create, Read, Update, Delete)
- Bulk Operations
- Classification Management
- Business Metadata Management
- Label Management
- Unique Attribute Operations
- Collection Movement
- CSV Import/Export
"""

from .endpoint import Endpoint, decorator, get_json, no_api_call_decorator
from .endpoints import PurviewEndpoints


class Entity(Endpoint):
    """Entity Management Operations - Complete Official API Implementation"""

    def __init__(self):
        Endpoint.__init__(self)
        self.app = "catalog"

    # === CORE ENTITY CRUD OPERATIONS ===

    @decorator
    def entityCreateOrUpdate(self, args):
        """Create or update an entity (Official API: Create Or Update)"""
        self.method = "POST"
        self.endpoint = PurviewEndpoints.ENTITY["base"]
        self.params = PurviewEndpoints.get_api_version_params("datamap")
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def entityCreate(self, args):
        """Create an entity (Alias for CreateOrUpdate)"""
        return self.entityCreateOrUpdate(args)

    @decorator
    def entityDelete(self, args):
        """Delete an entity identified by its GUID"""
        self.method = "DELETE"
        self.endpoint = f'{PurviewEndpoints.ENTITY["guid"]}/{args["--guid"][0]}'
        self.params = PurviewEndpoints.get_api_version_params("datamap")

    @decorator
    def entityRead(self, args):
        """Get complete definition of an entity given its GUID (Official API: Get)"""
        self.method = "GET"
        self.endpoint = f'{PurviewEndpoints.ENTITY["guid"]}/{args["--guid"][0]}'
        self.params = {
            **PurviewEndpoints.get_api_version_params("datamap"),
            "ignoreRelationships": str(args.get("--ignoreRelationships", False)).lower(),
            "minExtInfo": str(args.get("--minExtInfo", False)).lower(),
        }

    @decorator
    def entityUpdate(self, args):
        """Update an entity (Alias for CreateOrUpdate)"""
        return self.entityCreateOrUpdate(args)

    # === BULK OPERATIONS ===

    def _validate_entities_have_qualified_name(self, args):
        """Ensure every entity in the payload has a non-empty attributes.qualifiedName."""
        payload = get_json(args, "--payloadFile")
        entities = payload.get("entities", [])
        missing = [e for e in entities if not e.get("attributes", {}).get("qualifiedName")]
        if missing:
            raise ValueError(f"The following entities are missing 'qualifiedName': {missing}")

    @decorator
    def entityBulkCreateOrUpdate(self, args):
        """Create or update entities in bulk (Official API: Bulk Create Or Update)"""
        self._validate_entities_have_qualified_name(args)
        self.method = "POST"
        self.endpoint = PurviewEndpoints.ENTITY["bulk"]
        self.params = PurviewEndpoints.get_api_version_params("datamap")
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def entityCreateBulk(self, args):
        """Create entities in bulk (Alias for BulkCreateOrUpdate)"""
        return self.entityBulkCreateOrUpdate(args)

    @decorator
    def entityDeleteBulk(self, args):
        """Delete a list of entities in bulk (Official API: Bulk Delete)"""
        self.method = "DELETE"
        self.endpoint = PurviewEndpoints.ENTITY["bulk"]
        self.params = {**PurviewEndpoints.get_api_version_params("datamap"), "guid": args["--guid"]}

    @decorator
    def entityReadBulk(self, args):
        """List entities in bulk identified by GUIDs (Official API: List By Guids)"""
        self.method = "GET"
        self.endpoint = PurviewEndpoints.ENTITY["bulk"]
        self.params = {
            **PurviewEndpoints.get_api_version_params("datamap"),
            "guid": args["--guid"],
            "ignoreRelationships": str(args.get("--ignoreRelationships", False)).lower(),
            "minExtInfo": str(args.get("--minExtInfo", False)).lower(),
        }

    # === UNIQUE ATTRIBUTE OPERATIONS ===

    @decorator
    def entityReadUniqueAttribute(self, args):
        """Get entity by unique attributes (Official API: Get By Unique Attributes)"""
        self.method = "GET"
        self.endpoint = f'{PurviewEndpoints.ENTITY["unique_attribute"]}/{args["--typeName"]}'
        self.params = {
            **PurviewEndpoints.get_api_version_params("datamap"),
            "attr:qualifiedName": args["--qualifiedName"],
            "ignoreRelationships": str(args.get("--ignoreRelationships", False)).lower(),
            "minExtInfo": str(args.get("--minExtInfo", False)).lower(),
        }

    @decorator
    def entityReadBulkUniqueAttribute(self, args):
        """List entities by unique attributes (Official API: List By Unique Attributes)"""
        self.method = "GET"
        self.endpoint = f'{PurviewEndpoints.ENTITY["unique_attribute"]}/{args["--typeName"]}/bulk'
        params = {
            **PurviewEndpoints.get_api_version_params("datamap"),
            "ignoreRelationships": str(args.get("--ignoreRelationships", False)).lower(),
            "minExtInfo": str(args.get("--minExtInfo", False)).lower(),
        }

        # Add unique attributes
        for counter, qualifiedName in enumerate(args["--qualifiedName"]):
            params[f"attr_{counter}:qualifiedName"] = qualifiedName

        self.params = params

    @decorator
    def entityDeleteUniqueAttribute(self, args):
        """Delete entity by unique attributes (Official API: Delete By Unique Attribute)"""
        self.method = "DELETE"
        self.endpoint = f'{PurviewEndpoints.ENTITY["unique_attribute"]}/{args["--typeName"]}'
        self.params = {
            **PurviewEndpoints.get_api_version_params("datamap"),
            "attr:qualifiedName": args["--qualifiedName"],
        }

    @decorator
    def entityPartialUpdateByUniqueAttribute(self, args):
        """Partial update by unique attributes (Official API: Partial Update By Unique Attributes)"""
        self.method = "PUT"
        self.endpoint = f'{PurviewEndpoints.ENTITY["unique_attribute"]}/{args["--typeName"]}'
        self.params = {
            **PurviewEndpoints.get_api_version_params("datamap"),
            "attr:qualifiedName": args["--qualifiedName"],
        }
        self.payload = get_json(args, "--payloadFile")

    # === ENTITY HEADER OPERATIONS ===

    @decorator
    def entityReadHeader(self, args):
        """Get entity header given its GUID (Official API: Get Header)"""
        self.method = "GET"
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.ENTITY["header"], guid=args["--guid"][0]
        )
        self.params = PurviewEndpoints.get_api_version_params("datamap")

    # === PARTIAL UPDATE OPERATIONS ===

    @decorator
    def entityPartialUpdateAttribute(self, args):
        """Partial update entity attribute by GUID (Official API: Partial Update Attribute By Guid)"""
        self.method = "PUT"
        self.endpoint = f'{PurviewEndpoints.ENTITY["guid"]}/{args["--guid"][0]}'
        self.params = {
            **PurviewEndpoints.get_api_version_params("datamap"),
            "name": args["--attrName"],
        }
        self.payload = args["--attrValue"]

    @decorator
    def entityDelete(self, args):
        self.method = "DELETE"
        self.endpoint = f'{PurviewEndpoints.ENTITY["guid"]}/{args["--guid"][0]}'

    @decorator
    def entityRead(self, args):
        self.method = "GET"
        self.endpoint = f'{PurviewEndpoints.ENTITY["guid"]}/{args["--guid"][0]}'
        self.params = {
            "ignoreRelationships": str(args["--ignoreRelationships"]).lower(),
            "minExtInfo": str(args["--minExtInfo"]).lower(),
        }

    @decorator
    def entityPut(self, args):
        self.method = "PUT"
        self.endpoint = f'{PurviewEndpoints.ENTITY["guid"]}/{args["--guid"][0]}'
        self.params = {"name": args["--attrName"]}
        self.payload = args["--attrValue"]

    @decorator
    def entityDeleteClassification(self, args):
        self.method = "DELETE"
        self.endpoint = (
            PurviewEndpoints.format_endpoint(
                PurviewEndpoints.ENTITY["classification"], guid=args["--guid"][0]
            )
            + f'/{args["--classificationName"]}'
        )

    @decorator
    def entityReadClassification(self, args):
        self.method = "GET"
        self.endpoint = (
            PurviewEndpoints.format_endpoint(
                PurviewEndpoints.ENTITY["classification"], guid=args["--guid"][0]
            )
            + f'/{args["--classificationName"]}'
        )

    @decorator
    def entityReadClassifications(self, args):
        self.method = "GET"
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.ENTITY["classifications"], guid=args["--guid"][0]
        )

    @decorator
    def entityCreateClassifications(self, args):
        self.method = "POST"
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.ENTITY["classifications"], guid=args["--guid"][0]
        )
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def entityPutClassifications(self, args):
        self.method = "PUT"
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.ENTITY["classifications"], guid=args["--guid"][0]
        )
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def entityReadHeader(self, args):
        self.method = "GET"
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.ENTITY["header"], guid=args["--guid"][0]
        )

    @decorator
    def entityReadBulkUniqueAttribute(self, args):
        self.method = "GET"
        self.endpoint = f'{PurviewEndpoints.ENTITY["unique_attribute"]}/{args["--typeName"]}/bulk'
        self.params = {
            "ignoreRelationships": str(args["--ignoreRelationships"]).lower(),
            "minExtInfo": str(args["--minExtInfo"]).lower(),
        }
        counter = 0
        self.params = {}
        for qualifiedName in args["--qualifiedName"]:
            self.params[f"attr_{str(counter)}:qualifiedName"] = qualifiedName
            counter += 1

    @decorator
    def entityReadUniqueAttribute(self, args):
        self.method = "GET"
        self.endpoint = f'{PurviewEndpoints.ENTITY["unique_attribute"]}/{args["--typeName"]}'
        self.params = {
            "attr:qualifiedName": args["--qualifiedName"],
            "ignoreRelationships": str(args["--ignoreRelationships"]).lower(),
            "minExtInfo": str(args["--minExtInfo"]).lower(),
        }

    @decorator
    def entityDeleteUniqueAttribute(self, args):
        self.method = "DELETE"
        self.endpoint = f'{PurviewEndpoints.ENTITY["unique_attribute"]}/{args["--typeName"]}'
        self.params = {"attr:qualifiedName": args["--qualifiedName"]}

    @decorator
    def entityPutUniqueAttribute(self, args):
        self.method = "PUT"
        self.endpoint = f'{PurviewEndpoints.ENTITY["unique_attribute"]}/{args["--typeName"]}'
        self.payload = get_json(args, "--payloadFile")
        self.params = {"attr:qualifiedName": args["--qualifiedName"]}

    @decorator
    def entityDeleteUniqueAttributeClassification(self, args):
        self.method = "DELETE"
        self.endpoint = f'{PurviewEndpoints.ENTITY["unique_attribute"]}/{args["--typeName"]}/classification/{args["--classificationName"]}'
        self.params = {"attr:qualifiedName": args["--qualifiedName"]}

    @decorator
    def entityCreateUniqueAttributeClassifications(self, args):
        self.method = "POST"
        self.endpoint = (
            f'{PurviewEndpoints.ENTITY["unique_attribute"]}/{args["--typeName"]}/classifications'
        )
        self.payload = get_json(args, "--payloadFile")
        self.params = {"attr:qualifiedName": args["--qualifiedName"]}

    @decorator
    def entityPutUniqueAttributeClassifications(self, args):
        self.method = "PUT"
        self.endpoint = (
            f'{PurviewEndpoints.ENTITY["unique_attribute"]}/{args["--typeName"]}/classifications'
        )
        self.payload = get_json(args, "--payloadFile")
        self.params = {"attr:qualifiedName": args["--qualifiedName"]}

    @decorator
    def entityCreateOrUpdateCollection(self, args):
        collection = args["--collection"]
        self.method = "POST"
        self.endpoint = f"/catalog/api/collections/{collection}/entity"
        self.payload = get_json(args, "--payloadFile")
        self.params = PurviewEndpoints.get_api_version_params("catalog")

    @decorator
    def entityCreateOrUpdateCollectionBulk(self, args):
        collection = args["--collection"]
        self.method = "POST"
        self.endpoint = f"/catalog/api/collections/{collection}/entity/bulk"
        self.payload = get_json(args, "--payloadFile")
        self.params = PurviewEndpoints.get_api_version_params("catalog")

    @decorator
    def entityChangeCollection(self, args):
        collection = args["--collection"]
        self.method = "POST"
        self.endpoint = f"/catalog/api/collections/{collection}/entity/moveHere"
        self.payload = get_json(args, "--payloadFile")
        self.params = PurviewEndpoints.get_api_version_params("catalog")

    # === CLASSIFICATION OPERATIONS ===

    @decorator
    def entityAddClassification(self, args):
        """Associate a classification to multiple entities in bulk (Official API: Add Classification)"""
        self.method = "POST"
        self.endpoint = PurviewEndpoints.ENTITY["bulk_classification"]
        self.params = PurviewEndpoints.get_api_version_params("datamap")
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def entityBulkSetClassifications(self, args):
        """Set classifications on entities in bulk (Official API: Bulk Set Classifications)"""
        self.method = "POST"
        self.endpoint = PurviewEndpoints.ENTITY["bulk_set_classifications"]
        self.params = PurviewEndpoints.get_api_version_params("datamap")
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def entityAddClassifications(self, args):
        """Add classifications to an existing entity by GUID (Official API: Add Classifications)"""
        self.method = "POST"
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.ENTITY["classifications"], guid=args["--guid"][0]
        )
        self.params = PurviewEndpoints.get_api_version_params("datamap")
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def entityAddClassificationsByUniqueAttribute(self, args):
        """Add classification by unique attribute (Official API: Add Classifications By Unique Attribute)"""
        self.method = "POST"
        self.endpoint = (
            f'{PurviewEndpoints.ENTITY["unique_attribute"]}/{args["--typeName"]}/classifications'
        )
        self.params = {
            **PurviewEndpoints.get_api_version_params("datamap"),
            "attr:qualifiedName": args["--qualifiedName"],
        }
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def entityReadClassification(self, args):
        """Get classification for an entity by GUID (Official API: Get Classification)"""
        self.method = "GET"
        self.endpoint = (
            PurviewEndpoints.format_endpoint(
                PurviewEndpoints.ENTITY["classification"], guid=args["--guid"][0]
            )
            + f'/{args["--classificationName"]}'
        )
        self.params = PurviewEndpoints.get_api_version_params("datamap")

    @decorator
    def entityReadClassifications(self, args):
        """List classifications for an entity by GUID (Official API: Get Classifications)"""
        self.method = "GET"
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.ENTITY["classifications"], guid=args["--guid"][0]
        )
        self.params = PurviewEndpoints.get_api_version_params("datamap")

    @decorator
    def entityUpdateClassifications(self, args):
        """Update classifications on an entity by GUID (Official API: Update Classifications)"""
        self.method = "PUT"
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.ENTITY["classifications"], guid=args["--guid"][0]
        )
        self.params = PurviewEndpoints.get_api_version_params("datamap")
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def entityUpdateClassificationsByUniqueAttribute(self, args):
        """Update classification by unique attribute (Official API: Update Classifications By Unique Attribute)"""
        self.method = "PUT"
        self.endpoint = (
            f'{PurviewEndpoints.ENTITY["unique_attribute"]}/{args["--typeName"]}/classifications'
        )
        self.params = {
            **PurviewEndpoints.get_api_version_params("datamap"),
            "attr:qualifiedName": args["--qualifiedName"],
        }
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def entityDeleteClassification(self, args):
        """Remove classification from an entity by GUID (Official API: Remove Classification)"""
        self.method = "DELETE"
        self.endpoint = (
            PurviewEndpoints.format_endpoint(
                PurviewEndpoints.ENTITY["classification"], guid=args["--guid"][0]
            )
            + f'/{args["--classificationName"]}'
        )
        self.params = PurviewEndpoints.get_api_version_params("datamap")

    @decorator
    def entityDeleteClassificationByUniqueAttribute(self, args):
        """Remove classification by unique attribute (Official API: Remove Classification By Unique Attribute)"""
        self.method = "DELETE"
        self.endpoint = f'{PurviewEndpoints.ENTITY["unique_attribute"]}/{args["--typeName"]}/classification/{args["--classificationName"]}'
        self.params = {
            **PurviewEndpoints.get_api_version_params("datamap"),
            "attr:qualifiedName": args["--qualifiedName"],
        }

    # === LABEL OPERATIONS ===

    @decorator
    def entityAddLabels(self, args):
        """Add given labels to an entity by GUID (Official API: Add Label)"""
        self.method = "POST"
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.ENTITY["labels"], guid=args["--guid"][0]
        )
        self.params = PurviewEndpoints.get_api_version_params("datamap")
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def entityAddLabelsByUniqueAttribute(self, args):
        """Add labels by unique attribute (Official API: Add Labels By Unique Attribute)"""
        self.method = "POST"
        self.endpoint = f'{PurviewEndpoints.ENTITY["unique_attribute"]}/{args["--typeName"]}/labels'
        self.params = {
            **PurviewEndpoints.get_api_version_params("datamap"),
            "attr:qualifiedName": args["--qualifiedName"],
        }
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def entitySetLabels(self, args):
        """Set labels to an entity by GUID (Official API: Set Labels)"""
        self.method = "PUT"
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.ENTITY["labels"], guid=args["--guid"][0]
        )
        self.params = PurviewEndpoints.get_api_version_params("datamap")
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def entitySetLabelsByUniqueAttribute(self, args):
        """Set labels by unique attribute (Official API: Set Labels By Unique Attribute)"""
        self.method = "PUT"
        self.endpoint = f'{PurviewEndpoints.ENTITY["unique_attribute"]}/{args["--typeName"]}/labels'
        self.params = {
            **PurviewEndpoints.get_api_version_params("datamap"),
            "attr:qualifiedName": args["--qualifiedName"],
        }
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def entityRemoveLabels(self, args):
        """Remove labels from an entity by GUID (Official API: Remove Labels)"""
        self.method = "DELETE"
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.ENTITY["labels"], guid=args["--guid"][0]
        )
        self.params = PurviewEndpoints.get_api_version_params("datamap")
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def entityRemoveLabelsByUniqueAttribute(self, args):
        """Remove labels by unique attribute (Official API: Remove Labels By Unique Attribute)"""
        self.method = "DELETE"
        self.endpoint = f'{PurviewEndpoints.ENTITY["unique_attribute"]}/{args["--typeName"]}/labels'
        self.params = {
            **PurviewEndpoints.get_api_version_params("datamap"),
            "attr:qualifiedName": args["--qualifiedName"],
        }
        self.payload = get_json(args, "--payloadFile")

    # === COLLECTION OPERATIONS ===

    @decorator
    def entityMoveEntitiesToCollection(self, args):
        """Move existing entities to target collection (Official API: Move Entities To Collection)"""
        self.method = "POST"
        self.endpoint = PurviewEndpoints.ENTITY["move_to"]
        self.params = PurviewEndpoints.get_api_version_params("datamap")
        self.payload = get_json(args, "--payloadFile")

    # === BUSINESS METADATA OPERATIONS ===

    @decorator
    def entityAddOrUpdateBusinessMetadata(self, args):
        """Add or update business metadata to an entity (Official API: Add Or Update Business Metadata)"""
        guid = args["--guid"][0]
        self.method = "POST"
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.ENTITY["business_metadata"], guid=guid
        )
        self.params = {
            **PurviewEndpoints.get_api_version_params("datamap"),
            "isOverwrite": str(args.get("--isOverwrite", False)).lower(),
        }
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def entityAddOrUpdateBusinessMetadataAttributes(self, args):
        """Add or update business metadata attributes (Official API: Add Or Update Business Metadata Attributes)"""
        guid = args["--guid"][0]
        bmName = args["--bmName"]
        self.method = "POST"
        self.endpoint = f'{PurviewEndpoints.format_endpoint(PurviewEndpoints.ENTITY["business_metadata"], guid=guid)}/{bmName}'
        self.params = PurviewEndpoints.get_api_version_params("datamap")
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def entityRemoveBusinessMetadata(self, args):
        """Remove business metadata from an entity (Official API: Remove Business Metadata)"""
        guid = args["--guid"][0]
        self.method = "DELETE"
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.ENTITY["business_metadata"], guid=guid
        )
        self.params = PurviewEndpoints.get_api_version_params("datamap")
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def entityRemoveBusinessMetadataAttributes(self, args):
        """Delete business metadata attributes (Official API: Remove Business Metadata Attributes)"""
        guid = args["--guid"][0]
        bmName = args["--bmName"]
        self.method = "DELETE"
        self.endpoint = f'{PurviewEndpoints.format_endpoint(PurviewEndpoints.ENTITY["business_metadata"], guid=guid)}/{bmName}'
        self.params = PurviewEndpoints.get_api_version_params("datamap")
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def entityImportBusinessMetadata(self, args):
        """Import business metadata in bulk (Official API: Import Business Metadata)"""
        self.method = "POST"
        self.endpoint = PurviewEndpoints.ENTITY["business_metadata_import"]
        self.params = PurviewEndpoints.get_api_version_params("datamap")
        self.files = {"file": open(args["--bmFile"], "rb")}

    @decorator
    def entityGetBusinessMetadataTemplate(self, args):
        """Get sample template for business metadata (Official API: Get Sample Business Metadata Template)"""
        self.method = "GET"
        self.endpoint = PurviewEndpoints.ENTITY["business_metadata_template"]
        self.params = PurviewEndpoints.get_api_version_params("datamap")

    # === SAMPLE OPERATIONS ===

    @decorator
    def entityReadSample(self, args):
        """Get sample data for an entity (Official API: Get Sample)"""
        guid = args["--guid"][0]
        self.method = "GET"
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.ENTITY["sample"], guid=guid
        )
        self.params = PurviewEndpoints.get_api_version_params("datamap")

    # === LEGACY COMPATIBILITY METHODS (Deprecated but maintained for backward compatibility) ===

    # Collection operations (legacy)
    @decorator
    def entityCreateOrUpdateCollection(self, args):
        """Legacy: Create entity in collection (use entityMoveEntitiesToCollection instead)"""
        collection = args["--collection"]
        self.method = "POST"
        self.endpoint = f"/catalog/api/collections/{collection}/entity"
        self.payload = get_json(args, "--payloadFile")
        self.params = PurviewEndpoints.get_api_version_params("catalog")

    @decorator
    def entityCreateOrUpdateCollectionBulk(self, args):
        """Legacy: Create entities in collection bulk (use entityMoveEntitiesToCollection instead)"""
        collection = args["--collection"]
        self.method = "POST"
        self.endpoint = f"/catalog/api/collections/{collection}/entity/bulk"
        self.payload = get_json(args, "--payloadFile")
        self.params = PurviewEndpoints.get_api_version_params("catalog")

    @decorator
    def entityChangeCollection(self, args):
        """Legacy: Move entity to collection (use entityMoveEntitiesToCollection instead)"""
        collection = args["--collection"]
        self.method = "POST"
        self.endpoint = f"/catalog/api/collections/{collection}/entity/moveHere"
        self.payload = get_json(args, "--payloadFile")
        self.params = PurviewEndpoints.get_api_version_params("catalog")

    @decorator
    def entityReadAudit(self, args):
        """Get audit events for an entity by GUID (Official API: Get Audit Events)"""
        self.method = "GET"
        self.endpoint = PurviewEndpoints.ENTITY["audit"].format(guid=args["--guid"])
        self.params = PurviewEndpoints.get_api_version_params("datamap")

    def map_flat_entity_to_purview_entity(row: dict) -> dict:
        """
        Convert a flat dict (from CSV) to the nested Purview entity format.
        Only 'typeName' is top-level; all other fields go under 'attributes'.
        """
        entity = {"typeName": row.get("typeName", "DataSet"), "attributes": {}}
        for k, v in row.items():
            if k != "typeName":
                entity["attributes"][k] = v
        return entity

    # Example usage in your CSV import logic:
    # entities = [map_flat_entity_to_purview_entity(row) for row in csv_rows]

    @decorator
    def search_entities(self, search_args):
        """Search for entities using the Purview Search API."""
        # Build the request payload
        payload = {
            "keywords": search_args.get("keywords", "*"),
            "limit": search_args.get("limit", 100),
        }
        # Add filter if provided
        if "filter" in search_args and search_args["filter"]:
            payload["filter"] = search_args["filter"]
        # Use the search endpoint and correct API version
        self.method = "POST"
        self.endpoint = PurviewEndpoints.SEARCH["query"]
        self.params = PurviewEndpoints.get_api_version_params("search")
        self.payload = payload
        # Actually perform the request and return the result
        return self.send()

    def send(self):
        """Send the constructed HTTP request and return the result."""
        from .endpoint import get_data
        http_dict = {
            "app": self.app,
            "method": self.method,
            "endpoint": self.endpoint,
            "params": self.params,
            "payload": self.payload,
            "files": self.files,
            "headers": self.headers,
        }
        return get_data(http_dict)
