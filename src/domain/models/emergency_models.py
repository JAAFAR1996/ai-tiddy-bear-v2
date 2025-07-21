"""Emergency Response Models - Data models for emergency system"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AlertPayload(BaseModel):
    """نموذج بيانات التنبيه الواردة."""

    alerts: list[dict[str, Any]]
    receiver: str = Field(..., description="اسم المتلقي")
    status: str = Field(..., description="حالة التنبيه")


class EmergencyAlert(BaseModel):
    """نموذج التنبيه الطارئ."""

    id: str = Field(..., description="معرف التنبيه")
    severity: str = Field(..., description="مستوى الخطورة")
    description: str = Field(..., description="وصف التنبيه")
    source: str = Field(..., description="مصدر التنبيه")
    timestamp: datetime = Field(..., description="وقت التنبيه")
    child_id: str | None = Field(None, description="معرف الطفل المتأثر")
    action_required: bool = Field(True, description="يتطلب إجراء")
    metadata: dict[str, Any] = Field(default_factory=dict)


class SystemStatus(BaseModel):
    """نموذج حالة النظام."""

    service_name: str
    status: str
    last_check: datetime
    response_time_ms: float
    error_message: str | None = None


class HealthResponse(BaseModel):
    """نموذج استجابة فحص الصحة."""

    status: str = Field(..., description="حالة الخدمة")
    timestamp: datetime = Field(..., description="وقت الفحص")
    version: str = Field(..., description="إصدار الخدمة")
    uptime_seconds: float = Field(..., description="وقت التشغيل بالثواني")
    dependencies: dict[str, str] = Field(default_factory=dict)


class NotificationRequest(BaseModel):
    """نموذج طلب الإشعار."""

    alert_id: str
    child_id: str | None = None
    parent_contacts: list[str]
    message: str
    priority: str = Field(default="high", pattern="^(low|medium|high|critical)$")


class ResponseAction(BaseModel):
    """نموذج إجراء الاستجابة."""

    action_type: str
    target: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    success: bool = False
    error_message: str | None = None
    executed_at: datetime | None = None


class EmergencyContact(BaseModel):
    """نموذج جهة الاتصال الطارئة."""

    id: str = Field(..., description="معرف جهة الاتصال")
    name: str = Field(..., description="اسم جهة الاتصال")
    phone: str = Field(..., description="رقم الهاتف")
    email: str | None = Field(None, description="البريد الإلكتروني")
    relationship: str = Field(..., description="العلاقة بالطفل")
    priority: int = Field(1, description="أولوية الاتصال (1=أعلى)")
    is_active: bool = Field(True, description="هل جهة الاتصال نشطة")


class AlertRule(BaseModel):
    """نموذج قاعدة التنبيه."""

    id: str = Field(..., description="معرف القاعدة")
    name: str = Field(..., description="اسم القاعدة")
    condition: str = Field(..., description="شرط التفعيل")
    severity: str = Field(..., description="مستوى الخطورة")
    actions: list[str] = Field(default_factory=list, description="الإجراءات المطلوبة")
    is_enabled: bool = Field(True, description="هل القاعدة مفعلة")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class SafetyIncident(BaseModel):
    """نموذج حادث الأمان."""

    id: str = Field(..., description="معرف الحادث")
    child_id: str = Field(..., description="معرف الطفل")
    incident_type: str = Field(..., description="نوع الحادث")
    severity: str = Field(..., description="مستوى الخطورة")
    description: str = Field(..., description="وصف الحادث")
    location: str | None = Field(None, description="موقع الحادث")
    timestamp: datetime = Field(..., description="وقت الحادث")
    resolved: bool = Field(False, description="هل تم حل الحادث")
    resolved_at: datetime | None = Field(None, description="وقت الحل")
    resolution_notes: str | None = Field(None, description="ملاحظات الحل")


class AlertHistory(BaseModel):
    """نموذج تاريخ التنبيهات."""

    id: str = Field(..., description="معرف السجل")
    alert_id: str = Field(..., description="معرف التنبيه")
    status: str = Field(..., description="حالة التنبيه")
    timestamp: datetime = Field(..., description="وقت التحديث")
    updated_by: str = Field(..., description="محدث بواسطة")
    notes: str | None = Field(None, description="ملاحظات")


class ParentNotification(BaseModel):
    """نموذج إشعار الوالدين."""

    id: str = Field(..., description="معرف الإشعار")
    parent_id: str = Field(..., description="معرف الوالد")
    child_id: str = Field(..., description="معرف الطفل")
    notification_type: str = Field(..., description="نوع الإشعار")
    title: str = Field(..., description="عنوان الإشعار")
    message: str = Field(..., description="محتوى الإشعار")
    priority: str = Field(default="medium", pattern="^(low|medium|high|urgent)$")
    sent_at: datetime = Field(..., description="وقت الإرسال")
    read: bool = Field(False, description="هل تم قراءة الإشعار")
    read_at: datetime | None = Field(None, description="وقت القراءة")


class SystemConfig(BaseModel):
    """نموذج إعدادات النظام."""

    alert_threshold_minutes: int = Field(5, description="عتبة التنبيه بالدقائق")
    max_retry_attempts: int = Field(3, description="عدد محاولات الإعادة")
    notification_cooldown_seconds: int = Field(
        300, description="فترة التهدئة للإشعارات"
    )
    emergency_contacts_required: bool = Field(
        True, description="جهات الاتصال الطارئة مطلوبة"
    )
    auto_escalation_enabled: bool = Field(True, description="التصعيد التلقائي مفعل")
    safety_mode_strict: bool = Field(True, description="وضع الأمان الصارم")
