# Share Commands

Manage data sharing artifacts and workflows for sharing catalogs and assets with internal and external stakeholders.

!!! tip "Quick Start"
    Work with data sharing artifacts including share creation, asset mapping, and share activation.

## What You Can Do

- Create and manage data shares
- Configure share assets and mappings
- Manage share invitations
- Control share lifecycles
- Track received shares

## Available Actions

### Sent Shares

| Command | Purpose |
| --- | --- |
| `createsentshare` | Create outbound share |
| `deletesentshare` | Remove share |
| `getsentshare` | Get share details |
| `listsentshares` | List all sent shares |
| `createsentinvitation` | Send share invitation |
| `deletesentinvitation` | Revoke invitation |
| `getsentinvitation` | Get invitation details |
| `listsentinvitations` | List sent invitations |

### Received Shares

| Command | Purpose |
| --- | --- |
| `createreceivedshare` | Accept received share |
| `deletereceivedshare` | Reject or remove share |
| `getreceivedshare` | Get received share details |
| `listreceivedshares` | List received shares |
| `listacceptedshares` | List accepted shares |
| `getacceptedshare` | Get accepted share |
| `reinstateacceptedshare` | Restore share |
| `revokeacceptedshare` | Revoke accepted share |
| `updateexpirationacceptedshare` | Update expiration |

### Share Assets

| Command | Purpose |
| --- | --- |
| `createasset` | Add asset to share |
| `deleteasset` | Remove asset from share |
| `getasset` | Get asset details |
| `listassets` | List assets in share |
| `listreceivedassets` | List received assets |
| `createassetmapping` | Map asset to recipient |
| `deleteassetmapping` | Remove mapping |
| `getassetmapping` | Get mapping details |
| `listassetmappings` | List mappings |

### Email Management

| Command | Purpose |
| --- | --- |
| `activateemail` | Activate share via email |
| `registeremail` | Register email address |

### Invitations

| Command | Purpose |
| --- | --- |
| `getreceivedinvitation` | Get invitation details |
| `listreceivedinvitations` | List received invitations |
| `rejectreceivedinvitation` | Reject invitation |

## Common Workflows

### Share Assets Internally

```bash
# Create share
pvw share createsentshare --help

# Add assets
pvw share createasset --help

# Send invitation
pvw share createsentinvitation --help
```

## Related Topics

- [Entity commands](../entity/main.md)
- [Account commands](../account/main.md)
- [Create Tasks](../task-create.md)
