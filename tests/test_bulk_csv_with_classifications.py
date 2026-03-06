#!/usr/bin/env python3
"""
Test script for bulk CSV operations with classifications support
Demonstrates the new classification features in bulk-create-csv and bulk-update-csv
"""

import os
import sys
import pandas as pd

# Test data for bulk-create-csv
create_test_data = {
    'typeName': [
        'azure_datalake_gen2_path',
        'azure_datalake_gen2_path',
        'azure_datalake_gen2_path'
    ],
    'qualifiedName': [
        '//storage/container/data/customers.parquet',
        '//storage/container/data/orders.parquet',
        '//storage/container/public/analytics.csv'
    ],
    'displayName': ['Customer Data', 'Orders Data', 'Analytics Data'],
    'description': [
        'Customer master data',
        'Sales orders history',
        'Public analytics'
    ],
    'classification': ['PII;CONFIDENTIAL', 'CONFIDENTIAL', 'PUBLIC']
}

# Test data for bulk-update-csv
update_test_data = {
    'guid': [
        '00000000-0000-0000-0000-000000000001',
        '00000000-0000-0000-0000-000000000002',
        '00000000-0000-0000-0000-000000000003'
    ],
    'description': [
        'Updated customer column',
        'Updated order column',
        'Updated analytics table'
    ],
    'classification': ['PII;CONFIDENTIAL', 'INTERNAL', 'PUBLIC']
}

def test_bulk_create_with_classifications():
    """Test bulk-create-csv with classifications"""
    print("\n=== Test: bulk-create-csv with classifications ===")
    
    df = pd.DataFrame(create_test_data)
    csv_file = 'test_bulk_create_classif.csv'
    df.to_csv(csv_file, index=False)
    
    print(f"\nCSV file created: {csv_file}")
    print("\nCSV content:")
    print(df.to_string(index=False))
    
    print("\n[INFO] To run this test:")
    print(f"  pvw entity bulk-create-csv --csv-file {csv_file} --dry-run --debug")
    print("\n[INFO] To execute (creates entities + applies classifications):")
    print(f"  pvw entity bulk-create-csv --csv-file {csv_file} --debug")
    
    return csv_file

def test_bulk_update_with_classifications():
    """Test bulk-update-csv with classifications"""
    print("\n=== Test: bulk-update-csv with classifications ===")
    
    df = pd.DataFrame(update_test_data)
    csv_file = 'test_bulk_update_classif.csv'
    df.to_csv(csv_file, index=False)
    
    print(f"\nCSV file created: {csv_file}")
    print("\nCSV content:")
    print(df.to_string(index=False))
    
    print("\n[INFO] To run this test (requires valid GUIDs):")
    print(f"  pvw entity bulk-update-csv --csv-file {csv_file} --dry-run --debug")
    print("\n[INFO] To execute (updates attributes + applies classifications):")
    print(f"  pvw entity bulk-update-csv --csv-file {csv_file} --debug")
    
    return csv_file

def test_classification_parsing():
    """Test classification parsing logic"""
    print("\n=== Test: Classification parsing ===")
    
    test_cases = [
        "PII",
        "PII;CONFIDENTIAL",
        "PII,CONFIDENTIAL",
        "PII; CONFIDENTIAL; INTERNAL",
        "PII,CONFIDENTIAL,GDPR",
    ]
    
    print("\nTest cases:")
    for i, test_value in enumerate(test_cases, 1):
        # Simulate the parsing logic
        raw_items = [v.strip() for v in test_value.replace(",", ";").split(";")]
        classification_names = [v for v in raw_items if v]
        
        print(f"  {i}. Input: '{test_value}'")
        print(f"     Output: {classification_names}")
        print(f"     Payload: {[{'typeName': name} for name in classification_names]}")

if __name__ == '__main__':
    print("Testing CSV operations with classifications")
    print("=" * 60)
    
    try:
        # Test classification parsing
        test_classification_parsing()
        
        # Test bulk-create-csv
        create_csv = test_bulk_create_with_classifications()
        
        # Test bulk-update-csv
        update_csv = test_bulk_update_with_classifications()
        
        print("\n" + "=" * 60)
        print("[OK] All test files created successfully!")
        print("=" * 60)
        print("\n[NEXT STEPS]")
        print("1. Review the CSV files created")
        print("2. Run the commands shown above with --dry-run --debug")
        print("3. Update GUIDs in test_bulk_update_classif.csv with real GUIDs")
        print("4. Execute without --dry-run to apply changes")
        
    except Exception as e:
        print(f"\n[X] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
