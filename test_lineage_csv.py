"""
Test script for lineage CSV import functionality
"""
import sys
sys.path.insert(0, '.')

from purviewcli.client._lineage import Lineage

# Test CSV validation
lineage_client = Lineage()

# Test validation
print("Testing CSV validation...")
args_validate = {"csv_file": "trace.csv"}
result = lineage_client.lineageCSVValidate(args_validate)
print("Validation result:", result)

# Test CSV processing (dry run - just check payload generation)
if result.get("success"):
    print("\nTesting CSV processing (payload generation)...")
    args_process = {"csv_file": "trace.csv"}
    try:
        payload = lineage_client._process_csv_lineage("trace.csv", {})
        print("Payload generated successfully!")
        print("Entities:", len(payload.get("entities", [])))
        print("Relationships:", len(payload.get("relationships", [])))
        import json
        print("\nGenerated payload:")
        print(json.dumps(payload, indent=2))
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
