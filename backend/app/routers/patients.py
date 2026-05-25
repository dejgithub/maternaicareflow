from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from app.models.patient import Patient, VitalSigns, Symptom
from app.schemas.schemas import PatientCreate, SymptomReport, VitalSignsReport
from app.agents.risk_assessment import RiskAssessmentAgent
from app.config import settings

router = APIRouter(prefix="/api/patients", tags=["Patients"])
risk_agent = RiskAssessmentAgent(gemini_api_key=settings.gemini_api_key)


@router.post("/", response_model=Patient)
async def register_patient(data: PatientCreate):
    """Register a new mother/patient in the system."""
    patient_id = f"PAT-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{hash(data.email or data.phone or data.first_name) % 10000:04d}"
    existing = await Patient.find_one(Patient.email == data.email) if data.email else None
    if existing:
        raise HTTPException(status_code=409, detail="Patient with this email already exists")

    patient = Patient(
        patient_id=patient_id,
        first_name=data.first_name,
        last_name=data.last_name,
        date_of_birth=data.date_of_birth,
        age=data.age,
        phone=data.phone,
        email=data.email,
        address=data.address,
        emergency_contact_name=data.emergency_contact_name,
        emergency_contact_phone=data.emergency_contact_phone,
        blood_type=data.blood_type,
        allergies=data.allergies or [],
        pregnancy_week=data.pregnancy_week,
        expected_delivery_date=data.expected_delivery_date,
        national_id=data.national_id,
        risk_level="low",
        risk_score=0.0,
        assigned_facility="Primary Health Center - Main Branch",
    )
    await patient.insert()
    return patient


@router.get("/", response_model=List[Patient])
async def list_patients(
    risk_level: Optional[str] = Query(None),
    is_emergency: Optional[bool] = Query(None),
    is_active: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    """List patients with optional filtering."""
    query = {}
    if risk_level:
        query["risk_level"] = risk_level
    if is_emergency is not None:
        query["is_emergency"] = is_emergency
    if is_active is not None:
        query["is_active"] = is_active

    patients = await Patient.find(query).skip(skip).limit(limit).to_list()
    return patients


@router.get("/{patient_id}", response_model=Patient)
async def get_patient(patient_id: str):
    """Get detailed patient information."""
    patient = await Patient.find_one(Patient.patient_id == patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.post("/{patient_id}/symptoms")
async def report_symptom(patient_id: str, symptom: SymptomReport):
    """Report a new symptom for AI risk assessment."""
    patient = await Patient.find_one(Patient.patient_id == patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    new_symptom = Symptom(symptom=symptom.symptom, severity=symptom.severity)
    patient.symptoms.append(new_symptom)
    patient.updated_at = datetime.utcnow()
    await patient.save()

    patient_dict = {
        "age": patient.age,
        "pregnancy_week": patient.pregnancy_week,
        "missed_appointments": patient.missed_appointments,
        "symptoms": [{"symptom": s.symptom, "severity": s.severity} for s in patient.symptoms],
        "medical_history": [{"condition": m.condition} for m in patient.medical_history],
        "vital_signs": [{"blood_pressure_systolic": v.blood_pressure_systolic,
                         "blood_pressure_diastolic": v.blood_pressure_diastolic,
                         "heart_rate": v.heart_rate,
                         "temperature": v.temperature,
                         "oxygen_saturation": v.oxygen_saturation} for v in patient.vital_signs],
        "is_postnatal": patient.delivery_date is not None,
    }

    assessment = await risk_agent.assess(patient_dict)

    patient.risk_level = assessment.risk_level
    patient.risk_score = assessment.risk_score
    patient.is_emergency = assessment.risk_level == "emergency"
    await patient.save()

    return {
        "patient_id": patient_id,
        "symptom": symptom.symptom,
        "risk_assessment": {
            "risk_level": assessment.risk_level,
            "risk_score": assessment.risk_score,
            "recommendation": assessment.recommendation,
            "confidence": assessment.confidence,
            "requires_escalation": assessment.requires_escalation,
            "requires_human_review": assessment.requires_human_review,
            "danger_signs_detected": assessment.danger_signs_detected,
            "recommended_actions": assessment.recommended_actions,
        },
    }


@router.post("/{patient_id}/vitals")
async def record_vitals(patient_id: str, vitals: VitalSignsReport):
    """Record patient vital signs."""
    patient = await Patient.find_one(Patient.patient_id == patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    new_vitals = VitalSigns(
        blood_pressure_systolic=vitals.blood_pressure_systolic,
        blood_pressure_diastolic=vitals.blood_pressure_diastolic,
        heart_rate=vitals.heart_rate,
        temperature=vitals.temperature,
        oxygen_saturation=vitals.oxygen_saturation,
    )
    patient.vital_signs.append(new_vitals)
    patient.updated_at = datetime.utcnow()
    await patient.save()
    return {"status": "recorded", "patient_id": patient_id}


@router.post("/{patient_id}/assess-risk")
async def assess_patient_risk(patient_id: str):
    """Run AI risk assessment on a patient."""
    patient = await Patient.find_one(Patient.patient_id == patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    patient_dict = {
        "age": patient.age,
        "pregnancy_week": patient.pregnancy_week,
        "missed_appointments": patient.missed_appointments,
        "symptoms": [{"symptom": s.symptom, "severity": s.severity} for s in patient.symptoms],
        "medical_history": [{"condition": m.condition} for m in patient.medical_history],
        "delivery_type": patient.delivery_type,
        "is_postnatal": patient.delivery_date is not None,
    }

    assessment = await risk_agent.assess(patient_dict)
    patient.risk_level = assessment.risk_level
    patient.risk_score = assessment.risk_score
    patient.is_emergency = assessment.risk_level == "emergency"
    await patient.save()

    return {
        "patient_id": patient_id,
        "assessment": {
            "risk_level": assessment.risk_level,
            "risk_score": assessment.risk_score,
            "recommendation": assessment.recommendation,
            "confidence": assessment.confidence,
            "requires_escalation": assessment.requires_escalation,
            "requires_human_review": assessment.requires_human_review,
            "danger_signs_detected": assessment.danger_signs_detected,
            "recommended_actions": assessment.recommended_actions,
            "reasoning": assessment.reasoning,
        },
        "patient_status": {
            "is_emergency": patient.is_emergency,
            "missed_appointments": patient.missed_appointments,
            "symptom_count": len(patient.symptoms),
        },
    }


@router.get("/{patient_id}/timeline")
async def get_patient_timeline(patient_id: str):
    """Get patient care timeline including appointments, referrals, alerts."""
    from app.models.referral import Referral
    from app.models.appointment import Appointment
    from app.models.alert import Alert

    patient = await Patient.find_one(Patient.patient_id == patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    referrals = await Referral.find(Referral.patient_id == patient_id).to_list()
    appointments = await Appointment.find(Appointment.patient_id == patient_id).to_list()
    alerts = await Alert.find(Alert.patient_id == patient_id).to_list()

    timeline = []

    for ref in referrals:
        timeline.append({
            "type": "referral",
            "id": ref.referral_id,
            "date": ref.created_at.isoformat(),
            "status": ref.status,
            "description": f"Referral to {ref.target_facility_name or 'pending'}: {ref.referral_reason}",
        })

    for apt in appointments:
        timeline.append({
            "type": "appointment",
            "id": apt.appointment_id,
            "date": apt.scheduled_date.isoformat(),
            "status": apt.status,
            "description": f"{apt.appointment_type} at {apt.facility_name}",
        })

    for alert in alerts:
        timeline.append({
            "type": "alert",
            "id": alert.alert_id,
            "date": alert.created_at.isoformat(),
            "severity": alert.severity,
            "description": alert.message,
        })

    timeline.sort(key=lambda x: x["date"], reverse=True)
    return {"patient_id": patient_id, "timeline": timeline, "total": len(timeline)}
