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
import json
import click
from purviewcli.client._share import Share

@click.group()
def share():
    """Manage data sharing in Azure Purview.
    All share operations are exposed as modular Click-based commands for full CLI visibility.
    """
    pass

# Accepted Sent Shares
@share.command()
@click.option('--sent-share-name', required=True, help='The name of the sent share')
@click.option('--skip-token', required=False, help='Continuation token for paging')
def list_accepted_shares(sent_share_name, skip_token):
    """List accepted shares for a sent share"""
    try:
        args = {'--sentShareName': sent_share_name, '--skipToken': skip_token}
        client = Share()
        result = client.shareListAcceptedShares(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

@share.command()
@click.option('--sent-share-name', required=True, help='The name of the sent share')
@click.option('--accepted-sent-share-name', required=True, help='The name of the accepted sent share')
def get_accepted_share(sent_share_name, accepted_sent_share_name):
    """Get an accepted share by name"""
    try:
        args = {'--sentShareName': sent_share_name, '--acceptedSentShareName': accepted_sent_share_name}
        client = Share()
        result = client.shareGetAcceptedShare(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

@share.command()
@click.option('--sent-share-name', required=True)
@click.option('--accepted-sent-share-name', required=True)
@click.option('--payload-file', type=click.Path(exists=True), required=True)
def reinstate_accepted_share(sent_share_name, accepted_sent_share_name, payload_file):
    """Reinstate an accepted share"""
    try:
        args = {'--sentShareName': sent_share_name, '--acceptedSentShareName': accepted_sent_share_name, '--payloadFile': payload_file}
        client = Share()
        result = client.shareReinstateAcceptedShare(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

@share.command()
@click.option('--sent-share-name', required=True)
@click.option('--accepted-sent-share-name', required=True)
def revoke_accepted_share(sent_share_name, accepted_sent_share_name):
    """Revoke an accepted share"""
    try:
        args = {'--sentShareName': sent_share_name, '--acceptedSentShareName': accepted_sent_share_name}
        client = Share()
        result = client.shareRevokeAcceptedShare(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

@share.command()
@click.option('--sent-share-name', required=True)
@click.option('--accepted-sent-share-name', required=True)
@click.option('--payload-file', type=click.Path(exists=True), required=True)
def update_expiration_accepted_share(sent_share_name, accepted_sent_share_name, payload_file):
    """Update expiration for an accepted share"""
    try:
        args = {'--sentShareName': sent_share_name, '--acceptedSentShareName': accepted_sent_share_name, '--payloadFile': payload_file}
        client = Share()
        result = client.shareUpdateExpirationAcceptedShare(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

# Asset Mappings
@share.command()
@click.option('--received-share-name', required=True)
@click.option('--skip-token', required=False)
@click.option('--filter', required=False)
@click.option('--order-by', required=False)
def list_asset_mappings(received_share_name, skip_token, filter, order_by):
    """List asset mappings for a received share"""
    try:
        args = {'--receivedShareName': received_share_name, '--skipToken': skip_token, '--filter': filter, '--orderBy': order_by}
        client = Share()
        result = client.shareListAssetMappings(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

@share.command()
@click.option('--received-share-name', required=True)
@click.option('--asset-mapping-name', required=True)
@click.option('--payload-file', type=click.Path(exists=True), required=True)
def create_asset_mapping(received_share_name, asset_mapping_name, payload_file):
    """Create an asset mapping for a received share"""
    try:
        args = {'--receivedShareName': received_share_name, '--assetMappingName': asset_mapping_name, '--payloadFile': payload_file}
        client = Share()
        result = client.shareCreateAssetMapping(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

@share.command()
@click.option('--received-share-name', required=True)
@click.option('--asset-mapping-name', required=True)
def delete_asset_mapping(received_share_name, asset_mapping_name):
    """Delete an asset mapping for a received share"""
    try:
        args = {'--receivedShareName': received_share_name, '--assetMappingName': asset_mapping_name}
        client = Share()
        result = client.shareDeleteAssetMapping(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

@share.command()
@click.option('--received-share-name', required=True)
@click.option('--asset-mapping-name', required=True)
def get_asset_mapping(received_share_name, asset_mapping_name):
    """Get an asset mapping for a received share"""
    try:
        args = {'--receivedShareName': received_share_name, '--assetMappingName': asset_mapping_name}
        client = Share()
        result = client.shareGetAssetMapping(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

# Assets
@share.command()
@click.option('--sent-share-name', required=True)
@click.option('--skip-token', required=False)
@click.option('--filter', required=False)
@click.option('--order-by', required=False)
def list_assets(sent_share_name, skip_token, filter, order_by):
    """List assets for a sent share"""
    try:
        args = {'--sentShareName': sent_share_name, '--skipToken': skip_token, '--filter': filter, '--orderBy': order_by}
        client = Share()
        result = client.shareListAssets(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

@share.command()
@click.option('--sent-share-name', required=True)
@click.option('--asset-name', required=True)
@click.option('--payload-file', type=click.Path(exists=True), required=True)
def create_asset(sent_share_name, asset_name, payload_file):
    """Create an asset for a sent share"""
    try:
        args = {'--sentShareName': sent_share_name, '--assetName': asset_name, '--payloadFile': payload_file}
        client = Share()
        result = client.shareCreateAsset(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

@share.command()
@click.option('--sent-share-name', required=True)
@click.option('--asset-name', required=True)
def delete_asset(sent_share_name, asset_name):
    """Delete an asset for a sent share"""
    try:
        args = {'--sentShareName': sent_share_name, '--assetName': asset_name}
        client = Share()
        result = client.shareDeleteAsset(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

@share.command()
@click.option('--sent-share-name', required=True)
@click.option('--asset-name', required=True)
def get_asset(sent_share_name, asset_name):
    """Get an asset for a sent share"""
    try:
        args = {'--sentShareName': sent_share_name, '--assetName': asset_name}
        client = Share()
        result = client.shareGetAsset(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

# Email
@share.command()
@click.option('--payload-file', type=click.Path(exists=True), required=True)
def activate_email(payload_file):
    """Activate email for data sharing"""
    try:
        args = {'--payloadFile': payload_file}
        client = Share()
        result = client.shareActivateEmail(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

@share.command()
def register_email():
    """Register email for data sharing"""
    try:
        args = {}
        client = Share()
        result = client.shareRegisterEmail(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

# Received Assets
@share.command()
@click.option('--received-share-name', required=True)
@click.option('--skip-token', required=False)
def list_received_assets(received_share_name, skip_token):
    """List received assets for a received share"""
    try:
        args = {'--receivedShareName': received_share_name, '--skipToken': skip_token}
        client = Share()
        result = client.shareListReceivedAssets(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

# Received Invitations
@share.command()
@click.option('--skip-token', required=False)
@click.option('--filter', required=False)
@click.option('--order-by', required=False)
def list_received_invitations(skip_token, filter, order_by):
    """List received invitations"""
    try:
        args = {'--skipToken': skip_token, '--filter': filter, '--orderBy': order_by}
        client = Share()
        result = client.shareListReceivedInvitations(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

@share.command()
@click.option('--invitation-name', required=True)
def get_received_invitation(invitation_name):
    """Get a received invitation by name"""
    try:
        args = {'--invitationName': invitation_name}
        client = Share()
        result = client.shareGetReceivedInvitation(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

@share.command()
@click.option('--invitation-name', required=True)
@click.option('--payload-file', type=click.Path(exists=True), required=True)
def reject_received_invitation(invitation_name, payload_file):
    """Reject a received invitation"""
    try:
        args = {'--invitationName': invitation_name, '--payloadFile': payload_file}
        client = Share()
        result = client.shareRejectReceivedInvitation(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

# Received Shares
@share.command()
@click.option('--skip-token', required=False)
@click.option('--filter', required=False)
@click.option('--order-by', required=False)
def list_received_shares(skip_token, filter, order_by):
    """List received shares"""
    try:
        args = {'--skipToken': skip_token, '--filter': filter, '--orderBy': order_by}
        client = Share()
        result = client.shareListReceivedShares(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

@share.command()
@click.option('--received-share-name', required=True)
@click.option('--payload-file', type=click.Path(exists=True), required=True)
def create_received_share(received_share_name, payload_file):
    """Create a received share"""
    try:
        args = {'--receivedShareName': received_share_name, '--payloadFile': payload_file}
        client = Share()
        result = client.shareCreateReceivedShare(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

@share.command()
@click.option('--received-share-name', required=True)
def delete_received_share(received_share_name):
    """Delete a received share"""
    try:
        args = {'--receivedShareName': received_share_name}
        client = Share()
        result = client.shareDeleteReceivedShare(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

@share.command()
@click.option('--received-share-name', required=True)
def get_received_share(received_share_name):
    """Get a received share by name"""
    try:
        args = {'--receivedShareName': received_share_name}
        client = Share()
        result = client.shareGetReceivedShare(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

# Sent Invitations
@share.command()
@click.option('--sent-share-name', required=True)
@click.option('--skip-token', required=False)
@click.option('--filter', required=False)
@click.option('--order-by', required=False)
def list_sent_invitations(sent_share_name, skip_token, filter, order_by):
    """List sent invitations for a sent share"""
    try:
        args = {'--sentShareName': sent_share_name, '--skipToken': skip_token, '--filter': filter, '--orderBy': order_by}
        client = Share()
        result = client.shareListSentInvitations(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

@share.command()
@click.option('--sent-share-name', required=True)
@click.option('--invitation-name', required=True)
@click.option('--payload-file', type=click.Path(exists=True), required=True)
def create_sent_invitation(sent_share_name, invitation_name, payload_file):
    """Create a sent invitation for a sent share"""
    try:
        args = {'--sentShareName': sent_share_name, '--invitationName': invitation_name, '--payloadFile': payload_file}
        client = Share()
        result = client.shareCreateSentInvitation(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

@share.command()
@click.option('--sent-share-name', required=True)
@click.option('--invitation-name', required=True)
def delete_sent_invitation(sent_share_name, invitation_name):
    """Delete a sent invitation for a sent share"""
    try:
        args = {'--sentShareName': sent_share_name, '--invitationName': invitation_name}
        client = Share()
        result = client.shareDeleteSentInvitation(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

@share.command()
@click.option('--sent-share-name', required=True)
@click.option('--invitation-name', required=True)
def get_sent_invitation(sent_share_name, invitation_name):
    """Get a sent invitation for a sent share"""
    try:
        args = {'--sentShareName': sent_share_name, '--invitationName': invitation_name}
        client = Share()
        result = client.shareGetSentInvitation(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

# Sent Shares
@share.command()
@click.option('--skip-token', required=False)
@click.option('--filter', required=False)
@click.option('--order-by', required=False)
def list_sent_shares(skip_token, filter, order_by):
    """List sent shares"""
    try:
        args = {'--skipToken': skip_token, '--filter': filter, '--orderBy': order_by}
        client = Share()
        result = client.shareListSentShares(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

@share.command()
@click.option('--sent-share-name', required=True)
@click.option('--payload-file', type=click.Path(exists=True), required=True)
def create_sent_share(sent_share_name, payload_file):
    """Create a sent share"""
    try:
        args = {'--sentShareName': sent_share_name, '--payloadFile': payload_file}
        client = Share()
        result = client.shareCreateSentShare(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

@share.command()
@click.option('--sent-share-name', required=True)
def delete_sent_share(sent_share_name):
    """Delete a sent share"""
    try:
        args = {'--sentShareName': sent_share_name}
        client = Share()
        result = client.shareDeleteSentShare(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

@share.command()
@click.option('--sent-share-name', required=True)
def get_sent_share(sent_share_name):
    """Get a sent share by name"""
    try:
        args = {'--sentShareName': sent_share_name}
        client = Share()
        result = client.shareGetSentShare(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

__all__ = ['share']
