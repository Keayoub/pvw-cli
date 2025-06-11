"""
Collections Management Client for Azure Purview
Based on official API: https://learn.microsoft.com/en-us/rest/api/purview/accountdataplane/collections
API Version: 2019-11-01-preview

Official Collections Operations:
1. List Collections - GET /collections
2. Get Collection - GET /collections/{collectionName}
3. Create Or Update Collection - PUT /collections/{collectionName}
4. Delete Collection - DELETE /collections/{collectionName}
5. Get Collection Path - GET /collections/{collectionName}/getCollectionPath
6. List Child Collection Names - GET /collections/{collectionName}/getChildCollectionNames
"""

from .endpoint import Endpoint, decorator, get_json, no_api_call_decorator
from .endpoints import PurviewEndpoints
import random
import string


def get_random_string(length):
    """Generate random string for collection names"""
    return "".join(random.choice(string.ascii_letters + string.digits) for i in range(length))


class Collections(Endpoint):
    """Collections Management Operations - Official API Operations Only"""

    def __init__(self):
        Endpoint.__init__(self)
        self.app = "account"

    # === CORE COLLECTION OPERATIONS ===

    @decorator
    def collectionsGetCollections(self, args):
        """List Collections - Official API Operation"""
        self.method = "GET"
        self.endpoint = PurviewEndpoints.COLLECTIONS["base"]
        self.params = PurviewEndpoints.get_api_version_params("collections")

    @decorator
    def collectionsGetCollection(self, args):
        """Get Collection - Official API Operation"""
        self.method = "GET"
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.COLLECTIONS["collection"], collectionName=args["--collectionName"]
        )
        self.params = PurviewEndpoints.get_api_version_params("collections")

    @decorator
    def collectionsCreateCollection(self, args):
        """Create Collection - Official API Operation"""
        collection_name = args.get("--collectionName") or get_random_string(6)
        self.method = "PUT"
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.COLLECTIONS["collection"], collectionName=collection_name
        )
        self.params = PurviewEndpoints.get_api_version_params("collections")        # Build payload according to official API specification for creation
        if args.get("--payloadFile"):
            self.payload = get_json(args, "--payloadFile")
        else:
            import os
            self.payload = {
                "friendlyName": args.get("--friendlyName", collection_name),
                "description": args.get("--description", ""),
                "parentCollection": {"referenceName": args.get("--parentCollection", os.getenv("PURVIEW_ACCOUNT_NAME"))},
            }

    @decorator
    def collectionsUpdateCollection(self, args):
        """Update Collection - Official API Operation"""
        collection_name = args.get("--collectionName")
        if not collection_name:
            raise ValueError("Collection name is required for update operation")

        self.method = "PUT"
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.COLLECTIONS["collection"], collectionName=collection_name
        )
        self.params = PurviewEndpoints.get_api_version_params("collections")        # Build payload according to official API specification for update
        if args.get("--payloadFile"):
            self.payload = get_json(args, "--payloadFile")
        else:
            import os
            self.payload = {
                "friendlyName": args.get("--friendlyName", collection_name),
                "description": args.get("--description", ""),
                "parentCollection": {"referenceName": args.get("--parentCollection", os.getenv("PURVIEW_ACCOUNT_NAME"))},
            }

    @decorator
    def collectionsCreateOrUpdateCollection(self, args):
        """Create Or Update Collection - Official API Operation (Backward Compatibility)"""
        collection_name = args.get("--collectionName") or get_random_string(6)
        self.method = "PUT"
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.COLLECTIONS["collection"], collectionName=collection_name
        )
        self.params = PurviewEndpoints.get_api_version_params("collections")        # Build payload according to official API specification
        if args.get("--payloadFile"):
            self.payload = get_json(args, "--payloadFile")
        else:
            import os
            self.payload = {
                "friendlyName": args.get("--friendlyName", collection_name),
                "description": args.get("--description", ""),
                "parentCollection": {"referenceName": args.get("--parentCollection", os.getenv("PURVIEW_ACCOUNT_NAME"))},
            }

    @decorator
    def collectionsDeleteCollection(self, args):
        """Delete Collection - Official API Operation"""
        self.method = "DELETE"
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.COLLECTIONS["collection"], collectionName=args["--collectionName"]
        )
        self.params = PurviewEndpoints.get_api_version_params("collections")

    # === COLLECTION HIERARCHY OPERATIONS ===

    @decorator
    def collectionsGetCollectionPath(self, args):
        """Get Collection Path - Official API Operation"""
        self.method = "GET"
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.COLLECTIONS["collection_path"], collectionName=args["--collectionName"]
        )
        self.params = PurviewEndpoints.get_api_version_params("collections")

    @decorator
    def collectionsGetChildCollectionNames(self, args):
        """List Child Collection Names - Official API Operation"""
        self.method = "GET"
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.COLLECTIONS["child_collection_names"],
            collectionName=args["--collectionName"],
        )
        self.params = PurviewEndpoints.get_api_version_params(
            "collections"
        )  # === CSV IMPORT/EXPORT OPERATIONS ===

    @no_api_call_decorator
    def collectionsImportFromCSV(self, args):
        """Import Collections from CSV - Enhanced Operation"""
        import pandas as pd
        import os

        # Debug: Print all available args to understand parameter naming
        print(f"🔧 Debug: Available args keys: {list(args.keys())}")

        # Click framework parameter naming:
        # --csvfile -> csvfile (since it's a single word in CLI definition)
        # --csv-file -> csv_file (if it were kebab-case)
        csv_file = (
            args.get("csvfile")
            or args.get("--csvfile")
            or args.get("csv_file")
            or args.get("--csv-file")
        )
        print(f"📥 Preparing to import collections from CSV file: {csv_file}")

        if not csv_file or not os.path.exists(csv_file):
            raise ValueError(f"CSV file path is required and must exist. Got: {csv_file}")

        # Read CSV file
        try:
            df = pd.read_csv(csv_file)
        except Exception as e:
            raise ValueError(f"Failed to read CSV file: {str(e)}")

        # Validate required columns
        required_columns = ["collectionName", "friendlyName"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        print(f"📁 Successfully validated CSV file: {csv_file}")
        print(
            f"📊 Found {len(df)} collections to import"
        )  # Handle batch_size parameter (also snake_case conversion)
        batch_size = (
            args.get("batchsize") or args.get("--batchsize") or args.get("--batch-size") or 10
        )
        print(f"⚙️ Processing in batches of {batch_size}")

        # Display what will be imported
        for index, row in df.iterrows():
            print(f"  {index + 1}. {row['collectionName']} - {row['friendlyName']}")

        print("✅ CSV validation completed successfully")
        print("🚀 Starting collection creation/update process...")

        # Step 4: Process collections in batches
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

                collection_name = clean_value(row.get("collectionName"))

                # Skip default/root collections that cannot be updated
                if not collection_name or collection_name.lower() in [
                    "root",
                ]:
                    print(f"⏭️  Skipping system collection: {collection_name} (cannot be updated)")
                    continue

                # Prepare arguments for collection creation/update
                parent_collection_name = clean_value(row.get("parentCollection"))

                # Handle parent collection logic:
                # - If no parent specified or parent is empty, use the account name as root
                # - If parent is "root", convert to account name
                # - Otherwise use the specified parent
                if not parent_collection_name or parent_collection_name.lower() == "root":
                    # Default to the account name (which is the actual root collection)
                    parent_collection_name = self.app.account_name

                collection_args = {
                    "--collectionName": collection_name,
                    "--friendlyName": clean_value(row.get("friendlyName"), collection_name),
                    "--description": clean_value(row.get("description"), ""),
                    "--parentCollection": parent_collection_name,
                }

                # Remove empty values to use defaults
                collection_args = {k: v for k, v in collection_args.items() if v and v.strip()}

                print(f"📝 Creating/updating collection: {collection_name} (parent: {parent_collection_name})")

                # Use existing method to create or update collection
                result = self.collectionsCreateOrUpdateCollection(collection_args)

                if result and (not isinstance(result, dict) or result.get("status") != "error"):
                    success_count += 1
                    print(f"   ✅ Success: {collection_name}")
                else:
                    error_count += 1
                    error_msg = (
                        result.get("message", "Unknown error")
                        if isinstance(result, dict)
                        else "API call failed"
                    )
                    errors.append(f"{collection_name}: {error_msg}")
                    print(f"   ❌ Failed: {collection_name} - {error_msg}")

                # Process in batches - pause between batches
                if (index + 1) % batch_size == 0:
                    print(
                        f"⏸️  Batch {(index + 1) // batch_size} completed. Processed {index + 1}/{len(df)} collections"
                    )

            except Exception as e:
                error_count += 1
                error_msg = str(e)
                errors.append(f"{row.get('collectionName', 'Unknown')}: {error_msg}")
                print(f"❌ Exception for {row.get('collectionName', 'Unknown')}: {error_msg}")

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
    def collectionsExportToCSV(self, args):
        """Export Collections to CSV - Enhanced Operation"""
        import pandas as pd
        from datetime import datetime

        print("📤 Fetching collections from Azure Purview...")

        # Step 1: Use existing collectionsGetCollections method
        collections_data = self.collectionsGetCollections({})

        if (
            not collections_data
            or not isinstance(collections_data, dict)
            or "data" not in collections_data
        ):
            print("❌ Failed to fetch collections or no collections found")
            return {"status": "error", "message": "No collections data available"}

        collections = collections_data["data"]["value"]

        print(f"🔍 Fetched collections data: {collections}")
        print(f"✅ Found {len(collections)} collections")

        if not collections:
            print("❌ No collections found to export")
            return {"status": "error", "message": "No collections to export"}

        # Step 2: Process CLI parameters
        output_file = args.get("outputfile") or args.get("--outputfile") or args.get("output_file")
        if not output_file:
            # Generate default filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"collections_export_{timestamp}.csv"

        include_hierarchy = args.get("include_hierarchy") or args.get("--include-hierarchy") or True
        include_metadata = args.get("include_metadata") or args.get("--include-metadata") or True

        print(f"📁 Output file: {output_file}")
        print(
            f"⚙️ Options: Hierarchy={include_hierarchy}, Metadata={include_metadata}"
        )  # Step 3: Process collections data for CSV export
        csv_data = []
        for collection in collections:
            collection_name = collection.get("name", "")

            # Skip the default/root collection (usually the account name)
            # These collections cannot be created/updated via API
            if (
                not collection_name
                or collection_name.startswith("fabricpurview")
                or collection.get("friendlyName") == collection_name
                and collection.get("description") == "The default container."
            ):
                print(f"⏭️  Skipping default collection: {collection_name} (system collection)")
                continue

            row = {
                "collectionName": collection_name,
                "friendlyName": collection.get("friendlyName", ""),
                "description": collection.get("description", ""),
                "parentCollection": (
                    collection.get("parentCollection", {}).get("referenceName", "")
                    if collection.get("parentCollection")
                    else ""
                ),
            }

            # Add hierarchy information if requested
            if include_hierarchy:
                # Calculate collection path and level
                path_parts = []
                current = collection
                level = 0

                # Build path by traversing parent chain
                while current and current.get("name"):
                    path_parts.insert(0, current.get("name"))
                    parent = current.get("parentCollection")
                    if parent and parent.get("name"):
                        level += 1
                        # Note: We can't traverse full path without additional API calls
                        # So we'll show what we have
                        break
                    else:
                        break

                row["collectionPath"] = " > ".join(path_parts)
                row["level"] = level

            # Add metadata if requested
            if include_metadata:
                system_data = collection.get("systemData", {})
                row["systemData_createdAt"] = system_data.get("createdAt", "")
                row["systemData_lastModifiedAt"] = system_data.get("lastModifiedAt", "")
                row["systemData_createdBy"] = system_data.get("createdBy", "")

            csv_data.append(row)

        # Step 4: Create and export CSV
        try:
            df = pd.DataFrame(csv_data)
            df.to_csv(output_file, index=False)

            print(f"✅ Export completed: {output_file}")
            print(f"📊 Exported {len(csv_data)} collections")

            # Show summary of what was exported
            if csv_data:
                print("\n📋 Export Summary:")
                print(f"   • Collections: {len(csv_data)}")
                print(f"   • Columns: {len(df.columns)}")
                print(f"   • Hierarchy info: {'✓' if include_hierarchy else '✗'}")
                print(f"   • Metadata info: {'✓' if include_metadata else '✗'}")

            return {
                "status": "success",
                "message": f"Exported {len(csv_data)} collections to {output_file}",
            }

        except Exception as e:
            print(f"❌ Error creating CSV file: {str(e)}")
            return {"status": "error", "message": f"Failed to create CSV: {str(e)}"}
