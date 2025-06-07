# Enhanced Purview CLI v2.0 - Test Configuration
# Pytest configuration and test utilities

import pytest
import asyncio
import tempfile
import os
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient
from fastapi.testclient import TestClient

from app.main import app
from app.database.models import Base
from app.database.connection import get_session
from app.services.cache_service import cache
from app.core.config import settings

# Test database URL (use in-memory SQLite for tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    # Create test engine
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session factory
    TestSessionLocal = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with TestSessionLocal() as session:
        yield session
    
    # Clean up
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()

@pytest.fixture
async def client(test_db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with test database."""
    def get_test_session():
        return test_db
    
    app.dependency_overrides[get_session] = get_test_session
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()

@pytest.fixture
def sync_client() -> Generator[TestClient, None, None]:
    """Create synchronous test client for WebSocket testing."""
    with TestClient(app) as client:
        yield client

@pytest.fixture
async def auth_headers(client: AsyncClient) -> dict:
    """Create authentication headers for tests."""
    # Create test user and get token
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "full_name": "Test User"
    }
    
    # Register user
    await client.post("/api/auth/register", json=user_data)
    
    # Login and get token
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    
    response = await client.post("/api/auth/login", json=login_data)
    token_data = response.json()
    
    return {"Authorization": f"Bearer {token_data['access_token']}"}

@pytest.fixture
async def admin_headers(client: AsyncClient) -> dict:
    """Create admin authentication headers for tests."""
    # Create admin user and get token
    admin_data = {
        "username": "admin",
        "email": "admin@example.com", 
        "password": "admin123",
        "full_name": "Admin User",
        "role": "admin"
    }
    
    # Register admin
    await client.post("/api/auth/register", json=admin_data)
    
    # Login and get token
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = await client.post("/api/auth/login", json=login_data)
    token_data = response.json()
    
    return {"Authorization": f"Bearer {token_data['access_token']}"}

@pytest.fixture
def temp_file():
    """Create temporary file for upload tests."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        f.write("id,name,email\n1,John Doe,john@example.com\n2,Jane Smith,jane@example.com")
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)

@pytest.fixture(autouse=True)
async def setup_cache():
    """Setup test cache (mock Redis)."""
    # Use in-memory cache for tests
    cache.is_connected = False  # Disable Redis for tests
    yield
    # Cleanup after test

# Test data factories
class TestDataFactory:
    """Factory for creating test data."""
    
    @staticmethod
    def user_data(role: str = "user") -> dict:
        return {
            "username": f"testuser_{role}",
            "email": f"test_{role}@example.com",
            "password": "testpass123",
            "full_name": f"Test {role.title()} User",
            "role": role
        }
    
    @staticmethod
    def entity_data() -> dict:
        return {
            "name": "test_table",
            "qualified_name": "test_db.test_schema.test_table",
            "entity_type": "Table",
            "description": "Test table entity",
            "status": "ACTIVE",
            "properties": {
                "database": "test_db",
                "schema": "test_schema",
                "columns": ["id", "name", "email"]
            }
        }
    
    @staticmethod
    def data_source_data() -> dict:
        return {
            "name": "test_datasource",
            "type": "PostgreSQL",
            "connection_string": "postgresql://test:test@localhost/testdb",
            "description": "Test data source",
            "properties": {
                "host": "localhost",
                "port": 5432,
                "database": "testdb"
            }
        }
    
    @staticmethod
    def scan_data(data_source_id: str) -> dict:
        return {
            "name": "test_scan",
            "data_source_id": data_source_id,
            "scan_type": "FULL",
            "status": "PENDING",
            "configuration": {
                "include_patterns": ["*"],
                "exclude_patterns": ["temp_*"],
                "scan_classifications": True
            }
        }
    
    @staticmethod
    def governance_policy_data() -> dict:
        return {
            "name": "test_policy",
            "description": "Test governance policy",
            "policy_type": "DATA_ACCESS",
            "rules": {
                "access_conditions": ["user.role == 'admin'"],
                "data_classifications": ["PII"],
                "actions": ["ALLOW_READ"]
            },
            "is_active": True
        }
    
    @staticmethod
    def classification_data() -> dict:
        return {
            "name": "TEST_PII",
            "description": "Test PII classification",
            "level": "HIGH",
            "rules": {
                "patterns": ["email", "phone"],
                "confidence": 0.8
            }
        }

# Test utilities
class TestUtils:
    """Utility functions for tests."""
    
    @staticmethod
    async def create_test_user(client: AsyncClient, role: str = "user") -> dict:
        """Create a test user and return user data."""
        user_data = TestDataFactory.user_data(role)
        response = await client.post("/api/auth/register", json=user_data)
        assert response.status_code == 201
        return response.json()
    
    @staticmethod
    async def login_user(client: AsyncClient, username: str, password: str) -> dict:
        """Login user and return token data."""
        login_data = {"username": username, "password": password}
        response = await client.post("/api/auth/login", json=login_data)
        assert response.status_code == 200
        return response.json()
    
    @staticmethod
    async def create_test_entity(client: AsyncClient, headers: dict) -> dict:
        """Create a test entity and return entity data."""
        entity_data = TestDataFactory.entity_data()
        response = await client.post("/api/entities", json=entity_data, headers=headers)
        assert response.status_code == 201
        return response.json()
    
    @staticmethod
    async def create_test_data_source(client: AsyncClient, headers: dict) -> dict:
        """Create a test data source and return data source data."""
        ds_data = TestDataFactory.data_source_data()
        response = await client.post("/api/data-sources", json=ds_data, headers=headers)
        assert response.status_code == 201
        return response.json()
    
    @staticmethod
    def assert_valid_uuid(uuid_string: str):
        """Assert that string is a valid UUID."""
        import uuid
        try:
            uuid.UUID(uuid_string)
        except ValueError:
            pytest.fail(f"'{uuid_string}' is not a valid UUID")
    
    @staticmethod
    def assert_datetime_format(datetime_string: str):
        """Assert that string is a valid ISO datetime."""
        from datetime import datetime
        try:
            datetime.fromisoformat(datetime_string.replace('Z', '+00:00'))
        except ValueError:
            pytest.fail(f"'{datetime_string}' is not a valid ISO datetime")

# Custom pytest markers
pytest.register_assert_rewrite("tests.conftest")

# Test configuration
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "auth: mark test as requiring authentication"
    )
    config.addinivalue_line(
        "markers", "admin: mark test as requiring admin privileges"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "websocket: mark test as WebSocket test"
    )

# Test database initialization
async def init_test_database():
    """Initialize test database with test data."""
    from app.database.migrations import migration_manager
    await migration_manager.initialize()
    await migration_manager.migrate_up()

# Export commonly used items
__all__ = [
    "test_db",
    "client", 
    "sync_client",
    "auth_headers",
    "admin_headers",
    "temp_file",
    "TestDataFactory",
    "TestUtils",
    "init_test_database"
]
