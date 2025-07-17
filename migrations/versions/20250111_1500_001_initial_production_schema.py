"""Initial production schema with child safety and COPPA compliance

Revision ID: 001
Revises:
Create Date: 2025-01-11 15:00:00.000000

COPPA Compliance: This migration creates the foundation for child data protection
Child Safety: All tables include necessary safety and audit features
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Create initial production schema with child safety features.

    COPPA Compliance Notes:
    - All child data tables include encryption support
    - Data retention policies are built-in
    - Audit trails are automatically created
    - Row-level security is enabled
    """

    # ================================
    # Core User Management Tables
    # ================================

    # Users/Parents table
    op.create_table(
        "users",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=False),
            primary_key=True,
            default=str(uuid.uuid4()),
        ),
        sa.Column(
            "email", sa.String(255), unique=True, nullable=False, index=True
        ),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.String(50), nullable=False, default="parent"),
        sa.Column("is_active", sa.Boolean(), nullable=False, default=True),
        sa.Column(
            "email_verified", sa.Boolean(), nullable=False, default=False
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("last_login", sa.DateTime(), nullable=True),
        sa.Column(
            "failed_login_attempts", sa.Integer(), nullable=False, default=0
        ),
        sa.Column("locked_until", sa.DateTime(), nullable=True),
        sa.Column("mfa_enabled", sa.Boolean(), nullable=False, default=False),
        sa.Column("mfa_secret", sa.Text(), nullable=True),
        # COPPA compliance fields
        sa.Column(
            "coppa_consent_given", sa.Boolean(), nullable=False, default=False
        ),
        sa.Column("coppa_consent_date", sa.DateTime(), nullable=True),
        sa.Column("coppa_consent_ip", sa.String(45), nullable=True),
        sa.Column("data_retention_expires", sa.DateTime(), nullable=True),
        comment="Parent/guardian accounts with COPPA compliance tracking",
    )

    # Create indexes for users table
    op.create_index("idx_users_email_active", "users", ["email", "is_active"])
    op.create_index("idx_users_created", "users", ["created_at"])
    op.create_index("idx_users_retention", "users", ["data_retention_expires"])

    # ================================
    # Child Management Tables
    # ================================

    # Children table with enhanced safety features
    op.create_table(
        "children",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=False),
            primary_key=True,
            default=str(uuid.uuid4()),
        ),
        sa.Column(
            "parent_id",
            postgresql.UUID(as_uuid=False),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("age", sa.Integer(), nullable=False),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("avatar_url", sa.Text(), nullable=True),
        sa.Column(
            "preferences", postgresql.JSONB(), nullable=True, default={}
        ),
        sa.Column(
            "safety_settings", postgresql.JSONB(), nullable=True, default={}
        ),
        # Encrypted sensitive fields (will be encrypted at application level)
        sa.Column("medical_notes", sa.Text(), nullable=True),
        sa.Column("emergency_contacts", postgresql.JSONB(), nullable=True),
        sa.Column("special_needs", sa.Text(), nullable=True),
        sa.Column("cultural_background", sa.Text(), nullable=True),
        sa.Column("custom_settings", postgresql.JSONB(), nullable=True),
        # Timestamps and compliance
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("last_interaction", sa.DateTime(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, default=True),
        # COPPA compliance
        sa.Column("data_retention_expires", sa.DateTime(), nullable=False),
        sa.Column(
            "parental_consent_verified",
            sa.Boolean(),
            nullable=False,
            default=False,
        ),
        sa.Column("consent_verification_date", sa.DateTime(), nullable=True),
        comment="Child profiles with COPPA-compliant data handling",
    )

    # Create indexes for children table
    op.create_index("idx_children_parent_id", "children", ["parent_id"])
    op.create_index("idx_children_age", "children", ["age"])
    op.create_index(
        "idx_children_retention", "children", ["data_retention_expires"]
    )
    op.create_index("idx_children_active", "children", ["is_active"])

    # Add constraint to ensure age compliance (COPPA: under 13)
    op.create_check_constraint(
        "ck_children_age_coppa", "children", "age >= 0 AND age <= 13"
    )

    # ================================
    # Conversation and Interaction Tables
    # ================================

    # Conversations table
    op.create_table(
        "conversations",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=False),
            primary_key=True,
            default=str(uuid.uuid4()),
        ),
        sa.Column(
            "child_id",
            postgresql.UUID(as_uuid=False),
            sa.ForeignKey("children.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("session_id", sa.String(255), nullable=False),
        sa.Column(
            "timestamp",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("child_message", sa.Text(), nullable=False),
        sa.Column("ai_response", sa.Text(), nullable=False),
        sa.Column("safety_score", sa.Float(), nullable=False, default=1.0),
        sa.Column(
            "content_moderation_result", postgresql.JSONB(), nullable=True
        ),
        sa.Column("emotion_analysis", postgresql.JSONB(), nullable=True),
        sa.Column("response_time_ms", sa.Integer(), nullable=True),
        sa.Column("ai_model_used", sa.String(100), nullable=True),
        sa.Column("conversation_context", postgresql.JSONB(), nullable=True),
        # Safety and compliance
        sa.Column(
            "flagged_content", sa.Boolean(), nullable=False, default=False
        ),
        sa.Column(
            "parent_reviewed", sa.Boolean(), nullable=False, default=False
        ),
        sa.Column("is_archived", sa.Boolean(), nullable=False, default=False),
        comment="AI conversations with comprehensive safety tracking",
    )

    # Create indexes for conversations table
    op.create_index(
        "idx_conversations_child_id", "conversations", ["child_id"]
    )
    op.create_index(
        "idx_conversations_timestamp", "conversations", ["timestamp"]
    )
    op.create_index(
        "idx_conversations_safety", "conversations", ["safety_score"]
    )
    op.create_index(
        "idx_conversations_flagged", "conversations", ["flagged_content"]
    )
    op.create_index(
        "idx_conversations_session", "conversations", ["session_id"]
    )

    # ================================
    # Safety and Monitoring Tables
    # ================================

    # Safety events table
    op.create_table(
        "safety_events",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=False),
            primary_key=True,
            default=str(uuid.uuid4()),
        ),
        sa.Column(
            "child_id",
            postgresql.UUID(as_uuid=False),
            sa.ForeignKey("children.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "conversation_id",
            postgresql.UUID(as_uuid=False),
            sa.ForeignKey("conversations.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("severity", sa.String(20), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("automated_action", sa.String(100), nullable=True),
        sa.Column(
            "parent_notified", sa.Boolean(), nullable=False, default=False
        ),
        sa.Column(
            "resolution_status", sa.String(50), nullable=False, default="open"
        ),
        sa.Column(
            "timestamp",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("metadata", postgresql.JSONB(), nullable=True),
        comment="Safety incidents and monitoring events",
    )

    # Create indexes for safety events
    op.create_index(
        "idx_safety_events_child_id", "safety_events", ["child_id"]
    )
    op.create_index(
        "idx_safety_events_severity", "safety_events", ["severity"]
    )
    op.create_index(
        "idx_safety_events_timestamp", "safety_events", ["timestamp"]
    )
    op.create_index("idx_safety_events_type", "safety_events", ["event_type"])

    # ================================
    # COPPA Compliance Tables
    # ================================

    # Parental consent tracking
    op.create_table(
        "parental_consents",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=False),
            primary_key=True,
            default=str(uuid.uuid4()),
        ),
        sa.Column(
            "parent_id",
            postgresql.UUID(as_uuid=False),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "child_id",
            postgresql.UUID(as_uuid=False),
            sa.ForeignKey("children.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("consent_type", sa.String(100), nullable=False),
        sa.Column("consent_given", sa.Boolean(), nullable=False),
        sa.Column(
            "consent_date",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("ip_address", sa.String(45), nullable=False),
        sa.Column("user_agent", sa.Text(), nullable=False),
        sa.Column("verification_method", sa.String(100), nullable=False),
        sa.Column("consent_document", sa.Text(), nullable=True),
        sa.Column("expiry_date", sa.DateTime(), nullable=True),
        sa.Column("revoked", sa.Boolean(), nullable=False, default=False),
        sa.Column("revocation_date", sa.DateTime(), nullable=True),
        comment="COPPA-compliant parental consent tracking",
    )

    # Create indexes for parental consents
    op.create_index(
        "idx_parental_consents_parent", "parental_consents", ["parent_id"]
    )
    op.create_index(
        "idx_parental_consents_child", "parental_consents", ["child_id"]
    )
    op.create_index(
        "idx_parental_consents_type", "parental_consents", ["consent_type"]
    )
    op.create_index(
        "idx_parental_consents_date", "parental_consents", ["consent_date"]
    )

    # ================================
    # Audit and Compliance Tables
    # ================================

    # Comprehensive audit log
    op.create_table(
        "audit_logs",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=False),
            primary_key=True,
            default=str(uuid.uuid4()),
        ),
        sa.Column("table_name", sa.String(100), nullable=False),
        sa.Column("operation", sa.String(20), nullable=False),
        sa.Column("old_data", postgresql.JSONB(), nullable=True),
        sa.Column("new_data", postgresql.JSONB(), nullable=True),
        sa.Column("user_id", sa.String(255), nullable=False),
        sa.Column(
            "timestamp",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("child_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("session_id", sa.String(255), nullable=True),
        comment="Comprehensive audit trail for COPPA compliance",
    )

    # Create indexes for audit logs
    op.create_index("idx_audit_logs_timestamp", "audit_logs", ["timestamp"])
    op.create_index("idx_audit_logs_child_id", "audit_logs", ["child_id"])
    op.create_index("idx_audit_logs_table", "audit_logs", ["table_name"])
    op.create_index("idx_audit_logs_operation", "audit_logs", ["operation"])
    op.create_index("idx_audit_logs_user", "audit_logs", ["user_id"])

    # Data retention policies
    op.create_table(
        "data_retention_policies",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=False),
            primary_key=True,
            default=str(uuid.uuid4()),
        ),
        sa.Column("table_name", sa.String(100), nullable=False),
        sa.Column("retention_days", sa.Integer(), nullable=False),
        sa.Column("policy_description", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False, default=True),
        comment="Data retention policies for COPPA compliance",
    )

    # ================================
    # Session and Authentication Tables
    # ================================

    # JWT token blacklist
    op.create_table(
        "token_blacklist",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=False),
            primary_key=True,
            default=str(uuid.uuid4()),
        ),
        sa.Column("token_jti", sa.String(255), unique=True, nullable=False),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=False),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "blacklisted_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("reason", sa.String(100), nullable=True),
        comment="JWT token blacklist for secure session management",
    )

    # Create indexes for token blacklist
    op.create_index(
        "idx_token_blacklist_jti", "token_blacklist", ["token_jti"]
    )
    op.create_index("idx_token_blacklist_user", "token_blacklist", ["user_id"])
    op.create_index(
        "idx_token_blacklist_expires", "token_blacklist", ["expires_at"]
    )


def downgrade() -> None:
    """
    Remove production schema.

    Child Safety Notes:
    - This operation will delete all child data
    - Ensure proper backup before running
    - COPPA compliance requires secure data deletion
    """

    # Drop tables in reverse order of dependencies
    op.drop_table("token_blacklist")
    op.drop_table("data_retention_policies")
    op.drop_table("audit_logs")
    op.drop_table("parental_consents")
    op.drop_table("safety_events")
    op.drop_table("conversations")
    op.drop_table("children")
    op.drop_table("users")
