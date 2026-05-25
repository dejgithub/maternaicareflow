from datetime import datetime
from typing import Optional
from beanie import Document, Indexed
from pydantic import Field


class Escalation(Document):
    escalation_id: Indexed(str, unique=True)
    patient_id: str
    patient_name: str
    alert_type: str
    severity: str
    description: str
    ai_recommendation: Optional[str] = None
    status: str = "open"
    assigned_to: Optional[str] = None
    assigned_name: Optional[str] = None
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    requires_human_approval: bool = True
    approval_status: str = "pending"
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    linked_referral_id: Optional[str] = None
    linked_appointment_id: Optional[str] = None
    notification_sent: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "escalations"


class Alert(Document):
    alert_id: Indexed(str, unique=True)
    patient_id: str
    patient_name: str
    alert_type: str
    severity: str
    message: str
    is_read: bool = False
    acknowledged_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "alerts"
