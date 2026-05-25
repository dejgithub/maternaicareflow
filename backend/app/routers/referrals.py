from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from app.models.referral import Referral, HealthcareFacility
from app.models.patient import Patient
from app.schemas.schemas import ReferralCreate, ReferralApprove, ReferralReject
from app.agents.referral_coordinator import ReferralCoordinatorAgent
from app.agents.emergency_escalation import EmergencyEscalationAgent
from app.services.workflow import WorkflowOrchestrator
from app.config import settings

router = APIRouter(prefix="/api/referrals", tags=["Referrals"])
coordinator = ReferralCoordinatorAgent(gemini_api_key=settings.gemini_api_key)
escalation_agent = EmergencyEscalationAgent()
workflow = WorkflowOrchestrator(
    maestro_api_url=settings.uipath_maestro_api_url,
    maestro_api_key=settings.uipath_maestro_api_key,
)


@router.get("/facilities", response_model=List[HealthcareFacility])
async def list_facilities(facility_type: Optional[str] = Query(None)):
    """List available healthcare facilities."""
    query = {}
    if facility_type:
        query["type"] = facility_type
    facilities = await HealthcareFacility.find(query).to_list()
    return facilities


@router.post("/facilities")
async def create_facility(facility: HealthcareFacility):
    """Register a new healthcare facility."""
    existing = await HealthcareFacility.find_one(
        HealthcareFacility.facility_id == facility.facility_id
    )
    if existing:
        raise HTTPException(status_code=409, detail="Facility already exists")
    await facility.insert()
    return facility


@router.post("/", response_model=Referral)
async def create_referral(data: ReferralCreate):
    """Create a new referral with AI-powered facility recommendation."""
    patient = await Patient.find_one(Patient.patient_id == data.patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    referral_id = f"REF-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{hash(data.patient_id) % 10000:04d}"

    available = await HealthcareFacility.find(
        {"is_active": True}
    ).to_list()

    recommendation = await coordinator.recommend_facility(
        {
            "patient_id": patient.patient_id,
            "first_name": patient.first_name,
            "last_name": patient.last_name,
            "age": patient.age,
            "risk_level": patient.risk_level,
            "pregnancy_week": patient.pregnancy_week,
            "referral_reason": data.referral_reason,
        },
        [f.dict() for f in available],
    )

    referral = Referral(
        referral_id=referral_id,
        patient_id=data.patient_id,
        patient_name=patient.display_name(),
        risk_level=patient.risk_level,
        source_facility=data.source_facility,
        target_facility_id=recommendation.target_facility_id,
        target_facility_name=recommendation.target_facility_name,
        referral_reason=data.referral_reason,
        referral_notes=data.referral_notes,
        status="pending_approval",
        priority=data.priority,
        is_emergency=patient.is_emergency,
        ai_recommendation=recommendation.reasoning,
        ai_confidence_score=recommendation.confidence_score,
    )
    await referral.insert()

    await workflow.start_workflow("referral_approval", {
        "referral_id": referral_id,
        "patient_id": data.patient_id,
        "risk_level": patient.risk_level,
    })

    if patient.is_emergency:
        emergency = await escalation_agent.assess_emergency(
            {
                "patient_id": patient.patient_id,
                "first_name": patient.first_name,
                "last_name": patient.last_name,
                "age": patient.age,
                "risk_level": "emergency",
            },
            [s.symptom for s in patient.symptoms],
        )
        return {
            "referral": referral,
            "emergency_escalation": {
                "escalation_id": emergency.escalation_id,
                "severity": emergency.severity,
                "requires_immediate_action": emergency.requires_immediate_action,
                "ambulance_required": emergency.ambulance_required,
                "notify_list": emergency.notify_list,
                "required_actions": emergency.required_actions,
            },
        }

    return referral


@router.get("/", response_model=List[Referral])
async def list_referrals(
    status: Optional[str] = Query(None),
    risk_level: Optional[str] = Query(None),
    patient_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    """List referrals with optional filtering."""
    query = {}
    if status:
        query["status"] = status
    if risk_level:
        query["risk_level"] = risk_level
    if patient_id:
        query["patient_id"] = patient_id

    referrals = await Referral.find(query).skip(skip).limit(limit).to_list()
    return referrals


@router.get("/{referral_id}", response_model=Referral)
async def get_referral(referral_id: str):
    """Get referral details."""
    referral = await Referral.find_one(Referral.referral_id == referral_id)
    if not referral:
        raise HTTPException(status_code=404, detail="Referral not found")
    return referral


@router.post("/{referral_id}/approve")
async def approve_referral(referral_id: str, data: ReferralApprove):
    """Approve a referral (human-in-the-loop decision)."""
    referral = await Referral.find_one(Referral.referral_id == referral_id)
    if not referral:
        raise HTTPException(status_code=404, detail="Referral not found")

    referral.status = "approved"
    referral.target_facility_id = data.target_facility_id
    referral.approved_by = data.approved_by
    referral.approved_at = datetime.utcnow()
    referral.updated_at = datetime.utcnow()
    await referral.save()

    await workflow.complete_human_approval(
        f"approve-{referral_id}",
        "approved",
        data.approved_by,
    )

    return referral


@router.post("/{referral_id}/reject")
async def reject_referral(referral_id: str, data: ReferralReject):
    """Reject a referral with reason."""
    referral = await Referral.find_one(Referral.referral_id == referral_id)
    if not referral:
        raise HTTPException(status_code=404, detail="Referral not found")

    referral.status = "rejected"
    referral.rejected_by = data.rejected_by
    referral.rejection_reason = data.rejection_reason
    referral.updated_at = datetime.utcnow()
    await referral.save()

    return referral


@router.post("/{referral_id}/assign")
async def assign_worker(referral_id: str, worker_id: str = Query(...),
                        worker_name: str = Query(...)):
    """Assign a healthcare worker to a referral."""
    referral = await Referral.find_one(Referral.referral_id == referral_id)
    if not referral:
        raise HTTPException(status_code=404, detail="Referral not found")

    referral.assigned_healthcare_worker = worker_id
    referral.assigned_worker_name = worker_name
    referral.status = "assigned"
    referral.updated_at = datetime.utcnow()
    await referral.save()
    return referral


@router.post("/{referral_id}/complete")
async def complete_referral(referral_id: str):
    """Mark a referral as completed."""
    referral = await Referral.find_one(Referral.referral_id == referral_id)
    if not referral:
        raise HTTPException(status_code=404, detail="Referral not found")

    referral.status = "completed"
    referral.completed_at = datetime.utcnow()
    referral.updated_at = datetime.utcnow()
    await referral.save()
    return referral
