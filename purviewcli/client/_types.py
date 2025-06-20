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
        self.endpoint = f'{ENDPOINTS["types"]["classificationdef"]}/{typeDefKey}/{typeDefVal}'

    @decorator
    def typesReadEntityDef(self, args):
        self.method = "GET"
        typeDefKey = "guid" if args["--name"] is None else "name"
        typeDefVal = args["--guid"] if args["--name"] is None else args["--name"]
        self.endpoint = f'{ENDPOINTS["types"]["entitydef"]}/{typeDefKey}/{typeDefVal}'

    @decorator
    def typesReadEnumDef(self, args):
        self.method = "GET"
        typeDefKey = "guid" if args["--name"] is None else "name"
        typeDefVal = args["--guid"] if args["--name"] is None else args["--name"]
        self.endpoint = f'{ENDPOINTS["types"]["enumdef"]}/{typeDefKey}/{typeDefVal}'

    @decorator
    def typesReadRelationshipDef(self, args):
        self.method = "GET"
        typeDefKey = "guid" if args["--name"] is None else "name"
        typeDefVal = args["--guid"] if args["--name"] is None else args["--name"]
        self.endpoint = f'{ENDPOINTS["types"]["relationshipdef"]}/{typeDefKey}/{typeDefVal}'

    @decorator
    def typesReadStructDef(self, args):
        self.method = "GET"
        typeDefKey = "guid" if args["--name"] is None else "name"
        typeDefVal = args["--guid"] if args["--name"] is None else args["--name"]
        self.endpoint = f'{ENDPOINTS["types"]["structdef"]}/{typeDefKey}/{typeDefVal}'

    @decorator
    def typesReadTypeDef(self, args):
        self.method = "GET"
        typeDefKey = "guid" if args["--name"] is None else "name"
        typeDefVal = args["--guid"] if args["--name"] is None else args["--name"]
        self.endpoint = f'{ENDPOINTS["types"]["typedef"]}/{typeDefKey}/{typeDefVal}'

    @decorator
    def typesReadBusinessMetadataDef(self, args):
        self.method = "GET"
        typeDefKey = "guid" if args["--name"] is None else "name"
        typeDefVal = args["--guid"] if args["--name"] is None else args["--name"]
        self.endpoint = f'{ENDPOINTS["types"]["businessmetadatadef"]}/{typeDefKey}/{typeDefVal}'

    @decorator
    def typesReadTypeDefs(self, args):
        self.method = "GET"
        self.endpoint = f'{ENDPOINTS["types"]["base"]}/typedefs'
        self.params = {"includeTermTemplate": str(args["--includeTermTemplate"]).lower()}
        self.params["type"] = args["--type"] if args["--type"] else None

    @decorator
    def typesReadTypeDefsHeaders(self, args):
        self.method = "GET"
        self.endpoint = f'{ENDPOINTS["types"]["base"]}/typedefs/headers'
        self.params = {"includeTermTemplate": str(args["--includeTermTemplate"]).lower()}
        self.params["type"] = args["--type"] if args["--type"] else None

    @decorator
    def typesDeleteTypeDef(self, args):
        self.method = "DELETE"
        self.endpoint = f'{ENDPOINTS["types"]["typedef"]}/name/{args["--name"]}'

    @decorator
    def typesDeleteTypeDefs(self, args):
        self.method = "DELETE"
        self.endpoint = f'{ENDPOINTS["types"]["base"]}/typedefs'
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def typesCreateTypeDefs(self, args):
        self.method = "POST"
        self.endpoint = f'{ENDPOINTS["types"]["base"]}/typedefs'
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def typesPutTypeDefs(self, args):
        self.method = "PUT"
        self.endpoint = f'{ENDPOINTS["types"]["base"]}/typedefs'
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def typesReadStatistics(self, args):
        self.method = "GET"
        self.endpoint = f'{ENDPOINTS["types"]["base"]}/statistics' @ decorator

    def createBusinessMetadataDef(self, args):
        """Create a business metadata definition via POST."""
        self.method = "POST"
        self.endpoint = ENDPOINTS["types"]["list"]
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def updateBusinessMetadataDef(self, args):
        """Update a business metadata definition via PUT."""
        self.method = "PUT"
        self.endpoint = ENDPOINTS["types"]["list"]
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def deleteBusinessMetadataDef(self, args):
        """Delete a business metadata definition by name via DELETE."""
        self.method = "DELETE"
        self.endpoint = (
            f"{ENDPOINTS['types']['get_business_metadata_def_by_name']}/{args['--name']}"
        )

    @decorator
    def createTermTemplateDef(self, args):
        """Create a term template definition via POST."""
        self.method = "POST"
        self.endpoint = ENDPOINTS["types"]["get_term_template_def_by_name"]
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def updateTermTemplateDef(self, args):
        """Update a term template definition via PUT."""
        self.method = "PUT"
        self.endpoint = ENDPOINTS["types"]["get_term_template_def_by_name"]
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def deleteTermTemplateDef(self, args):
        """Delete a term template definition by name via DELETE."""
        self.method = "DELETE"
        self.endpoint = f"{ENDPOINTS['types']['get_term_template_def_by_name']}/{args['--name']}"

    # NOT SUPPORTED IN Microsoft Purview
    # @decorator
    # def typesReadBusinessmetadataDef(self, args):
    #     self.method = 'GET'
    #     typeDefKey = 'guid' if args['--name'] is None else 'name'
    #     typeDefVal = args['--guid'] if args['--name'] is None else args['--name']
    #     self.endpoint = f'/api/atlas/v2/types/businessmetadatadef/{typeDefKey}/{typeDefVal}'
