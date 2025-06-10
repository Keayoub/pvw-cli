from .endpoint import Endpoint, decorator, get_json
from .endpoints import PurviewEndpoints

class Search(Endpoint):
    def __init__(self):
        Endpoint.__init__(self)
        self.app = 'catalog'

    @decorator
    def searchQuery(self, args):
        self.method = 'POST'
        self.endpoint = PurviewEndpoints.SEARCH['query']
        self.params = PurviewEndpoints.get_api_version_params('search')
        self.payload = {
            'keywords': args['--keywords'],
            'limit': args['--limit'],
            'offset': args['--offset'],
            'filter': get_json(args,'--filterFile'),
            'facets': get_json(args,'--facets-file')
        }
    
    @decorator
    def searchAutoComplete(self, args):
        self.method = 'POST'
        self.endpoint = PurviewEndpoints.SEARCH['autocomplete']
        self.params = PurviewEndpoints.get_api_version_params('search')
        self.payload = {
            "keywords": args['--keywords'],
            "filter": get_json(args,'--filterFile'),
            "limit": args['--limit']
        }

    @decorator
    def searchSuggest(self, args):
        self.method = 'POST'
        self.endpoint = PurviewEndpoints.SEARCH['suggest']
        self.params = PurviewEndpoints.get_api_version_params('search')
        self.payload = {
            "keywords": args['--keywords'],
            "filter": get_json(args,'--filterFile'),
            "limit": args['--limit']
        }
    
    @decorator
    def searchBrowse(self, args):
        self.method = 'POST'
        self.endpoint = PurviewEndpoints.SEARCH['browse']
        self.params = PurviewEndpoints.get_api_version_params('search')
        self.payload = {
            "entityType": args['--entityType'],
            "path": args['--path'],
            "limit": args['--limit'],
            'offset': args['--offset']

        }
