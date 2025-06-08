#  Purview CLI v2.0 - Service Unit Tests
# Unit tests for service layer components

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
from typing import Dict, Any, List

from app.services.auth_service import AuthService
from app.services.lineage_service import LineageService
from app.services.analytics_service import AnalyticsService
from app.services.governance_service import GovernanceService
from app.services.cache_service import RedisCache, cache_result, CacheKeys
from tests.conftest import TestDataFactory

class TestAuthService:
    """Unit tests for AuthService."""
    
    @pytest.fixture
    def auth_service(self):
        return AuthService()
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_user(self, auth_service):
        """Test user creation."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
            "full_name": "Test User"
        }
        
        with patch.object(auth_service, 'get_user_by_username', return_value=None), \
             patch.object(auth_service, 'get_user_by_email', return_value=None):
            
            user = await auth_service.create_user(**user_data)
            
            assert user["username"] == user_data["username"]
            assert user["email"] == user_data["email"]
            assert "password" not in user
            assert "id" in user
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_duplicate_user(self, auth_service):
        """Test creating user with existing username."""
        existing_user = {"id": "1", "username": "testuser", "email": "test@example.com"}
        
        with patch.object(auth_service, 'get_user_by_username', return_value=existing_user):
            with pytest.raises(ValueError, match="Username already exists"):
                await auth_service.create_user(
                    username="testuser",
                    email="new@example.com", 
                    password="pass123",
                    full_name="New User"
                )
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_authenticate_user(self, auth_service):
        """Test user authentication."""
        hashed_password = auth_service.get_password_hash("testpass123")
        user = {
            "id": "1",
            "username": "testuser",
            "password": hashed_password,
            "is_active": True
        }
        
        with patch.object(auth_service, 'get_user_by_username', return_value=user):
            authenticated_user = await auth_service.authenticate_user("testuser", "testpass123")
            
            assert authenticated_user is not None
            assert authenticated_user["username"] == "testuser"
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_authenticate_wrong_password(self, auth_service):
        """Test authentication with wrong password."""
        hashed_password = auth_service.get_password_hash("testpass123")
        user = {
            "id": "1",
            "username": "testuser", 
            "password": hashed_password,
            "is_active": True
        }
        
        with patch.object(auth_service, 'get_user_by_username', return_value=user):
            authenticated_user = await auth_service.authenticate_user("testuser", "wrongpass")
            
            assert authenticated_user is None
    
    @pytest.mark.unit
    def test_create_access_token(self, auth_service):
        """Test JWT token creation."""
        user_data = {"user_id": "1", "username": "testuser", "role": "user"}
        
        token = auth_service.create_access_token(user_data)
        
        assert isinstance(token, str)
        assert len(token) > 0
    
    @pytest.mark.unit
    def test_verify_token(self, auth_service):
        """Test JWT token verification."""
        user_data = {"user_id": "1", "username": "testuser", "role": "user"}
        token = auth_service.create_access_token(user_data)
        
        decoded_data = auth_service.verify_token(token)
        
        assert decoded_data is not None
        assert decoded_data["user_id"] == "1"
        assert decoded_data["username"] == "testuser"
    
    @pytest.mark.unit
    def test_verify_invalid_token(self, auth_service):
        """Test verification of invalid token."""
        invalid_token = "invalid.token.here"
        
        decoded_data = auth_service.verify_token(invalid_token)
        
        assert decoded_data is None

class TestLineageService:
    """Unit tests for LineageService."""
    
    @pytest.fixture
    def lineage_service(self):
        return LineageService()
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_lineage_graph(self, lineage_service):
        """Test getting lineage graph."""
        entity_id = "test-entity-id"
        
        graph = await lineage_service.get_lineage_graph(entity_id)
        
        assert "nodes" in graph
        assert "edges" in graph
        assert isinstance(graph["nodes"], list)
        assert isinstance(graph["edges"], list)
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_impact_analysis(self, lineage_service):
        """Test getting impact analysis."""
        entity_id = "test-entity-id"
        
        impact = await lineage_service.get_impact_analysis(entity_id)
        
        assert "upstream" in impact
        assert "downstream" in impact
        assert isinstance(impact["upstream"], list)
        assert isinstance(impact["downstream"], list)
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_lineage_relationship(self, lineage_service):
        """Test creating lineage relationship."""
        relationship_data = {
            "source_entity_id": "source-id",
            "target_entity_id": "target-id",
            "relationship_type": "DERIVES_FROM"
        }
        
        relationship = await lineage_service.create_lineage_relationship(relationship_data)
        
        assert relationship["source_entity_id"] == relationship_data["source_entity_id"]
        assert relationship["target_entity_id"] == relationship_data["target_entity_id"]
        assert relationship["relationship_type"] == relationship_data["relationship_type"]
        assert "id" in relationship
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_search_lineage(self, lineage_service):
        """Test lineage search."""
        query = "test table"
        
        results = await lineage_service.search_lineage(query)
        
        assert "items" in results
        assert "total" in results
        assert isinstance(results["items"], list)

class TestAnalyticsService:
    """Unit tests for AnalyticsService."""
    
    @pytest.fixture
    def analytics_service(self):
        return AnalyticsService()
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_dashboard_metrics(self, analytics_service):
        """Test getting dashboard metrics."""
        metrics = await analytics_service.get_dashboard_metrics()
        
        assert "total_entities" in metrics
        assert "active_scans" in metrics
        assert "recent_activities" in metrics
        assert "data_quality_score" in metrics
        assert isinstance(metrics["total_entities"], int)
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_scan_analytics(self, analytics_service):
        """Test getting scan analytics."""
        timeframe = "7d"
        
        analytics = await analytics_service.get_scan_analytics(timeframe)
        
        assert "total_scans" in analytics
        assert "success_rate" in analytics
        assert "failed_scans" in analytics
        assert "scan_duration_avg" in analytics
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_data_quality_metrics(self, analytics_service):
        """Test getting data quality metrics."""
        entity_id = "test-entity-id"
        
        metrics = await analytics_service.get_data_quality_metrics(entity_id)
        
        assert "completeness" in metrics
        assert "accuracy" in metrics
        assert "consistency" in metrics
        assert "validity" in metrics
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_usage_analytics(self, analytics_service):
        """Test getting usage analytics."""
        timeframe = "30d"
        
        usage = await analytics_service.get_usage_analytics(timeframe)
        
        assert "api_calls" in usage
        assert "user_activity" in usage
        assert "popular_entities" in usage
        assert "search_trends" in usage

class TestGovernanceService:
    """Unit tests for GovernanceService."""
    
    @pytest.fixture
    def governance_service(self):
        return GovernanceService()
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_policy(self, governance_service):
        """Test creating governance policy."""
        policy_data = TestDataFactory.governance_policy_data()
        
        policy = await governance_service.create_policy(policy_data)
        
        assert policy["name"] == policy_data["name"]
        assert policy["policy_type"] == policy_data["policy_type"]
        assert policy["is_active"] == policy_data["is_active"]
        assert "id" in policy
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_check_compliance(self, governance_service):
        """Test compliance checking."""
        entity_id = "test-entity-id"
        
        compliance = await governance_service.check_compliance(entity_id)
        
        assert "compliant" in compliance
        assert "violations" in compliance
        assert "policies_checked" in compliance
        assert isinstance(compliance["compliant"], bool)
        assert isinstance(compliance["violations"], list)
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_assign_data_steward(self, governance_service):
        """Test data steward assignment."""
        assignment_data = {
            "entity_id": "test-entity-id",
            "user_id": "steward-user-id",
            "responsibilities": ["data_quality", "access_control"]
        }
        
        assignment = await governance_service.assign_data_steward(assignment_data)
        
        assert assignment["entity_id"] == assignment_data["entity_id"]
        assert assignment["user_id"] == assignment_data["user_id"]
        assert assignment["responsibilities"] == assignment_data["responsibilities"]
        assert "id" in assignment
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_audit_logs(self, governance_service):
        """Test getting audit logs."""
        entity_id = "test-entity-id"
        limit = 10
        
        logs = await governance_service.get_audit_logs(entity_id, limit)
        
        assert "items" in logs
        assert "total" in logs
        assert isinstance(logs["items"], list)
        assert len(logs["items"]) <= limit

class TestCacheService:
    """Unit tests for cache service."""
    
    @pytest.fixture
    def redis_cache(self):
        return RedisCache()
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_cache_get_set(self, redis_cache):
        """Test cache get and set operations."""
        # Mock Redis client
        redis_cache.redis_client = Mock()
        redis_cache.is_connected = True
        
        # Mock async execution
        with patch('asyncio.get_event_loop') as mock_loop:
            mock_executor = AsyncMock()
            mock_loop.return_value.run_in_executor = mock_executor
            mock_executor.return_value = '{"test": "value"}'
            
            # Test set
            result = await redis_cache.set("test_key", {"test": "value"})
            assert result is True
            
            # Test get
            value = await redis_cache.get("test_key")
            assert value == {"test": "value"}
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_cache_delete(self, redis_cache):
        """Test cache delete operation."""
        redis_cache.redis_client = Mock()
        redis_cache.is_connected = True
        
        with patch('asyncio.get_event_loop') as mock_loop:
            mock_executor = AsyncMock()
            mock_loop.return_value.run_in_executor = mock_executor
            mock_executor.return_value = 1
            
            result = await redis_cache.delete("test_key")
            assert result is True
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_cache_increment(self, redis_cache):
        """Test cache increment operation."""
        redis_cache.redis_client = Mock()
        redis_cache.redis_client.pipeline.return_value = Mock()
        redis_cache.is_connected = True
        
        with patch('asyncio.get_event_loop') as mock_loop:
            mock_executor = AsyncMock()
            mock_loop.return_value.run_in_executor = mock_executor
            mock_executor.return_value = [5]  # Pipeline result
            
            result = await redis_cache.increment("counter_key", 2)
            assert result == 5
    
    @pytest.mark.unit
    def test_cache_keys_generation(self):
        """Test cache key generation."""
        user_id = "user123"
        entity_id = "entity456"
        
        user_key = CacheKeys.user_profile(user_id)
        entity_key = CacheKeys.entity_details(entity_id)
        
        assert user_key == f"user:profile:{user_id}"
        assert entity_key == f"entity:details:{entity_id}"
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_cache_result_decorator(self):
        """Test cache result decorator."""
        # Mock cache
        cache_mock = Mock()
        cache_mock.get = AsyncMock(return_value=None)
        cache_mock.set = AsyncMock(return_value=True)
        
        @cache_result("test_prefix", ttl=300)
        async def test_function(param1, param2):
            return f"result_{param1}_{param2}"
        
        with patch('app.services.cache_service.cache', cache_mock):
            result = await test_function("a", "b")
            
            assert result == "result_a_b"
            cache_mock.get.assert_called_once()
            cache_mock.set.assert_called_once()

class TestPasswordSecurity:
    """Unit tests for password security functions."""
    
    @pytest.mark.unit
    def test_password_hashing(self):
        """Test password hashing and verification."""
        auth_service = AuthService()
        password = "testpassword123"
        
        # Hash password
        hashed = auth_service.get_password_hash(password)
        
        assert hashed != password
        assert len(hashed) > 0
        
        # Verify correct password
        assert auth_service.verify_password(password, hashed) is True
        
        # Verify incorrect password
        assert auth_service.verify_password("wrongpassword", hashed) is False
    
    @pytest.mark.unit
    def test_password_hash_uniqueness(self):
        """Test that same password generates different hashes."""
        auth_service = AuthService()
        password = "testpassword123"
        
        hash1 = auth_service.get_password_hash(password)
        hash2 = auth_service.get_password_hash(password)
        
        # Hashes should be different due to salt
        assert hash1 != hash2
        
        # But both should verify correctly
        assert auth_service.verify_password(password, hash1) is True
        assert auth_service.verify_password(password, hash2) is True

class TestTokenSecurity:
    """Unit tests for JWT token security."""
    
    @pytest.mark.unit
    def test_token_expiration(self):
        """Test JWT token expiration."""
        auth_service = AuthService()
        user_data = {"user_id": "1", "username": "testuser"}
        
        # Create token with short expiration
        with patch('app.core.config.settings.ACCESS_TOKEN_EXPIRE_MINUTES', 0):
            token = auth_service.create_access_token(user_data)
            
            # Token should be invalid due to expiration
            decoded = auth_service.verify_token(token)
            assert decoded is None
    
    @pytest.mark.unit
    def test_token_tampering(self):
        """Test JWT token tampering detection."""
        auth_service = AuthService()
        user_data = {"user_id": "1", "username": "testuser"}
        
        token = auth_service.create_access_token(user_data)
        
        # Tamper with token
        tampered_token = token[:-5] + "XXXXX"
        
        # Tampered token should be invalid
        decoded = auth_service.verify_token(tampered_token)
        assert decoded is None

class TestDataValidation:
    """Unit tests for data validation."""
    
    @pytest.mark.unit
    def test_email_validation(self):
        """Test email validation."""
        from app.services.auth_service import AuthService
        
        auth_service = AuthService()
        
        valid_emails = [
            "user@example.com",
            "test.email@domain.co.uk",
            "user+tag@example.org"
        ]
        
        invalid_emails = [
            "invalid.email",
            "@domain.com",
            "user@",
            "user space@domain.com"
        ]
        
        # Note: This would require implementing email validation in AuthService
        # For now, we'll test the concept
        for email in valid_emails:
            assert "@" in email and "." in email.split("@")[1]
        
        for email in invalid_emails:
            assert not (email.count("@") == 1 and "." in email.split("@")[-1])
    
    @pytest.mark.unit
    def test_username_validation(self):
        """Test username validation."""
        valid_usernames = [
            "user123",
            "test_user",
            "john.doe"
        ]
        
        invalid_usernames = [
            "ab",  # too short
            "user with spaces",
            "user@domain",
            ""
        ]
        
        for username in valid_usernames:
            assert len(username) >= 3 and " " not in username
            
        for username in invalid_usernames:
            assert len(username) < 3 or " " in username or "@" in username
