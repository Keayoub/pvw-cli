from .endpoint import Endpoint, decorator, get_json
from .endpoints import PurviewEndpoints

class Share(Endpoint):
    def __init__(self):
        Endpoint.__init__(self)
        self.app = 'share'

    # Accepted Sent Shares
    @decorator
    def shareListAcceptedShares(self, args):
        sentShareName = args['--sentShareName']
        self.params = PurviewEndpoints.get_api_version_params('share')
        self.method = "GET"
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.SHARE['accepted_sent_shares'], 
            sentShareName=sentShareName
        )

    @decorator
    def shareGetAcceptedShare(self, args):
        sentShareName = args['--sentShareName']
        acceptedSentShareName = args['--acceptedSentShareName']
        self.params = PurviewEndpoints.get_api_version_params('share')
        self.method = "GET"
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.SHARE['accepted_sent_share'], 
            sentShareName=sentShareName,
            acceptedSentShareName=acceptedSentShareName
        )

    @decorator
    def shareReinstateAcceptedShare(self, args):
        sentShareName = args['--sentShareName']
        acceptedSentShareName = args['--acceptedSentShareName']
        self.params = PurviewEndpoints.get_api_version_params('share')
        self.method = "POST"
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.SHARE['reinstate_accepted_share'], 
            sentShareName=sentShareName,
            acceptedSentShareName=acceptedSentShareName
        )
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def shareRevokeAcceptedShare(self, args):
        sentShareName = args['--sentShareName']
        acceptedSentShareName = args['--acceptedSentShareName']
        self.params = PurviewEndpoints.get_api_version_params('share')
        self.method = "POST"
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.SHARE['revoke_accepted_share'], 
            sentShareName=sentShareName,
            acceptedSentShareName=acceptedSentShareName
        )

    @decorator
    def shareUpdateExpirationAcceptedShare(self, args):
        sentShareName = args['--sentShareName']
        acceptedSentShareName = args['--acceptedSentShareName']
        self.params = PurviewEndpoints.get_api_version_params('share')
        self.method = "POST"
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.SHARE['update_expiration_accepted_share'], 
            sentShareName=sentShareName,
            acceptedSentShareName=acceptedSentShareName
        )
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def shareListAssetMappings(self, args):
        receivedShareName = args['--receivedShareName']
        self.params = PurviewEndpoints.get_api_version_params('share')
        self.method = "GET"
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.SHARE['asset_mappings'], 
            receivedShareName=receivedShareName
        )

    @decorator
    def shareCreateAssetMapping(self, args):
        receivedShareName = args['--receivedShareName']
        assetMappingName = args['--assetMappingName']
        self.params = PurviewEndpoints.get_api_version_params('share')
        self.method = "PUT"
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.SHARE['asset_mapping'], 
            receivedShareName=receivedShareName,
            assetMappingName=assetMappingName
        )
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def shareDeleteAssetMapping(self, args):
        receivedShareName = args['--receivedShareName']
        assetMappingName = args['--assetMappingName']
        self.params = PurviewEndpoints.get_api_version_params('share')
        self.method = "DELETE"
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.SHARE['asset_mapping'], 
            receivedShareName=receivedShareName,
            assetMappingName=assetMappingName
        )

    @decorator
    def shareGetAssetMapping(self, args):
        receivedShareName = args['--receivedShareName']
        assetMappingName = args['--assetMappingName']
        self.params = PurviewEndpoints.get_api_version_params('share')
        self.method = "GET"
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.SHARE['asset_mapping'], 
            receivedShareName=receivedShareName,
            assetMappingName=assetMappingName
        )

    @decorator
    def shareListAssets(self, args):
        sentShareName = args['--sentShareName']
        self.params = PurviewEndpoints.get_api_version_params('share')
        self.method = "GET"
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.SHARE['assets'], 
            sentShareName=sentShareName
        )

    @decorator
    def shareCreateAsset(self, args):
        sentShareName = args['--sentShareName']
        assetName = args['--assetName']
        self.params = PurviewEndpoints.get_api_version_params('share')
        self.method = "PUT"
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.SHARE['asset'], 
            sentShareName=sentShareName,
            assetName=assetName
        )
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def shareDeleteAsset(self, args):
        sentShareName = args['--sentShareName']
        assetName = args['--assetName']
        self.params = PurviewEndpoints.get_api_version_params('share')
        self.method = "DELETE"
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.SHARE['asset'], 
            sentShareName=sentShareName,
            assetName=assetName
        )

    @decorator
    def shareGetAsset(self, args):
        sentShareName = args['--sentShareName']
        assetName = args['--assetName']
        self.params = PurviewEndpoints.get_api_version_params('share')
        self.method = "GET"
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.SHARE['asset'], 
            sentShareName=sentShareName,
            assetName=assetName
        )

    @decorator
    def shareActivateEmail(self, args):
        self.params = PurviewEndpoints.get_api_version_params('share')
        self.method = "POST"
        self.endpoint = PurviewEndpoints.SHARE['activate_email']
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def shareRegisterEmail(self, args):
        self.params = PurviewEndpoints.get_api_version_params('share')
        self.method = "POST"
        self.endpoint = "/registerEmail"

    @decorator
    def shareListReceivedAssets(self, args):
        receivedShareName = args['--receivedShareName']
        self.params = PurviewEndpoints.get_api_version_params('share')
        self.method = "GET"
        self.endpoint = f"/receivedShares/{receivedShareName}/receivedAssets"

    @decorator
    def shareListReceivedInvitations(self, args):
        self.params = PurviewEndpoints.get_api_version_params('share')
        self.method = "GET"
        self.endpoint = "/receivedInvitations"

    @decorator
    def shareGetReceivedInvitation(self, args):
        receivedInvitationName = args['--invitationName']
        self.params = PurviewEndpoints.get_api_version_params('share')
        self.method = "GET"
        self.endpoint = f"/receivedInvitations/{receivedInvitationName}"

    @decorator
    def shareRejectReceivedInvitation(self, args):
        receivedInvitationName = args['--invitationName']
        self.params = PurviewEndpoints.get_api_version_params('share')
        self.method = "POST"
        self.endpoint = f"/receivedInvitations/{receivedInvitationName}:reject"
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def shareListReceivedShares(self, args):
        self.params = PurviewEndpoints.get_api_version_params('share')
        self.method = "GET"
        self.endpoint = "/receivedShares"

    @decorator
    def shareCreateReceivedShare(self, args):
        receivedShareName = args['--receivedShareName']
        self.params = PurviewEndpoints.get_api_version_params('share')
        self.method = "PUT"
        self.endpoint = f"/receivedShares/{receivedShareName}"
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def shareDeleteReceivedShare(self, args):
        receivedShareName = args['--receivedShareName']
        self.params = PurviewEndpoints.get_api_version_params('share')
        self.method = "DELETE"
        self.endpoint = f"/receivedShares/{receivedShareName}"

    @decorator
    def shareGetReceivedShare(self, args):
        receivedShareName = args['--receivedShareName']
        self.params = PurviewEndpoints.get_api_version_params('share')
        self.method = "GET"
        self.endpoint = f"/receivedShares/{receivedShareName}"

    @decorator
    def shareListSentInvitations(self, args):
        sentShareName = args['--sentShareName']
        self.params = PurviewEndpoints.get_api_version_params('share')
        self.method = "GET"
        self.endpoint = f"/sentShares/{sentShareName}/sentShareInvitations"

    @decorator
    def shareCreateSentInvitation(self, args):
        sentShareName = args['--sentShareName']
        sentShareInvitationName = args['--invitationName']
        self.params = PurviewEndpoints.get_api_version_params('share')
        self.method = "PUT"
        self.endpoint = f"/sentShares/{sentShareName}/sentShareInvitations/{sentShareInvitationName}"
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def shareDeleteSentInvitation(self, args):
        sentShareName = args['--sentShareName']
        sentShareInvitationName = args['--invitationName']
        self.params = PurviewEndpoints.get_api_version_params('share')
        self.method = "DELETE"
        self.endpoint = f"/sentShares/{sentShareName}/sentShareInvitations/{sentShareInvitationName}"

    @decorator
    def shareGetSentInvitation(self, args):
        sentShareName = args['--sentShareName']
        sentShareInvitationName = args['--invitationName']
        self.params = PurviewEndpoints.get_api_version_params('share')
        self.method = "GET"
        self.endpoint = f"/sentShares/{sentShareName}/sentShareInvitations/{sentShareInvitationName}"

    @decorator
    def shareListSentShares(self, args):
        self.params = PurviewEndpoints.get_api_version_params('share')
        self.method = "GET"
        self.endpoint = "/sentShares"

    @decorator
    def shareCreateSentShare(self, args):
        sentShareName = args['--sentShareName']
        self.params = PurviewEndpoints.get_api_version_params('share')
        self.method = "PUT"
        self.endpoint = f"/sentShares/{sentShareName}"
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def shareDeleteSentShare(self, args):
        sentShareName = args['--sentShareName']
        self.params = PurviewEndpoints.get_api_version_params('share')
        self.method = "DELETE"
        self.endpoint = f"/sentShares/{sentShareName}"

    @decorator
    def shareGetSentShare(self, args):
        sentShareName = args['--sentShareName']
        self.params = PurviewEndpoints.get_api_version_params('share')
        self.method = "GET"
        self.endpoint = f"/sentShares/{sentShareName}"
