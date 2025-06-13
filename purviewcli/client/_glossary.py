from .endpoint import Endpoint, decorator, get_json, no_api_call_decorator
from .endpoints import PurviewEndpoints

class Glossary(Endpoint):
    def __init__(self):
        Endpoint.__init__(self)
        self.app = 'catalog'

    @decorator
    def glossaryRead(self, args):
        self.method = 'GET'
        if args["--glossaryGuid"] is None:
            self.endpoint = PurviewEndpoints.GLOSSARY['base']
        else:
            self.endpoint = f'{PurviewEndpoints.GLOSSARY["base"]}/{args["--glossaryGuid"]}'
        self.params = {'limit': args['--limit'], 'offset': args['--offset'], 'sort': args['--sort'], 'ignoreTermsAndCategories': args['--ignoreTermsAndCategories']}

    @decorator
    def glossaryCreate(self, args):
        self.method = 'POST'
        self.endpoint = PurviewEndpoints.GLOSSARY['base']
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def glossaryCreateCategories(self, args):
        self.method = 'POST'
        self.endpoint = PurviewEndpoints.GLOSSARY['categories']
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def glossaryCreateCategory(self, args):
        self.method = 'POST'
        self.endpoint = PurviewEndpoints.GLOSSARY['category']
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def glossaryDeleteCategory(self, args):
        self.method = 'DELETE'
        self.endpoint = f'{PurviewEndpoints.GLOSSARY["category"]}/{args["--categoryGuid"]}'

    @decorator
    def glossaryReadCategory(self, args):
        self.method = 'GET'
        self.endpoint = f'{PurviewEndpoints.GLOSSARY["category"]}/{args["--categoryGuid"]}'
        self.params = {'limit': args['--limit'], 'offset': args['--offset'], 'sort': args['--sort']}

    @decorator
    def glossaryPutCategory(self, args):
        self.method = 'PUT'
        self.endpoint = f'{PurviewEndpoints.GLOSSARY["category"]}/{args["--categoryGuid"]}'
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def glossaryPutCategoryPartial(self, args):
        self.method = 'PUT'
        self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.GLOSSARY['category_partial'], categoryGuid=args["--categoryGuid"])
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def glossaryReadCategoryRelated(self, args):
        self.method = 'GET'
        self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.GLOSSARY['category_related'], categoryGuid=args["--categoryGuid"])

    @decorator
    def glossaryReadCategoryTerms(self, args):
        self.method = 'GET'
        self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.GLOSSARY['category_terms'], categoryGuid=args["--categoryGuid"])
        self.params = {'limit': args['--limit'], 'offset': args['--offset'], 'sort': args['--sort']}

    @decorator
    def glossaryCreateTerm(self, args):
        self.method = 'POST'
        self.endpoint = PurviewEndpoints.GLOSSARY['term']
        self.payload = get_json(args, '--payloadFile')
        self.params = {'includeTermHierarchy': args['--includeTermHierarchy']}

    @decorator
    def glossaryDeleteTerm(self, args):
        self.method = 'DELETE'
        self.endpoint = f'{PurviewEndpoints.GLOSSARY["term"]}/{args["--termGuid"][0]}'

    @decorator
    def glossaryReadTerm(self, args):
        self.method = 'GET'
        self.endpoint = f'{PurviewEndpoints.GLOSSARY["term"]}/{args["--termGuid"][0]}'
        self.params = {'includeTermHierarchy': args['--includeTermHierarchy']}

    @decorator
    def glossaryPutTerm(self, args):
        self.method = 'PUT'
        self.endpoint = f'{PurviewEndpoints.GLOSSARY["term"]}/{args["--termGuid"][0]}'
        self.params = {'includeTermHierarchy': args['--includeTermHierarchy']}
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def glossaryPutTermPartial(self, args):
        self.method = 'PUT'
        self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.GLOSSARY['term_partial'], termGuid=args["--termGuid"][0])
        self.params = {'includeTermHierarchy': args['--includeTermHierarchy']}
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def glossaryCreateTerms(self, args):
        self.method = 'POST'
        self.endpoint = PurviewEndpoints.GLOSSARY['terms']
        self.payload = get_json(args, '--payloadFile')
        self.params = {'includeTermHierarchy': args['--includeTermHierarchy']}

    @decorator
    def glossaryDeleteTermsAssignedEntities(self, args):
        self.method = 'DELETE'
        self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.GLOSSARY['term_assigned_entities'], termGuid=args["--termGuid"][0])
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def glossaryReadTermsAssignedEntities(self, args):
        self.method = 'GET'
        self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.GLOSSARY['term_assigned_entities'], termGuid=args["--termGuid"][0])
        self.params = {'limit': args['--limit'], 'offset': args['--offset'], 'sort': args['--sort']}

    @decorator
    def glossaryCreateTermsAssignedEntities(self, args):
        self.method = 'POST'
        self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.GLOSSARY['term_assigned_entities'], termGuid=args["--termGuid"][0])
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def glossaryPutTermsAssignedEntities(self, args):
        self.method = 'PUT'
        self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.GLOSSARY['term_assigned_entities'], termGuid=args["--termGuid"][0])
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def glossaryReadTermsRelated(self, args):
        self.method = 'GET'
        self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.GLOSSARY['term_related'], termGuid=args["--termGuid"][0])
        self.params = {'limit': args['--limit'], 'offset': args['--offset'], 'sort': args['--sort']}

    @decorator
    def glossaryDelete(self, args):
        self.method = 'DELETE'
        self.endpoint = f'{PurviewEndpoints.GLOSSARY["base"]}/{args["--glossaryGuid"]}'

    @decorator
    def glossaryPut(self, args):
        self.method = 'PUT'
        self.endpoint = f'{PurviewEndpoints.GLOSSARY["base"]}/{args["--glossaryGuid"]}'
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def glossaryReadCategories(self, args):
        self.method = 'GET'
        self.endpoint = f'{PurviewEndpoints.GLOSSARY["base"]}/{args["--glossaryGuid"]}/categories'
        self.params = {'limit': args['--limit'], 'offset': args['--offset'], 'sort': args['--sort']}

    @decorator
    def glossaryReadCategoriesHeaders(self, args):
        self.method = 'GET'
        self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.GLOSSARY['categories_headers'], glossaryGuid=args["--glossaryGuid"])
        self.params = {'limit': args['--limit'], 'offset': args['--offset'], 'sort': args['--sort']}

    @decorator
    def glossaryReadDetailed(self, args):
        self.method = 'GET'
        self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.GLOSSARY['detailed'], glossaryGuid=args["--glossaryGuid"])
        self.params = {'includeTermHierarchy': args['--includeTermHierarchy']}

    @decorator
    def glossaryPutPartial(self, args):
        self.method = 'PUT'
        self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.GLOSSARY['partial'], glossaryGuid=args["--glossaryGuid"])
        self.payload = get_json(args, '--payloadFile')
        self.params = {'includeTermHierarchy': args['--includeTermHierarchy']}

    @decorator
    def glossaryReadTerms(self, args):
        glossaryName = 'Glossary'
        self.method = 'GET'
        if args['--glossaryGuid']:
            self.endpoint = f'{PurviewEndpoints.GLOSSARY["base"]}/{args["--glossaryGuid"]}/terms'
        else:
            self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.GLOSSARY['terms_import_by_name'], glossaryName=glossaryName).replace('/terms/import', '/terms')
        self.params = {'limit': args['--limit'], 'offset': args['--offset'], 'sort': args['--sort'], 'extInfo': args['--extInfo'], 'includeTermHierarchy': args['--includeTermHierarchy'], 'api-version': '2021-05-01-preview'}

    @decorator
    def glossaryReadTermsHeaders(self, args):
        self.method = 'GET'
        self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.GLOSSARY['terms_headers'], glossaryGuid=args["--glossaryGuid"])
        self.params = {'limit': args['--limit'], 'offset': args['--offset'], 'sort': args['--sort']}

    @decorator
    def glossaryCreateTermsExport(self, args):
        self.method = 'POST'
        self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.GLOSSARY['terms_export'], glossaryGuid=args["--glossaryGuid"])
        self.payload = args['--termGuid']
        self.params = {
            'api-version': '2021-05-01-preview',
            'includeTermHierarchy': args['--includeTermHierarchy']
            }

    @decorator
    def glossaryCreateTermsImport(self, args):
        glossaryName = 'Glossary'
        self.method = 'POST'
        if args['--glossaryGuid']:
            self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.GLOSSARY['terms_import'], glossaryGuid=args["--glossaryGuid"])
        else:
            self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.GLOSSARY['terms_import_by_name'], glossaryName=glossaryName)
        self.files = {'file': open(args["--glossaryFile"], 'rb')}
        self.params = {
            **PurviewEndpoints.get_api_version_params("datamap"),
            'includeTermHierarchy': args['--includeTermHierarchy']
        }
        
    @decorator
    def glossaryReadTermsImport(self, args):
        self.method = 'GET'
        self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.GLOSSARY['terms_import_operation'], operationGuid=args["--operationGuid"])
        self.params = PurviewEndpoints.get_api_version_params("datamap")


    # === CSV IMPORT/EXPORT OPERATIONS ===
    @no_api_call_decorator
    def glossaryImportTermsFromCSV(self, args):
        """Import Glossary Terms from CSV - Enhanced Operation"""
        import pandas as pd
        import os

        print(f"🔧 Debug: Available args keys: {list(args.keys())}")

        # Click framework parameter naming
        csv_file = (
            args.get("csvfile")
            or args.get("--csvfile")
            or args.get("csv_file")
            or args.get("--csv-file")
        )
        glossary_guid = args.get("glossary_guid") or args.get("--glossary-guid")
        
        print(f"📥 Preparing to import glossary terms from CSV file: {csv_file}")
        print(f"🎯 Target glossary GUID: {glossary_guid}")

        if not csv_file or not os.path.exists(csv_file):
            raise ValueError(f"CSV file path is required and must exist. Got: {csv_file}")
        
        if not glossary_guid:
            raise ValueError("Glossary GUID is required for terms import")

        # Read CSV file
        try:
            df = pd.read_csv(csv_file)
        except Exception as e:
            raise ValueError(f"Failed to read CSV file: {str(e)}")

        # Validate required columns
        required_columns = ["name", "definition"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        print(f"📁 Successfully validated CSV file: {csv_file}")
        print(f"📊 Found {len(df)} terms to import")

        # Handle batch_size parameter
        batch_size = (
            args.get("batchsize") or args.get("--batchsize") or args.get("--batch-size") or 10
        )
        print(f"⚙️ Processing in batches of {batch_size}")

        # Display what will be imported
        for index, row in df.iterrows():
            print(f"  {index + 1}. {row['name']} - {row.get('definition', 'No definition')[:50]}...")

        print("✅ CSV validation completed successfully")
        print("🚀 Starting glossary term creation process...")

        # Process terms in batches
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

                term_name = clean_value(row.get("name"))
                term_definition = clean_value(row.get("definition"))

                if not term_name or not term_definition:
                    print(f"⏭️  Skipping term: missing required fields (name or definition)")
                    continue

                # Build term payload
                term_payload = {
                    "name": term_name,
                    "shortDescription": term_definition,
                    "longDescription": clean_value(row.get("longDescription"), term_definition),
                    "anchor": {
                        "glossaryGuid": glossary_guid
                    },
                    "status": clean_value(row.get("status"), "Active"),
                }

                # Add optional fields if present
                if not pd.isna(row.get("abbreviation")):
                    term_payload["abbreviation"] = clean_value(row.get("abbreviation"))
                
                if not pd.isna(row.get("usage")):
                    term_payload["usage"] = clean_value(row.get("usage"))

                # Add synonyms if present (comma-separated)
                synonyms = clean_value(row.get("synonyms"))
                if synonyms:
                    term_payload["synonyms"] = [{"displayText": s.strip()} for s in synonyms.split(",") if s.strip()]

                term_args = {
                    "--payloadFile": None,  # We'll set payload directly
                    "--includeTermHierarchy": False
                }

                print(f"📝 Creating term: {term_name}")

                # Create a temporary JSON file for the payload
                import tempfile
                import json
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
                    json.dump(term_payload, temp_file, indent=2)
                    temp_filename = temp_file.name

                try:
                    term_args["--payloadFile"] = temp_filename
                    result = self.glossaryCreateTerm(term_args)

                    if result and (not isinstance(result, dict) or result.get("status") != "error"):
                        success_count += 1
                        print(f"   ✅ Success: {term_name}")
                    else:
                        error_count += 1
                        error_msg = (
                            result.get("message", "Unknown error")
                            if isinstance(result, dict)
                            else "API call failed"
                        )
                        errors.append(f"{term_name}: {error_msg}")
                        print(f"   ❌ Failed: {term_name} - {error_msg}")
                finally:
                    # Clean up temporary file
                    try:
                        os.unlink(temp_filename)
                    except:
                        pass

                # Process in batches
                if (index + 1) % batch_size == 0:
                    print(f"⏸️  Batch {(index + 1) // batch_size} completed. Processed {index + 1}/{len(df)} terms")

            except Exception as e:
                error_count += 1
                error_msg = str(e)
                errors.append(f"{row.get('name', 'Unknown')}: {error_msg}")
                print(f"   ❌ Exception for {row.get('name', 'Unknown')}: {error_msg}")

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
    def glossaryExportToCSV(self, args):
        """Export Glossary and Terms to CSV - Enhanced Operation"""
        import pandas as pd
        from datetime import datetime

        print("📤 Fetching glossaries from Microsoft Purview...")

        # Step 1: Get all glossaries
        glossaries_data = self.glossaryRead({"--glossaryGuid": None, "--limit": 1000, "--offset": 0, "--sort": "ASC", "--ignoreTermsAndCategories": False})

        if not glossaries_data or not isinstance(glossaries_data, dict):
            print("❌ Failed to fetch glossaries")
            return {"status": "error", "message": "No glossaries data available"}

        glossaries = glossaries_data.get("data", [])
        if isinstance(glossaries, dict) and "value" in glossaries:
            glossaries = glossaries["value"]

        print(f"✅ Found {len(glossaries)} glossaries")

        # Step 2: Process CLI parameters
        output_file = args.get("outputfile") or args.get("--outputfile") or args.get("output_file")
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"glossary_export_{timestamp}.csv"

        export_type = args.get("export_type") or args.get("--export-type") or "both"  # both, glossaries, terms
        include_metadata = args.get("include_metadata") or args.get("--include-metadata") or True

        print(f"📁 Output file: {output_file}")
        print(f"⚙️ Export type: {export_type}, Metadata: {include_metadata}")

        # Step 3: Process glossary and terms data for CSV export
        csv_data = []

        for glossary in glossaries:
            glossary_guid = glossary.get("guid", "")
            glossary_name = glossary.get("name", "")

            if export_type in ["both", "glossaries"]:
                # Add glossary row
                row = {
                    "type": "glossary",
                    "name": glossary_name,
                    "guid": glossary_guid,
                    "definition": glossary.get("shortDescription", ""),
                    "longDescription": glossary.get("longDescription", ""),
                    "status": glossary.get("status", ""),
                    "language": glossary.get("language", ""),
                    "usage": glossary.get("usage", ""),
                    "parentGlossaryGuid": "",
                    "parentTermGuid": "",
                    "abbreviation": "",
                    "synonyms": ""
                }

                if include_metadata:
                    row["createTime"] = glossary.get("createTime", "")
                    row["updateTime"] = glossary.get("updateTime", "")
                    row["createdBy"] = glossary.get("createdBy", "")
                    row["updatedBy"] = glossary.get("updatedBy", "")

                csv_data.append(row)

            # Get terms for this glossary if exporting terms
            if export_type in ["both", "terms"]:
                try:
                    # Get terms for this glossary
                    terms_data = self.glossaryRead({
                        "--glossaryGuid": glossary_guid,
                        "--limit": 1000,
                        "--offset": 0,
                        "--sort": "ASC",
                        "--ignoreTermsAndCategories": False
                    })

                    if terms_data and isinstance(terms_data, dict):
                        terms = terms_data.get("terms", [])
                        
                        for term in terms:
                            term_row = {
                                "type": "term",
                                "name": term.get("displayText", ""),
                                "guid": term.get("termGuid", ""),
                                "definition": term.get("shortDescription", ""),
                                "longDescription": term.get("longDescription", ""),
                                "status": term.get("status", ""),
                                "language": term.get("language", ""),
                                "usage": term.get("usage", ""),
                                "parentGlossaryGuid": glossary_guid,
                                "parentTermGuid": "",
                                "abbreviation": term.get("abbreviation", ""),
                                "synonyms": ", ".join([s.get("displayText", "") for s in term.get("synonyms", [])])
                            }

                            if include_metadata:
                                term_row["createTime"] = term.get("createTime", "")
                                term_row["updateTime"] = term.get("updateTime", "")
                                term_row["createdBy"] = term.get("createdBy", "")
                                term_row["updatedBy"] = term.get("updatedBy", "")

                            csv_data.append(term_row)

                except Exception as e:
                    print(f"⚠️  Warning: Failed to get terms for glossary {glossary_name}: {str(e)}")

        # Step 4: Create and export CSV
        try:
            df = pd.DataFrame(csv_data)
            df.to_csv(output_file, index=False)

            print(f"✅ Export completed: {output_file}")
            print(f"📊 Exported {len(csv_data)} items")

            # Show summary of what was exported
            if csv_data:
                print("\n📋 Export Summary:")
                print(f"   • Total items: {len(csv_data)}")
                print(f"   • Glossaries: {len([item for item in csv_data if item.get('type') == 'glossary'])}")
                print(f"   • Terms: {len([item for item in csv_data if item.get('type') == 'term'])}")
                print(f"   • Columns: {len(df.columns)}")
                print(f"   • Metadata info: {'✓' if include_metadata else '✗'}")

            return {
                "status": "success",
                "message": f"Exported {len(csv_data)} items to {output_file}",
            }

        except Exception as e:
            print(f"❌ Error creating CSV file: {str(e)}")
            return {"status": "error", "message": f"Failed to create CSV: {str(e)}"}