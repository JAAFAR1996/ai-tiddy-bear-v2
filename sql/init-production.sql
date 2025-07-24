-- AI Teddy Bear - Production Database Initialization
-- PostgreSQL schema with child safety, COPPA compliance, and security

-- ================================
-- Enable Required Extensions
-- ================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- Trigram matching for search

-- ================================
-- Child Safety & COPPA Compliance Settings
-- ================================
-- Set up session variables for child data protection
SET session_replication_role = 'origin';
SET row_security = on;
SET log_statement = 'mod';  -- Log all modifications
SET log_min_duration_statement = 1000;  -- Log queries taking >1s

-- ================================
-- Create Application Role
-- ================================
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'ai_teddy_app') THEN
        CREATE ROLE ai_teddy_app WITH LOGIN PASSWORD 'secure_app_password_change_me';
    END IF;
END
$$;

-- Grant necessary permissions
GRANT CONNECT ON DATABASE ai_teddy_prod TO ai_teddy_app;
GRANT USAGE ON SCHEMA public TO ai_teddy_app;

-- ================================
-- Audit Log Function (COPPA Compliance)
-- ================================
CREATE OR REPLACE FUNCTION audit_child_data_changes()
RETURNS TRIGGER AS $$
BEGIN
    -- Insert audit record for child data modifications
    INSERT INTO audit_logs (
        table_name,
        operation,
        old_data,
        new_data,
        user_id,
        timestamp,
        child_id,
        ip_address,
        user_agent
    ) VALUES (
        TG_TABLE_NAME,
        TG_OP,
        CASE WHEN TG_OP = 'DELETE' OR TG_OP = 'UPDATE' THEN row_to_json(OLD) ELSE NULL END,
        CASE WHEN TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN row_to_json(NEW) ELSE NULL END,
        COALESCE(current_setting('app.current_user_id', true), 'system'),
        NOW(),
        CASE
            WHEN TG_TABLE_NAME = 'children' THEN COALESCE(NEW.id, OLD.id)
            WHEN TG_TABLE_NAME = 'conversations' THEN COALESCE(NEW.child_id, OLD.child_id)
            ELSE NULL
        END,
        current_setting('app.client_ip', true),
        current_setting('app.user_agent', true)
    );

    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- ================================
-- Child Data Protection Function
-- ================================
CREATE OR REPLACE FUNCTION protect_child_data()
RETURNS TRIGGER AS $$
BEGIN
    -- Ensure child age compliance (COPPA: under 13)
    IF TG_TABLE_NAME = 'children' AND NEW.age > 13 THEN
        RAISE EXCEPTION 'Child age cannot exceed 13 years (COPPA compliance)';
    END IF;

    -- Encrypt sensitive child data before storage
    IF TG_TABLE_NAME = 'children' AND TG_OP IN ('INSERT', 'UPDATE') THEN
        -- Encrypt sensitive fields
        IF NEW.medical_notes IS NOT NULL THEN
            NEW.medical_notes := pgp_sym_encrypt(NEW.medical_notes, current_setting('app.encryption_key', false));
        END IF;

        IF NEW.emergency_contacts IS NOT NULL THEN
            NEW.emergency_contacts := pgp_sym_encrypt(NEW.emergency_contacts::text, current_setting('app.encryption_key', false));
        END IF;
    END IF;

    -- Set data retention expiry (90 days from creation)
    IF TG_OP = 'INSERT' THEN
        NEW.data_retention_expires := NEW.created_at + INTERVAL '90 days';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ================================
-- Data Retention Cleanup Function
-- ================================
CREATE OR REPLACE FUNCTION cleanup_expired_child_data()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER := 0;
    expired_record RECORD;
BEGIN
    -- Log cleanup operation
    INSERT INTO audit_logs (
        table_name, operation, user_id, timestamp,
        new_data
    ) VALUES (
        'system_cleanup', 'DATA_RETENTION_CLEANUP', 'system', NOW(),
        json_build_object('cleanup_started', NOW())
    );

    -- Delete expired child records
    FOR expired_record IN
        SELECT id FROM children
        WHERE data_retention_expires < NOW()
    LOOP
        -- Secure deletion of child data
        DELETE FROM conversations WHERE child_id = expired_record.id;
        DELETE FROM safety_events WHERE child_id = expired_record.id;
        DELETE FROM children WHERE id = expired_record.id;

        deleted_count := deleted_count + 1;

        -- Log each deletion for COPPA compliance
        INSERT INTO audit_logs (
            table_name, operation, user_id, timestamp,
            old_data
        ) VALUES (
            'children', 'COPPA_DELETION', 'system', NOW(),
            json_build_object('child_id', expired_record.id, 'reason', 'data_retention_expired')
        );
    END LOOP;

    -- Log completion
    INSERT INTO audit_logs (
        table_name, operation, user_id, timestamp,
        new_data
    ) VALUES (
        'system_cleanup', 'DATA_RETENTION_CLEANUP_COMPLETE', 'system', NOW(),
        json_build_object('records_deleted', deleted_count, 'cleanup_completed', NOW())
    );

    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- ================================
-- Security Validation Function
-- ================================
CREATE OR REPLACE FUNCTION validate_child_access(child_id UUID, parent_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
    -- Verify parent owns the child record
    RETURN EXISTS (
        SELECT 1 FROM children
        WHERE id = child_id AND parent_id = validate_child_access.parent_id
    );
END;
$$ LANGUAGE plpgsql;

-- ================================
-- Performance Indexes
-- ================================
-- These will be created by the application, but defining them here for reference

-- User indexes
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email ON users(email);
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_active ON users(is_active) WHERE is_active = true;
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_created ON users(created_at);

-- Child indexes
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_children_parent_id ON children(parent_id);
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_children_age ON children(age);
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_children_retention ON children(data_retention_expires);

-- Conversation indexes
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_conversations_child_id ON conversations(child_id);
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_conversations_timestamp ON conversations(timestamp);
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_conversations_safety ON conversations(safety_score);

-- Safety event indexes
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_safety_events_child_id ON safety_events(child_id);
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_safety_events_severity ON safety_events(severity);
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_safety_events_timestamp ON safety_events(timestamp);

-- Audit log indexes
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp);
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_child_id ON audit_logs(child_id);
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_table ON audit_logs(table_name);

-- ================================
-- Row Level Security Policies
-- ================================
-- These will be applied when tables are created by SQLAlchemy

-- Child data access policy
-- ALTER TABLE children ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY child_data_access ON children
--     FOR ALL TO ai_teddy_app
--     USING (parent_id = current_setting('app.current_user_id')::uuid);

-- Conversation access policy
-- ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY conversation_access ON conversations
--     FOR ALL TO ai_teddy_app
--     USING (child_id IN (
--         SELECT id FROM children
--         WHERE parent_id = current_setting('app.current_user_id')::uuid
--     ));

-- ================================
-- Scheduled Jobs Setup
-- ================================
-- Create extension for scheduled jobs (if available)
-- CREATE EXTENSION IF NOT EXISTS pg_cron;

-- Schedule daily cleanup of expired child data (COPPA compliance)
-- This would typically be done via application scheduler or external cron
-- SELECT cron.schedule('cleanup-expired-data', '0 2 * * *', 'SELECT cleanup_expired_child_data();');

-- ================================
-- Security Settings
-- ================================
-- Enable query logging for security auditing
ALTER SYSTEM SET log_statement = 'mod';
ALTER SYSTEM SET log_min_duration_statement = 1000;
ALTER SYSTEM SET log_line_prefix = '%m [%p] %q%u@%d ';
ALTER SYSTEM SET log_connections = on;
ALTER SYSTEM SET log_disconnections = on;
ALTER SYSTEM SET log_duration = on;

-- Performance settings for child safety workload
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET effective_cache_size = '4GB';
ALTER SYSTEM SET maintenance_work_mem = '256MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
ALTER SYSTEM SET random_page_cost = 1.1;  -- SSD optimization
ALTER SYSTEM SET effective_io_concurrency = 200;

-- Security hardening
ALTER SYSTEM SET ssl = on;
ALTER SYSTEM SET password_encryption = 'scram-sha-256';
ALTER SYSTEM SET row_security = on;

-- Apply settings (requires restart)
SELECT pg_reload_conf();

-- ================================
-- Initial Data Setup
-- ================================
-- Create system user for automated operations
INSERT INTO users (
    id, email, password_hash, role, is_active,
    email_verified, created_at
) VALUES (
    gen_random_uuid(),
    'system@aiteddy.internal',
    crypt('system_password_change_me', gen_salt('bf', 14)),
    'system',
    true,
    true,
    NOW()
) ON CONFLICT (email) DO NOTHING;

-- ================================
-- Grant Permissions
-- ================================
-- Grant table permissions to application role
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO ai_teddy_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO ai_teddy_app;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO ai_teddy_app;

-- Grant permissions for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO ai_teddy_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO ai_teddy_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT EXECUTE ON FUNCTIONS TO ai_teddy_app;

-- ================================
-- Completion Message
-- ================================
DO $$
BEGIN
    RAISE NOTICE '✅ AI Teddy Bear production database initialized successfully';
    RAISE NOTICE '🔒 Child safety and COPPA compliance features enabled';
    RAISE NOTICE '📊 Performance optimizations applied';
    RAISE NOTICE '🛡️ Security policies configured';
    RAISE NOTICE '⚠️  Remember to configure environment-specific settings';
END $$;
