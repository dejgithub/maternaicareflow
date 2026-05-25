"""
MaternAI CareFlow - Referral Coordination Agent

Orchestrates referrals between healthcare facilities, checking availability,
routing to appropriate specialists, and notifying all stakeholders.
"""
import logging
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ReferralRecommendation:
    target_facility_id: str
    target_facility_name: str
    confidence_score: float
    reasoning: str
    estimated_wait_time: Optional[str] = None
    specialist_type: Optional[str] = None
    priority: str = "normal"


class ReferralCoordinatorAgent:
    """AI-powered referral coordination agent for healthcare facility matching."""

    FACILITY_TYPES = {
        "primary_clinic": {"level": 1, "name": "Primary Health Clinic"},
        "general_hospital": {"level": 2, "name": "General Hospital"},
        "specialty_hospital": {"level": 3, "name": "Specialty Hospital"},
        "maternity_hospital": {"level": 3, "name": "Maternity Hospital"},
        "teaching_hospital": {"level": 4, "name": "Teaching & Referral Hospital"},
    }

    REFERRAL_MATRIX = {
        "low": {"facility_type": "primary_clinic", "urgency": "routine"},
        "medium": {"facility_type": "general_hospital", "urgency": "within_48h"},
        "high": {"facility_type": "specialty_hospital", "urgency": "within_24h"},
        "emergency": {"facility_type": "teaching_hospital", "urgency": "immediate"},
    }

    def __init__(self, gemini_api_key: Optional[str] = None):
        self.gemini_api_key = gemini_api_key
        self._llm_available = False
        self._init_llm()

    def _init_llm(self):
        try:
            if self.gemini_api_key:
                from langchain_google_genai import ChatGoogleGenerativeAI
                self.llm = ChatGoogleGenerativeAI(
                    model="gemini-pro",
                    google_api_key=self.gemini_api_key,
                    temperature=0.2
                )
                self._llm_available = True
                logger.info("Gemini LLM initialized for ReferralCoordinatorAgent")
        except Exception as e:
            logger.warning(f"LLM init failed for ReferralCoordinator: {e}")

    async def recommend_facility(self, patient_data: Dict[str, Any],
                                  available_facilities: List[Dict[str, Any]]) -> ReferralRecommendation:
        """Recommend the best facility for a referral based on patient needs and facility availability."""
        risk_level = patient_data.get("risk_level", "low")
        referral_reason = patient_data.get("referral_reason", "")

        matrix = self.REFERRAL_MATRIX.get(risk_level, self.REFERRAL_MATRIX["low"])
        target_type = matrix["facility_type"]

        suitable = [f for f in available_facilities
                    if f.get("type") == target_type and f.get("is_active", True)]

        if not suitable:
            suitable = [f for f in available_facilities if f.get("is_active", True)]

        if not suitable:
            return ReferralRecommendation(
                target_facility_id="unavailable",
                target_facility_name="No facility available",
                confidence_score=0.0,
                reasoning="No suitable healthcare facilities currently available",
                priority=matrix["urgency"],
            )

        best = suitable[0]
        for f in suitable:
            load_ratio = f.get("current_load", 0) / max(f.get("capacity", 1), 1)
            best_load = best.get("current_load", 0) / max(best.get("capacity", 1), 1)
            if load_ratio < best_load:
                best = f

        ai_recommendation = None
        if self._llm_available:
            try:
                ai_recommendation = await self._llm_recommend(
                    patient_data, suitable
                )
            except Exception as e:
                logger.error(f"LLM recommendation failed: {e}")

        if ai_recommendation:
            return ai_recommendation

        return ReferralRecommendation(
            target_facility_id=best.get("facility_id", ""),
            target_facility_name=best.get("name", "Unknown Facility"),
            confidence_score=0.8,
            reasoning=f"Best available {target_type} facility with lowest current load",
            specialist_type=self._get_specialist_type(referral_reason, risk_level),
            priority=matrix["urgency"],
        )

    async def _llm_recommend(self, patient_data: Dict[str, Any],
                               facilities: List[Dict[str, Any]]) -> Optional[ReferralRecommendation]:
        try:
            prompt = f"""You are a healthcare referral coordinator. Select the best facility for this maternal patient.

Patient Risk Level: {patient_data.get('risk_level')}
Referral Reason: {patient_data.get('referral_reason')}
Patient Age: {patient_data.get('age')}
Pregnancy Week: {patient_data.get('pregnancy_week')}

Available Facilities:
{json.dumps(facilities, indent=2)}

Return JSON only with:
- target_facility_id (string)
- target_facility_name (string)
- confidence_score (float 0-1)
- reasoning (string)
- specialist_type (string)
- priority (string)
"""
            response = await self.llm.agenerate([[prompt]])
            text = response.generations[0][0].text.strip()
            text = text.replace("```json", "").replace("```", "").strip()
            result = json.loads(text)
            return ReferralRecommendation(
                target_facility_id=result.get("target_facility_id", ""),
                target_facility_name=result.get("target_facility_name", ""),
                confidence_score=float(result.get("confidence_score", 0.7)),
                reasoning=result.get("reasoning", ""),
                specialist_type=result.get("specialist_type"),
                priority=result.get("priority", "normal"),
            )
        except Exception as e:
            logger.error(f"LLM recommendation parse error: {e}")
            return None

    def _get_specialist_type(self, referral_reason: str, risk_level: str) -> str:
        reason_lower = referral_reason.lower()
        if "cardiac" in reason_lower or "heart" in reason_lower:
            return "Cardiologist"
        if "infection" in reason_lower or "fever" in reason_lower:
            return "Infectious Disease Specialist"
        if "mental" in reason_lower or "depression" in reason_lower or "psych" in reason_lower:
            return "Perinatal Mental Health Specialist"
        if "bleeding" in reason_lower or "hemorrhage" in reason_lower:
            return "Obstetric Emergency Specialist"
        if "high" in risk_level or "emergency" in risk_level:
            return "Maternal-Fetal Medicine Specialist"
        return "Obstetrician-Gynecologist"

    async def check_service_availability(self, facility_id: str,
                                          service_type: str) -> Dict[str, Any]:
        """Mock service availability check - in production, calls actual facility APIs."""
        import random
        return {
            "facility_id": facility_id,
            "service_type": service_type,
            "available": random.choice([True, True, True, False]),
            "estimated_wait_days": random.randint(0, 7),
            "capacity_available": random.randint(0, 10),
        }

    def generate_referral_notes(self, patient_data: Dict[str, Any],
                                 risk_level: str) -> str:
        template = f"""REFERRAL SUMMARY
Patient: {patient_data.get('first_name', '')} {patient_data.get('last_name', '')}
Risk Classification: {risk_level.upper()}
Risk Score: {patient_data.get('risk_score', 'N/A')}
Pregnancy Week: {patient_data.get('pregnancy_week', 'N/A')}
Key Concerns: {patient_data.get('referral_reason', 'Routine referral')}
Action Required: {'URGENT - Immediate attention required' if risk_level in ('high', 'emergency') else 'Standard referral processing'}
"""
        return template
