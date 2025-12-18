#!/usr/bin/env python3
"""
Test script for bulk-update-csv with custom attributes and debug mode
Demonstrates the new features for bulk updating entities with custom attributes
"""

import os
import sys
import tempfile
import pandas as pd
import json

# Add the Purview CLI to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from purviewcli.client._entity import map_flat_entity_to_purview_entity

def test_map_simple_attributes():
    """Test mapping simple attributes"""
    print("\n=== Test 1: Simple Attributes ===")
    row = {
        'typeName': 'DataSet',
        'qualifiedName': 'test@cluster',
        'displayName': 'My Test Asset',
        'description': 'Test Description'
    }
    
    result = map_flat_entity_to_purview_entity(row, debug=True)
    print(json.dumps(result, indent=2))
    assert result['typeName'] == 'DataSet'
    assert result['attributes']['displayName'] == 'My Test Asset'
    print("✓ Test 1 passed")

def test_map_custom_attributes():
    """Test mapping custom attributes"""
    print("\n=== Test 2: Custom Attributes ===")
    row = {
        'typeName': 'DataSet',
        'qualifiedName': 'test@cluster',
        'displayName': 'Asset with Custom Attrs',
        'customAttr1': 'Value1',
        'customAttr2': 'Value2',
        'myCustomField': 'CustomValue'
    }
    
    result = map_flat_entity_to_purview_entity(row, debug=True)
    print(json.dumps(result, indent=2))
    assert result['attributes']['customAttr1'] == 'Value1'
    assert result['attributes']['myCustomField'] == 'CustomValue'
    print("✓ Test 2 passed")

def test_map_business_metadata():
    """Test mapping nested business metadata"""
    print("\n=== Test 3: Business Metadata (Nested) ===")
    row = {
        'typeName': 'DataSet',
        'qualifiedName': 'test@cluster',
        'displayName': 'Asset with Business Metadata',
        'businessMetadata.department': 'Sales',
        'businessMetadata.costCenter': '12345',
        'businessMetadata.owner': 'john.doe@company.com'
    }
    
    result = map_flat_entity_to_purview_entity(row, debug=True)
    print(json.dumps(result, indent=2))
    assert 'businessMetadata' in result['attributes']
    assert result['attributes']['businessMetadata']['department'] == 'Sales'
    assert result['attributes']['businessMetadata']['costCenter'] == '12345'
    print("✓ Test 3 passed")

def test_map_custom_attributes_section():
    """Test mapping to customAttributes section"""
    print("\n=== Test 4: Custom Attributes Section ===")
    row = {
        'typeName': 'DataSet',
        'qualifiedName': 'test@cluster',
        'displayName': 'Asset with Custom Section',
        'customAttributes.internalId': 'INT-12345',
        'customAttributes.classification': 'PII',
        'customAttributes.riskLevel': 'HIGH'
    }
    
    result = map_flat_entity_to_purview_entity(row, debug=True)
    print(json.dumps(result, indent=2))
    assert 'customAttributes' in result['attributes']
    assert result['attributes']['customAttributes']['internalId'] == 'INT-12345'
    print("✓ Test 4 passed")

def test_map_mixed_attributes():
    """Test mapping a mix of all attribute types"""
    print("\n=== Test 5: Mixed Attributes ===")
    row = {
        'typeName': 'DataSet',
        'qualifiedName': 'test@cluster',
        'displayName': 'Complex Asset',
        'description': 'Full example with all attribute types',
        'customAttr': 'Simple Custom',
        'businessMetadata.department': 'Engineering',
        'businessMetadata.projectCode': 'PROJ-001',
        'customAttributes.dataClassification': 'CONFIDENTIAL',
        'customAttributes.retentionDays': '365'
    }
    
    result = map_flat_entity_to_purview_entity(row, debug=True)
    print(json.dumps(result, indent=2))
    assert result['attributes']['customAttr'] == 'Simple Custom'
    assert result['attributes']['businessMetadata']['department'] == 'Engineering'
    assert result['attributes']['customAttributes']['dataClassification'] == 'CONFIDENTIAL'
    print("✓ Test 5 passed")

def test_map_with_guid():
    """Test mapping with GUID (for partial updates)"""
    print("\n=== Test 6: Mapping with GUID (Partial Update) ===")
    row = {
        'guid': 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee',
        'displayName': 'Updated Name',
        'description': 'Updated Description',
        'customAttr': 'Updated Value'
    }
    
    result = map_flat_entity_to_purview_entity(row, debug=True)
    print(json.dumps(result, indent=2))
    assert result['guid'] == 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'
    assert result['attributes']['displayName'] == 'Updated Name'
    print("✓ Test 6 passed")

def test_csv_processing():
    """Test processing a CSV file with custom attributes"""
    print("\n=== Test 7: CSV Processing ===")
    
    # Create test CSV
    csv_data = {
        'guid': [
            'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee',
            'bbbbbbbb-cccc-dddd-eeee-aaaaaaaaaaaa',
            'cccccccc-dddd-eeee-aaaa-bbbbbbbbbbbb'
        ],
        'displayName': ['Asset 1', 'Asset 2', 'Asset 3'],
        'description': ['Desc 1', 'Desc 2', 'Desc 3'],
        'customAttr1': ['Value1', 'Value2', 'Value3'],
        'businessMetadata.department': ['Sales', 'Marketing', 'Engineering']
    }
    
    df = pd.DataFrame(csv_data)
    
    # Process each row
    entities = []
    for _, row in df.iterrows():
        entity = map_flat_entity_to_purview_entity(row, debug=False)
        entities.append(entity)
    
    print(f"Processed {len(entities)} entities from CSV")
    for i, entity in enumerate(entities, 1):
        print(f"\nEntity {i}:")
        print(json.dumps(entity, indent=2))
    
    assert len(entities) == 3
    assert entities[0]['guid'] == 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'
    print("✓ Test 7 passed")

if __name__ == '__main__':
    print("Running bulk-update-csv tests with custom attributes")
    print("=" * 60)
    
    try:
        test_map_simple_attributes()
        test_map_custom_attributes()
        test_map_business_metadata()
        test_map_custom_attributes_section()
        test_map_mixed_attributes()
        test_map_with_guid()
        test_csv_processing()
        
        print("\n" + "=" * 60)
        print("✓ All tests passed successfully!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
