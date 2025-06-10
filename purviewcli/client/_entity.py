from .endpoint import Endpoint, decorator, get_json
from .endpoints import PurviewEndpoints

class Entity(Endpoint):
    def __init__(self):
        Endpoint.__init__(self)
        self.app = 'catalog'

    @decorator
    def entityCreate(self, args):
        self.method = 'POST'
        self.endpoint = PurviewEndpoints.ENTITY['base']
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def entityDeleteBulk(self, args):
        self.method = 'DELETE'
        self.headers = {'Content-Type':'application/json'}
        self.endpoint = PurviewEndpoints.ENTITY['bulk']
        self.params = {'guid': args['--guid']}

    @decorator
    def entityReadBulk(self, args):
        self.method = 'GET'
        self.endpoint = PurviewEndpoints.ENTITY['bulk']
        self.params = {'guid': args['--guid'], 'ignoreRelationships': str(args['--ignoreRelationships']).lower(), 'minExtInfo': str(args['--minExtInfo']).lower()}

    @decorator
    def entityCreateBulk(self, args):
        self.method = 'POST'
        self.endpoint = PurviewEndpoints.ENTITY['bulk']
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def entityCreateBulkClassification(self, args):
        # Associates a classification to multiple entities in bulk.
        self.method = 'POST'
        self.endpoint = PurviewEndpoints.ENTITY['bulk_classification']
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def entityCreateBulkSetClassifications(self, args):
        # Set classifications on entities in bulk (Classification -< Entities).
        self.method = 'POST'
        self.endpoint = PurviewEndpoints.ENTITY['bulk_set_classifications']
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def entityDelete(self, args):
        self.method = 'DELETE'
        self.endpoint = f'{PurviewEndpoints.ENTITY["guid"]}/{args["--guid"][0]}'

    @decorator
    def entityRead(self, args):
        self.method = 'GET'
        self.endpoint = f'{PurviewEndpoints.ENTITY["guid"]}/{args["--guid"][0]}'
        self.params = {'ignoreRelationships': str(args['--ignoreRelationships']).lower(), 'minExtInfo': str(args['--minExtInfo']).lower()}

    @decorator
    def entityPut(self, args):
        self.method = 'PUT'
        self.endpoint = f'{PurviewEndpoints.ENTITY["guid"]}/{args["--guid"][0]}'
        self.params = {'name': args['--attrName']}
        self.payload = args['--attrValue']

    @decorator
    def entityDeleteClassification(self, args):
        self.method = 'DELETE'
        self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.ENTITY['classification'], guid=args["--guid"][0]) + f'/{args["--classificationName"]}'

    @decorator
    def entityReadClassification(self, args):
        self.method = 'GET'
        self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.ENTITY['classification'], guid=args["--guid"][0]) + f'/{args["--classificationName"]}'

    @decorator
    def entityReadClassifications(self, args):
        self.method = 'GET'
        self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.ENTITY['classifications'], guid=args["--guid"][0])

    @decorator
    def entityCreateClassifications(self, args):
        self.method = 'POST'
        self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.ENTITY['classifications'], guid=args["--guid"][0])
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def entityPutClassifications(self, args):
        self.method = 'PUT'
        self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.ENTITY['classifications'], guid=args["--guid"][0])
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def entityReadHeader(self, args):
        self.method = 'GET'
        self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.ENTITY['header'], guid=args["--guid"][0])

    @decorator
    def entityReadBulkUniqueAttribute(self, args):
        self.method = 'GET'
        self.endpoint = f'{PurviewEndpoints.ENTITY["unique_attribute"]}/{args["--typeName"]}/bulk'
        self.params = {'ignoreRelationships': str(args['--ignoreRelationships']).lower(), 'minExtInfo': str(args['--minExtInfo']).lower()}
        counter = 0
        self.params = {}
        for qualifiedName in args['--qualifiedName']:
            self.params[f"attr_{str(counter)}:qualifiedName"] = qualifiedName
            counter += 1


    @decorator
    def entityReadUniqueAttribute(self, args):
        self.method = 'GET'
        self.endpoint = f'{PurviewEndpoints.ENTITY["unique_attribute"]}/{args["--typeName"]}'
        self.params = {'attr:qualifiedName': args['--qualifiedName'], 'ignoreRelationships': str(args['--ignoreRelationships']).lower(), 'minExtInfo': str(args['--minExtInfo']).lower()}

    @decorator
    def entityDeleteUniqueAttribute(self, args):
        self.method = 'DELETE'
        self.endpoint = f'{PurviewEndpoints.ENTITY["unique_attribute"]}/{args["--typeName"]}'
        self.params = { 'attr:qualifiedName': args["--qualifiedName"]}

    @decorator
    def entityPutUniqueAttribute(self, args):
        self.method = 'PUT'
        self.endpoint = f'{PurviewEndpoints.ENTITY["unique_attribute"]}/{args["--typeName"]}'
        self.payload = get_json(args, '--payloadFile')
        self.params = { 'attr:qualifiedName': args["--qualifiedName"]}

    @decorator
    def entityDeleteUniqueAttributeClassification(self, args):
        self.method = 'DELETE'
        self.endpoint = f'{PurviewEndpoints.ENTITY["unique_attribute"]}/{args["--typeName"]}/classification/{args["--classificationName"]}'
        self.params = { 'attr:qualifiedName': args["--qualifiedName"]}

    @decorator
    def entityCreateUniqueAttributeClassifications(self, args):
        self.method = 'POST'
        self.endpoint = f'{PurviewEndpoints.ENTITY["unique_attribute"]}/{args["--typeName"]}/classifications'
        self.payload = get_json(args, '--payloadFile')
        self.params = { 'attr:qualifiedName': args["--qualifiedName"]}

    @decorator
    def entityPutUniqueAttributeClassifications(self, args):
        self.method = 'PUT'
        self.endpoint = f'{PurviewEndpoints.ENTITY["unique_attribute"]}/{args["--typeName"]}/classifications'
        self.payload = get_json(args, '--payloadFile')
        self.params = { 'attr:qualifiedName': args["--qualifiedName"]}

    @decorator
    def entityCreateOrUpdateCollection(self, args):
        collection = args['--collection']
        self.method = 'POST'
        self.endpoint = f'/catalog/api/collections/{collection}/entity'
        self.payload = get_json(args, '--payloadFile')
        self.params = {'api-version':'2021-05-01-preview'}

    @decorator
    def entityCreateOrUpdateCollectionBulk(self, args):
        collection = args['--collection']
        self.method = 'POST'
        self.endpoint = f'/catalog/api/collections/{collection}/entity/bulk'
        self.payload = get_json(args, '--payloadFile')
        self.params = {'api-version':'2021-05-01-preview'}

    @decorator
    def entityChangeCollection(self, args):
        collection = args['--collection']
        self.method = 'POST'
        self.endpoint = f'/catalog/api/collections/{collection}/entity/moveHere'
        self.payload = get_json(args, '--payloadFile')
        self.params = {'api-version':'2021-05-01-preview'}

    # Business Metadata
    @decorator
    def entityImportBusinessMetadata(self, args):
        self.method = 'POST'
        self.endpoint = f'{PurviewEndpoints.DATAMAP_BASE}/{PurviewEndpoints.ATLAS_V2}/entity/businessmetadata/import'
        self.params = {'api-version':'2022-03-01-preview'}
        self.files = {'file': open(args["--bmFile"], 'rb')}

    @decorator
    def entityGetBusinessMetadataTemplate(self, args):
        self.method = 'GET'
        self.endpoint = f'{PurviewEndpoints.DATAMAP_BASE}/{PurviewEndpoints.ATLAS_V2}/entity/businessmetadata/import/template'
        self.params = {'api-version':'2022-03-01-preview'}

    @decorator
    def entityAddOrUpdateBusinessMetadata(self, args):
        guid = args['--guid'][0]
        isOverwrite = args['--isOverwrite']
        self.method = 'POST'
        self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.ENTITY['business_metadata'], guid=guid)
        self.params = {
            'api-version':'2022-03-01-preview',
            'isOverwrite': isOverwrite
        }
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def entityDeleteBusinessMetadata(self, args):
        guid = args['--guid'][0]
        self.method = 'DELETE'
        self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.ENTITY['business_metadata'], guid=guid)
        self.params = {'api-version':'2022-03-01-preview'}
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def entityAddOrUpdateBusinessAttribute(self, args):
        guid = args['--guid'][0]
        bmName = args['--bmName']
        self.method = 'POST'
        self.endpoint = f'{PurviewEndpoints.format_endpoint(PurviewEndpoints.ENTITY["business_metadata"], guid=guid)}/{bmName}'
        self.params = {'api-version':'2022-03-01-preview'}
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def entityDeleteBusinessAttribute(self, args):
        guid = args['--guid'][0]
        bmName = args['--bmName']
        self.method = 'DELETE'
        self.endpoint = f'{PurviewEndpoints.format_endpoint(PurviewEndpoints.ENTITY["business_metadata"], guid=guid)}/{bmName}'
        self.params = {'api-version':'2022-03-01-preview'}
        self.payload = get_json(args, '--payloadFile')

    # Labels
    @decorator
    def entityAddLabels(self, args):
        guid = args['--guid'][0]
        self.method = 'PUT'
        self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.ENTITY['labels'], guid=guid)
        self.params = {'api-version':'2022-03-01-preview'}
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def entityDeleteLabels(self, args):
        guid = args['--guid'][0]
        self.method = 'DELETE'
        self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.ENTITY['labels'], guid=guid)
        self.params = {'api-version':'2022-03-01-preview'}
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def entitySetLabels(self, args):
        guid = args['--guid'][0]
        self.method = 'POST'
        self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.ENTITY['labels'], guid=guid)
        self.params = {'api-version':'2022-03-01-preview'}
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def entityAddLabelsByUniqueAttribute(self, args):
        typeName = args['--typeName']
        qualifiedName = args['--qualifiedName']
        self.method = 'PUT'
        self.endpoint = f'{PurviewEndpoints.ENTITY["unique_attribute"]}/{typeName}/labels'
        self.params = {
            'api-version':'2022-03-01-preview',
            'attr:qualifiedName': qualifiedName
        }
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def entityDeleteLabelsByUniqueAttribute(self, args):
        typeName = args['--typeName']
        qualifiedName = args['--qualifiedName']
        self.method = 'DELETE'
        self.endpoint = f'{PurviewEndpoints.ENTITY["unique_attribute"]}/{typeName}/labels'
        self.params = {
            'api-version':'2022-03-01-preview',
            'attr:qualifiedName': qualifiedName
        }
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def entitySetLabelsByUniqueAttribute(self, args):
        typeName = args['--typeName']
        qualifiedName = args['--qualifiedName']
        self.method = 'POST'
        self.endpoint = f'{PurviewEndpoints.ENTITY["unique_attribute"]}/{typeName}/labels'
        self.params = {
            'api-version':'2022-03-01-preview',
            'attr:qualifiedName': qualifiedName
        }
        self.payload = get_json(args, '--payloadFile')