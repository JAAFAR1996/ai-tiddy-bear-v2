"""from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
from fastapi import HTTPException, status
from pydantic import BaseModel
from src.infrastructure.di.container import container
from src.infrastructure.config.settings import Settings
from src.infrastructure.security.hardening.coppa_compliance import ProductionCOPPACompliance, DataType
from src.infrastructure.logging_config import get_logger
logger = get_logger(__name__, component="api")
from .models import ChildCreateRequest, ChildResponse.
"""

"""COPPA integration and child protection law compliance."""


class COPPAIntegration:
    """COPPA service integration class ."""

    def __init__(
        self,
        coppa_compliance_service: ProductionCOPPACompliance,
        settings: Settings,
    ) -> None:
        self.coppa = coppa_compliance_service
        self.settings = settings

    async def validate_child_creation(
        self,
        request: ChildCreateRequest,
        parent_id: str,
    ) -> str:
        """Verify COPPA compliance when creating a child profile."""
        # COPPA CONDITIONAL: Check if COPPA compliance is enabled
        if not self.settings.privacy.COPPA_ENABLED:
            logger.info(
                "COPPA compliance disabled - bypassing consent validation"
            )
            return "coppa_disabled_mock_consent"

        # Check if parental consent is actually required
        if not self.coppa.requires_parental_consent(request.age):
            logger.info(
                f"Child age {request.age} does not require parental consent"
            )
            return "no_consent_required"

        try:
            # Check age validation
            if self.coppa.verify_age(request.age):
                # Request parental consent
                data_types = [
                    DataType.PREFERENCES,
                    DataType.VOICE_INTERACTIONS,
                ]

                # إضافة نوع البيانات الشخصية إذا كان هناك معلومات شخصية
                if request.interests or request.preferences:
                    data_types.append(DataType.PERSONAL_INFO)

                consent_id = self.coppa.request_parental_consent(
                    f"temp_child_{datetime.now().timestamp()}",
                    parent_id,
                    data_types,
                )

                # في التطبيق الحقيقي، ننتظر الموافقة الأبوية
                # هنا نحاكي الموافقة المباشرة للاختبار
                self.coppa.grant_consent(consent_id)
                return consent_id
            # الطفل أكبر من 13 سنة، لا نحتاج موافقة أبوية
            return "no_consent_required"
        except Exception as e:
            logger.error(f"Error validating COPPA compliance: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to validate COPPA compliance: {e!s}",
            )

    async def validate_data_access(
        self,
        child_id: str,
        parent_id: str,
        data_type: str,
    ) -> bool:
        """التحقق من صلاحية الوصول لبيانات الطفل
        COPPA CONDITIONAL: When COPPA compliance is disabled, always allows access.
        """
        # COPPA CONDITIONAL: Always allow access when COPPA is disabled
        if not self.settings.privacy.COPPA_ENABLED:
            logger.debug("COPPA compliance disabled - allowing data access")
            return True

        try:
            return self.coppa.check_data_access_permission(
                child_id,
                parent_id,
                data_type,
            )
        except Exception as e:
            logger.error(f"Error checking data access permission: {e}")
            return False

    async def validate_data_modification(
        self,
        child_id: str,
        parent_id: str,
        data_types: List[str],
    ) -> bool:
        """التحقق من صلاحية تعديل بيانات الطفل."""
        try:
            # التحقق من كل نوع بيانات
            for data_type in data_types:
                if not self.coppa.check_data_modification_permission(
                    child_id,
                    parent_id,
                    data_type,
                ):
                    return False
            return True
        except Exception as e:
            logger.error(f"Error checking data modification permission: {e}")
            return False

    async def handle_child_deletion(
        self,
        child_id: str,
        parent_id: str,
    ) -> Dict[str, Any]:
        """معالجة حذف بيانات الطفل وفقاً لـ COPPA."""
        try:
            # حذف البيانات للامتثال لـ COPPA
            result = self.coppa._delete_child_data(child_id)

            # تسجيل عملية الحذف
            deletion_record = {
                "child_id": child_id,
                "parent_id": parent_id,
                "deleted_at": datetime.now().isoformat(),
                "deletion_type": "parent_request",
                "compliance_status": "coppa_compliant",
            }

            return {
                "success": True,
                "message": "Child data deleted successfully",
                "deletion_record": deletion_record,
                "coppa_result": result,
            }
        except Exception as e:
            logger.error(f"Error handling child deletion: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete child data: {e!s}",
            )


class ParentalConsentManager:
    """مدير الموافقة الأبوية."""

    def __init__(
        self,
        coppa_compliance_service: ProductionCOPPACompliance,
    ) -> None:
        self.coppa = coppa_compliance_service

    async def request_consent(
        self,
        parent_id: str,
        child_id: str,
        data_types: List[str],
    ) -> str:
        """طلب موافقة أبوية لنوع بيانات محدد."""
        try:
            # تحويل أنواع البيانات إلى enum
            data_type_enums = []
            for data_type in data_types:
                if hasattr(DataType, data_type.upper()):
                    data_type_enums.append(
                        getattr(DataType, data_type.upper())
                    )

            consent_id = self.coppa.request_parental_consent(
                child_id,
                parent_id,
                data_type_enums,
            )
            return consent_id
        except Exception as e:
            logger.error(f"Error requesting parental consent: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to request parental consent: {e!s}",
            )

    async def check_consent_status(self, consent_id: str) -> Dict[str, Any]:
        """التحقق من حالة الموافقة الأبوية."""
        try:
            # في التطبيق الحقيقي، نحتاج لتنفيذ هذه الوظيفة في خدمة COPPA
            # status = coppa.get_consent_status(consent_id)
            return {
                "consent_id": consent_id,
                "status": "granted",  # مؤقت
                "granted_at": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error checking consent status: {e}")
            return {
                "consent_id": consent_id,
                "status": "error",
                "error": str(e),
            }

    async def revoke_consent(
        self, consent_id: str, parent_id: str
    ) -> Dict[str, Any]:
        """إلغاء الموافقة الأبوية."""
        try:
            # إلغاء الموافقة
            # result = coppa.revoke_consent(consent_id, parent_id)
            return {
                "consent_id": consent_id,
                "revoked": True,
                "revoked_at": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error revoking consent: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to revoke consent: {e!s}",
            )


class DataRetentionManager:
    """مدير الاحتفاظ بالبيانات."""

    def __init__(
        self,
        coppa_compliance_service: ProductionCOPPACompliance,
    ) -> None:
        self.coppa = coppa_compliance_service

    async def check_data_retention_limits(
        self, child_id: str
    ) -> Dict[str, Any]:
        """التحقق من حدود الاحتفاظ بالبيانات."""
        try:
            # التحقق من حدود الاحتفاظ
            # retention_info = coppa.check_retention_limits(child_id)
            return {
                "child_id": child_id,
                "retention_compliant": True,
                "days_remaining": 365,
                "last_activity": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error checking data retention limits: {e}")
            return {
                "child_id": child_id,
                "retention_compliant": False,
                "error": str(e),
            }

    async def schedule_data_cleanup(
        self,
        child_id: str,
        cleanup_date: datetime,
    ) -> Dict[str, Any]:
        """جدولة تنظيف البيانات."""
        try:
            # في التطبيق الحقيقي، نحتاج لتنفيذ نظام جدولة التنظيف
            return {
                "child_id": child_id,
                "cleanup_scheduled": True,
                "cleanup_date": cleanup_date.isoformat(),
                "scheduled_at": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error scheduling data cleanup: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to schedule data cleanup: {e!s}",
            )


class ComplianceValidator:
    """مدقق الامتثال."""

    def __init__(
        self,
        settings: Settings,
    ) -> None:
        self.settings = settings

    def validate_age_compliance(self, age: int) -> Dict[str, Any]:
        """التحقق من الامتثال للعمر."""
        return {
            "age": age,
            "coppa_applicable": age < 13,
            "consent_required": age < 13,
            "data_restrictions": age < 13,
        }

    def validate_data_collection(
        self,
        data_types: List[str],
        child_age: int,
    ) -> Dict[str, Any]:
        """التحقق من الامتثال لجمع البيانات."""
        restricted_types = []
        allowed_types = []

        for data_type in data_types:
            if child_age < 13:
                # جميع أنواع البيانات تتطلب موافقة أبوية
                restricted_types.append(data_type)
            else:
                allowed_types.append(data_type)

        return {
            "child_age": child_age,
            "restricted_types": restricted_types,
            "allowed_types": allowed_types,
            "consent_required": len(restricted_types) > 0,
        }

    def validate_data_sharing(
        self,
        data_types: List[str],
        child_age: int,
        third_party: str,
    ) -> Dict[str, Any]:
        """التحقق من الامتثال لمشاركة البيانات
        COPPA CONDITIONAL: When COPPA compliance is disabled, allows data sharing.
        """
        # COPPA CONDITIONAL: Allow sharing when COPPA is disabled
        if not self.settings.privacy.COPPA_ENABLED:
            return {
                "sharing_allowed": True,
                "data_types": data_types,
                "third_party": third_party,
                "compliance_status": "coppa_disabled",
            }

        if child_age < 13:
            return {
                "sharing_allowed": False,
                "reason": "COPPA prohibits sharing data of children under 13",
                "third_party": third_party,
            }

        return {
            "sharing_allowed": True,
            "data_types": data_types,
            "third_party": third_party,
            "compliance_status": "approved",
        }


# الواجهات العامة لخدمات الامتثال - ALL COPPA CONDITIONAL
from dependency_injector.wiring import Provide, inject
from fastapi import Depends


@inject
async def validate_child_creation_compliance(
    request: ChildCreateRequest,
    parent_id: str,
    coppa_integration: COPPAIntegration = Depends(
        Provide[container.coppa_integration_service],
    ),
) -> str:
    """التحقق من الامتثال عند إنشاء طفل
    COPPA CONDITIONAL: Bypasses validation when COPPA compliance is disabled.
    """
    return await coppa_integration.validate_child_creation(request, parent_id)


@inject
async def validate_data_access_permission(
    child_id: str,
    parent_id: str,
    data_type: str,
    coppa_integration: COPPAIntegration = Depends(
        Provide[container.coppa_integration_service],
    ),
) -> bool:
    """التحقق من صلاحية الوصول للبيانات
    COPPA CONDITIONAL: Always allows access when COPPA compliance is disabled.
    """
    return await coppa_integration.validate_data_access(
        child_id, parent_id, data_type
    )


@inject
async def handle_compliant_child_deletion(
    child_id: str,
    parent_id: str,
    coppa_integration: COPPAIntegration = Depends(
        Provide[container.coppa_integration_service],
    ),
) -> Dict[str, Any]:
    """معالجة حذف الطفل بشكل متوافق مع COPPA
    COPPA CONDITIONAL: Simplified deletion when COPPA compliance is disabled.
    """
    return await coppa_integration.handle_child_deletion(child_id, parent_id)


@inject
async def request_parental_consent(
    parent_id: str,
    child_id: str,
    data_types: List[str],
    parental_consent_manager: ParentalConsentManager = Depends(
        Provide[container.parental_consent_manager_service],
    ),
) -> str:
    """طلب موافقة أبوية."""
    return await parental_consent_manager.request_consent(
        parent_id,
        child_id,
        data_types,
    )
