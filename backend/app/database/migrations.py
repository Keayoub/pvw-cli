#  Purview CLI v2.0 - Database Migration Manager
# Handles database schema creation, updates, and migrations

import asyncio
import logging
from typing import List, Dict, Any
from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

from app.database.connection import get_engine, get_session
from app.database.models import Base, User, Entity, DataSource, Scan, GovernancePolicy, Classification, LineageRelationship, AuditLog, Notification, Tag, DataSourceConnection, EntityMetadata

logger = logging.getLogger(__name__)

class MigrationManager:
    """Manages database schema migrations and updates"""
    
    def __init__(self):
        self.engine = None
        self.migrations = []
        self._register_migrations()
        
    async def initialize(self):
        """Initialize migration manager"""
        self.engine = get_engine()
        
    def _register_migrations(self):
        """Register all available migrations"""
        self.migrations = [
            {
                "version": "001",
                "name": "initial_schema",
                "description": "Create initial database schema",
                "up": self._migration_001_up,
                "down": self._migration_001_down
            },
            {
                "version": "002", 
                "name": "add_indexes",
                "description": "Add performance indexes",
                "up": self._migration_002_up,
                "down": self._migration_002_down
            },
            {
                "version": "003",
                "name": "add_audit_triggers",
                "description": "Add audit triggers for change tracking",
                "up": self._migration_003_up,
                "down": self._migration_003_down
            }
        ]
        
    async def create_migration_table(self):
        """Create migrations tracking table"""
        create_migration_table_sql = """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version VARCHAR(10) PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            rollback_sql TEXT
        )
        """
        
        try:
            async with get_session() as session:
                await session.execute(text(create_migration_table_sql))
                await session.commit()
                logger.info("Migration tracking table created")
                
        except Exception as e:
            logger.error(f"Failed to create migration table: {e}")
            raise
            
    async def get_applied_migrations(self) -> List[str]:
        """Get list of applied migration versions"""
        try:
            async with get_session() as session:
                result = await session.execute(
                    text("SELECT version FROM schema_migrations ORDER BY version")
                )
                return [row[0] for row in result.fetchall()]
                
        except Exception as e:
            logger.error(f"Failed to get applied migrations: {e}")
            return []
            
    async def mark_migration_applied(self, migration: Dict[str, Any]):
        """Mark a migration as applied"""
        try:
            async with get_session() as session:
                await session.execute(
                    text("""
                        INSERT INTO schema_migrations (version, name, description)
                        VALUES (:version, :name, :description)
                    """),
                    {
                        "version": migration["version"],
                        "name": migration["name"],
                        "description": migration["description"]
                    }
                )
                await session.commit()
                logger.info(f"Migration {migration['version']} marked as applied")
                
        except Exception as e:
            logger.error(f"Failed to mark migration as applied: {e}")
            raise
            
    async def remove_migration_record(self, version: str):
        """Remove migration record (for rollback)"""
        try:
            async with get_session() as session:
                await session.execute(
                    text("DELETE FROM schema_migrations WHERE version = :version"),
                    {"version": version}
                )
                await session.commit()
                logger.info(f"Migration {version} record removed")
                
        except Exception as e:
            logger.error(f"Failed to remove migration record: {e}")
            raise
            
    async def migrate_up(self, target_version: str = None):
        """Apply pending migrations up to target version"""
        await self.create_migration_table()
        applied_migrations = await self.get_applied_migrations()
        
        pending_migrations = [
            m for m in self.migrations 
            if m["version"] not in applied_migrations
        ]
        
        if target_version:
            pending_migrations = [
                m for m in pending_migrations
                if m["version"] <= target_version
            ]
            
        for migration in pending_migrations:
            logger.info(f"Applying migration {migration['version']}: {migration['name']}")
            
            try:
                await migration["up"]()
                await self.mark_migration_applied(migration)
                logger.info(f"Migration {migration['version']} applied successfully")
                
            except Exception as e:
                logger.error(f"Migration {migration['version']} failed: {e}")
                raise
                
    async def migrate_down(self, target_version: str):
        """Rollback migrations down to target version"""
        applied_migrations = await self.get_applied_migrations()
        
        rollback_migrations = [
            m for m in reversed(self.migrations)
            if m["version"] in applied_migrations and m["version"] > target_version
        ]
        
        for migration in rollback_migrations:
            logger.info(f"Rolling back migration {migration['version']}: {migration['name']}")
            
            try:
                await migration["down"]()
                await self.remove_migration_record(migration["version"])
                logger.info(f"Migration {migration['version']} rolled back successfully")
                
            except Exception as e:
                logger.error(f"Migration rollback {migration['version']} failed: {e}")
                raise
                
    async def _migration_001_up(self):
        """Migration 001: Create initial schema"""
        logger.info("Creating initial database schema")
        
        try:
            # Create all tables using SQLAlchemy metadata
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
                
            # Create default admin user
            await self._create_default_admin_user()
            
            # Create default classifications
            await self._create_default_classifications()
            
            logger.info("Initial schema created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create initial schema: {e}")
            raise
            
    async def _migration_001_down(self):
        """Migration 001 rollback: Drop all tables"""
        logger.info("Dropping all database tables")
        
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
                
            logger.info("All tables dropped successfully")
            
        except Exception as e:
            logger.error(f"Failed to drop tables: {e}")
            raise
            
    async def _migration_002_up(self):
        """Migration 002: Add performance indexes"""
        logger.info("Adding performance indexes")
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_entities_name ON entities(name)",
            "CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(entity_type)",
            "CREATE INDEX IF NOT EXISTS idx_entities_status ON entities(status)",
            "CREATE INDEX IF NOT EXISTS idx_entities_created_at ON entities(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_scans_status ON scans(status)",
            "CREATE INDEX IF NOT EXISTS idx_scans_data_source ON scans(data_source_id)",
            "CREATE INDEX IF NOT EXISTS idx_scans_created_at ON scans(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_lineage_source ON lineage_relationships(source_entity_id)",
            "CREATE INDEX IF NOT EXISTS idx_lineage_target ON lineage_relationships(target_entity_id)",
            "CREATE INDEX IF NOT EXISTS idx_audit_entity ON audit_logs(entity_id)",
            "CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_logs(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
            "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)",
            "CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_notifications_read ON notifications(is_read)"
        ]
        
        try:
            async with get_session() as session:
                for index_sql in indexes:
                    await session.execute(text(index_sql))
                await session.commit()
                
            logger.info("Performance indexes added successfully")
            
        except Exception as e:
            logger.error(f"Failed to add indexes: {e}")
            raise
            
    async def _migration_002_down(self):
        """Migration 002 rollback: Drop performance indexes"""
        logger.info("Dropping performance indexes")
        
        indexes = [
            "DROP INDEX IF EXISTS idx_entities_name",
            "DROP INDEX IF EXISTS idx_entities_type", 
            "DROP INDEX IF EXISTS idx_entities_status",
            "DROP INDEX IF EXISTS idx_entities_created_at",
            "DROP INDEX IF EXISTS idx_scans_status",
            "DROP INDEX IF EXISTS idx_scans_data_source",
            "DROP INDEX IF EXISTS idx_scans_created_at",
            "DROP INDEX IF EXISTS idx_lineage_source",
            "DROP INDEX IF EXISTS idx_lineage_target",
            "DROP INDEX IF EXISTS idx_audit_entity",
            "DROP INDEX IF EXISTS idx_audit_user",
            "DROP INDEX IF EXISTS idx_audit_timestamp",
            "DROP INDEX IF EXISTS idx_users_email",
            "DROP INDEX IF EXISTS idx_users_username",
            "DROP INDEX IF EXISTS idx_notifications_user",
            "DROP INDEX IF EXISTS idx_notifications_read"
        ]
        
        try:
            async with get_session() as session:
                for index_sql in indexes:
                    await session.execute(text(index_sql))
                await session.commit()
                
            logger.info("Performance indexes dropped successfully")
            
        except Exception as e:
            logger.error(f"Failed to drop indexes: {e}")
            raise
            
    async def _migration_003_up(self):
        """Migration 003: Add audit triggers"""
        logger.info("Adding audit triggers")
        
        # Note: This is SQLite-specific. For PostgreSQL, use different syntax
        triggers = [
            """
            CREATE TRIGGER IF NOT EXISTS audit_entities_update
            AFTER UPDATE ON entities
            FOR EACH ROW
            BEGIN
                INSERT INTO audit_logs (entity_id, action, old_values, new_values, timestamp)
                VALUES (
                    NEW.id,
                    'UPDATE',
                    json_object('name', OLD.name, 'status', OLD.status),
                    json_object('name', NEW.name, 'status', NEW.status),
                    datetime('now')
                );
            END
            """,
            """
            CREATE TRIGGER IF NOT EXISTS audit_entities_delete
            AFTER DELETE ON entities
            FOR EACH ROW
            BEGIN
                INSERT INTO audit_logs (entity_id, action, old_values, timestamp)
                VALUES (
                    OLD.id,
                    'DELETE',
                    json_object('name', OLD.name, 'status', OLD.status),
                    datetime('now')
                );
            END
            """
        ]
        
        try:
            async with get_session() as session:
                for trigger_sql in triggers:
                    await session.execute(text(trigger_sql))
                await session.commit()
                
            logger.info("Audit triggers added successfully")
            
        except Exception as e:
            logger.error(f"Failed to add audit triggers: {e}")
            raise
            
    async def _migration_003_down(self):
        """Migration 003 rollback: Drop audit triggers"""
        logger.info("Dropping audit triggers")
        
        triggers = [
            "DROP TRIGGER IF EXISTS audit_entities_update",
            "DROP TRIGGER IF EXISTS audit_entities_delete"
        ]
        
        try:
            async with get_session() as session:
                for trigger_sql in triggers:
                    await session.execute(text(trigger_sql))
                await session.commit()
                
            logger.info("Audit triggers dropped successfully")
            
        except Exception as e:
            logger.error(f"Failed to drop audit triggers: {e}")
            raise
            
    async def _create_default_admin_user(self):
        """Create default admin user"""
        try:
            from app.services.auth_service import AuthService
            auth_service = AuthService()
            
            # Check if admin user already exists
            async with get_session() as session:
                result = await session.execute(
                    text("SELECT id FROM users WHERE username = 'admin'")
                )
                if result.fetchone():
                    logger.info("Admin user already exists")
                    return
                    
            # Create admin user
            admin_user = await auth_service.create_user(
                username="admin",
                email="admin@purview-cli.local",
                password="admin123",  # Should be changed after first login
                full_name="System Administrator",
                role="admin"
            )
            
            logger.info("Default admin user created")
            
        except Exception as e:
            logger.error(f"Failed to create default admin user: {e}")
            
    async def _create_default_classifications(self):
        """Create default classification definitions"""
        try:
            async with get_session() as session:
                # Check if classifications already exist
                result = await session.execute(
                    text("SELECT COUNT(*) FROM classifications")
                )
                count = result.scalar()
                
                if count > 0:
                    logger.info("Classifications already exist")
                    return
                    
                # Create default classifications
                default_classifications = [
                    {
                        "name": "PII",
                        "description": "Personally Identifiable Information",
                        "level": "HIGH",
                        "rules": {"patterns": ["email", "ssn", "phone"], "confidence": 0.8}
                    },
                    {
                        "name": "Financial",
                        "description": "Financial and monetary data",
                        "level": "HIGH", 
                        "rules": {"patterns": ["credit_card", "bank_account"], "confidence": 0.9}
                    },
                    {
                        "name": "Confidential",
                        "description": "Confidential business information",
                        "level": "MEDIUM",
                        "rules": {"patterns": ["confidential", "internal"], "confidence": 0.7}
                    },
                    {
                        "name": "Public",
                        "description": "Publicly available information",
                        "level": "LOW",
                        "rules": {"patterns": ["public", "open"], "confidence": 0.5}
                    }
                ]
                
                for classification_data in default_classifications:
                    await session.execute(
                        text("""
                            INSERT INTO classifications (name, description, level, rules, created_at)
                            VALUES (:name, :description, :level, :rules, :created_at)
                        """),
                        {
                            **classification_data,
                            "rules": str(classification_data["rules"]),
                            "created_at": datetime.utcnow()
                        }
                    )
                    
                await session.commit()
                logger.info("Default classifications created")
                
        except Exception as e:
            logger.error(f"Failed to create default classifications: {e}")
            
    async def check_database_health(self) -> Dict[str, Any]:
        """Check database health and return status"""
        health_status = {
            "database_connected": False,
            "tables_exist": False,
            "migrations_applied": [],
            "indexes_exist": False,
            "triggers_exist": False,
            "record_counts": {}
        }
        
        try:
            # Check database connection
            async with get_session() as session:
                await session.execute(text("SELECT 1"))
                health_status["database_connected"] = True
                
                # Check if main tables exist
                inspector = inspect(self.engine)
                tables = inspector.get_table_names()
                expected_tables = ['users', 'entities', 'data_sources', 'scans', 'governance_policies']
                health_status["tables_exist"] = all(table in tables for table in expected_tables)
                
                # Get applied migrations
                if 'schema_migrations' in tables:
                    result = await session.execute(text("SELECT version FROM schema_migrations"))
                    health_status["migrations_applied"] = [row[0] for row in result.fetchall()]
                    
                # Check indexes
                if health_status["tables_exist"]:
                    result = await session.execute(text("SELECT name FROM sqlite_master WHERE type='index'"))
                    indexes = [row[0] for row in result.fetchall()]
                    health_status["indexes_exist"] = any(idx.startswith('idx_') for idx in indexes)
                    
                # Get record counts
                for table in expected_tables:
                    if table in tables:
                        result = await session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                        health_status["record_counts"][table] = result.scalar()
                        
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            
        return health_status

# Create migration manager instance
migration_manager = MigrationManager()

async def run_migrations():
    """Run database migrations"""
    await migration_manager.initialize()
    await migration_manager.migrate_up()
    logger.info("Database migrations completed")

async def check_database():
    """Check database health"""
    await migration_manager.initialize()
    return await migration_manager.check_database_health()
