from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from app.models.alert import Alert, Escalation
from app.models.patient import Patient
from app.schemas.schemas import EscalationAction, EscalationResolve, ApprovalAction
from app.agents.emergency_escalation import EmergencyEscalationAgent
from app.services.workflow import WorkflowOrchestrator
from app.services.notification import NotificationService
from app.config import settings

router = APIRouter(prefix="/api/alerts", tags=["Alerts & Escalations"])
escalation_agent = EmergencyEscalationAgent()
workflow = WorkflowOrchestrator(
    maestro_api_url=settings.uipath_maestro_api_url,
    maestro_api_key=settings.uipath_maestro_api_key,
)
notifier = NotificationService(
    twilio_sid=settings.twilio_account_sid,
    twilio_token=settings.twilio_auth_token,
    twilio_phone=settings.twilio_phone_number,
    sendgrid_key=settings.sendgrid_api_key,
    from_email=settings.from_email,
)


@router.post("/escalations", response_model=Escalation)
async def create_escalation(patient_id: str = Query(...), description: str = Query(...)):
    """Create an emergency escalation for a patient."""
    patient = await Patient.find_one(Patient.patient_id == patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    escalation_id = f"ESC-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{hash(patient_id) % 10000:04d}"

    assessment = await escalation_agent.assess_emergency(
        {
            "patient_id": patient.patient_id,
            "first_name": patient.first_name,
            "last_name": patient.last_name,
            "age": patient.age,
            "pregnancy_week": patient.pregnancy_week,
            "risk_level": patient.risk_level,
        },
        [s.symptom for s in patient.symptoms],
    )

    escalation = Escalation(
        escalation_id=escalation_id,
        patient_id=patient_id,
        patient_name=patient.display_name(),
        alert_type="emergency",
        severity=assessment.severity,
        description=description,
        ai_recommendation=assessment.escalation_id,
        status="open",
        requires_human_approval=True,
        approval_status="pending",
    )
    await escalation.insert()

    patient.is_emergency = True
    await patient.save()

    await workflow.start_workflow("emergency_escalation", {
        "escalation_id": escalation_id,
        "patient_id": patient_id,
        "severity": assessment.severity,
        "ambulance_required": assessment.ambulance_required,
    })

    if assessment.ambulance_required:
        ambulance = await escalation_agent.coordinate_ambulance(
            {"patient_id": patient_id, "first_name": patient.first_name},
            patient.assigned_facility or "",
        )
        escalation.linked_referral_id = ambulance.get("ambulance_id")

    await escalation.save()
    return escalation


@router.get("/escalations", response_model=List[Escalation])
async def list_escalations(
    status: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    patient_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    """List escalations with optional filtering."""
    query = {}
    if status:
        query["status"] = status
    if severity:
        query["severity"] = severity
    if patient_id:
        query["patient_id"] = patient_id

    escalations = await Escalation.find(query).skip(skip).limit(limit).to_list()
    return escalations


@router.get("/escalations/{escalation_id}", response_model=Escalation)
async def get_escalation(escalation_id: str):
    """Get escalation details."""
    escalation = await Escalation.find_one(
        Escalation.escalation_id == escalation_id
    )
    if not escalation:
        raise HTTPException(status_code=404, detail="Escalation not found")
    return escalation


@router.post("/escalations/{escalation_id}/assign")
async def assign_escalation(escalation_id: str, action: EscalationAction):
    """Assign escalation to a healthcare provider."""
    escalation = await Escalation.find_one(
        Escalation.escalation_id == escalation_id
    )
    if not escalation:
        raise HTTPException(status_code=404, detail="Escalation not found")

    escalation.assigned_to = action.assigned_to
    escalation.assigned_name = action.assigned_name
    escalation.updated_at = datetime.utcnow()
    await escalation.save()
    return escalation


@router.post("/escalations/{escalation_id}/acknowledge")
async def acknowledge_escalation(escalation_id: str, acknowledged_by: str = Query(...)):
    """Acknowledge an escalation (human-in-the-loop)."""
    escalation = await Escalation.find_one(
        Escalation.escalation_id == escalation_id
    )
    if not escalation:
        raise HTTPException(status_code=404, detail="Escalation not found")

    escalation.acknowledged_by = acknowledged_by
    escalation.acknowledged_at = datetime.utcnow()
    escalation.status = "acknowledged"
    escalation.updated_at = datetime.utcnow()
    await escalation.save()
    return escalation


@router.post("/escalations/{escalation_id}/approve")
async def approve_escalation(escalation_id: str, action: ApprovalAction):
    """Human approval for escalation decision."""
    escalation = await Escalation.find_one(
        Escalation.escalation_id == escalation_id
    )
    if not escalation:
        raise HTTPException(status_code=404, detail="Escalation not found")

    escalation.approval_status = "approved" if action.approve else "rejected"
    escalation.approved_by = action.approved_by
    escalation.approved_at = datetime.utcnow()
    escalation.status = "approved" if action.approve else "rejected"
    escalation.resolution_notes = action.notes
    escalation.updated_at = datetime.utcnow()
    await escalation.save()
    return escalation


@router.post("/escalations/{escalation_id}/resolve")
async def resolve_escalation(escalation_id: str, action: EscalationResolve):
    """Resolve an escalation after intervention."""
    escalation = await Escalation.find_one(
        Escalation.escalation_id == escalation_id
    )
    if not escalation:
        raise HTTPException(status_code=404, detail="Escalation not found")

    escalation.resolved_by = action.resolved_by
    escalation.resolved_at = datetime.utcnow()
    escalation.resolution_notes = action.resolution_notes
    escalation.status = "resolved"
    escalation.updated_at = datetime.utcnow()
    await escalation.save()

    patient = await Patient.find_one(Patient.patient_id == escalation.patient_id)
    if patient:
        patient.is_emergency = False
        await patient.save()

    return escalation


@router.get("/", response_model=List[Alert])
async def list_alerts(
    patient_id: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    is_read: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    """List alerts with optional filtering."""
    query = {}
    if patient_id:
        query["patient_id"] = patient_id
    if severity:
        query["severity"] = severity
    if is_read is not None:
        query["is_read"] = is_read

    alerts = await Alert.find(query).skip(skip).limit(limit).to_list()
    return alerts


@router.post("/{alert_id}/read")
async def mark_alert_read(alert_id: str):
    """Mark an alert as read."""
    alert = await Alert.find_one(Alert.alert_id == alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.is_read = True
    await alert.save()
    return alert
