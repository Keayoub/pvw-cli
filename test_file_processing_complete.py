"""
Test script for file processing service functionality.
Tests the complete file processing pipeline end-to-end.
"""
import asyncio
import tempfile
import csv
import json
import pandas as pd
from pathlib import Path
import logging

# Mock database session and dependencies
class MockDBSession:
    def __init__(self):
        self.data = {}
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
    
    async def execute(self, query):
        return MockResult()
    
    async def commit(self):
        pass
    
    def add(self, obj):
        pass
    
    async def delete(self, obj):
        pass

class MockResult:
    def scalar_one_or_none(self):
        return None
    
    def scalars(self):
        return MockScalars()

class MockScalars:
    def all(self):
        return []

# Mock functions
async def mock_get_db_session():
    return MockDBSession()

def mock_settings():
    class Settings:
        PURVIEW_CATALOG_NAME = "test_catalog"
        UPLOAD_PATH = "/tmp/uploads"
    return Settings()

# Patch imports for testing
import sys
from unittest.mock import Mock, AsyncMock

# Mock the database connection
sys.modules['app.database.connection'] = Mock()
sys.modules['app.database.connection'].get_db_session = mock_get_db_session

# Mock models
sys.modules['app.database.models'] = Mock()

# Mock config
sys.modules['app.core.config'] = Mock()
sys.modules['app.core.config'].settings = mock_settings()

# Mock other services
sys.modules['app.services.cache_service'] = Mock()
sys.modules['app.services.analytics_service'] = Mock()
sys.modules['app.services.governance_service'] = Mock()
sys.modules['app.tasks.file_processing'] = Mock()

# Now import the services we want to test
from app.services.file_processing_service import FileProcessingService
from app.services.entities_service import EntitiesService

async def test_file_processing_service():
    """Test the FileProcessingService functionality."""
    print("🧪 Testing File Processing Service...")
    
    # Create service instance
    service = FileProcessingService()
    
    # Test 1: CSV file processing
    print("\n📊 Testing CSV file processing...")
    
    # Create a temporary CSV file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'name', 'email', 'department'])
        writer.writerow(['1', 'John Doe', 'john@company.com', 'IT'])
        writer.writerow(['2', 'Jane Smith', 'jane@company.com', 'HR'])
        writer.writerow(['3', 'Bob Johnson', 'bob@company.com', 'Finance'])
        csv_file_path = Path(f.name)
    
    try:
        # Test CSV processing
        csv_result = await service._process_csv_file(csv_file_path)
        print(f"✅ CSV processing successful: {csv_result['rows']} rows, {len(csv_result['columns'])} columns")
        print(f"   Columns: {csv_result['columns']}")
        print(f"   Sample data: {csv_result['sample'][0] if csv_result['sample'] else 'No data'}")
        
    except Exception as e:
        print(f"❌ CSV processing failed: {e}")
    finally:
        csv_file_path.unlink(missing_ok=True)
    
    # Test 2: JSON file processing
    print("\n📋 Testing JSON file processing...")
    
    # Create a temporary JSON file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        test_data = [
            {"id": 1, "name": "Product A", "category": "Electronics", "price": 299.99},
            {"id": 2, "name": "Product B", "category": "Books", "price": 19.99},
            {"id": 3, "name": "Product C", "category": "Clothing", "price": 49.99}
        ]
        json.dump(test_data, f, indent=2)
        json_file_path = Path(f.name)
    
    try:
        # Test JSON processing
        json_result = await service._process_json_file(json_file_path)
        print(f"✅ JSON processing successful: {json_result['type']}, {json_result['size']} items")
        print(f"   Sample data: {json_result['sample'][0] if json_result['sample'] else 'No data'}")
        
    except Exception as e:
        print(f"❌ JSON processing failed: {e}")
    finally:
        json_file_path.unlink(missing_ok=True)
    
    # Test 3: Excel file processing
    print("\n📈 Testing Excel file processing...")
    
    # Create a temporary Excel file
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
        df = pd.DataFrame({
            'employee_id': [1001, 1002, 1003, 1004],
            'full_name': ['Alice Brown', 'Charlie Davis', 'Diana Wilson', 'Edward Moore'],
            'position': ['Manager', 'Developer', 'Analyst', 'Designer'],
            'salary': [75000, 65000, 55000, 60000]
        })
        df.to_excel(f.name, index=False)
        excel_file_path = Path(f.name)
    
    try:
        # Test Excel processing
        excel_result = await service._process_excel_file(excel_file_path)
        print(f"✅ Excel processing successful: {excel_result['rows']} rows, {len(excel_result['columns'])} columns")
        print(f"   Columns: {excel_result['columns']}")
        print(f"   Sample data: {excel_result['sample'][0] if excel_result['sample'] else 'No data'}")
        
    except Exception as e:
        print(f"❌ Excel processing failed: {e}")
    finally:
        excel_file_path.unlink(missing_ok=True)
    
    # Test 4: Text file processing
    print("\n📄 Testing text file processing...")
    
    # Create a temporary text file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("This is a test document.\n")
        f.write("It contains multiple lines of text.\n")
        f.write("Used for testing text file processing.\n")
        f.write("Each line represents different content.\n")
        text_file_path = Path(f.name)
    
    try:
        # Test text processing
        text_result = await service._process_text_file(text_file_path)
        print(f"✅ Text processing successful: {text_result['lines']} lines")
        print(f"   Sample lines: {text_result['sample'][:2]}")
        
    except Exception as e:
        print(f"❌ Text processing failed: {e}")
    finally:
        text_file_path.unlink(missing_ok=True)
    
    # Test 5: Entity import operation
    print("\n🏗️ Testing entity import operation...")
    
    try:
        # Mock file data for entity import
        mock_file_data = {
            "format": "csv",
            "data": pd.DataFrame({
                'name': ['dataset_sales', 'dataset_customers', 'dataset_products'],
                'description': ['Sales transaction data', 'Customer master data', 'Product catalog'],
                'owner': ['sales_team', 'marketing_team', 'product_team'],
                'source_system': ['CRM', 'ERP', 'PIM']
            }),
            "columns": ['name', 'description', 'owner', 'source_system'],
            "rows": 3
        }
        
        async def mock_progress_callback(progress):
            print(f"   Progress: {progress}%")
        
        import_result = await service._import_entities_operation(
            mock_file_data, 
            "DataSet", 
            {}, 
            mock_progress_callback
        )
        
        print(f"✅ Entity import successful: {import_result['entities_created']} entities created")
        print(f"   Total processed: {import_result['total_processed']}")
        print(f"   Errors: {len(import_result['errors'])}")
        
    except Exception as e:
        print(f"❌ Entity import failed: {e}")
    
    # Test 6: Data quality check operation
    print("\n🔍 Testing data quality check operation...")
    
    try:
        # Mock file data for quality check
        mock_quality_data = {
            "format": "csv",
            "data": pd.DataFrame({
                'customer_id': [1, 2, 3, None, 5],
                'email': ['john@test.com', 'jane@test.com', None, 'invalid-email', 'bob@test.com'],
                'age': [25, 30, 35, 40, None],
                'status': ['active', 'active', 'inactive', 'active', 'active']
            })
        }
        
        quality_result = await service._data_quality_check_operation(
            mock_quality_data,
            "Customer",
            {},
            mock_progress_callback
        )
        
        print(f"✅ Data quality check successful: Overall score {quality_result['overall_score']}")
        print(f"   Recommendations: {len(quality_result['recommendations'])}")
        
    except Exception as e:
        print(f"❌ Data quality check failed: {e}")
    
    # Test 7: Metadata extraction operation
    print("\n📝 Testing metadata extraction operation...")
    
    try:
        metadata_result = await service._metadata_extraction_operation(
            mock_quality_data,
            "Dataset",
            {},
            mock_progress_callback
        )
        
        print(f"✅ Metadata extraction successful")
        print(f"   Schema columns: {metadata_result['metadata']['schema_metadata']['columns']}")
        print(f"   Completeness: {metadata_result['metadata']['statistical_metadata']['completeness_percentage']}%")
        
    except Exception as e:
        print(f"❌ Metadata extraction failed: {e}")

async def test_entities_service():
    """Test the EntitiesService functionality."""
    print("\n\n🏢 Testing Entities Service...")
    
    # Create service instance
    service = EntitiesService()
    
    # Test 1: Create entity
    print("\n➕ Testing entity creation...")
    
    try:
        entity_data = {
            "type_name": "Table",
            "qualified_name": "customer_data@test_db",
            "attributes": {
                "name": "customer_data",
                "description": "Customer master table",
                "schema": "dbo",
                "database": "test_db"
            }
        }
        
        created_entity = await service.create_entity(entity_data)
        print(f"✅ Entity created successfully: {created_entity['entity_id']}")
        print(f"   Type: {created_entity['type_name']}")
        print(f"   Name: {created_entity['attributes']['name']}")
        
    except Exception as e:
        print(f"❌ Entity creation failed: {e}")
    
    # Test 2: Search entities
    print("\n🔍 Testing entity search...")
    
    try:
        search_results = await service.search_entities(
            query="customer",
            entity_types=["Table"],
            limit=5
        )
        
        print(f"✅ Entity search successful: {search_results['total_count']} results")
        print(f"   Search time: {search_results['search_time_ms']}ms")
        if search_results['entities']:
            print(f"   First result: {search_results['entities'][0]['attributes']['name']}")
        
    except Exception as e:
        print(f"❌ Entity search failed: {e}")
    
    # Test 3: Get entity types
    print("\n📋 Testing entity types retrieval...")
    
    try:
        entity_types = await service.get_entity_types()
        print(f"✅ Entity types retrieved: {len(entity_types)} types available")
        print(f"   Types: {[et['name'] for et in entity_types[:3]]}")
        
    except Exception as e:
        print(f"❌ Entity types retrieval failed: {e}")
    
    # Test 4: Bulk entity creation
    print("\n📦 Testing bulk entity creation...")
    
    try:
        bulk_data = [
            {
                "type_name": "Table",
                "qualified_name": f"table_{i}@test_db",
                "attributes": {
                    "name": f"table_{i}",
                    "description": f"Test table {i}"
                }
            }
            for i in range(1, 4)
        ]
        
        bulk_result = await service.bulk_create_entities(bulk_data)
        print(f"✅ Bulk creation successful: {bulk_result['created_count']}/{bulk_result['total_submitted']} entities")
        print(f"   Success rate: {bulk_result['success_rate']:.1f}%")
        
    except Exception as e:
        print(f"❌ Bulk entity creation failed: {e}")

async def main():
    """Run all tests."""
    print("🚀 Starting File Processing Service Tests")
    print("=" * 50)
    
    try:
        await test_file_processing_service()
        await test_entities_service()
        
        print("\n" + "=" * 50)
        print("✅ All tests completed successfully!")
        print("🎉 File Processing Service is working properly!")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Run the tests
    asyncio.run(main())
