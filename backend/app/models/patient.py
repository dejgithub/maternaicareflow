from datetime import datetime, date
from typing import Optional, List
from beanie import Document, Indexed
from pydantic import BaseModel, Field


class Newborn(BaseModel):
    name: str
    date_of_birth: date
    gender: str
    weight_kg: float
    height_cm: Optional[float] = None
    blood_type: Optional[str] = None
    notes: Optional[str] = None


class MedicalHistory(BaseModel):
    condition: str
    diagnosed_date: Optional[date] = None
    severity: Optional[str] = None
    medications: List[str] = []
    notes: Optional[str] = None


class VitalSigns(BaseModel):
    blood_pressure_systolic: Optional[int] = None
    blood_pressure_diastolic: Optional[int] = None
    heart_rate: Optional[int] = None
    temperature: Optional[float] = None
    oxygen_saturation: Optional[float] = None
    recorded_at: datetime = Field(default_factory=datetime.utcnow)


class Symptom(BaseModel):
    symptom: str
    severity: str = "mild"
    reported_at: datetime = Field(default_factory=datetime.utcnow)
    resolved: bool = False


class Patient(Document):
    patient_id: Indexed(str, unique=True)
    national_id: Optional[str] = None
    first_name: str
    last_name: str
    date_of_birth: date
    age: int
    gender: str = "female"
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    blood_type: Optional[str] = None
    allergies: List[str] = []
    risk_level: str = "low"
    risk_score: float = 0.0
    assigned_facility: Optional[str] = None
    assigned_nurse: Optional[str] = None
    assigned_doctor: Optional[str] = None
    pregnancy_week: Optional[int] = None
    expected_delivery_date: Optional[date] = None
    delivery_date: Optional[date] = None
    delivery_type: Optional[str] = None
    newborns: List[Newborn] = []
    medical_history: List[MedicalHistory] = []
    vital_signs: List[VitalSigns] = []
    symptoms: List[Symptom] = []
    missed_appointments: int = 0
    is_active: bool = True
    is_emergency: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "patients"

    def display_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
