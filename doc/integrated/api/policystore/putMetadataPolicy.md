# pvw policystore putMetadataPolicy
[Command Reference](../../../README.md#command-reference) > [policystore](./main.md) > putMetadataPolicy

## Description
Updates a metadata policy.

## Syntax
```
pvw policystore putMetadataPolicy --policyId=<val> --payloadFile=<val>
```

## Required Arguments
`--policyId` (string)  
The unique policy id.

`--payloadFile` (string)  
File path to a valid JSON document.

## Optional Arguments
*None*

## API Mapping
Metadata Policy Data Plane > Metadata Policy > [Update](https://docs.microsoft.com/en-us/rest/api/purview/metadatapolicydataplane/metadata-policy/update)
```
PUT https://{accountName}.purview.azure.com/policystore/metadataPolicies/{policyId}
```

## Examples
Update an existing metadata policy.
```powershell
 pvw policystore putMetadataPolicy --policyId "67c667b7-8f1c-468f-ab3b-f19fd943de95" --payloadFile "/path/to/file.json"
```
<details><summary>Example payload.</summary>
<p>

```json
{
    "id": "a17fef61-3a7d-4453-925c-8cbf7b83af92",
    "name": "policy_esg-26fa7f24-pvw",
    "properties": {
        "attributeRules": [
            {
                "dnfCondition": [
                    [
                        {
                            "attributeName": "principal.microsoft.id",
                            "attributeValueIncludedIn": [
                                "095354ff-cae8-44ff-8120-22ec5a941b40"
                            ]
                        },
                        {
                            "attributeName": "derived.purview.role",
                            "attributeValueIncludes": "purviewmetadatarole_builtin_collection-administrator",
                            "fromRule": "purviewmetadatarole_builtin_collection-administrator"
                        }
                    ]
                ],
                "id": "purviewmetadatarole_builtin_collection-administrator:esg-26fa7f24-pvw",
                "kind": "attributerule",
                "name": "purviewmetadatarole_builtin_collection-administrator:esg-26fa7f24-pvw"
            },
            {
                "dnfCondition": [
                    [
                        {
                            "attributeName": "principal.microsoft.id",
                            "attributeValueIncludedIn": [
                                "095354ff-cae8-44ff-8120-22ec5a941b40"
                            ]
                        },
                        {
                            "attributeName": "derived.purview.role",
                            "attributeValueIncludes": "purviewmetadatarole_builtin_purview-reader",
                            "fromRule": "purviewmetadatarole_builtin_purview-reader"
                        }
                    ]
                ],
                "id": "purviewmetadatarole_builtin_purview-reader:esg-26fa7f24-pvw",
                "kind": "attributerule",
                "name": "purviewmetadatarole_builtin_purview-reader:esg-26fa7f24-pvw"
            },
            {
                "dnfCondition": [
                    [
                        {
                            "attributeName": "principal.microsoft.id",
                            "attributeValueIncludedIn": [
                                "095354ff-cae8-44ff-8120-22ec5a941b40",
                                "60117586-ca87-4eac-a217-9d130ded9af0"
                            ]
                        },
                        {
                            "attributeName": "derived.purview.role",
                            "attributeValueIncludes": "purviewmetadatarole_builtin_data-curator",
                            "fromRule": "purviewmetadatarole_builtin_data-curator"
                        }
                    ]
                ],
                "id": "purviewmetadatarole_builtin_data-curator:esg-26fa7f24-pvw",
                "kind": "attributerule",
                "name": "purviewmetadatarole_builtin_data-curator:esg-26fa7f24-pvw"
            },
            {
                "dnfCondition": [
                    [
                        {
                            "attributeName": "principal.microsoft.id",
                            "attributeValueIncludedIn": [
                                "095354ff-cae8-44ff-8120-22ec5a941b40",
                                "60117586-ca87-4eac-a217-9d130ded9af0"
                            ]
                        },
                        {
                            "attributeName": "derived.purview.role",
                            "attributeValueIncludes": "purviewmetadatarole_builtin_data-source-administrator",
                            "fromRule": "purviewmetadatarole_builtin_data-source-administrator"
                        }
                    ]
                ],
                "id": "purviewmetadatarole_builtin_data-source-administrator:esg-26fa7f24-pvw",
                "kind": "attributerule",
                "name": "purviewmetadatarole_builtin_data-source-administrator:esg-26fa7f24-pvw"
            },
            {
                "dnfCondition": [
                    [
                        {
                            "attributeName": "derived.purview.permission",
                            "attributeValueIncludes": "purviewmetadatarole_builtin_collection-administrator:esg-26fa7f24-pvw",
                            "fromRule": "purviewmetadatarole_builtin_collection-administrator:esg-26fa7f24-pvw"
                        }
                    ],
                    [
                        {
                            "attributeName": "derived.purview.permission",
                            "attributeValueIncludes": "purviewmetadatarole_builtin_purview-reader:esg-26fa7f24-pvw",
                            "fromRule": "purviewmetadatarole_builtin_purview-reader:esg-26fa7f24-pvw"
                        }
                    ],
                    [
                        {
                            "attributeName": "derived.purview.permission",
                            "attributeValueIncludes": "purviewmetadatarole_builtin_data-curator:esg-26fa7f24-pvw",
                            "fromRule": "purviewmetadatarole_builtin_data-curator:esg-26fa7f24-pvw"
                        }
                    ],
                    [
                        {
                            "attributeName": "derived.purview.permission",
                            "attributeValueIncludes": "purviewmetadatarole_builtin_data-source-administrator:esg-26fa7f24-pvw",
                            "fromRule": "purviewmetadatarole_builtin_data-source-administrator:esg-26fa7f24-pvw"
                        }
                    ]
                ],
                "id": "permission:esg-26fa7f24-pvw",
                "kind": "attributerule",
                "name": "permission:esg-26fa7f24-pvw"
            }
        ],
        "collection": {
            "referenceName": "esg-26fa7f24-pvw",
            "type": "CollectionReference"
        },
        "decisionRules": [
            {
                "dnfCondition": [
                    [
                        {
                            "attributeName": "resource.purview.collection",
                            "attributeValueIncludes": "esg-26fa7f24-pvw"
                        },
                        {
                            "attributeName": "derived.purview.permission",
                            "attributeValueIncludes": "permission:esg-26fa7f24-pvw",
                            "fromRule": "permission:esg-26fa7f24-pvw"
                        }
                    ]
                ],
                "effect": "Permit",
                "kind": "decisionrule"
            }
        ],
        "description": ""
    },
    "version": 1
}
```
</p>
</details>
