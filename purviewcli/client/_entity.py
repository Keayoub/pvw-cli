from .endpoint import Endpoint, decorator, get_json, no_api_call_decorator
from .endpoints import PurviewEndpoints


class Entity(Endpoint):
    def __init__(self):
        Endpoint.__init__(self)
        self.app = "catalog"

    @decorator
    def entityCreate(self, args):
        self.method = "POST"
        self.endpoint = PurviewEndpoints.ENTITY["base"]
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def entityDeleteBulk(self, args):
        self.method = "DELETE"
        self.headers = {"Content-Type": "application/json"}
        self.endpoint = PurviewEndpoints.ENTITY["bulk"]
        self.params = {"guid": args["--guid"]}

    @decorator
    def entityReadBulk(self, args):
        self.method = "GET"
        self.endpoint = PurviewEndpoints.ENTITY["bulk"]
        self.params = {
            "guid": args["--guid"],
            "ignoreRelationships": str(args["--ignoreRelationships"]).lower(),
            "minExtInfo": str(args["--minExtInfo"]).lower(),
        }

    @decorator
    def entityCreateBulk(self, args):
        self.method = "POST"
        self.endpoint = PurviewEndpoints.ENTITY["bulk"]
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def entityCreateBulkClassification(self, args):
        # Associates a classification to multiple entities in bulk.
        self.method = "POST"
        self.endpoint = PurviewEndpoints.ENTITY["bulk_classification"]
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def entityCreateBulkSetClassifications(self, args):
        # Set classifications on entities in bulk (Classification -< Entities).
        self.method = "POST"
        self.endpoint = PurviewEndpoints.ENTITY["bulk_set_classifications"]
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def entityDelete(self, args):
        self.method = "DELETE"
        self.endpoint = f'{PurviewEndpoints.ENTITY["guid"]}/{args["--guid"][0]}'

    @decorator
    def entityRead(self, args):
        self.method = "GET"
        self.endpoint = f'{PurviewEndpoints.ENTITY["guid"]}/{args["--guid"][0]}'
        self.params = {
            "ignoreRelationships": str(args["--ignoreRelationships"]).lower(),
            "minExtInfo": str(args["--minExtInfo"]).lower(),
        }

    @decorator
    def entityPut(self, args):
        self.method = "PUT"
        self.endpoint = f'{PurviewEndpoints.ENTITY["guid"]}/{args["--guid"][0]}'
        self.params = {"name": args["--attrName"]}
        self.payload = args["--attrValue"]

    @decorator
    def entityDeleteClassification(self, args):
        self.method = "DELETE"
        self.endpoint = (
            PurviewEndpoints.format_endpoint(
                PurviewEndpoints.ENTITY["classification"], guid=args["--guid"][0]
            )
            + f'/{args["--classificationName"]}'
        )

    @decorator
    def entityReadClassification(self, args):
        self.method = "GET"
        self.endpoint = (
            PurviewEndpoints.format_endpoint(
                PurviewEndpoints.ENTITY["classification"], guid=args["--guid"][0]
            )
            + f'/{args["--classificationName"]}'
        )

    @decorator
    def entityReadClassifications(self, args):
        self.method = "GET"
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.ENTITY["classifications"], guid=args["--guid"][0]
        )

    @decorator
    def entityCreateClassifications(self, args):
        self.method = "POST"
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.ENTITY["classifications"], guid=args["--guid"][0]
        )
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def entityPutClassifications(self, args):
        self.method = "PUT"
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.ENTITY["classifications"], guid=args["--guid"][0]
        )
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def entityReadHeader(self, args):
        self.method = "GET"
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.ENTITY["header"], guid=args["--guid"][0]
        )

    @decorator
    def entityReadBulkUniqueAttribute(self, args):
        self.method = "GET"
        self.endpoint = f'{PurviewEndpoints.ENTITY["unique_attribute"]}/{args["--typeName"]}/bulk'
        self.params = {
            "ignoreRelationships": str(args["--ignoreRelationships"]).lower(),
            "minExtInfo": str(args["--minExtInfo"]).lower(),
        }
        counter = 0
        self.params = {}
        for qualifiedName in args["--qualifiedName"]:
            self.params[f"attr_{str(counter)}:qualifiedName"] = qualifiedName
            counter += 1

    @decorator
    def entityReadUniqueAttribute(self, args):
        self.method = "GET"
        self.endpoint = f'{PurviewEndpoints.ENTITY["unique_attribute"]}/{args["--typeName"]}'
        self.params = {
            "attr:qualifiedName": args["--qualifiedName"],
            "ignoreRelationships": str(args["--ignoreRelationships"]).lower(),
            "minExtInfo": str(args["--minExtInfo"]).lower(),
        }

    @decorator
    def entityDeleteUniqueAttribute(self, args):
        self.method = "DELETE"
        self.endpoint = f'{PurviewEndpoints.ENTITY["unique_attribute"]}/{args["--typeName"]}'
        self.params = {"attr:qualifiedName": args["--qualifiedName"]}

    @decorator
    def entityPutUniqueAttribute(self, args):
        self.method = "PUT"
        self.endpoint = f'{PurviewEndpoints.ENTITY["unique_attribute"]}/{args["--typeName"]}'
        self.payload = get_json(args, "--payloadFile")
        self.params = {"attr:qualifiedName": args["--qualifiedName"]}

    @decorator
    def entityDeleteUniqueAttributeClassification(self, args):
        self.method = "DELETE"
        self.endpoint = f'{PurviewEndpoints.ENTITY["unique_attribute"]}/{args["--typeName"]}/classification/{args["--classificationName"]}'
        self.params = {"attr:qualifiedName": args["--qualifiedName"]}

    @decorator
    def entityCreateUniqueAttributeClassifications(self, args):
        self.method = "POST"
        self.endpoint = (
            f'{PurviewEndpoints.ENTITY["unique_attribute"]}/{args["--typeName"]}/classifications'
        )
        self.payload = get_json(args, "--payloadFile")
        self.params = {"attr:qualifiedName": args["--qualifiedName"]}

    @decorator
    def entityPutUniqueAttributeClassifications(self, args):
        self.method = "PUT"
        self.endpoint = (
            f'{PurviewEndpoints.ENTITY["unique_attribute"]}/{args["--typeName"]}/classifications'
        )
        self.payload = get_json(args, "--payloadFile")
        self.params = {"attr:qualifiedName": args["--qualifiedName"]}

    @decorator
    def entityCreateOrUpdateCollection(self, args):
        collection = args["--collection"]
        self.method = "POST"
        self.endpoint = f"/catalog/api/collections/{collection}/entity"
        self.payload = get_json(args, "--payloadFile")
        self.params = PurviewEndpoints.get_api_version_params("catalog")

    @decorator
    def entityCreateOrUpdateCollectionBulk(self, args):
        collection = args["--collection"]
        self.method = "POST"
        self.endpoint = f"/catalog/api/collections/{collection}/entity/bulk"
        self.payload = get_json(args, "--payloadFile")
        self.params = PurviewEndpoints.get_api_version_params("catalog")

    @decorator
    def entityChangeCollection(self, args):
        collection = args["--collection"]
        self.method = "POST"
        self.endpoint = f"/catalog/api/collections/{collection}/entity/moveHere"
        self.payload = get_json(args, "--payloadFile")
        self.params = PurviewEndpoints.get_api_version_params("catalog")

    # Business Metadata
    @decorator
    def entityImportBusinessMetadata(self, args):
        self.method = "POST"
        self.endpoint = PurviewEndpoints.ENTITY["business_metadata_import"]
        self.params = PurviewEndpoints.get_api_version_params("datamap")
        self.files = {"file": open(args["--bmFile"], "rb")}

    @decorator
    def entityGetBusinessMetadataTemplate(self, args):
        self.method = "GET"
        self.endpoint = PurviewEndpoints.ENTITY["business_metadata_template"]
        self.params = PurviewEndpoints.get_api_version_params("datamap")

    @decorator
    def entityAddOrUpdateBusinessMetadata(self, args):
        guid = args["--guid"][0]
        isOverwrite = args["--isOverwrite"]
        self.method = "POST"
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.ENTITY["business_metadata"], guid=guid
        )
        self.params = {**PurviewEndpoints.get_api_version_params("datamap"), "isOverwrite": isOverwrite}
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def entityDeleteBusinessMetadata(self, args):
        guid = args["--guid"][0]
        self.method = "DELETE"
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.ENTITY["business_metadata"], guid=guid
        )
        self.params = PurviewEndpoints.get_api_version_params("datamap")
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def entityAddOrUpdateBusinessAttribute(self, args):
        guid = args["--guid"][0]
        bmName = args["--bmName"]
        self.method = "POST"
        self.endpoint = f'{PurviewEndpoints.format_endpoint(PurviewEndpoints.ENTITY["business_metadata"], guid=guid)}/{bmName}'
        self.params = PurviewEndpoints.get_api_version_params("datamap")
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def entityDeleteBusinessAttribute(self, args):
        guid = args["--guid"][0]
        bmName = args["--bmName"]
        self.method = "DELETE"
        self.endpoint = f'{PurviewEndpoints.format_endpoint(PurviewEndpoints.ENTITY["business_metadata"], guid=guid)}/{bmName}'
        self.params = PurviewEndpoints.get_api_version_params("datamap")
        self.payload = get_json(args, "--payloadFile")

    # Enhanced Business Metadata Operations
    @decorator
    def entityBulkUpdateBusinessMetadata(self, args):
        """Bulk update business metadata across multiple entities"""
        self.method = "POST"
        self.endpoint = PurviewEndpoints.ENTITY["business_metadata_bulk"]
        self.params = PurviewEndpoints.get_api_version_params("datamap")
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def entityExportBusinessMetadata(self, args):
        """Export business metadata to CSV format"""
        self.method = "GET"
        self.endpoint = PurviewEndpoints.ENTITY["business_metadata_export"]
        self.params = {
            **PurviewEndpoints.get_api_version_params("datamap"),
            "format": args.get("--format", "csv"),
            "collectionName": args.get("--collectionName"),
        }

    @decorator
    def entityValidateBusinessMetadata(self, args):
        """Validate business metadata template before import"""
        self.method = "POST"
        self.endpoint = f'{PurviewEndpoints.ENTITY["business_metadata_import"]}/validate'
        self.params = PurviewEndpoints.get_api_version_params("datamap")
        self.files = {"file": open(args["--bmFile"], "rb")}

    @decorator
    def entityGetBusinessMetadataStatus(self, args):
        """Get status of business metadata import operation"""
        operationId = args["--operationId"]
        self.method = "GET"
        self.endpoint = (
            f'{PurviewEndpoints.ENTITY["business_metadata_import"]}/operations/{operationId}'
        )
        self.params = PurviewEndpoints.get_api_version_params("datamap")

    @decorator
    def entitySearchBusinessMetadata(self, args):
        """Search entities by business metadata attributes"""
        self.method = "POST"
        self.endpoint = (
            f"{PurviewEndpoints.DATAMAP_BASE}/{PurviewEndpoints.ATLAS_V2}/search/businessmetadata"
        )
        self.params = PurviewEndpoints.get_api_version_params("datamap")
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def entityGetBusinessMetadataStatistics(self, args):
        """Get business metadata usage statistics"""
        self.method = "GET"
        self.endpoint = f"{PurviewEndpoints.DATAMAP_BASE}/{PurviewEndpoints.ATLAS_V2}/entity/businessmetadata/statistics"
        self.params = PurviewEndpoints.get_api_version_params("datamap")
        if args.get("--collectionName"):
            self.params["collectionName"] = args["--collectionName"]

    # === CSV IMPORT/EXPORT OPERATIONS ===

    @no_api_call_decorator
    def entityImportFromCSV(self, args):
        """Import Entities from CSV - Enhanced Operation"""
        import pandas as pd
        import os

        # Debug: Print all available args to understand parameter naming
        print(f"🔧 Debug: Available args keys: {list(args.keys())}")

        # Click framework parameter naming
        csv_file = (
            args.get("csvfile")
            or args.get("--csvfile")
            or args.get("csv_file")
            or args.get("--csv-file")
        )
        print(f"📥 Preparing to import entities from CSV file: {csv_file}")

        if not csv_file or not os.path.exists(csv_file):
            raise ValueError(f"CSV file path is required and must exist. Got: {csv_file}")

        # Read CSV file
        try:
            df = pd.read_csv(csv_file)
        except Exception as e:
            raise ValueError(f"Failed to read CSV file: {str(e)}")

        # Validate required columns
        required_columns = ["typeName", "qualifiedName", "displayName"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        print(f"📁 Successfully validated CSV file: {csv_file}")
        print(f"📊 Found {len(df)} entities to import")

        # Handle batch_size parameter
        batch_size = (
            args.get("batchsize") or args.get("--batchsize") or args.get("--batch-size") or 10
        )
        print(f"⚙️ Processing in batches of {batch_size}")

        # Display what will be imported
        for index, row in df.iterrows():
            print(f"  {index + 1}. {row['typeName']}: {row['qualifiedName']}")

        print("✅ CSV validation completed successfully")
        print("🚀 Starting entity creation process...")

        # Step 4: Process entities in batches
        success_count = 0
        error_count = 0
        errors = []

        for index, row in df.iterrows():
            try:
                # Clean NaN values and convert to proper strings
                def clean_value(val, default=""):
                    import pandas as pd

                    if pd.isna(val) or val is None:
                        return default
                    return str(val).strip()

                type_name = clean_value(row.get("typeName"))
                qualified_name = clean_value(row.get("qualifiedName"))
                display_name = clean_value(row.get("displayName"), qualified_name)

                if not type_name or not qualified_name:
                    print(
                        f"⏭️  Skipping entity: missing required fields (typeName or qualifiedName)"
                    )
                    continue

                # Build entity payload
                entity_payload = {
                    "entity": {
                        "typeName": type_name,
                        "attributes": {
                            "qualifiedName": qualified_name,
                            "name": display_name,
                        },
                    }
                }

                # Add optional attributes if present
                for col in df.columns:
                    if col not in ["typeName", "qualifiedName", "displayName"] and not pd.isna(
                        row.get(col)
                    ):
                        entity_payload["entity"]["attributes"][col] = clean_value(row.get(col))

                # Add collection if specified
                collection_name = clean_value(row.get("collectionName"))
                if collection_name:
                    entity_payload["entity"]["collections"] = [{"referenceName": collection_name}]

                entity_args = {"--payloadFile": None}  # We'll set payload directly

                print(f"📝 Creating entity: {type_name} - {qualified_name}")

                # Create a temporary JSON file for the payload
                import tempfile
                import json

                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".json", delete=False
                ) as temp_file:
                    json.dump(entity_payload, temp_file, indent=2)
                    temp_filename = temp_file.name

                try:
                    entity_args["--payloadFile"] = temp_filename
                    result = self.entityCreate(entity_args)

                    if result and (not isinstance(result, dict) or result.get("status") != "error"):
                        success_count += 1
                        print(f"   ✅ Success: {qualified_name}")
                    else:
                        error_count += 1
                        error_msg = (
                            result.get("message", "Unknown error")
                            if isinstance(result, dict)
                            else "API call failed"
                        )
                        errors.append(f"{qualified_name}: {error_msg}")
                        print(f"   ❌ Failed: {qualified_name} - {error_msg}")
                finally:
                    # Clean up temporary file
                    try:
                        os.unlink(temp_filename)
                    except:
                        pass

                # Process in batches - pause between batches
                if (index + 1) % batch_size == 0:
                    print(
                        f"⏸️  Batch {(index + 1) // batch_size} completed. Processed {index + 1}/{len(df)} entities"
                    )

            except Exception as e:
                error_count += 1
                error_msg = str(e)
                errors.append(f"{row.get('qualifiedName', 'Unknown')}: {error_msg}")
                print(f"   ❌ Exception for {row.get('qualifiedName', 'Unknown')}: {error_msg}")

        # Final summary
        print(f"\n📊 Import Summary:")
        print(f"   ✅ Successful: {success_count}")
        print(f"   ❌ Failed: {error_count}")
        print(f"   📄 Total processed: {len(df)}")

        if errors:
            print(f"\n🔍 Errors encountered:")
            for error in errors:
                print(f"   • {error}")

        return {
            "status": "success" if error_count == 0 else "partial",
            "message": f"Import completed. Success: {success_count}, Failed: {error_count}",
            "details": {
                "total": len(df),
                "success": success_count,
                "failed": error_count,
                "errors": errors,
            },
        }

    @no_api_call_decorator
    def entityExportToCSV(self, args):
        """Export Entities to CSV - Enhanced Operation"""
        import pandas as pd
        from datetime import datetime

        # Get search parameters
        search_query = args.get("query") or args.get("--query") or "*"
        entity_type = args.get("entitytype") or args.get("--entity-type")
        collection_name = args.get("collectionname") or args.get("--collection-name")

        # Use search to get entities
        search_args = {}

        # Build search payload
        search_payload = {"keywords": search_query, "limit": args.get("limit") or 1000, "offset": 0}

        if entity_type:
            search_payload["filter"] = {"entityType": entity_type}

        if collection_name:
            if "filter" not in search_payload:
                search_payload["filter"] = {}
            search_payload["filter"]["collectionId"] = collection_name

        # Create temporary search payload file
        import tempfile
        import json

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as temp_file:
            json.dump(search_payload, temp_file, indent=2)
            search_args["--payloadFile"] = temp_file.name

        # Note: This would require a search method in entity class
        # For now, we'll simulate with a basic structure
        print(
            f"🔍 Search parameters: query='{search_query}', type='{entity_type}', collection='{collection_name}'"
        )

        # Simulated entity data structure - in real implementation this would come from search results
        entities_data = {
            "data": {
                "value": [
                    # This would be populated from actual search results
                ]
            }
        }

        print(f"✅ Found {len(entities_data.get('data', {}).get('value', []))} entities")

        # Step 2: Process CLI parameters
        output_file = args.get("outputfile") or args.get("--outputfile") or args.get("output_file")
        if not output_file:
            # Generate default filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"entities_export_{timestamp}.csv"

        include_metadata = args.get("include_metadata") or args.get("--include-metadata") or True
        include_attributes = (
            args.get("include_attributes") or args.get("--include-attributes") or True
        )

        print(f"📁 Output file: {output_file}")
        print(f"⚙️ Options: Metadata={include_metadata}, Attributes={include_attributes}")

        # Step 3: Process entities data for CSV export
        csv_data = []
        entities = entities_data.get("data", {}).get("value", [])

        for entity in entities:
            row = {
                "typeName": entity.get("typeName", ""),
                "qualifiedName": entity.get("attributes", {}).get("qualifiedName", ""),
                "displayName": entity.get("displayName", ""),
                "guid": entity.get("guid", ""),
                "status": entity.get("status", ""),
            }

            # Add collection information
            collections = entity.get("collections", [])
            if collections:
                row["collectionName"] = collections[0].get("referenceName", "")

            # Add attributes if requested
            if include_attributes:
                attributes = entity.get("attributes", {})
                for attr_name, attr_value in attributes.items():
                    if attr_name not in ["qualifiedName"]:  # Skip already included attributes
                        row[f"attr_{attr_name}"] = str(attr_value) if attr_value is not None else ""

            # Add metadata if requested
            if include_metadata:
                row["createTime"] = entity.get("createTime", "")
                row["updateTime"] = entity.get("updateTime", "")
                row["createdBy"] = entity.get("createdBy", "")
                row["updatedBy"] = entity.get("updatedBy", "")

            csv_data.append(row)

        # Step 4: Create and export CSV
        try:
            df = pd.DataFrame(csv_data)
            df.to_csv(output_file, index=False)

            print(f"✅ Export completed: {output_file}")
            print(f"📊 Exported {len(csv_data)} entities")

            # Show summary of what was exported
            if csv_data:
                print("\n📋 Export Summary:")
                print(f"   • Entities: {len(csv_data)}")
                print(f"   • Columns: {len(df.columns)}")
                print(f"   • Attributes info: {'✓' if include_attributes else '✗'}")
                print(f"   • Metadata info: {'✓' if include_metadata else '✗'}")

            return {
                "status": "success",
                "message": f"Exported {len(csv_data)} entities to {output_file}",
            }

        except Exception as e:
            print(f"❌ Error creating CSV file: {str(e)}")
            return {"status": "error", "message": f"Failed to create CSV: {str(e)}"}
