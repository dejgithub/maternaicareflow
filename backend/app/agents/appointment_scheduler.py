"""
MaternAI CareFlow - Appointment Scheduling Agent

Automatically schedules follow-up visits, sends reminders,
detects missed appointments, and triggers re-engagement workflows.
"""
import logging
from datetime import datetime, timedelta, date
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ScheduleRecommendation:
    suggested_date: datetime
    appointment_type: str
    facility: str
    healthcare_provider: Optional[str] = None
    notes: str = ""
    priority: str = "normal"


class AppointmentSchedulerAgent:
    """AI-powered agent for intelligent appointment scheduling and follow-up management."""

    FOLLOW_UP_INTERVALS = {
        "emergency": {"days": 1, "type": "Emergency Follow-up", "priority": "critical"},
        "high": {"days": 3, "type": "Urgent Follow-up", "priority": "high"},
        "medium": {"days": 7, "type": "Follow-up Visit", "priority": "normal"},
        "low": {"days": 30, "type": "Routine Check-up", "priority": "low"},
    }

    REMINDER_SCHEDULE = [
        {"hours_before": 72, "type": "initial", "channel": "email"},
        {"hours_before": 24, "type": "reminder", "channel": "sms"},
        {"hours_before": 2, "type": "final", "channel": "sms"},
    ]

    def __init__(self):
        logger.info("AppointmentSchedulerAgent initialized")

    def suggest_follow_up(self, risk_level: str, patient_data: Dict[str, Any]) -> ScheduleRecommendation:
        """Suggest optimal follow-up schedule based on risk level and patient context."""
        interval = self.FOLLOW_UP_INTERVALS.get(risk_level, self.FOLLOW_UP_INTERVALS["low"])
        suggested = datetime.utcnow() + timedelta(days=interval["days"])

        return ScheduleRecommendation(
            suggested_date=suggested,
            appointment_type=interval["type"],
            facility=patient_data.get("assigned_facility", "Primary Health Center"),
            healthcare_provider=patient_data.get("assigned_doctor"),
            notes=f"Risk level: {risk_level}. {interval['type']} scheduled automatically.",
            priority=interval["priority"],
        )

    def generate_reminder_message(self, appointment: Dict[str, Any], reminder_type: str) -> str:
        """Generate personalized reminder messages."""
        patient_name = appointment.get("patient_name", "Patient")
        appt_type = appointment.get("appointment_type", "appointment")
        facility = appointment.get("facility_name", "your healthcare facility")
        scheduled = appointment.get("scheduled_date", "")

        if reminder_type == "initial":
            return (
                f"Dear {patient_name}, this is a reminder for your upcoming {appt_type} "
                f"at {facility}. Please confirm your attendance."
            )
        elif reminder_type == "reminder":
            return (
                f"REMINDER: {patient_name}, your {appt_type} is tomorrow at {facility}. "
                f"Please arrive 15 minutes early."
            )
        elif reminder_type == "final":
            return (
                f"URGENT: {patient_name}, your {appt_type} at {facility} is in 2 hours. "
                f"Please proceed to the facility."
            )
        return f"Appointment reminder for {patient_name} at {facility}."

    def detect_missed_appointment(self, appointment: Dict[str, Any]) -> bool:
        """Detect if an appointment was missed based on scheduled time and status."""
        scheduled = appointment.get("scheduled_date")
        status = appointment.get("status", "")
        attended = appointment.get("attended")

        if status == "scheduled" and scheduled:
            scheduled_dt = scheduled if isinstance(scheduled, datetime) else datetime.fromisoformat(str(scheduled).replace("Z", "+00:00"))
            if datetime.utcnow() > scheduled_dt + timedelta(hours=2):
                return attended is not True
        return False

    async def trigger_re_engagement(self, patient_data: Dict[str, Any],
                                     missed_appointment: Dict[str, Any]) -> Dict[str, Any]:
        """Generate re-engagement workflow for missed appointments."""
        return {
            "patient_id": patient_data.get("patient_id"),
            "patient_name": f"{patient_data.get('first_name', '')} {patient_data.get('last_name', '')}",
            "missed_date": missed_appointment.get("scheduled_date"),
            "appointment_type": missed_appointment.get("appointment_type"),
            "action": "re_engagement",
            "suggested_new_date": datetime.utcnow() + timedelta(days=1),
            "message": (
                f"We noticed you missed your {missed_appointment.get('appointment_type', 'appointment')} "
                f"scheduled for {missed_appointment.get('scheduled_date', 'recently')}. "
                f"Your health is important to us. Please reschedule at your earliest convenience."
            ),
            "requires_outreach": True,
        }

    async def optimize_schedule(self, appointments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optimize appointment scheduling to reduce conflicts and improve flow."""
        sorted_appts = sorted(appointments, key=lambda a: (
            {"emergency": 0, "high": 1, "medium": 2, "low": 3}.get(
                a.get("priority", "normal"), 4
            ),
            a.get("scheduled_date", datetime.max),
        ))
        return sorted_appts


class AppointmentAnalytics:
    """Analytics for appointment patterns and adherence."""

    @staticmethod
    def calculate_no_show_rate(appointments: List[Dict[str, Any]]) -> float:
        total = len(appointments)
        if total == 0:
            return 0.0
        missed = sum(1 for a in appointments if a.get("attended") is False)
        return round((missed / total) * 100, 1)

    @staticmethod
    def average_wait_time(appointments: List[Dict[str, Any]]) -> float:
        wait_times = []
        for a in appointments:
            if a.get("scheduled_date") and a.get("created_at"):
                scheduled = a["scheduled_date"]
                if isinstance(scheduled, str):
                    scheduled = datetime.fromisoformat(scheduled.replace("Z", "+00:00"))
                created = a["created_at"]
                if isinstance(created, str):
                    created = datetime.fromisoformat(created.replace("Z", "+00:00"))
                wait = (scheduled - created).total_seconds() / 3600
                wait_times.append(wait)
        if not wait_times:
            return 0.0
        return round(sum(wait_times) / len(wait_times), 1)

    @staticmethod
    def adherence_rate(completed: int, scheduled: int) -> float:
        if scheduled == 0:
            return 100.0
        return round((completed / scheduled) * 100, 1)
