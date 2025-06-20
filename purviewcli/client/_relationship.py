from .endpoint import Endpoint, decorator, get_json
from .endpoints import ENDPOINTS, DATAMAP_API_VERSION

class Relationship(Endpoint):
    def __init__(self):
        Endpoint.__init__(self)
        self.app = 'catalog'

    @decorator
    def relationshipCreate(self, args):
        self.method = 'POST'
        self.endpoint = ENDPOINTS['relationship']['base']
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def relationshipPut(self, args):
        self.method = 'PUT'
        self.endpoint = ENDPOINTS['relationship']['base']
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def relationshipDelete(self, args):
        self.method = 'DELETE'
        self.endpoint = ENDPOINTS['relationship']['guid'].format(guid=args["--guid"])

    @decorator
    def relationshipRead(self, args):
        self.method = 'GET'
        self.endpoint = ENDPOINTS['relationship']['guid'].format(guid=args["--guid"])
        self.params = {'extendedInfo': str(args["--extendedInfo"]).lower()}
