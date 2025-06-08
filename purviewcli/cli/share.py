"""
usage: 
    pvw share listAcceptedShares --sentShareName=<val> [--skipToken=<val>]
    pvw share getAcceptedShare --sentShareName=<val> --acceptedSentShareName=<val>
    pvw share reinstateAcceptedShare --sentShareName=<val> --acceptedSentShareName=<val> --payloadFile=<val>
    pvw share revokeAcceptedShare --sentShareName=<val> --acceptedSentShareName=<val>
    pvw share updateExpirationAcceptedShare --sentShareName=<val> --acceptedSentShareName=<val> --payloadFile=<val>
    pvw share listAssetMappings --receivedShareName=<val> [--skipToken=<val> --filter=<val> --orderBy=<val>]
    pvw share createAssetMapping --receivedShareName=<val> --assetMappingName=<val> --payloadFile=<val>
    pvw share deleteAssetMapping --receivedShareName=<val> --assetMappingName=<val>
    pvw share getAssetMapping --receivedShareName=<val> --assetMappingName=<val>
    pvw share listAssets --sentShareName=<val> [--skipToken=<val> --filter=<val> --orderBy=<val>]
    pvw share createAsset --sentShareName=<val> --assetName=<val> --payloadFile=<val>
    pvw share deleteAsset --sentShareName=<val> --assetName=<val>
    pvw share getAsset --sentShareName=<val> --assetName=<val>
    pvw share activateEmail --payloadFile=<val>
    pvw share registerEmail
    pvw share listReceivedAssets --receivedShareName=<val> [--skipToken=<val>]
    pvw share listReceivedInvitations [--skipToken=<val> --filter=<val> --orderBy=<val>]
    pvw share getReceivedInvitation --invitationName=<val>
    pvw share rejectReceivedInvitation --invitationName=<val> --payloadFile=<val>
    pvw share listReceivedShares [--skipToken=<val> --filter=<val> --orderBy=<val>]
    pvw share createReceivedShare --receivedShareName=<val> --payloadFile=<val>
    pvw share deleteReceivedShare --receivedShareName=<val>
    pvw share getReceivedShare --receivedShareName=<val>
    pvw share listSentInvitations --sentShareName=<val> [--skipToken=<val> --filter=<val> --orderBy=<val>]
    pvw share createSentInvitation --sentShareName=<val> --invitationName=<val> --payloadFile=<val>
    pvw share deleteSentInvitation --sentShareName=<val> --invitationName=<val>
    pvw share getSentInvitation --sentShareName=<val> --invitationName=<val>
    pvw share listSentShares [--skipToken=<val> --filter=<val> --orderBy=<val>]
    pvw share createSentShare --sentShareName=<val> --payloadFile=<val>
    pvw share deleteSentShare --sentShareName=<val>
    pvw share getSentShare --sentShareName=<val>


options:
    --purviewName=<val>           [string]  The name of the Microsoft Purview account.
    --receivedShareName=<val>     [string]  The name of the received share.
    --sentShareName=<val>         [string]  The name of the sent share.
    --acceptedSentShareName=<val> [string]  The name of the accepted sent share.
    --assetMappingName=<val>      [string]  The name of the asset mapping.
    --assetName=<val>             [string]  The name of the asset.
    --invitationName=<val>        [string]  The name of the invitation.
    --skipToken=<val>             [string]  The continuation token to list the next page.
    --filter=<val>                [string]  Filters the results using OData syntax.
    --orderBy=<val>               [string]  Sorts the results using OData syntax.
    --payloadFile=<val>           [string]  File path to a valid JSON document.

"""
from docopt import docopt

if __name__ == '__main__':
    arguments = docopt(__doc__)
