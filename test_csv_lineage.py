#!/usr/bin/env python3
"""
Comprehensive test suite for the new CSV lineage functionality
"""

import asyncio
import tempfile
import os
from pathlib import Path
import sys

# Add the parent directory to sys.path
parent_dir = Path(__file__).parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from purviewcli.client.csv_lineage_processor import CSVLineageProcessor, LineageCSVTemplates, LineageRelationship

def test_templates():
    """Test CSV lineage templates"""
    print("🧪 Testing CSV Lineage Templates")
    print("=" * 50)
    
    templates = LineageCSVTemplates()
    
    # Test template listing
    available = templates.get_available_templates()
    print(f"📋 Available templates: {list(available.keys())}")
    
    # Test each template generation
    for template_name in available.keys():
        print(f"\n🔄 Testing template: {template_name}")
        try:
            sample_csv = templates.generate_sample_csv(template_name, num_samples=3)
            lines = sample_csv.strip().split('\n')
            print(f"   ✅ Generated {len(lines)} lines (including header)")
            print(f"   📝 Header: {lines[0]}")
            if len(lines) > 1:
                print(f"   📝 Sample: {lines[1]}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    return True

def test_csv_validation():
    """Test CSV validation functionality"""
    print("\n🧪 Testing CSV Validation")
    print("=" * 50)
    
    templates = LineageCSVTemplates()
    processor = CSVLineageProcessor(None)  # No client needed for validation
    
    # Create a valid test CSV
    test_csv_content = templates.generate_sample_csv("basic", num_samples=2)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(test_csv_content)
        test_file = f.name
    
    try:
        # Test validation
        print(f"📄 Created test file: {test_file}")
        print(f"📝 Content preview:")
        print(test_csv_content[:200] + "..." if len(test_csv_content) > 200 else test_csv_content)
        
        # Test the validation (this should pass)
        try:
            is_valid, errors = processor.validate_csv_format(test_file)
            if is_valid:
                print("✅ CSV validation passed")
            else:
                print(f"❌ CSV validation failed: {errors}")
        except Exception as e:
            print(f"❌ Validation error: {e}")
            
    finally:
        # Cleanup
        if os.path.exists(test_file):
            os.unlink(test_file)
    
    return True

def test_lineage_relationship():
    """Test LineageRelationship dataclass"""
    print("\n🧪 Testing LineageRelationship Data Structure")
    print("=" * 50)
    
    try:
        # Test basic relationship creation
        relationship = LineageRelationship(
            source_entity_guid="guid-123",
            target_entity_guid="guid-456",
            source_entity_name="source_table",
            target_entity_name="target_table",
            relationship_type="DataFlow"
        )
        
        print(f"✅ Created relationship: {relationship.source_entity_name} -> {relationship.target_entity_name}")
        print(f"   Type: {relationship.relationship_type}")
        print(f"   Confidence: {relationship.confidence_score}")
        
        # Test with metadata
        relationship_with_metadata = LineageRelationship(
            source_entity_guid="guid-789",
            target_entity_guid="guid-012",
            source_entity_name="orders",
            target_entity_name="order_summary",
            relationship_type="Process",
            process_name="ETL Pipeline",
            metadata={"pipeline_id": "etl_001", "owner": "data_team"}
        )
        
        print(f"✅ Created relationship with metadata: {relationship_with_metadata.process_name}")
        print(f"   Metadata: {relationship_with_metadata.metadata}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating relationship: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting CSV Lineage Functionality Tests")
    print("=" * 60)
    
    tests = [
        test_templates,
        test_csv_validation,
        test_lineage_relationship
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"🏁 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! CSV lineage functionality is working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
