# API Mapping Reference

This document maps Purview CLI commands to Microsoft Purview REST API endpoints.

## Command to API Mapping

| Command Group | Action | HTTP Method | Endpoint | Description |
|---------------|--------|-------------|----------|-------------|
| entity | importBusinessMetadata | POST | `https://{accountName}.purview.azure.com/catalog/api/atlas/v2/entity/businessmetadata/import` |  Import business metadata in bulk. |
| entity | getBusinessMetadataTemplate | GET | `https://{accountName}.purview.azure.com/catalog/api/atlas/v2/entity/businessmetadata/import/template` | Get a sample template for uploading/creating business metadata in bulk. |
| entity | addOrUpdateBusinessMetadata | POST | `https://{accountName}.purview.azure.com/catalog/api/atlas/v2/entity/guid/{guid}/businessmetadata` | Add or update business metadata to an entity. |
| entity | deleteBusinessMetadata | DELETE | `https://{accountName}.purview.azure.com/catalog/api/atlas/v2/entity/guid/{guid}/businessmetadata` | Remove business metadata from an entity. |
| entity | addOrUpdateBusinessAttribute | POST | `https://{accountName}.purview.azure.com/catalog/api/atlas/v2/entity/guid/{guid}/businessmetadata/{bmName}` | Add or update business attributes to an entity. |
| entity | deleteBusinessAttribute | DELETE | `https://{accountName}.purview.azure.com/catalog/api/atlas/v2/entity/guid/{guid}/businessmetadata/{bmName}` | Delete business metadata from an entity. |
| entity | addLabels | PUT | `https://{accountName}.purview.azure.com/catalog/api/atlas/v2/entity/guid/{guid}/labels` | Append labels to an entity. |
| entity | deleteLabels | DELETE | `https://{accountName}.purview.azure.com/catalog/api/atlas/v2/entity/guid/{guid}/labels` | Delete label(s) from an entity. |
| entity | setLabels | POST | `https://{accountName}.purview.azure.com/catalog/api/atlas/v2/entity/guid/{guid}/labels` | Overwrite labels for an entity. |
| entity | addLabelsByUniqueAttribute | PUT | `https://{accountName}.purview.azure.com/catalog/api/atlas/v2/entity/uniqueAttribute/type/{typeName}/labels` | Append labels to an entity identified by its type and unique attributes. |
| entity | deleteLabelsByUniqueAttribute | DELETE | `https://{accountName}.purview.azure.com/catalog/api/atlas/v2/entity/uniqueAttribute/type/{typeName}/labels` | Delete label(s) from an entity identified by its type and unique attributes. |
| entity | setLabelsByUniqueAttribute | POST | `https://{accountName}.purview.azure.com/catalog/api/atlas/v2/entity/uniqueAttribute/type/{typeName}/labels` | Overwrite labels for an entity identified by its type and unique attributes. |
| types | readBusinessMetadataDef | GET | `https://{accountName}.purview.azure.com/catalog/api/atlas/v2/types/businessmetadatadef/name/{name}` | Get the business metadata definition by GUID or its name (unique). |

## Authentication

All API calls require proper authentication. The CLI supports:

- Azure CLI authentication (`az login`)
- Service Principal authentication
- Managed Identity authentication
- Environment variable authentication

## Rate Limiting

The CLI includes built-in rate limiting and retry logic to handle API throttling.

## Error Handling

Common HTTP status codes:

- `200` - Success
- `401` - Authentication failed
- `403` - Authorization failed  
- `404` - Resource not found
- `429` - Rate limit exceeded
- `500` - Server error
