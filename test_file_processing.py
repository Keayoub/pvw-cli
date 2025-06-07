#!/usr/bin/env python3
"""
End-to-End File Processing Test
Tests the complete file processing pipeline from upload to completion
"""
import asyncio
import json
import os
import tempfile
import time
from pathlib import Path
import pandas as pd
import requests
import csv

class FileProcessingTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.auth_token = None
        self.session = requests.Session()
        
    def authenticate(self):
        """Authenticate with the API"""
        auth_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        response = self.session.post(f"{self.base_url}/api/v1/auth/login", json=auth_data)
        if response.status_code == 200:
            self.auth_token = response.json()["access_token"]
            self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
            print("✅ Authentication successful")
            return True
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return False
    
    def create_test_files(self):
        """Create test files for different formats"""
        test_files = {}
        
        # Create CSV file
        csv_data = [
            ["id", "name", "type", "database", "schema", "description"],
            ["1", "customers", "table", "sales_db", "public", "Customer information table"],
            ["2", "orders", "table", "sales_db", "public", "Order tracking table"],
            ["3", "products", "table", "inventory_db", "public", "Product catalog table"],
            ["4", "user_profile", "table", "user_db", "public", "User profile data"],
            ["5", "transaction_log", "table", "audit_db", "public", "Transaction audit log"]
        ]
        
        csv_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        writer = csv.writer(csv_file)
        writer.writerows(csv_data)
        csv_file.close()
        test_files['csv'] = csv_file.name
        
        # Create JSON file
        json_data = {
            "entities": [
                {
                    "id": "dataset_001",
                    "name": "sales_summary",
                    "type": "dataset",
                    "attributes": {
                        "database": "analytics_db",
                        "schema": "reporting",
                        "description": "Monthly sales summary dataset"
                    }
                },
                {
                    "id": "dataset_002", 
                    "name": "customer_metrics",
                    "type": "dataset",
                    "attributes": {
                        "database": "analytics_db",
                        "schema": "metrics",
                        "description": "Customer behavior metrics"
                    }
                }
            ]
        }
        
        json_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(json_data, json_file, indent=2)
        json_file.close()
        test_files['json'] = json_file.name
        
        # Create Excel file
        excel_data = pd.DataFrame({
            'table_name': ['users', 'roles', 'permissions', 'audit_logs'],
            'database': ['auth_db', 'auth_db', 'auth_db', 'system_db'],
            'schema': ['public', 'public', 'public', 'audit'],
            'classification': ['PII', 'Internal', 'Internal', 'Confidential'],
            'data_quality_score': [8.5, 9.2, 9.0, 7.8]
        })
        
        excel_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
        excel_data.to_excel(excel_file.name, index=False)
        excel_file.close()
        test_files['excel'] = excel_file.name
        
        print(f"✅ Created test files: {list(test_files.keys())}")
        return test_files
    
    def upload_file(self, file_path, processing_options=None):
        """Upload a file to the API"""
        if processing_options is None:
            processing_options = {
                "operation": "import_entities",
                "auto_process": True,
                "notification_email": "test@example.com"
            }
        
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {
                'processing_options': json.dumps(processing_options)
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/upload/file",
                files=files,
                data=data
            )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ File uploaded successfully: {result['file_id']}")
            return result
        else:
            print(f"❌ File upload failed: {response.status_code} - {response.text}")
            return None
    
    def check_processing_status(self, job_id):
        """Check the status of a processing job"""
        response = self.session.get(f"{self.base_url}/api/v1/upload/jobs/{job_id}")
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get job status: {response.status_code}")
            return None
    
    def wait_for_completion(self, job_id, timeout=300):
        """Wait for a processing job to complete"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = self.check_processing_status(job_id)
            if not status:
                return False
            
            print(f"⏳ Job {job_id} status: {status['status']} - Progress: {status.get('progress', 0)}%")
            
            if status['status'] in ['completed', 'failed', 'cancelled']:
                return status
            
            time.sleep(5)
        
        print(f"❌ Job {job_id} timed out after {timeout} seconds")
        return False
    
    def test_file_processing_operations(self):
        """Test different file processing operations"""
        test_files = self.create_test_files()
        
        operations = [
            {
                "name": "Import Entities",
                "operation": "import_entities",
                "file_type": "csv"
            },
            {
                "name": "Bulk Classification",
                "operation": "bulk_classification", 
                "file_type": "excel"
            },
            {
                "name": "Data Quality Check",
                "operation": "data_quality_check",
                "file_type": "csv"
            },
            {
                "name": "Metadata Extraction",
                "operation": "metadata_extraction",
                "file_type": "json"
            },
            {
                "name": "Lineage Discovery",
                "operation": "lineage_discovery",
                "file_type": "csv"
            }
        ]
        
        results = []
        
        for op in operations:
            print(f"\n🔄 Testing {op['name']} operation...")
            
            processing_options = {
                "operation": op["operation"],
                "auto_process": True,
                "notification_email": "test@example.com"
            }
            
            # Upload file
            upload_result = self.upload_file(
                test_files[op['file_type']], 
                processing_options
            )
            
            if not upload_result:
                results.append({
                    "operation": op["name"],
                    "status": "failed",
                    "error": "Upload failed"
                })
                continue
            
            # Wait for processing to complete
            job_result = self.wait_for_completion(upload_result['job_id'])
            
            if job_result:
                results.append({
                    "operation": op["name"],
                    "status": job_result['status'],
                    "job_id": upload_result['job_id'],
                    "file_id": upload_result['file_id'],
                    "progress": job_result.get('progress', 0),
                    "result": job_result.get('result', {})
                })
                
                if job_result['status'] == 'completed':
                    print(f"✅ {op['name']} completed successfully")
                else:
                    print(f"❌ {op['name']} failed: {job_result.get('error_message', 'Unknown error')}")
            else:
                results.append({
                    "operation": op["name"],
                    "status": "timeout",
                    "job_id": upload_result['job_id']
                })
        
        # Cleanup test files
        for file_path in test_files.values():
            os.unlink(file_path)
        
        return results
    
    def test_file_management(self):
        """Test file management operations"""
        print("\n🔄 Testing file management operations...")
        
        # List files
        response = self.session.get(f"{self.base_url}/api/v1/upload/files")
        if response.status_code == 200:
            files = response.json()
            print(f"✅ Listed {len(files)} files")
            
            if files:
                file_id = files[0]['id']
                
                # Get file details
                response = self.session.get(f"{self.base_url}/api/v1/upload/files/{file_id}")
                if response.status_code == 200:
                    print("✅ Retrieved file details")
                else:
                    print(f"❌ Failed to get file details: {response.status_code}")
                
                # Download file
                response = self.session.get(f"{self.base_url}/api/v1/upload/files/{file_id}/download")
                if response.status_code == 200:
                    print("✅ Downloaded file successfully")
                else:
                    print(f"❌ Failed to download file: {response.status_code}")
        else:
            print(f"❌ Failed to list files: {response.status_code}")
    
    def test_system_health(self):
        """Test system health endpoints"""
        print("\n🔄 Testing system health...")
        
        # Health check
        response = self.session.get(f"{self.base_url}/health")
        if response.status_code == 200:
            health = response.json()
            print(f"✅ System health: {health['status']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
        
        # Detailed health
        response = self.session.get(f"{self.base_url}/api/v1/health")
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Detailed health check: Database={health['database']}, Cache={health['cache']}")
        else:
            print(f"❌ Detailed health check failed: {response.status_code}")
    
    def run_full_test(self):
        """Run the complete test suite"""
        print("🚀 Starting End-to-End File Processing Test")
        print("=" * 50)
        
        # Authenticate
        if not self.authenticate():
            return False
        
        # Test system health
        self.test_system_health()
        
        # Test file processing operations
        results = self.test_file_processing_operations()
        
        # Test file management
        self.test_file_management()
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 50)
        
        successful = 0
        failed = 0
        
        for result in results:
            status_icon = "✅" if result['status'] == 'completed' else "❌"
            print(f"{status_icon} {result['operation']}: {result['status']}")
            
            if result['status'] == 'completed':
                successful += 1
            else:
                failed += 1
        
        print(f"\n📈 Summary: {successful} successful, {failed} failed")
        
        return successful > 0

def main():
    """Main test function"""
    tester = FileProcessingTester()
    
    print("Starting File Processing Pipeline Test...")
    print("Make sure the backend server is running on http://localhost:8000")
    print("Press Enter to continue or Ctrl+C to cancel...")
    input()
    
    success = tester.run_full_test()
    
    if success:
        print("\n🎉 File processing pipeline test completed successfully!")
    else:
        print("\n💥 File processing pipeline test failed!")
    
    return success

if __name__ == "__main__":
    main()
