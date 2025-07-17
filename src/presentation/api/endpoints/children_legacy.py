"""API endpoints لإدارة ملفات الأطفال - Legacy compatibility file
This file provides backward compatibility by re-exporting all children endpoints."""

import logging
from src.infrastructure.logging_config import get_logger
logger = get_logger(__name__, component="api")

# استيراد محدد من الحزمة الجديدة للتوافق العكسي - SECURE IMPORTS
from .children.models import (
    ChildCreateRequest,
    ChildUpdateRequest,
    ChildResponse,
    ChildSafetySummary,
    ChildDeleteResponse
)

from .children.routes import (
    router,
    create_child,
    get_children,
    get_child,
    update_child,
    delete_child
)

from .children.operations import (
    create_child as create_child_operation,
    get_children as get_children_operation,
    get_child as get_child_operation,
    update_child as update_child_operation,
    delete_child as delete_child_operation
)

from .children.compliance import (
    validate_child_creation_compliance,
    validate_data_access_permission,
    handle_compliant_child_deletion,
    request_parental_consent
)

from .children.safety import (
    get_child_safety_summary,
    record_safety_event,
    validate_interaction_safety,
    track_child_usage
)

logger.info("Children endpoints loaded from refactored modules - legacy compatibility")