"""
MaternAI CareFlow - Emergency Escalation Agent

Handles emergency case detection, escalation workflows, ambulance coordination,
stakeholder notification, and exception handling for critical maternal cases.
"""
import logging
import asyncio
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class EmergencyResponse:
    escalation_id: str
    severity: str
    requires_immediate_action: bool
    required_actions: List[str]
    notify_list: List[str]
    ambulance_required: bool
    estimated_response_minutes: Optional[int] = None


class EmergencyEscalationAgent:
    """AI-powered emergency escalation agent for critical maternal health events."""

    ESCALATION_MATRIX = {
        "cardiac_arrest": {"severity": "critical", "response": "immediate", "ambulance": True},
        "seizures": {"severity": "critical", "response": "immediate", "ambulance": True},
        "heavy_bleeding": {"severity": "critical", "response": "immediate", "ambulance": True},
        "loss_of_consciousness": {"severity": "critical", "response": "immediate", "ambulance": True},
        "difficulty_breathing": {"severity": "critical", "response": "immediate", "ambulance": True},
        "severe_abdominal_pain": {"severity": "high", "response": "urgent", "ambulance": False},
        "severe_headache": {"severity": "high", "response": "urgent", "ambulance": False},
        "fever_over_38": {"severity": "high", "response": "urgent", "ambulance": False},
        "blurred_vision": {"severity": "high", "response": "urgent", "ambulance": False},
        "signs_of_infection": {"severity": "medium", "response": "priority", "ambulance": False},
    }

    NOTIFICATION_PRIORITY = {
        "critical": ["emergency_services", "on_call_obstetrician", "hospital_ed", "head_nurse", "medical_director"],
        "high": ["on_call_obstetrician", "head_nurse", "attending_physician"],
        "medium": ["attending_physician", "assigned_nurse"],
    }

    def __init__(self):
        logger.info("EmergencyEscalationAgent initialized")

    async def assess_emergency(self, patient_data: Dict[str, Any],
                                symptoms: List[str],
                                vital_signs: Optional[Dict[str, Any]] = None) -> EmergencyResponse:
        """Assess patient data and determine if emergency escalation is needed."""
        detected_severity = "low"
        detected_symptoms = []
        ambulance_needed = False
        critical_symptoms = []

        for symptom in symptoms:
            symptom_key = symptom.lower().replace(" ", "_")
            matrix = self.ESCALATION_MATRIX.get(symptom_key)
            if matrix:
                detected_symptoms.append(symptom_key)
                if matrix["severity"] == "critical":
                    critical_symptoms.append(symptom_key)
                    if matrix["ambulance"]:
                        ambulance_needed = True

        if critical_symptoms:
            detected_severity = "critical"
        elif any(s in dict(self.ESCALATION_MATRIX).keys() for s in detected_symptoms):
            severities = [self.ESCALATION_MATRIX[s]["severity"] for s in detected_symptoms if s in self.ESCALATION_MATRIX]
            if "high" in severities:
                detected_severity = "high"
            else:
                detected_severity = "medium"

        if vital_signs:
            vs = vital_signs
            if (vs.get("blood_pressure_systolic", 120) > 180 or
                vs.get("blood_pressure_diastolic", 80) > 120):
                detected_severity = "critical"
                ambulance_needed = True
                detected_symptoms.append("hypertensive_crisis")
            if vs.get("oxygen_saturation", 98) < 90:
                detected_severity = "critical"
                ambulance_needed = True
                detected_symptoms.append("hypoxia")
            if vs.get("heart_rate", 80) > 140 or vs.get("heart_rate", 80) < 40:
                detected_severity = "critical"
                ambulance_needed = True
                detected_symptoms.append("abnormal_heart_rate")

        escalation_id = f"ESC-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{hash(str(patient_data.get('patient_id', ''))) % 10000:04d}"
        notify_list = self.NOTIFICATION_PRIORITY.get(detected_severity, ["assigned_nurse"])

        return EmergencyResponse(
            escalation_id=escalation_id,
            severity=detected_severity,
            requires_immediate_action=detected_severity in ("critical", "high"),
            required_actions=self._get_required_actions(detected_severity, ambulance_needed, detected_symptoms),
            notify_list=notify_list,
            ambulance_required=ambulance_needed,
            estimated_response_minutes=5 if detected_severity == "critical" else (30 if detected_severity == "high" else 120),
        )

    def _get_required_actions(self, severity: str, ambulance: bool,
                               symptoms: List[str]) -> List[str]:
        actions = []
        if ambulance:
            actions.append("Dispatch ambulance immediately")
            actions.append("Alert emergency department with patient status")
        if severity == "critical":
            actions.append("Activate code blue / medical emergency team")
            actions.append("Prepare emergency operating room if needed")
            actions.append("Notify blood bank for potential transfusion")
            actions.append("Alert neonatal intensive care if applicable")
        if severity == "high":
            actions.append("Contact on-call obstetrician stat")
            actions.append("Prepare for urgent transfer if needed")
            actions.append("Begin continuous fetal monitoring")
        actions.append("Document all interventions in patient record")
        actions.append("Notify next of kin")
        return actions

    async def coordinate_ambulance(self, patient_data: Dict[str, Any],
                                    facility: str) -> Dict[str, Any]:
        """Mock ambulance coordination - in production, calls emergency dispatch API."""
        await asyncio.sleep(0.5)
        return {
            "ambulance_dispatched": True,
            "dispatch_time": datetime.utcnow().isoformat(),
            "estimated_arrival_minutes": 8,
            "ambulance_id": f"AMB-{datetime.utcnow().strftime('%H%M%S')}",
            "destination": facility,
            "patient_id": patient_data.get("patient_id"),
            "status": "dispatched",
        }

    async def notify_stakeholders(self, patient_data: Dict[str, Any],
                                   escalation: EmergencyResponse) -> List[Dict[str, Any]]:
        """Send multi-channel notifications to all relevant stakeholders."""
        notifications = []
        patient_name = f"{patient_data.get('first_name', '')} {patient_data.get('last_name', '')}"

        for recipient in escalation.notify_list:
            notification = {
                "recipient_role": recipient,
                "patient_name": patient_name,
                "patient_id": patient_data.get("patient_id"),
                "severity": escalation.severity,
                "message": f"EMERGENCY: {escalation.severity.upper()} - Patient {patient_name} requires immediate attention. Escalation ID: {escalation.escalation_id}",
                "channel": "sms" if recipient == "emergency_services" else "in_app",
                "sent_at": datetime.utcnow().isoformat(),
                "status": "sent",
            }
            notifications.append(notification)
        return notifications

    def generate_escalation_summary(self, patient_data: Dict[str, Any],
                                     escalation: EmergencyResponse) -> str:
        return f"""
EMERGENCY ESCALATION SUMMARY
============================
Escalation ID: {escalation.escalation_id}
Timestamp: {datetime.utcnow().isoformat()}
Severity Level: {escalation.severity.upper()}

PATIENT INFORMATION
------------------
Name: {patient_data.get('first_name', '')} {patient_data.get('last_name', '')}
Patient ID: {patient_data.get('patient_id', '')}
Age: {patient_data.get('age', 'N/A')}
Pregnancy Week: {patient_data.get('pregnancy_week', 'N/A')}
Risk Level: {patient_data.get('risk_level', 'N/A')}

EMERGENCY DETAILS
-----------------
Ambulance Required: {'YES' if escalation.ambulance_required else 'NO'}
Immediate Action Required: {'YES' if escalation.requires_immediate_action else 'NO'}

REQUIRED ACTIONS:
{chr(10).join(f'  - {a}' for a in escalation.required_actions)}

NOTIFIED STAKEHOLDERS:
{chr(10).join(f'  - {n}' for n in escalation.notify_list)}

STATUS: ACTIVE - Requires immediate intervention
"""
