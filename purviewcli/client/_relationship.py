from .endpoint import Endpoint, decorator, get_json
from .endpoints import PurviewEndpoints

class Relationship(Endpoint):
    def __init__(self):
        Endpoint.__init__(self)
        self.app = 'catalog'

    @decorator
    def relationshipCreate(self, args):
        self.method = 'POST'
        self.endpoint = PurviewEndpoints.RELATIONSHIP['base']
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def relationshipPut(self, args):
        self.method = 'PUT'
        self.endpoint = PurviewEndpoints.RELATIONSHIP['base']
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def relationshipDelete(self, args):
        self.method = 'DELETE'
        self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.RELATIONSHIP['guid'], guid=args["--guid"])

    @decorator
    def relationshipRead(self, args):
        self.method = 'GET'
        self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.RELATIONSHIP['guid'], guid=args["--guid"])
        self.params = {'extendedInfo': str(args["--extendedInfo"]).lower()}
