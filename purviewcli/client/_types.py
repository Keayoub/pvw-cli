from .endpoint import Endpoint, decorator, get_json
from .endpoints import ENDPOINTS, DATAMAP_API_VERSION, format_endpoint, get_api_version_params
import json


class Types(Endpoint):
    def __init__(self):
        Endpoint.__init__(self)
        self.app = "catalog"

    @decorator
    def typesReadTermTemplateDef(self, args):
        self.method = "GET"
        typeDefKey = "guid" if args["--name"] is None else "name"
        typeDefVal = args["--guid"] if args["--name"] is None else args["--name"]
        self.endpoint = f"/catalog/api/types/termtemplatedef/{typeDefKey}/{typeDefVal}"
        self.params = get_api_version_params("datamap")

    @decorator
    def typesReadClassificationDef(self, args):
        self.method = "GET"
        typeDefKey = "guid" if args["--name"] is None else "name"
        typeDefVal = args["--guid"] if args["--name"] is None else args["--name"]
        # Use format_endpoint to construct the proper URL
        if typeDefKey == "guid":
            self.endpoint = format_endpoint(
                ENDPOINTS["types"]["get_classification_def_by_guid"], guid=typeDefVal
            )
        else:
            self.endpoint = format_endpoint(
                ENDPOINTS["types"]["get_classification_def_by_name"], name=typeDefVal
            )
        self.params = get_api_version_params("datamap")

    @decorator
    def typesReadEntityDef(self, args):
        self.method = "GET"
        typeDefKey = "guid" if args["--name"] is None else "name"
        typeDefVal = args["--guid"] if args["--name"] is None else args["--name"]
        # Use format_endpoint to construct the proper URL
        if typeDefKey == "guid":
            self.endpoint = format_endpoint(
                ENDPOINTS["types"]["get_entity_def_by_guid"], guid=typeDefVal
            )
        else:
            self.endpoint = format_endpoint(
                ENDPOINTS["types"]["get_entity_def_by_name"], name=typeDefVal
            )
        self.params = get_api_version_params("datamap")

    @decorator
    def typesReadEnumDef(self, args):
        self.method = "GET"
        typeDefKey = "guid" if args["--name"] is None else "name"
        typeDefVal = args["--guid"] if args["--name"] is None else args["--name"]
        # Use format_endpoint to construct the proper URL
        if typeDefKey == "guid":
            self.endpoint = format_endpoint(
                ENDPOINTS["types"]["get_enum_def_by_guid"], guid=typeDefVal
            )
        else:
            self.endpoint = format_endpoint(
                ENDPOINTS["types"]["get_enum_def_by_name"], name=typeDefVal
            )
        self.params = get_api_version_params("datamap")

    @decorator
    def typesReadRelationshipDef(self, args):
        self.method = "GET"
        typeDefKey = "guid" if args["--name"] is None else "name"
        typeDefVal = args["--guid"] if args["--name"] is None else args["--name"]
        # Use format_endpoint to construct the proper URL
        if typeDefKey == "guid":
            self.endpoint = format_endpoint(
                ENDPOINTS["types"]["get_relationship_def_by_guid"], guid=typeDefVal
            )
        else:
            self.endpoint = format_endpoint(
                ENDPOINTS["types"]["get_relationship_def_by_name"], name=typeDefVal
            )
        self.params = get_api_version_params("datamap")

    @decorator
    def typesReadStructDef(self, args):
        self.method = "GET"
        typeDefKey = "guid" if args["--name"] is None else "name"
        typeDefVal = args["--guid"] if args["--name"] is None else args["--name"]
        # Use format_endpoint to construct the proper URL
        if typeDefKey == "guid":
            self.endpoint = format_endpoint(
                ENDPOINTS["types"]["get_struct_def_by_guid"], guid=typeDefVal
            )
        else:
            self.endpoint = format_endpoint(
                ENDPOINTS["types"]["get_struct_def_by_name"], name=typeDefVal
            )
        self.params = get_api_version_params("datamap")

    @decorator
    def typesReadBusinessMetadataDef(self, args):
        self.method = "GET"
        typeDefKey = "guid" if args["--name"] is None else "name"
        typeDefVal = args["--guid"] if args["--name"] is None else args["--name"]
        # Use format_endpoint to construct the proper URL
        if typeDefKey == "guid":
            self.endpoint = format_endpoint(
                ENDPOINTS["types"]["get_business_metadata_def_by_guid"], guid=typeDefVal
            )
        else:
            self.endpoint = format_endpoint(
                ENDPOINTS["types"]["get_business_metadata_def_by_name"], name=typeDefVal
            )
        self.params = get_api_version_params("datamap")

    @decorator
    def typesReadTypeDefs(self, args):
        self.method = "GET"
        self.endpoint = ENDPOINTS["types"]["list"]
        self.params = {
            "includeTermTemplate": str(args["--includeTermTemplate"]).lower(),
            **get_api_version_params("datamap"),
        }
        if args["--type"]:
            self.params["type"] = args["--type"]

    @decorator
    def typesReadTypeDefsHeaders(self, args):
        self.method = "GET"
        self.endpoint = ENDPOINTS["types"]["list_headers"]
        self.params = {
            "includeTermTemplate": str(args["--includeTermTemplate"]).lower(),
            **get_api_version_params("datamap"),
        }
        if args["--type"]:
            self.params["type"] = args["--type"]

    @decorator
    def typesDeleteTypeDef(self, args):
        self.method = "DELETE"
        self.endpoint = format_endpoint(ENDPOINTS["types"]["delete"], name=args["--name"])
        self.params = get_api_version_params("datamap")

    @decorator
    def typesDeleteTypeDefs(self, args):
        self.method = "DELETE"
        self.endpoint = ENDPOINTS["types"]["bulk_delete"]
        self.payload = get_json(args, "--payloadFile")
        self.params = get_api_version_params("datamap")

    @decorator
    def typesCreateTypeDefs(self, args):
        self.method = "POST"
        self.endpoint = ENDPOINTS["types"]["bulk_create"]
        self.payload = get_json(args, "--payloadFile")
        self.params = get_api_version_params("datamap")

    @decorator
    def typesPutTypeDefs(self, args):
        self.method = "PUT"
        self.endpoint = ENDPOINTS["types"]["bulk_update"]
        self.payload = get_json(args, "--payloadFile")
        self.params = get_api_version_params("datamap")

    @decorator
    def typesReadStatistics(self, args):
        self.method = "GET"
        # Statistics endpoint is not available in 2024-03-01-preview, use list with count
        self.endpoint = ENDPOINTS["types"]["list"]
        self.params = {"includeStatistics": "true", **get_api_version_params("datamap")}

    @decorator
    def createBusinessMetadataDef(self, args):
        """Create a business metadata definition via POST."""
        self.method = "POST"
        self.endpoint = ENDPOINTS["types"]["bulk_create"]
        self.payload = get_json(args, "--payloadFile")
        self.params = get_api_version_params("datamap")

    @decorator
    def updateBusinessMetadataDef(self, args):
        """Update a business metadata definition via PUT."""
        self.method = "PUT"
        self.endpoint = ENDPOINTS["types"]["bulk_update"]
        self.payload = get_json(args, "--payloadFile")
        self.params = get_api_version_params("datamap")

    @decorator
    def deleteBusinessMetadataDef(self, args):
        """Delete a business metadata definition by name via DELETE."""
        self.method = "DELETE"
        self.endpoint = format_endpoint(
            ENDPOINTS["types"]["get_business_metadata_def_by_name"], name=args["--name"]
        )
        self.params = get_api_version_params("datamap")

    @decorator
    def createTermTemplateDef(self, args):
        """Create a term template definition via POST."""
        self.method = "POST"
        # Term templates use their own endpoint
        self.endpoint = "/datamap/api/types/termtemplatedef"
        self.payload = get_json(args, "--payloadFile")
        self.params = get_api_version_params("datamap")

    @decorator
    def updateTermTemplateDef(self, args):
        """Update a term template definition via PUT."""
        self.method = "PUT"
        # Term templates use their own endpoint
        self.endpoint = "/datamap/api/types/termtemplatedef"
        self.payload = get_json(args, "--payloadFile")
        self.params = get_api_version_params("datamap")

    @decorator
    def deleteTermTemplateDef(self, args):
        """Delete a term template definition by name via DELETE."""
        self.method = "DELETE"
        self.endpoint = format_endpoint(
            ENDPOINTS["types"]["get_term_template_def_by_name"], name=args["--name"]
        )
        self.params = get_api_version_params("datamap")

    # NOT SUPPORTED IN Microsoft Purview
    # @decorator
    # def typesReadBusinessmetadataDef(self, args):
    #     self.method = 'GET'
    #     typeDefKey = 'guid' if args['--name'] is None else 'name'
    #     typeDefVal = args['--guid'] if args['--name'] is None else args['--name']
    #     self.endpoint = f'{ENDPOINTS["types"]["businessmetadatadef"]}/{typeDefKey}/{typeDefVal}'
