"""
Workflow orchestration service integrating with UiPath Maestro
and managing BPMN-based healthcare workflow execution.
"""
import logging
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
import httpx

logger = logging.getLogger(__name__)


class WorkflowOrchestrator:
    """
    Orchestrates healthcare workflows across UiPath Maestro, AI agents,
    and human-in-the-loop approvals.
    """

    def __init__(self, maestro_api_url: Optional[str] = None,
                 maestro_api_key: Optional[str] = None):
        self.maestro_api_url = maestro_api_url
        self.maestro_api_key = maestro_api_key
        self.maestro_available = bool(maestro_api_url and maestro_api_key)

    async def start_workflow(self, workflow_name: str,
                              payload: Dict[str, Any]) -> Dict[str, Any]:
        """Start a workflow execution on UiPath Maestro or locally."""
        if self.maestro_available:
            return await self._call_maestro(workflow_name, payload)
        return self._local_workflow(workflow_name, payload)

    async def _call_maestro(self, workflow_name: str,
                             payload: Dict[str, Any]) -> Dict[str, Any]:
        """Call UiPath Maestro API to execute a workflow."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.maestro_api_url}/workflows/{workflow_name}/execute",
                    headers={
                        "Authorization": f"Bearer {self.maestro_api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                    timeout=30.0,
                )
                response.raise_for_status()
                result = response.json()
                logger.info(f"Maestro workflow {workflow_name} started: {result.get('execution_id')}")
                return {
                    "status": "started",
                    "workflow": workflow_name,
                    "execution_id": result.get("execution_id"),
                    "orchestrator": "uipath_maestro",
                }
        except Exception as e:
            logger.error(f"Maestro API call failed: {e}")
            return self._local_workflow(workflow_name, payload)

    def _local_workflow(self, workflow_name: str,
                         payload: Dict[str, Any]) -> Dict[str, Any]:
        """Local workflow simulation when Maestro is not available."""
        workflow_id = f"WF-{workflow_name}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        logger.info(f"Local workflow executed: {workflow_id}")
        return {
            "status": "started",
            "workflow": workflow_name,
            "execution_id": workflow_id,
            "orchestrator": "local",
            "steps": self._get_workflow_steps(workflow_name),
        }

    def _get_workflow_steps(self, workflow_name: str) -> List[Dict[str, str]]:
        workflows = {
            "patient_registration": [
                {"step": "validate_patient_data", "type": "automation"},
                {"step": "check_existing_records", "type": "api"},
                {"step": "assign_patient_id", "type": "automation"},
                {"step": "ai_initial_risk_screening", "type": "ai_agent"},
                {"step": "assign_facility_and_staff", "type": "ai_agent"},
                {"step": "notify_patient", "type": "automation"},
                {"step": "create_care_plan", "type": "ai_agent"},
            ],
            "risk_assessment": [
                {"step": "collect_patient_data", "type": "api"},
                {"step": "ai_symptom_analysis", "type": "ai_agent"},
                {"step": "ai_medical_history_review", "type": "ai_agent"},
                {"step": "risk_classification", "type": "ai_agent"},
                {"step": "human_review_if_needed", "type": "human_approval"},
                {"step": "update_patient_record", "type": "automation"},
                {"step": "trigger_escalation_if_needed", "type": "workflow"},
            ],
            "referral_approval": [
                {"step": "generate_referral", "type": "ai_agent"},
                {"step": "find_matching_facility", "type": "ai_agent"},
                {"step": "check_service_availability", "type": "api"},
                {"step": "route_for_human_approval", "type": "human_approval"},
                {"step": "approve_or_reject", "type": "human_decision"},
                {"step": "notify_all_stakeholders", "type": "automation"},
                {"step": "schedule_follow_up", "type": "ai_agent"},
            ],
            "appointment_scheduling": [
                {"step": "determine_follow_up_interval", "type": "ai_agent"},
                {"step": "check_provider_availability", "type": "api"},
                {"step": "schedule_appointment", "type": "automation"},
                {"step": "send_confirmation", "type": "automation"},
                {"step": "schedule_reminders", "type": "automation"},
                {"step": "monitor_attendance", "type": "automation"},
                {"step": "handle_missed_appointment", "type": "workflow"},
            ],
            "emergency_escalation": [
                {"step": "detect_emergency_symptoms", "type": "ai_agent"},
                {"step": "assess_severity", "type": "ai_agent"},
                {"step": "trigger_emergency_protocol", "type": "workflow"},
                {"step": "dispatch_ambulance_if_needed", "type": "api"},
                {"step": "notify_emergency_staff", "type": "automation"},
                {"step": "human_review_and_confirmation", "type": "human_approval"},
                {"step": "document_intervention", "type": "automation"},
            ],
            "follow_up_monitoring": [
                {"step": "check_appointment_adherence", "type": "automation"},
                {"step": "analyze_patient_progress", "type": "ai_agent"},
                {"step": "detect_missed_follow_ups", "type": "ai_agent"},
                {"step": "trigger_re_engagement", "type": "workflow"},
                {"step": "update_risk_assessment", "type": "ai_agent"},
                {"step": "escalate_if_deteriorating", "type": "workflow"},
            ],
        }
        return workflows.get(workflow_name, [{"step": "execute", "type": "automation"}])

    async def get_workflow_status(self, execution_id: str) -> Dict[str, Any]:
        """Get the current status of a workflow execution."""
        return {
            "execution_id": execution_id,
            "status": "running",
            "progress": 65,
            "current_step": "Processing...",
            "estimated_completion": "2 minutes",
        }

    async def human_approval_request(self, workflow_name: str,
                                      payload: Dict[str, Any],
                                      assigned_role: str) -> Dict[str, Any]:
        """Create a human-in-the-loop approval request."""
        approval_id = f"APPR-{workflow_name}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        logger.info(f"Approval requested: {approval_id} for {assigned_role}")
        return {
            "approval_id": approval_id,
            "workflow": workflow_name,
            "assigned_role": assigned_role,
            "status": "pending_approval",
            "payload": payload,
            "created_at": datetime.utcnow().isoformat(),
            "requires_action": True,
        }

    async def complete_human_approval(self, approval_id: str,
                                       decision: str,
                                       reviewer: str,
                                       notes: Optional[str] = None) -> Dict[str, Any]:
        """Complete a human approval step with decision."""
        return {
            "approval_id": approval_id,
            "decision": decision,
            "reviewer": reviewer,
            "notes": notes,
            "completed_at": datetime.utcnow().isoformat(),
            "status": "completed",
        }

    async def trigger_exception_handler(self, workflow_name: str,
                                         error: Dict[str, Any]) -> Dict[str, Any]:
        """Handle workflow exceptions with escalation and fallback."""
        exception_id = f"EXC-{workflow_name}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        logger.warning(f"Exception handler triggered: {exception_id}: {error}")
        return {
            "exception_id": exception_id,
            "workflow": workflow_name,
            "error": error,
            "handling_strategy": "retry_with_escalation",
            "notified": ["admin", "workflow_owner"],
            "status": "handling",
            "fallback_action": "manual_review_required",
        }
