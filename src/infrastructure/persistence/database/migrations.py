import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from .config import DatabaseConfig

"""Database Migration and Security Setup
Extracted from production_database_config.py to reduce file size
Translated Arabic comments to English"""

from src.infrastructure.logging_config import get_logger
logger = get_logger(__name__, component="persistence")


class DatabaseMigrationManager:
    """Database migration manager"""
    
    def __init__(self, config: DatabaseConfig) -> None:
        self.config = config
    
    async def create_production_schema(self) -> bool:
        """Create secure production schema"""
        try:
            if self.config.engine_type != "postgresql":
                logger.warning("Production schema optimization only available for PostgreSQL")
                return True
            
            engine = create_async_engine(self.config.database_url, **self.config.get_engine_kwargs())
            async with engine.begin() as conn:
                # Enable necessary PostgreSQL extensions
                await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
                await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "pgcrypto"'))
                await conn.execute(
                    text('CREATE EXTENSION IF NOT EXISTS "pg_stat_statements"')
                )
                
                # Create audit function for COPPA compliance
                audit_function = """
                CREATE OR REPLACE FUNCTION audit_child_data_changes()
                RETURNS TRIGGER AS $$
                BEGIN
                    INSERT INTO audit_logs (
                        table_name, operation, old_data, new_data,
                        user_id, timestamp, child_id
                    ) VALUES (
                        TG_TABLE_NAME, TG_OP,
                        row_to_json(OLD), row_to_json(NEW),
                        current_setting('app.current_user_id', true),
                        NOW(),
                        COALESCE(NEW.id, OLD.id)
                    );
                    RETURN COALESCE(NEW, OLD);
                END;
                $$ LANGUAGE plpgsql;
                """
                await conn.execute(text(audit_function))
                
                # Security settings for child data protection
                security_settings = [
                    "SET row_security = on",
                    "SET log_statement = 'mod'",  # Log modifications
                    "SET log_min_duration_statement = 1000",  # Log slow queries
                ]
                for setting in security_settings:
                    await conn.execute(text(setting))
                
                logger.info("Production PostgreSQL schema optimizations applied")
            
            await engine.dispose()
            return True
        except Exception as e:
            logger.error(f"Failed to create production schema: {e}")
            if self.config.environment == "production":
                raise RuntimeError(f"Production schema creation failed: {e}")
            return False
    
    async def setup_child_data_security(self) -> bool:
        """Setup child data security"""
        try:
            engine = create_async_engine(
                self.config.database_url, **self.config.get_engine_kwargs()
            )
            async with engine.begin() as conn:
                if self.config.engine_type == "postgresql":
                    # Create row-level security policies for child data
                    child_security_policies = [
                        """
                        CREATE POLICY child_data_access ON children
                        FOR ALL TO ai_teddy_app
                        USING (parent_id = current_setting('app.current_user_id')::uuid)
                        """,
                        """
                        CREATE POLICY conversation_access ON conversations
                        FOR ALL TO ai_teddy_app
                        USING (child_id IN (
                            SELECT id FROM children
                            WHERE parent_id = current_setting('app.current_user_id')::uuid
                        ))
                        """,
                    ]
                    for policy in child_security_policies:
                        try:
                            await conn.execute(text(policy))
                        except Exception as e:
                            if "already exists" not in str(e):
                                logger.warning(f"Failed to create security policy: {e}")
                
                # Create indexes for performance
                performance_indexes = [
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_children_parent_id ON children(parent_id)",
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_conversations_child_id ON conversations(child_id)",
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_conversations_timestamp ON conversations(timestamp)",
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_safety_events_child_id ON safety_events(child_id)",
                    "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp)",
                ]
                for index in performance_indexes:
                    try:
                        await conn.execute(text(index))
                    except Exception as e:
                        if "already exists" not in str(e):
                            logger.warning(f"Failed to create index: {e}")
                
                logger.info("Child data security measures configured")
            
            await engine.dispose()
            return True
        except Exception as e:
            logger.error(f"Failed to setup child data security: {e}")
            return False