#  Purview CLI v2.0 - API Integration Tests
# Comprehensive tests for API endpoints

import pytest
import json
from httpx import AsyncClient
from typing import Dict, Any

from tests.conftest import TestDataFactory, TestUtils

class TestAuthAPI:
    """Test authentication API endpoints."""
    
    @pytest.mark.integration
    async def test_user_registration(self, client: AsyncClient):
        """Test user registration."""
        user_data = TestDataFactory.user_data()
        
        response = await client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]
        assert "id" in data
        assert "password" not in data  # Password should not be returned
        
    @pytest.mark.integration
    async def test_user_login(self, client: AsyncClient):
        """Test user login."""
        # First register user
        user_data = TestDataFactory.user_data()
        await client.post("/api/auth/register", json=user_data)
        
        # Then login
        login_data = {
            "username": user_data["username"],
            "password": user_data["password"]
        }
        
        response = await client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        
    @pytest.mark.integration
    async def test_invalid_login(self, client: AsyncClient):
        """Test login with invalid credentials."""
        login_data = {
            "username": "nonexistent",
            "password": "wrongpassword"
        }
        
        response = await client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 401
        
    @pytest.mark.integration
    async def test_token_refresh(self, client: AsyncClient):
        """Test token refresh."""
        # Register and login user
        user_data = TestDataFactory.user_data()
        await client.post("/api/auth/register", json=user_data)
        
        login_response = await client.post("/api/auth/login", json={
            "username": user_data["username"],
            "password": user_data["password"]
        })
        
        tokens = login_response.json()
        
        # Refresh token
        refresh_response = await client.post("/api/auth/refresh", json={
            "refresh_token": tokens["refresh_token"]
        })
        
        assert refresh_response.status_code == 200
        new_tokens = refresh_response.json()
        assert "access_token" in new_tokens
        assert new_tokens["access_token"] != tokens["access_token"]
        
    @pytest.mark.integration
    async def test_user_profile(self, client: AsyncClient, auth_headers: Dict[str, str]):
        """Test getting user profile."""
        response = await client.get("/api/auth/profile", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "username" in data
        assert "email" in data
        assert "full_name" in data
        
    @pytest.mark.integration
    async def test_unauthorized_access(self, client: AsyncClient):
        """Test accessing protected endpoint without authentication."""
        response = await client.get("/api/auth/profile")
        
        assert response.status_code == 401

class TestEntitiesAPI:
    """Test entities API endpoints."""
    
    @pytest.mark.integration
    async def test_create_entity(self, client: AsyncClient, auth_headers: Dict[str, str]):
        """Test creating a new entity."""
        entity_data = TestDataFactory.entity_data()
        
        response = await client.post("/api/entities", json=entity_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == entity_data["name"]
        assert data["entity_type"] == entity_data["entity_type"]
        TestUtils.assert_valid_uuid(data["id"])
        
    @pytest.mark.integration
    async def test_get_entities(self, client: AsyncClient, auth_headers: Dict[str, str]):
        """Test getting list of entities."""
        # Create test entity first
        await TestUtils.create_test_entity(client, auth_headers)
        
        response = await client.get("/api/entities", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) >= 1
        
    @pytest.mark.integration
    async def test_get_entity_by_id(self, client: AsyncClient, auth_headers: Dict[str, str]):
        """Test getting entity by ID."""
        # Create test entity
        entity = await TestUtils.create_test_entity(client, auth_headers)
        
        response = await client.get(f"/api/entities/{entity['id']}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == entity["id"]
        assert data["name"] == entity["name"]
        
    @pytest.mark.integration
    async def test_update_entity(self, client: AsyncClient, auth_headers: Dict[str, str]):
        """Test updating an entity."""
        # Create test entity
        entity = await TestUtils.create_test_entity(client, auth_headers)
        
        update_data = {
            "description": "Updated description",
            "status": "INACTIVE"
        }
        
        response = await client.put(
            f"/api/entities/{entity['id']}", 
            json=update_data, 
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == update_data["description"]
        assert data["status"] == update_data["status"]
        
    @pytest.mark.integration
    async def test_delete_entity(self, client: AsyncClient, auth_headers: Dict[str, str]):
        """Test deleting an entity."""
        # Create test entity
        entity = await TestUtils.create_test_entity(client, auth_headers)
        
        response = await client.delete(f"/api/entities/{entity['id']}", headers=auth_headers)
        
        assert response.status_code == 204
        
        # Verify entity is deleted
        get_response = await client.get(f"/api/entities/{entity['id']}", headers=auth_headers)
        assert get_response.status_code == 404
        
    @pytest.mark.integration
    async def test_search_entities(self, client: AsyncClient, auth_headers: Dict[str, str]):
        """Test searching entities."""
        # Create test entity
        await TestUtils.create_test_entity(client, auth_headers)
        
        response = await client.get(
            "/api/entities/search?query=test_table", 
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

class TestDataSourcesAPI:
    """Test data sources API endpoints."""
    
    @pytest.mark.integration
    async def test_create_data_source(self, client: AsyncClient, auth_headers: Dict[str, str]):
        """Test creating a new data source."""
        ds_data = TestDataFactory.data_source_data()
        
        response = await client.post("/api/data-sources", json=ds_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == ds_data["name"]
        assert data["type"] == ds_data["type"]
        TestUtils.assert_valid_uuid(data["id"])
        
    @pytest.mark.integration
    async def test_get_data_sources(self, client: AsyncClient, auth_headers: Dict[str, str]):
        """Test getting list of data sources."""
        # Create test data source first
        await TestUtils.create_test_data_source(client, auth_headers)
        
        response = await client.get("/api/data-sources", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) >= 1
        
    @pytest.mark.integration
    async def test_test_connection(self, client: AsyncClient, auth_headers: Dict[str, str]):
        """Test data source connection testing."""
        ds_data = TestDataFactory.data_source_data()
        
        response = await client.post(
            "/api/data-sources/test-connection", 
            json=ds_data, 
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "message" in data

class TestScansAPI:
    """Test scans API endpoints."""
    
    @pytest.mark.integration
    async def test_create_scan(self, client: AsyncClient, auth_headers: Dict[str, str]):
        """Test creating a new scan."""
        # Create data source first
        data_source = await TestUtils.create_test_data_source(client, auth_headers)
        
        scan_data = TestDataFactory.scan_data(data_source["id"])
        
        response = await client.post("/api/scans", json=scan_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == scan_data["name"]
        assert data["scan_type"] == scan_data["scan_type"]
        TestUtils.assert_valid_uuid(data["id"])
        
    @pytest.mark.integration
    async def test_get_scans(self, client: AsyncClient, auth_headers: Dict[str, str]):
        """Test getting list of scans."""
        response = await client.get("/api/scans", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        
    @pytest.mark.integration
    async def test_run_scan(self, client: AsyncClient, auth_headers: Dict[str, str]):
        """Test running a scan."""
        # Create data source and scan
        data_source = await TestUtils.create_test_data_source(client, auth_headers)
        
        scan_data = TestDataFactory.scan_data(data_source["id"])
        scan_response = await client.post("/api/scans", json=scan_data, headers=auth_headers)
        scan = scan_response.json()
        
        # Run scan
        response = await client.post(f"/api/scans/{scan['id']}/run", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "message" in data

class TestLineageAPI:
    """Test lineage API endpoints."""
    
    @pytest.mark.integration
    async def test_get_lineage_graph(self, client: AsyncClient, auth_headers: Dict[str, str]):
        """Test getting lineage graph."""
        # Create test entity
        entity = await TestUtils.create_test_entity(client, auth_headers)
        
        response = await client.get(
            f"/api/lineage/{entity['id']}/graph", 
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "nodes" in data
        assert "edges" in data
        
    @pytest.mark.integration
    async def test_get_impact_analysis(self, client: AsyncClient, auth_headers: Dict[str, str]):
        """Test getting impact analysis."""
        # Create test entity
        entity = await TestUtils.create_test_entity(client, auth_headers)
        
        response = await client.get(
            f"/api/lineage/{entity['id']}/impact", 
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "upstream" in data
        assert "downstream" in data

class TestAnalyticsAPI:
    """Test analytics API endpoints."""
    
    @pytest.mark.integration
    async def test_get_dashboard_metrics(self, client: AsyncClient, auth_headers: Dict[str, str]):
        """Test getting dashboard metrics."""
        response = await client.get("/api/analytics/dashboard", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "total_entities" in data
        assert "active_scans" in data
        assert "recent_activities" in data
        
    @pytest.mark.integration
    async def test_get_scan_analytics(self, client: AsyncClient, auth_headers: Dict[str, str]):
        """Test getting scan analytics."""
        response = await client.get("/api/analytics/scans", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "total_scans" in data
        assert "success_rate" in data
        
    @pytest.mark.integration
    async def test_get_usage_analytics(self, client: AsyncClient, auth_headers: Dict[str, str]):
        """Test getting usage analytics."""
        response = await client.get("/api/analytics/usage", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "api_calls" in data
        assert "user_activity" in data

class TestGovernanceAPI:
    """Test governance API endpoints."""
    
    @pytest.mark.integration
    async def test_create_policy(self, client: AsyncClient, admin_headers: Dict[str, str]):
        """Test creating a governance policy."""
        policy_data = TestDataFactory.governance_policy_data()
        
        response = await client.post("/api/governance/policies", json=policy_data, headers=admin_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == policy_data["name"]
        assert data["policy_type"] == policy_data["policy_type"]
        
    @pytest.mark.integration
    async def test_get_policies(self, client: AsyncClient, auth_headers: Dict[str, str]):
        """Test getting governance policies."""
        response = await client.get("/api/governance/policies", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        
    @pytest.mark.integration
    async def test_check_compliance(self, client: AsyncClient, auth_headers: Dict[str, str]):
        """Test compliance checking."""
        # Create test entity
        entity = await TestUtils.create_test_entity(client, auth_headers)
        
        response = await client.get(
            f"/api/governance/compliance/{entity['id']}", 
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "compliant" in data
        assert "violations" in data

class TestClassificationAPI:
    """Test classification API endpoints."""
    
    @pytest.mark.integration
    async def test_get_classifications(self, client: AsyncClient, auth_headers: Dict[str, str]):
        """Test getting classifications."""
        response = await client.get("/api/classifications", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        
    @pytest.mark.integration
    async def test_create_classification(self, client: AsyncClient, admin_headers: Dict[str, str]):
        """Test creating a classification."""
        classification_data = TestDataFactory.classification_data()
        
        response = await client.post(
            "/api/classifications", 
            json=classification_data, 
            headers=admin_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == classification_data["name"]
        assert data["level"] == classification_data["level"]

class TestFileUploadAPI:
    """Test file upload API endpoints."""
    
    @pytest.mark.integration
    async def test_upload_file(self, client: AsyncClient, auth_headers: Dict[str, str], temp_file: str):
        """Test file upload."""
        with open(temp_file, 'rb') as f:
            files = {"file": ("test.csv", f, "text/csv")}
            response = await client.post(
                "/api/upload", 
                files=files, 
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "file_id" in data
        assert "filename" in data
        assert "size" in data

class TestHealthAPI:
    """Test health check endpoints."""
    
    @pytest.mark.integration
    async def test_health_check(self, client: AsyncClient):
        """Test health check endpoint."""
        response = await client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
        
    @pytest.mark.integration
    async def test_database_health(self, client: AsyncClient):
        """Test database health check."""
        response = await client.get("/health/database")
        
        assert response.status_code == 200
        data = response.json()
        assert "database_connected" in data
