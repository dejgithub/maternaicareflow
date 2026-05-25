from datetime import datetime
from typing import Optional, List
from beanie import Document, Indexed
from pydantic import Field


class HealthcareFacility(Document):
    facility_id: str
    name: str
    type: str
    address: str
    phone: Optional[str] = None
    email: Optional[str] = None
    services: List[str] = []
    capacity: int = 0
    current_load: int = 0
    is_active: bool = True

    class Settings:
        name = "healthcare_facilities"


class Referral(Document):
    referral_id: Indexed(str, unique=True)
    patient_id: str
    patient_name: str
    risk_level: str
    source_facility: str
    target_facility_id: Optional[str] = None
    target_facility_name: Optional[str] = None
    referral_reason: str
    referral_notes: Optional[str] = None
    status: str = "pending"
    priority: str = "normal"
    assigned_healthcare_worker: Optional[str] = None
    assigned_worker_name: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    rejected_by: Optional[str] = None
    rejection_reason: Optional[str] = None
    is_emergency: bool = False
    ai_recommendation: Optional[str] = None
    ai_confidence_score: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    class Settings:
        name = "referrals"
