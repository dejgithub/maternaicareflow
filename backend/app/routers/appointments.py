from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from app.models.appointment import Appointment, Reminder
from app.models.patient import Patient
from app.schemas.schemas import AppointmentCreate, AppointmentReschedule
from app.agents.appointment_scheduler import AppointmentSchedulerAgent
from app.services.notification import NotificationService
from app.config import settings

router = APIRouter(prefix="/api/appointments", tags=["Appointments"])
scheduler = AppointmentSchedulerAgent()
notifier = NotificationService(
    twilio_sid=settings.twilio_account_sid,
    twilio_token=settings.twilio_auth_token,
    twilio_phone=settings.twilio_phone_number,
    sendgrid_key=settings.sendgrid_api_key,
    from_email=settings.from_email,
)


@router.post("/", response_model=Appointment)
async def create_appointment(data: AppointmentCreate):
    """Create a new appointment."""
    patient = await Patient.find_one(Patient.patient_id == data.patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    appointment_id = f"APT-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{hash(data.patient_id) % 10000:04d}"

    appointment = Appointment(
        appointment_id=appointment_id,
        patient_id=data.patient_id,
        patient_name=patient.display_name(),
        referral_id=data.referral_id,
        appointment_type=data.appointment_type,
        facility_name=data.facility_name,
        scheduled_date=data.scheduled_date,
        healthcare_provider=data.healthcare_provider,
        notes=data.notes,
        created_by="system",
    )
    await appointment.insert()
    return appointment


@router.get("/", response_model=List[Appointment])
async def list_appointments(
    patient_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    appointment_type: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    """List appointments with optional filtering."""
    query = {}
    if patient_id:
        query["patient_id"] = patient_id
    if status:
        query["status"] = status
    if appointment_type:
        query["appointment_type"] = appointment_type

    appointments = await Appointment.find(query).skip(skip).limit(limit).to_list()
    return appointments


@router.get("/{appointment_id}", response_model=Appointment)
async def get_appointment(appointment_id: str):
    """Get appointment details."""
    appointment = await Appointment.find_one(
        Appointment.appointment_id == appointment_id
    )
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment


@router.post("/{appointment_id}/reschedule")
async def reschedule_appointment(appointment_id: str, data: AppointmentReschedule):
    """Reschedule an appointment."""
    appointment = await Appointment.find_one(
        Appointment.appointment_id == appointment_id
    )
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    appointment.reschedule_requested = True
    appointment.rescheduled_to = data.new_date
    appointment.status = "rescheduled"
    appointment.updated_at = datetime.utcnow()
    await appointment.save()
    return appointment


@router.post("/{appointment_id}/cancel")
async def cancel_appointment(appointment_id: str, reason: str = Query("")):
    """Cancel an appointment."""
    appointment = await Appointment.find_one(
        Appointment.appointment_id == appointment_id
    )
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    appointment.status = "cancelled"
    appointment.notes = (appointment.notes or "") + f" Cancelled: {reason}"
    appointment.updated_at = datetime.utcnow()
    await appointment.save()
    return appointment


@router.post("/{appointment_id}/confirm-attendance")
async def confirm_attendance(appointment_id: str, attended: bool = Query(...)):
    """Confirm whether patient attended the appointment."""
    appointment = await Appointment.find_one(
        Appointment.appointment_id == appointment_id
    )
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    appointment.attended = attended
    appointment.status = "completed" if attended else "missed"
    appointment.updated_at = datetime.utcnow()
    await appointment.save()

    if not attended:
        patient = await Patient.find_one(Patient.patient_id == appointment.patient_id)
        if patient:
            patient.missed_appointments = (patient.missed_appointments or 0) + 1
            await patient.save()

    return appointment


@router.post("/{appointment_id}/send-reminder")
async def send_appointment_reminder(appointment_id: str):
    """Send reminder for an appointment."""
    appointment = await Appointment.find_one(
        Appointment.appointment_id == appointment_id
    )
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    patient = await Patient.find_one(Patient.patient_id == appointment.patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    results = await notifier.send_appointment_reminder(
        patient.phone,
        patient.email,
        {
            "patient_name": appointment.patient_name,
            "patient_id": appointment.patient_id,
            "appointment_type": appointment.appointment_type,
            "facility_name": appointment.facility_name,
            "scheduled_date": appointment.scheduled_date.isoformat(),
        },
    )

    appointment.reminder_sent = True
    appointment.reminders.append(Reminder(
        reminder_type="reminder",
        sent_at=datetime.utcnow(),
        channel="multi",
        status="sent",
    ))
    await appointment.save()

    return {"status": "reminders_sent", "results": results}


@router.get("/{appointment_id}/suggest-followup")
async def suggest_followup(appointment_id: str):
    """Suggest follow-up appointment based on patient data."""
    appointment = await Appointment.find_one(
        Appointment.appointment_id == appointment_id
    )
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    patient = await Patient.find_one(Patient.patient_id == appointment.patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    suggestion = scheduler.suggest_follow_up(
        patient.risk_level,
        {
            "assigned_facility": appointment.facility_name,
            "assigned_doctor": appointment.healthcare_provider,
        },
    )

    return {
        "current_appointment_id": appointment_id,
        "suggested_follow_up": {
            "suggested_date": suggestion.suggested_date.isoformat(),
            "appointment_type": suggestion.appointment_type,
            "facility": suggestion.facility,
            "healthcare_provider": suggestion.healthcare_provider,
            "priority": suggestion.priority,
            "notes": suggestion.notes,
        },
    }


@router.get("/analytics/overview")
async def get_appointment_analytics():
    """Get appointment analytics overview."""
    all_appts = await Appointment.find().to_list()
    total = len(all_appts)
    completed = sum(1 for a in all_appts if a.status == "completed")
    missed = sum(1 for a in all_appts if a.status == "missed" or a.attended is False)
    scheduled = sum(1 for a in all_appts if a.status == "scheduled")
    cancelled = sum(1 for a in all_appts if a.status == "cancelled")
    rescheduled = sum(1 for a in all_appts if a.reschedule_requested)

    return {
        "total": total,
        "completed": completed,
        "missed": missed,
        "scheduled": scheduled,
        "cancelled": cancelled,
        "rescheduled": rescheduled,
        "adherence_rate": round((completed / total) * 100, 1) if total > 0 else 0,
        "no_show_rate": round((missed / total) * 100, 1) if total > 0 else 0,
    }
