"""
MaternAI CareFlow - AI Risk Assessment Agent

This agent analyzes patient data including symptoms, medical history,
vital signs, and appointment adherence to classify maternal risk levels.

Uses LangChain for prompt chaining and structured AI reasoning.
"""
import logging
import json
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RiskAssessmentResult:
    risk_level: str
    risk_score: float
    recommendation: str
    confidence: float
    requires_escalation: bool
    requires_human_review: bool
    reasoning: str
    danger_signs_detected: List[str]
    recommended_actions: List[str]


class RiskAssessmentAgent:
    """AI-powered maternal risk assessment agent using rule-based + LLM hybrid approach."""

    DANGER_SIGNS = {
        "severe_headache": "Possible preeclampsia indicator",
        "blurred_vision": "Possible preeclampsia indicator",
        "chest_pain": "Cardiorespiratory concern requiring immediate attention",
        "difficulty_breathing": "Cardiorespiratory concern requiring immediate attention",
        "severe_abdominal_pain": "Possible placental abruption or complication",
        "heavy_bleeding": "Postpartum hemorrhage risk",
        "fever_over_38": "Possible infection (puerperal sepsis risk)",
        "seizures": "Eclampsia - life-threatening emergency",
        "loss_of_consciousness": "Critical emergency",
        "severe_swelling": "Possible preeclampsia indicator",
        "decreased_fetal_movement": "Fetal distress indicator",
        "water_breaking_early": "Preterm labor risk",
        "signs_of_infection": "Postnatal infection risk",
        "mental_health_crisis": "Postpartum depression or psychosis risk",
    }

    EMERGENCY_SIGNS = [
        "seizures", "loss_of_consciousness", "chest_pain",
        "difficulty_breathing", "heavy_bleeding", "severe_abdominal_pain"
    ]

    HIGH_RISK_SIGNS = [
        "severe_headache", "blurred_vision", "fever_over_38",
        "severe_swelling", "decreased_fetal_movement"
    ]

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
                    temperature=0.1
                )
                self._llm_available = True
                logger.info("Gemini LLM initialized for RiskAssessmentAgent")
        except Exception as e:
            logger.warning(f"LLM initialization failed (using rule-based fallback): {e}")

    async def assess(self, patient_data: Dict[str, Any]) -> RiskAssessmentResult:
        """Primary assessment method combining rule-based and AI analysis."""
        rule_result = self._rule_based_assessment(patient_data)
        ai_result = None

        if self._llm_available:
            try:
                ai_result = await self._llm_assessment(patient_data)
            except Exception as e:
                logger.error(f"AI assessment failed: {e}")

        return self._merge_results(rule_result, ai_result)

    def _rule_based_assessment(self, data: Dict[str, Any]) -> RiskAssessmentResult:
        symptoms = [s.get("symptom", "").lower().replace(" ", "_") if isinstance(s, dict) else str(s).lower().replace(" ", "_") for s in data.get("symptoms", [])]
        medical_history = [m.get("condition", "").lower() if isinstance(m, dict) else str(m).lower() for m in data.get("medical_history", [])]
        missed_appts = data.get("missed_appointments", 0)
        age = data.get("age", 25)
        pregnancy_week = data.get("pregnancy_week", 0)

        danger_signs_detected = []
        score = 0.0
        reasoning_parts = []

        for s in symptoms:
            if s in self.EMERGENCY_SIGNS:
                danger_signs_detected.append(s)
                score += 40
                reasoning_parts.append(f"EMERGENCY sign detected: {s}")
            elif s in self.HIGH_RISK_SIGNS:
                danger_signs_detected.append(s)
                score += 20
                reasoning_parts.append(f"High-risk sign detected: {s}")
            elif s in self.DANGER_SIGNS:
                danger_signs_detected.append(s)
                score += 10
                reasoning_parts.append(f"Danger sign detected: {s}")

        high_risk_conditions = ["preeclampsia", "gestational_diabetes", "placenta_previa",
                                 "previous_c_section", "multiple_pregnancy", "heart_disease",
                                 "hypertension", "diabetes", "thyroid_disorder", "anemia"]
        for condition in medical_history:
            for hrc in high_risk_conditions:
                if hrc in condition:
                    score += 15
                    reasoning_parts.append(f"High-risk condition: {condition}")
                    break

        if missed_appts > 2:
            score += 15
            reasoning_parts.append(f"Multiple missed appointments ({missed_appts})")
        elif missed_appts > 0:
            score += 5
            reasoning_parts.append(f"Missed appointments: {missed_appts}")

        if age > 35:
            score += 5
            reasoning_parts.append(f"Maternal age > 35 ({age})")
        elif age < 18:
            score += 10
            reasoning_parts.append(f"Adolescent mother (age {age})")

        if pregnancy_week and pregnancy_week < 37:
            score += 10
            reasoning_parts.append(f"Preterm pregnancy (week {pregnancy_week})")

        if data.get("is_postnatal", False):
            score += 5
            reasoning_parts.append("Postnatal period - increased monitoring required")

        emergency_signs_present = any(s in self.EMERGENCY_SIGNS for s in [sym.get("symptom", "").lower().replace(" ", "_") if isinstance(sym, dict) else str(sym).lower().replace(" ", "_") for sym in data.get("symptoms", [])])

        if emergency_signs_present or score >= 80:
            risk_level = "emergency"
        elif score >= 50:
            risk_level = "high"
        elif score >= 25:
            risk_level = "medium"
        else:
            risk_level = "low"

        score = min(score, 100.0)

        return RiskAssessmentResult(
            risk_level=risk_level,
            risk_score=score,
            recommendation=self._get_recommendation(risk_level, danger_signs_detected),
            confidence=0.85,
            requires_escalation=risk_level in ("high", "emergency"),
            requires_human_review=risk_level in ("medium", "high", "emergency"),
            reasoning="; ".join(reasoning_parts) if reasoning_parts else "No significant risk factors detected",
            danger_signs_detected=danger_signs_detected,
            recommended_actions=self._get_recommended_actions(risk_level, danger_signs_detected),
        )

    async def _llm_assessment(self, data: Dict[str, Any]) -> Optional[RiskAssessmentResult]:
        if not self._llm_available:
            return None
        try:
            prompt = f"""You are a maternal healthcare AI risk assessment specialist. Analyze this patient and return a JSON object with risk assessment.

Patient Data:
- Age: {data.get('age')}
- Pregnancy Week: {data.get('pregnancy_week')}
- Missed Appointments: {data.get('missed_appointments')}
- Symptoms: {json.dumps(data.get('symptoms', []))}
- Medical History: {json.dumps(data.get('medical_history', []))}
- Vital Signs: {json.dumps(data.get('vital_signs', []))}
- Delivery Type: {data.get('delivery_type', 'N/A')}
- Postnatal: {data.get('is_postnatal', False)}

Return valid JSON only with fields:
- risk_level (string: "low"/"medium"/"high"/"emergency")
- risk_score (float 0-100)
- recommendation (string)
- confidence (float 0-1)
- requires_escalation (boolean)
- requires_human_review (boolean)
- reasoning (string)
- danger_signs_detected (list of strings)
- recommended_actions (list of strings)
"""
            response = await self.llm.agenerate([[prompt]])
            text = response.generations[0][0].text.strip()
            text = text.replace("```json", "").replace("```", "").strip()
            result = json.loads(text)
            return RiskAssessmentResult(
                risk_level=result.get("risk_level", "low"),
                risk_score=float(result.get("risk_score", 0)),
                recommendation=result.get("recommendation", ""),
                confidence=float(result.get("confidence", 0.7)),
                requires_escalation=bool(result.get("requires_escalation", False)),
                requires_human_review=bool(result.get("requires_human_review", True)),
                reasoning=result.get("reasoning", ""),
                danger_signs_detected=result.get("danger_signs_detected", []),
                recommended_actions=result.get("recommended_actions", []),
            )
        except Exception as e:
            logger.error(f"LLM assessment parsing error: {e}")
            return None

    def _merge_results(self, rule_result: RiskAssessmentResult,
                       ai_result: Optional[RiskAssessmentResult]) -> RiskAssessmentResult:
        if ai_result is None:
            return rule_result

        merged_score = (rule_result.risk_score * 0.4 + ai_result.risk_score * 0.6)
        merged_level = self._determine_merged_level(merged_score, rule_result, ai_result)
        merged_confidence = max(rule_result.confidence, ai_result.confidence)

        all_danger = list(set(rule_result.danger_signs_detected + ai_result.danger_signs_detected))
        all_actions = list(dict.fromkeys(rule_result.recommended_actions + ai_result.recommended_actions))

        return RiskAssessmentResult(
            risk_level=merged_level,
            risk_score=round(merged_score, 1),
            recommendation=ai_result.recommendation if ai_result.confidence > rule_result.confidence else rule_result.recommendation,
            confidence=round(merged_confidence, 2),
            requires_escalation=merged_level in ("high", "emergency"),
            requires_human_review=merged_level in ("medium", "high", "emergency"),
            reasoning=f"Rule-based: {rule_result.reasoning} | AI: {ai_result.reasoning}",
            danger_signs_detected=all_danger,
            recommended_actions=all_actions,
        )

    def _determine_merged_level(self, score: float, rule: RiskAssessmentResult,
                                 ai: RiskAssessmentResult) -> str:
        if rule.risk_level == "emergency" or ai.risk_level == "emergency":
            return "emergency"
        if score >= 80:
            return "emergency"
        if score >= 50 or rule.risk_level == "high" or ai.risk_level == "high":
            return "high"
        if score >= 25 or rule.risk_level == "medium" or ai.risk_level == "medium":
            return "medium"
        return "low"

    def _get_recommendation(self, risk_level: str, danger_signs: List[str]) -> str:
        recommendations = {
            "emergency": "IMMEDIATE EMERGENCY ESCALATION REQUIRED. Activate emergency response protocol.",
            "high": "Urgent specialist referral needed. Schedule appointment within 24 hours.",
            "medium": "Schedule follow-up within 48 hours. Monitor symptoms closely.",
            "low": "Routine follow-up as scheduled. Continue standard postnatal care.",
        }
        return recommendations.get(risk_level, "Standard monitoring recommended.")

    def _get_recommended_actions(self, risk_level: str, danger_signs: List[str]) -> List[str]:
        actions = {
            "emergency": [
                "Call emergency services immediately",
                "Notify on-call obstetrician",
                "Prepare emergency transport",
                "Alert emergency department",
            ],
            "high": [
                "Refer to specialist within 24 hours",
                "Schedule urgent follow-up",
                "Notify care team lead",
                "Begin intensive monitoring",
            ],
            "medium": [
                "Schedule follow-up within 48 hours",
                "Provide symptom monitoring instructions",
                "Educate on warning signs",
            ],
            "low": [
                "Continue routine care schedule",
                "Provide health education materials",
                "Schedule next routine appointment",
            ],
        }
        return actions.get(risk_level, ["Continue standard care protocol"])


class RiskAssessmentCrew:
    """CrewAI-based multi-agent risk assessment team for comprehensive evaluation."""

    def __init__(self, gemini_api_key: Optional[str] = None):
        self.api_key = gemini_api_key
        self.agents = []
        self._init_crew()

    def _init_crew(self):
        try:
            from crewai import Agent, Task, Crew, Process

            self.symptom_analyzer = Agent(
                role="Symptom Analyst",
                goal="Analyze maternal symptoms for danger signs and risk indicators",
                backstory="Expert in maternal-fetal medicine with 15 years experience",
                verbose=False,
                allow_delegation=False,
            )

            self.history_reviewer = Agent(
                role="Medical History Reviewer",
                goal="Review patient medical history for risk factors",
                backstory="Specialist in obstetric medical history analysis",
                verbose=False,
                allow_delegation=False,
            )

            self.risk_classifier = Agent(
                role="Risk Classifier",
                goal="Classify overall maternal risk level based on all available data",
                backstory="Senior maternal-fetal medicine specialist",
                verbose=False,
                allow_delegation=True,
            )

            self.symptom_task = Task(
                description="Analyze reported symptoms and vital signs for danger signs",
                agent=self.symptom_analyzer,
                expected_output="List of detected danger signs and severity assessment",
            )

            self.history_task = Task(
                description="Review medical history for risk conditions",
                agent=self.history_reviewer,
                expected_output="Risk factor analysis from medical history",
            )

            self.classification_task = Task(
                description="Classify overall risk level and recommend actions",
                agent=self.risk_classifier,
                expected_output="Final risk classification with recommendations",
            )

            self.crew = Crew(
                agents=[self.symptom_analyzer, self.history_reviewer, self.risk_classifier],
                tasks=[self.symptom_task, self.history_task, self.classification_task],
                process=Process.sequential,
                verbose=False,
            )
            logger.info("CrewAI RiskAssessmentCrew initialized")
        except Exception as e:
            logger.warning(f"CrewAI initialization failed: {e}")
            self.crew = None
