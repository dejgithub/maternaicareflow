from datetime import datetime, date
from typing import Optional
from beanie import Document, Indexed
from pydantic import BaseModel, Field


class Reminder(BaseModel):
    reminder_type: str
    sent_at: datetime
    channel: str
    status: str


class Appointment(Document):
    appointment_id: Indexed(str, unique=True)
    patient_id: str
    patient_name: str
    referral_id: Optional[str] = None
    appointment_type: str
    facility_name: str
    facility_address: Optional[str] = None
    scheduled_date: datetime
    end_time: Optional[datetime] = None
    status: str = "scheduled"
    notes: Optional[str] = None
    healthcare_provider: Optional[str] = None
    reminder_sent: bool = False
    reminders: list[Reminder] = []
    attended: Optional[bool] = None
    missed_reason: Optional[str] = None
    reschedule_requested: bool = False
    rescheduled_to: Optional[datetime] = None
    created_by: str = "system"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "appointments"
