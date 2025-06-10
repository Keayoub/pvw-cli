from .endpoint import Endpoint, decorator, get_json
from .endpoints import PurviewEndpoints

class Glossary(Endpoint):
    def __init__(self):
        Endpoint.__init__(self)
        self.app = 'catalog'

    @decorator
    def glossaryRead(self, args):
        self.method = 'GET'
        if args["--glossaryGuid"] is None:
            self.endpoint = PurviewEndpoints.GLOSSARY['base']
        else:
            self.endpoint = f'{PurviewEndpoints.GLOSSARY["base"]}/{args["--glossaryGuid"]}'
        self.params = {'limit': args['--limit'], 'offset': args['--offset'], 'sort': args['--sort'], 'ignoreTermsAndCategories': args['--ignoreTermsAndCategories']}

    @decorator
    def glossaryCreate(self, args):
        self.method = 'POST'
        self.endpoint = PurviewEndpoints.GLOSSARY['base']
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def glossaryCreateCategories(self, args):
        self.method = 'POST'
        self.endpoint = PurviewEndpoints.GLOSSARY['categories']
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def glossaryCreateCategory(self, args):
        self.method = 'POST'
        self.endpoint = PurviewEndpoints.GLOSSARY['category']
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def glossaryDeleteCategory(self, args):
        self.method = 'DELETE'
        self.endpoint = f'{PurviewEndpoints.GLOSSARY["category"]}/{args["--categoryGuid"]}'

    @decorator
    def glossaryReadCategory(self, args):
        self.method = 'GET'
        self.endpoint = f'{PurviewEndpoints.GLOSSARY["category"]}/{args["--categoryGuid"]}'
        self.params = {'limit': args['--limit'], 'offset': args['--offset'], 'sort': args['--sort']}

    @decorator
    def glossaryPutCategory(self, args):
        self.method = 'PUT'
        self.endpoint = f'{PurviewEndpoints.GLOSSARY["category"]}/{args["--categoryGuid"]}'
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def glossaryPutCategoryPartial(self, args):
        self.method = 'PUT'
        self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.GLOSSARY['category_partial'], categoryGuid=args["--categoryGuid"])
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def glossaryReadCategoryRelated(self, args):
        self.method = 'GET'
        self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.GLOSSARY['category_related'], categoryGuid=args["--categoryGuid"])

    @decorator
    def glossaryReadCategoryTerms(self, args):
        self.method = 'GET'
        self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.GLOSSARY['category_terms'], categoryGuid=args["--categoryGuid"])
        self.params = {'limit': args['--limit'], 'offset': args['--offset'], 'sort': args['--sort']}

    @decorator
    def glossaryCreateTerm(self, args):
        self.method = 'POST'
        self.endpoint = PurviewEndpoints.GLOSSARY['term']
        self.payload = get_json(args, '--payloadFile')
        self.params = {'includeTermHierarchy': args['--includeTermHierarchy']}

    @decorator
    def glossaryDeleteTerm(self, args):
        self.method = 'DELETE'
        self.endpoint = f'{PurviewEndpoints.GLOSSARY["term"]}/{args["--termGuid"][0]}'

    @decorator
    def glossaryReadTerm(self, args):
        self.method = 'GET'
        self.endpoint = f'{PurviewEndpoints.GLOSSARY["term"]}/{args["--termGuid"][0]}'
        self.params = {'includeTermHierarchy': args['--includeTermHierarchy']}

    @decorator
    def glossaryPutTerm(self, args):
        self.method = 'PUT'
        self.endpoint = f'{PurviewEndpoints.GLOSSARY["term"]}/{args["--termGuid"][0]}'
        self.params = {'includeTermHierarchy': args['--includeTermHierarchy']}
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def glossaryPutTermPartial(self, args):
        self.method = 'PUT'
        self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.GLOSSARY['term_partial'], termGuid=args["--termGuid"][0])
        self.params = {'includeTermHierarchy': args['--includeTermHierarchy']}
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def glossaryCreateTerms(self, args):
        self.method = 'POST'
        self.endpoint = PurviewEndpoints.GLOSSARY['terms']
        self.payload = get_json(args, '--payloadFile')
        self.params = {'includeTermHierarchy': args['--includeTermHierarchy']}

    @decorator
    def glossaryDeleteTermsAssignedEntities(self, args):
        self.method = 'DELETE'
        self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.GLOSSARY['term_assigned_entities'], termGuid=args["--termGuid"][0])
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def glossaryReadTermsAssignedEntities(self, args):
        self.method = 'GET'
        self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.GLOSSARY['term_assigned_entities'], termGuid=args["--termGuid"][0])
        self.params = {'limit': args['--limit'], 'offset': args['--offset'], 'sort': args['--sort']}

    @decorator
    def glossaryCreateTermsAssignedEntities(self, args):
        self.method = 'POST'
        self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.GLOSSARY['term_assigned_entities'], termGuid=args["--termGuid"][0])
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def glossaryPutTermsAssignedEntities(self, args):
        self.method = 'PUT'
        self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.GLOSSARY['term_assigned_entities'], termGuid=args["--termGuid"][0])
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def glossaryReadTermsRelated(self, args):
        self.method = 'GET'
        self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.GLOSSARY['term_related'], termGuid=args["--termGuid"][0])
        self.params = {'limit': args['--limit'], 'offset': args['--offset'], 'sort': args['--sort']}

    @decorator
    def glossaryDelete(self, args):
        self.method = 'DELETE'
        self.endpoint = f'{PurviewEndpoints.GLOSSARY["base"]}/{args["--glossaryGuid"]}'

    @decorator
    def glossaryPut(self, args):
        self.method = 'PUT'
        self.endpoint = f'{PurviewEndpoints.GLOSSARY["base"]}/{args["--glossaryGuid"]}'
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def glossaryReadCategories(self, args):
        self.method = 'GET'
        self.endpoint = f'{PurviewEndpoints.GLOSSARY["base"]}/{args["--glossaryGuid"]}/categories'
        self.params = {'limit': args['--limit'], 'offset': args['--offset'], 'sort': args['--sort']}

    @decorator
    def glossaryReadCategoriesHeaders(self, args):
        self.method = 'GET'
        self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.GLOSSARY['categories_headers'], glossaryGuid=args["--glossaryGuid"])
        self.params = {'limit': args['--limit'], 'offset': args['--offset'], 'sort': args['--sort']}

    @decorator
    def glossaryReadDetailed(self, args):
        self.method = 'GET'
        self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.GLOSSARY['detailed'], glossaryGuid=args["--glossaryGuid"])
        self.params = {'includeTermHierarchy': args['--includeTermHierarchy']}

    @decorator
    def glossaryPutPartial(self, args):
        self.method = 'PUT'
        self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.GLOSSARY['partial'], glossaryGuid=args["--glossaryGuid"])
        self.payload = get_json(args, '--payloadFile')
        self.params = {'includeTermHierarchy': args['--includeTermHierarchy']}

    @decorator
    def glossaryReadTerms(self, args):
        glossaryName = 'Glossary'
        self.method = 'GET'
        if args['--glossaryGuid']:
            self.endpoint = f'{PurviewEndpoints.GLOSSARY["base"]}/{args["--glossaryGuid"]}/terms'
        else:
            self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.GLOSSARY['terms_import_by_name'], glossaryName=glossaryName).replace('/terms/import', '/terms')
        self.params = {'limit': args['--limit'], 'offset': args['--offset'], 'sort': args['--sort'], 'extInfo': args['--extInfo'], 'includeTermHierarchy': args['--includeTermHierarchy'], 'api-version': '2021-05-01-preview'}

    @decorator
    def glossaryReadTermsHeaders(self, args):
        self.method = 'GET'
        self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.GLOSSARY['terms_headers'], glossaryGuid=args["--glossaryGuid"])
        self.params = {'limit': args['--limit'], 'offset': args['--offset'], 'sort': args['--sort']}

    @decorator
    def glossaryCreateTermsExport(self, args):
        self.method = 'POST'
        self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.GLOSSARY['terms_export'], glossaryGuid=args["--glossaryGuid"])
        self.payload = args['--termGuid']
        self.params = {
            'api-version': '2021-05-01-preview',
            'includeTermHierarchy': args['--includeTermHierarchy']
            }

    @decorator
    def glossaryCreateTermsImport(self, args):
        glossaryName = 'Glossary'
        self.method = 'POST'
        if args['--glossaryGuid']:
            self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.GLOSSARY['terms_import'], glossaryGuid=args["--glossaryGuid"])
        else:
            self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.GLOSSARY['terms_import_by_name'], glossaryName=glossaryName)
        self.files = {'file': open(args["--glossaryFile"], 'rb')}
        self.params = {
            "api-version": "2021-05-01-preview",
            'includeTermHierarchy': args['--includeTermHierarchy']
        }
        
    @decorator
    def glossaryReadTermsImport(self, args):
        self.method = 'GET'
        self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.GLOSSARY['terms_import_operation'], operationGuid=args["--operationGuid"])
        self.params = {'api-version': '2021-05-01-preview'}


    # NOT SUPPORTED IN AZURE PURVIEW
    # @decorator
    # def glossaryCreateTemplate(self, args):
    #     self.method = 'POST'
    #     self.endpoint = '/api/atlas/v2/glossary/import'
    #     self.payload = get_json(args, '--payloadFile')

    # NOT SUPPORTED IN AZURE PURVIEW
    # @decorator
    # def glossaryReadTemplate(self, args):
    #     self.method = 'GET'
    #     self.endpoint = '/api/atlas/v2/glossary/import/template'