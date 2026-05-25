from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Query
from app.models.patient import Patient
from app.models.referral import Referral
from app.models.appointment import Appointment
from app.models.alert import Escalation, Alert

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/dashboard")
async def get_dashboard_overview():
    """Get comprehensive dashboard analytics."""
    total_patients = await Patient.find().count()
    high_risk = await Patient.find({"risk_level": "high"}).count()
    emergency = await Patient.find({"risk_level": "emergency"}).count()
    medium_risk = await Patient.find({"risk_level": "medium"}).count()

    total_referrals = await Referral.find().count()
    pending_referrals = await Referral.find({"status": "pending_approval"}).count()
    approved_referrals = await Referral.find({"status": "approved"}).count()
    completed_referrals = await Referral.find({"status": "completed"}).count()

    total_appointments = await Appointment.find().count()
    missed_appointments = await Appointment.find({"status": "missed"}).count()
    upcoming_appointments = await Appointment.find({"status": "scheduled"}).count()

    open_escalations = await Escalation.find({"status": "open"}).count()
    critical_escalations = await Escalation.find({"severity": "critical", "status": "open"}).count()

    recent_patients = await Patient.find().sort(-Patient.created_at).limit(5).to_list()
    recent_alerts = await Alert.find().sort(-Alert.created_at).limit(10).to_list()

    return {
        "summary": {
            "total_patients": total_patients,
            "high_risk_patients": high_risk,
            "emergency_patients": emergency,
            "medium_risk_patients": medium_risk,
            "total_referrals": total_referrals,
            "pending_referrals": pending_referrals,
            "approved_referrals": approved_referrals,
            "completed_referrals": completed_referrals,
            "total_appointments": total_appointments,
            "missed_appointments": missed_appointments,
            "upcoming_appointments": upcoming_appointments,
            "open_escalations": open_escalations,
            "critical_escalations": critical_escalations,
        },
        "risk_distribution": {
            "low": await Patient.find({"risk_level": "low"}).count(),
            "medium": medium_risk,
            "high": high_risk,
            "emergency": emergency,
        },
        "referral_status": {
            "pending_approval": pending_referrals,
            "approved": approved_referrals,
            "assigned": await Referral.find({"status": "assigned"}).count(),
            "completed": completed_referrals,
            "rejected": await Referral.find({"status": "rejected"}).count(),
        },
        "appointment_metrics": {
            "total": total_appointments,
            "scheduled": upcoming_appointments,
            "completed": await Appointment.find({"status": "completed"}).count(),
            "missed": missed_appointments,
            "cancelled": await Appointment.find({"status": "cancelled"}).count(),
        },
        "recent_patients": [
            {
                "patient_id": p.patient_id,
                "name": p.display_name(),
                "risk_level": p.risk_level,
                "created_at": p.created_at.isoformat(),
            }
            for p in recent_patients
        ],
        "recent_alerts": [
            {
                "alert_id": a.alert_id,
                "patient_name": a.patient_name,
                "alert_type": a.alert_type,
                "severity": a.severity,
                "message": a.message,
                "created_at": a.created_at.isoformat(),
            }
            for a in recent_alerts
        ],
    }


@router.get("/risk-trends")
async def get_risk_trends(days: int = Query(30, ge=1, le=365)):
    """Get risk level trends over time."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    patients = await Patient.find({"created_at": {"$gte": cutoff}}).to_list()

    trends = {"low": [], "medium": [], "high": [], "emergency": []}
    for i in range(days):
        day = cutoff + timedelta(days=i)
        day_end = day + timedelta(days=1)
        day_patients = [p for p in patients if day <= p.created_at < day_end]
        for level in trends:
            trends[level].append({
                "date": day.date().isoformat(),
                "count": sum(1 for p in day_patients if p.risk_level == level),
            })

    return {
        "period_days": days,
        "trends": trends,
        "current_distribution": {
            "low": await Patient.find({"risk_level": "low"}).count(),
            "medium": await Patient.find({"risk_level": "medium"}).count(),
            "high": await Patient.find({"risk_level": "high"}).count(),
            "emergency": await Patient.find({"risk_level": "emergency"}).count(),
        },
    }


@router.get("/workflow-performance")
async def get_workflow_performance():
    """Get workflow execution performance metrics."""
    referrals = await Referral.find().to_list()
    appointments = await Appointment.find().to_list()
    escalations = await Escalation.find().to_list()

    referral_avg_time = None
    completed_refs = [r for r in referrals if r.completed_at and r.created_at]
    if completed_refs:
        times = [(r.completed_at - r.created_at).total_seconds() / 3600 for r in completed_refs]
        referral_avg_time = round(sum(times) / len(times), 1)

    return {
        "total_workflows_executed": len(referrals) + len(appointments) + len(escalations),
        "referral_metrics": {
            "total": len(referrals),
            "avg_completion_time_hours": referral_avg_time,
            "approval_rate": round(
                (sum(1 for r in referrals if r.status == "approved") / max(len(referrals), 1)) * 100, 1
            ),
        },
        "escalation_metrics": {
            "total": len(escalations),
            "open": sum(1 for e in escalations if e.status == "open"),
            "resolved": sum(1 for e in escalations if e.status == "resolved"),
            "avg_resolution_time": None,
        },
        "human_approval_metrics": {
            "total_approvals": sum(1 for r in referrals if r.approved_by),
            "total_rejections": sum(1 for r in referrals if r.status == "rejected"),
        },
    }


@router.get("/facility-load")
async def get_facility_load():
    """Get healthcare facility workload distribution."""
    from app.models.referral import HealthcareFacility
    facilities = await HealthcareFacility.find().to_list()
    referrals = await Referral.find().to_list()

    facility_stats = []
    for facility in facilities:
        facility_refs = [r for r in referrals if r.target_facility_id == facility.facility_id]
        load_pct = round((facility.current_load / max(facility.capacity, 1)) * 100, 1)
        facility_stats.append({
            "facility_id": facility.facility_id,
            "name": facility.name,
            "type": facility.type,
            "capacity": facility.capacity,
            "current_load": facility.current_load,
            "load_percentage": load_pct,
            "active_referrals": len(facility_refs),
            "pending_referrals": sum(1 for r in facility_refs if r.status == "pending_approval"),
        })

    return {
        "facilities": facility_stats,
        "total_capacity": sum(f.capacity for f in facilities),
        "total_load": sum(f.current_load for f in facilities),
        "overall_load_pct": round(
            (sum(f.current_load for f in facilities) / max(sum(f.capacity for f in facilities), 1)) * 100, 1
        ),
    }
