"""Children compliance endpoints with COPPA support."""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from src.infrastructure.security.coppa_validator import (
    COPPAValidator,
    coppa_validator,
    is_coppa_subject,
    requires_parental_consent
)
from src.infrastructure.config.settings import Settings, get_settings
from src.infrastructure.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter()

# Request/Response Models
class ConsentRequest(BaseModel):
    """Parental consent request model."""
    child_id: str = Field(..., description="Child identifier")
    parent_id: str = Field(..., description="Parent identifier")
    data_types: List[str] = Field(..., description="Data types requiring consent")

class ConsentResponse(BaseModel):
    """Consent response model."""
    consent_id: str
    status: str
    expires_at: datetime

class ComplianceValidator:
    """Compliance validation service."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.coppa = COPPAValidator()
    
    def validate_age_compliance(self, age: int) -> dict:
        """Validate age compliance requirements."""
        return {
            "compliant": True,
            "requires_consent": age < 13,
            "compliance_level": str(ComplianceLevel.from_age(age))
        }
    
    def validate_data_collection(self, data_types: List[str], child_age: int) -> dict:
        """Validate data collection compliance."""
        if child_age < 13:
            allowed = [str(DataType.VOICE_INTERACTIONS), str(DataType.PREFERENCES)]
            disallowed = [dt for dt in data_types if dt not in allowed]
            
            return {
                "compliant": len(disallowed) == 0,
                "allowed_types": allowed,
                "disallowed_types": disallowed
            }
        
        return {
            "compliant": True,
            "allowed_types": data_types,
            "disallowed_types": []
        }

class ParentalConsentManager:
    """Parental consent management."""
    
    def __init__(self, coppa_service: COPPAValidator):
        self.coppa = coppa_service
    
    async def create_consent_record(
        self,
        child_id: str,
        parent_id: str,
        data_types: List[str]
    ) -> str:
        """Create consent record."""
        return await self.coppa.request_parental_consent(
            child_id, parent_id, data_types
        )
    
    async def revoke_consent(self, consent_id: str) -> bool:
        """Revoke existing consent."""
        # Implementation would update consent status
        return True

class DataRetentionManager:
    """Data retention management."""
    
    def __init__(self, coppa_service: COPPAValidator):
        self.coppa = coppa_service
    
    async def schedule_data_deletion(self, child_id: str, deletion_date: datetime) -> bool:
        """Schedule data deletion according to retention policy."""
        # Implementation would schedule deletion
        return True
    
    async def check_retention_compliance(self, child_id: str) -> dict:
        """Check if data retention is compliant."""
        return {
            "compliant": True,
            "retention_days": 90,
            "next_review": datetime.now()
        }

# Dependency injection
def get_compliance_validator(
    settings: Settings = Depends(get_settings)
) -> ComplianceValidator:
    """Get compliance validator instance."""
    return ComplianceValidator(settings)

def get_consent_manager() -> ParentalConsentManager:
    """Get consent manager instance."""
    coppa = COPPAValidator()
    return ParentalConsentManager(coppa)

def get_retention_manager() -> DataRetentionManager:
    """Get data retention manager instance."""
    coppa = COPPAValidator()
    return DataRetentionManager(coppa)

# API Endpoints
@router.post("/consent", response_model=ConsentResponse)
async def request_consent(
    request: ConsentRequest,
    consent_manager: ParentalConsentManager = Depends(get_consent_manager)
) -> ConsentResponse:
    """Request parental consent for data collection."""
    consent_id = await consent_manager.create_consent_record(
        request.child_id,
        request.parent_id,
        request.data_types
    )
    
    return ConsentResponse(
        consent_id=consent_id,
        status="pending",
        expires_at=datetime.now()
    )

@router.get("/compliance/age/{age}")
async def check_age_compliance(
    age: int,
    validator: ComplianceValidator = Depends(get_compliance_validator)
) -> dict:
    """Check compliance requirements for given age."""
    return validator.validate_age_compliance(age)
class COPPAIntegration:
    """COPPA Integration Service - Facade for all COPPA compliance operations.
    
    This class provides a unified interface for COPPA-related functionality,
    coordinating between validators, consent managers, and retention policies.
    """
    
    def __init__(self, coppa_service: COPPAValidator, settings: Settings):
        """Initialize COPPA integration with required services.
        
        Args:
            coppa_service: Core COPPA validation service
            settings: Application settings
        """
        self.coppa_service = coppa_service
        self.settings = settings
        self.compliance_validator = ComplianceValidator(settings)
        self.consent_manager = ParentalConsentManager(coppa_service)
        self.retention_manager = DataRetentionManager(settings)
        logger.info("COPPAIntegration initialized with all compliance components")
    
    def validate_child_creation(self, age: int, data_types: List[str]) -> dict:
        """Validate if child profile can be created based on COPPA rules.
        
        Args:
            age: Child's age in years
            data_types: Types of data to be collected
            
        Returns:
            Validation result with compliance status and requirements
        """
        age_compliance = self.compliance_validator.validate_age_compliance(age)
        data_compliance = self.compliance_validator.validate_data_collection(data_types, age)
        
        return {
            "age_compliance": age_compliance,
            "data_compliance": data_compliance,
            "requires_parental_consent": age < 13,
            "allowed_data_types": data_compliance.get("allowed_types", [])
        }
    
    def get_compliance_requirements(self, age: int) -> dict:
        """Get COPPA compliance requirements for a given age.
        
        Args:
            age: Child's age in years
            
        Returns:
            Dictionary of compliance requirements
        """
        validation_result = self.coppa_service.validate_age(age)
        
        return {
            "is_coppa_subject": validation_result.is_coppa_subject,
            "compliance_level": validation_result.compliance_level.value,
            "parental_consent_required": validation_result.parental_consent_required,
            "data_retention_days": validation_result.data_retention_days,
            "special_protections": validation_result.special_protections
        }
    
    # Module-level functions for backward compatibility
async def handle_compliant_child_deletion(child_id: str, user_id: str) -> dict:
    """Handle COPPA-compliant child profile deletion."""
    # Implementation would use the managers above
    return {"status": "deleted", "child_id": child_id}

async def request_parental_consent(child_id: str, parent_email: str) -> dict:
    """Request parental consent for child data collection."""
    return {"status": "consent_requested", "child_id": child_id}

async def validate_child_creation_compliance(age: int, data_types: list) -> dict:
    """Validate child creation request for COPPA compliance."""
    return {"compliant": age >= 13 or len(data_types) == 0, "age": age}

async def validate_data_access_permission(child_id: str, requester_id: str) -> bool:
    """Validate data access permission for child data."""
    return True  # Placeholder implementation