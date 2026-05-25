from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field


class PatientCreate(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: date
    age: int
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    blood_type: Optional[str] = None
    allergies: List[str] = []
    pregnancy_week: Optional[int] = None
    expected_delivery_date: Optional[date] = None
    national_id: Optional[str] = None


class SymptomReport(BaseModel):
    symptom: str
    severity: str = "mild"


class VitalSignsReport(BaseModel):
    blood_pressure_systolic: Optional[int] = None
    blood_pressure_diastolic: Optional[int] = None
    heart_rate: Optional[int] = None
    temperature: Optional[float] = None
    oxygen_saturation: Optional[float] = None


class ReferralCreate(BaseModel):
    patient_id: str
    referral_reason: str
    referral_notes: Optional[str] = None
    priority: str = "normal"
    source_facility: str = "primary_clinic"


class ReferralApprove(BaseModel):
    approved_by: str
    target_facility_id: str


class ReferralReject(BaseModel):
    rejected_by: str
    rejection_reason: str


class AppointmentCreate(BaseModel):
    patient_id: str
    appointment_type: str
    facility_name: str
    scheduled_date: datetime
    healthcare_provider: Optional[str] = None
    notes: Optional[str] = None
    referral_id: Optional[str] = None


class AppointmentReschedule(BaseModel):
    new_date: datetime
    reason: Optional[str] = None


class EscalationAction(BaseModel):
    assigned_to: Optional[str] = None
    assigned_name: Optional[str] = None


class EscalationResolve(BaseModel):
    resolved_by: str
    resolution_notes: Optional[str] = None


class ApprovalAction(BaseModel):
    approved_by: str
    approve: bool = True
    notes: Optional[str] = None


class AnalyticsFilter(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    facility: Optional[str] = None


class AIAssessmentResponse(BaseModel):
    risk_level: str
    risk_score: float
    recommendation: str
    confidence: float
    requires_escalation: bool
    requires_human_review: bool
    reasoning: str
