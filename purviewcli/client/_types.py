from .endpoint import Endpoint, decorator, get_json
from .endpoints import PurviewEndpoints

class Types(Endpoint):
    def __init__(self):
        Endpoint.__init__(self)
        self.app = 'catalog'

    @decorator
    def typesReadTermTemplateDef(self, args):
        self.method = 'GET'
        typeDefKey = 'guid' if args['--name'] is None else 'name'
        typeDefVal = args['--guid'] if args['--name'] is None else args['--name']
        self.endpoint = f'/catalog/api/types/termtemplatedef/{typeDefKey}/{typeDefVal}'
        self.params = {'api-version': '2021-05-01-preview'}

    @decorator
    def typesReadClassificationDef(self, args):
        self.method = 'GET'
        typeDefKey = 'guid' if args['--name'] is None else 'name'
        typeDefVal = args['--guid'] if args['--name'] is None else args['--name']
        self.endpoint = f'{PurviewEndpoints.TYPES["classificationdef"]}/{typeDefKey}/{typeDefVal}'

    @decorator
    def typesReadEntityDef(self, args):
        self.method = 'GET'
        typeDefKey = 'guid' if args['--name'] is None else 'name'
        typeDefVal = args['--guid'] if args['--name'] is None else args['--name']
        self.endpoint = f'{PurviewEndpoints.TYPES["entitydef"]}/{typeDefKey}/{typeDefVal}'

    @decorator
    def typesReadEnumDef(self, args):
        self.method = 'GET'
        typeDefKey = 'guid' if args['--name'] is None else 'name'
        typeDefVal = args['--guid'] if args['--name'] is None else args['--name']
        self.endpoint = f'{PurviewEndpoints.TYPES["enumdef"]}/{typeDefKey}/{typeDefVal}'

    @decorator
    def typesReadRelationshipDef(self, args):
        self.method = 'GET'
        typeDefKey = 'guid' if args['--name'] is None else 'name'
        typeDefVal = args['--guid'] if args['--name'] is None else args['--name']
        self.endpoint = f'{PurviewEndpoints.TYPES["relationshipdef"]}/{typeDefKey}/{typeDefVal}'

    @decorator
    def typesReadStructDef(self, args):
        self.method = 'GET'
        typeDefKey = 'guid' if args['--name'] is None else 'name'
        typeDefVal = args['--guid'] if args['--name'] is None else args['--name']
        self.endpoint = f'{PurviewEndpoints.TYPES["structdef"]}/{typeDefKey}/{typeDefVal}'

    @decorator
    def typesReadTypeDef(self, args):
        self.method = 'GET'
        typeDefKey = 'guid' if args['--name'] is None else 'name'
        typeDefVal = args['--guid'] if args['--name'] is None else args['--name']
        self.endpoint = f'{PurviewEndpoints.TYPES["typedef"]}/{typeDefKey}/{typeDefVal}'

    @decorator
    def typesReadBusinessMetadataDef(self, args):
        self.method = 'GET'
        typeDefKey = 'guid' if args['--name'] is None else 'name'
        typeDefVal = args['--guid'] if args['--name'] is None else args['--name']
        self.endpoint = f'{PurviewEndpoints.TYPES["businessmetadatadef"]}/{typeDefKey}/{typeDefVal}'

    @decorator
    def typesReadTypeDefs(self, args):
        self.method = 'GET'
        self.endpoint = f'{PurviewEndpoints.TYPES["base"]}/typedefs'
        self.params = {'includeTermTemplate': str(args["--includeTermTemplate"]).lower()}
        self.params['type'] = args["--type"] if args["--type"] else None

    @decorator
    def typesReadTypeDefsHeaders(self, args):
      self.method = 'GET'
      self.endpoint = f'{PurviewEndpoints.TYPES["base"]}/typedefs/headers'
      self.params = {'includeTermTemplate': str(args["--includeTermTemplate"]).lower()}
      self.params['type'] = args["--type"] if args["--type"] else None

    @decorator
    def typesDeleteTypeDef(self, args):
        self.method = 'DELETE'
        self.endpoint = f'{PurviewEndpoints.TYPES["typedef"]}/name/{args["--name"]}'

    @decorator
    def typesDeleteTypeDefs(self, args):
        self.method = 'DELETE'
        self.endpoint = f'{PurviewEndpoints.TYPES["base"]}/typedefs'
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def typesCreateTypeDefs(self, args):
        self.method = 'POST'
        self.endpoint = f'{PurviewEndpoints.TYPES["base"]}/typedefs'
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def typesPutTypeDefs(self, args):
        self.method = 'PUT'
        self.endpoint = f'{PurviewEndpoints.TYPES["base"]}/typedefs'
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def typesReadStatistics(self, args):
        self.method = 'GET'
        self.endpoint = f'{PurviewEndpoints.TYPES["base"]}/statistics'

    # NOT SUPPORTED IN AZURE PURVIEW
    # @decorator
    # def typesReadBusinessmetadataDef(self, args):
    #     self.method = 'GET'
    #     typeDefKey = 'guid' if args['--name'] is None else 'name'
    #     typeDefVal = args['--guid'] if args['--name'] is None else args['--name']
    #     self.endpoint = f'/api/atlas/v2/types/businessmetadatadef/{typeDefKey}/{typeDefVal}'