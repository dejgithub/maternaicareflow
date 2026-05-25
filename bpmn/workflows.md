# MaternAI CareFlow — BPMN Workflow Definitions

This document describes the BPMN 2.0 workflows designed for the MaternAI CareFlow platform.
Each workflow orchestrates humans, AI agents, APIs, and automation within UiPath Maestro.

---

## 1. Patient Registration Workflow

**BPMN Process ID:** `patient_registration`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL"
  xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI"
  targetNamespace="http://maternaicareflow.ai/bpmn">

  <bpmn:process id="patient_registration" name="Patient Registration">
    <bpmn:startEvent id="start" name="Patient Arrives" />
    <bpmn:userTask id="collect_info" name="Collect Patient Information">
      <bpmn:humanPerformer><bpmn:resourceAssignmentExpression>
        <bpmn:formalExpression>Nurse</bpmn:formalExpression>
      </bpmn:resourceAssignmentExpression></bpmn:humanPerformer>
    </bpmn:userTask>
    <bpmn:serviceTask id="check_duplicate" name="Check Duplicate Records"
      implementation="##WebService" />
    <bpmn:scriptTask id="generate_id" name="Generate Case ID" />
    <bpmn:serviceTask id="ai_screening" name="AI Initial Risk Screening"
      implementation="##WebService" />
    <bpmn:serviceTask id="assign_facility" name="Assign Facility & Staff"
      implementation="##WebService" />
    <bpmn:serviceTask id="notify_patient" name="Notify Patient"
      implementation="##WebService" />
    <bpmn:serviceTask id="create_care_plan" name="Create Care Plan"
      implementation="##WebService" />
    <bpmn:endEvent id="end" name="Registration Complete" />

    <bpmn:sequenceFlow from="start" to="collect_info" />
    <bpmn:sequenceFlow from="collect_info" to="check_duplicate" />
    <bpmn:sequenceFlow from="check_duplicate" to="generate_id" />
    <bpmn:sequenceFlow from="generate_id" to="ai_screening" />
    <bpmn:sequenceFlow from="ai_screening" to="assign_facility" />
    <bpmn:sequenceFlow from="assign_facility" to="notify_patient" />
    <bpmn:sequenceFlow from="notify_patient" to="create_care_plan" />
    <bpmn:sequenceFlow from="create_care_plan" to="end" />
  </bpmn:process>
</bpmn:definitions>
```

**Workflow Steps:**

| Step | Type | Description |
|------|------|-------------|
| Collect Information | Human (Nurse) | Enter patient demographic and medical data |
| Check Duplicates | API | Verify against existing records |
| Generate Case ID | Automation | Create unique patient identifier |
| AI Risk Screening | AI Agent | LangChain agent analyzes initial risk factors |
| Assign Facility | AI Agent | Determine optimal healthcare facility |
| Notify Patient | Automation | Multi-channel welcome & instructions |
| Create Care Plan | AI Agent | Generate personalized postnatal care plan |

**Exception Handling:**
- Duplicate found → Merge records workflow triggered
- Incomplete data → Escalate to nurse supervisor

---

## 2. Risk Evaluation Workflow

**BPMN Process ID:** `risk_evaluation`

```xml
<bpmn:process id="risk_evaluation" name="Risk Evaluation">
  <bpmn:startEvent id="start" name="Trigger: Symptom Reported" />
  <bpmn:serviceTask id="collect_data" name="Gather Patient Data"
    implementation="##WebService" />
  <bpmn:serviceTask id="symptom_analysis" name="AI Symptom Analysis"
    implementation="##WebService" />
  <bpmn:serviceTask id="history_review" name="AI History Review"
    implementation="##WebService" />
  <bpmn:scriptTask id="classify_risk" name="Classify Risk Level" />
  <bpmn:exclusiveGateway id="risk_gateway" name="Risk Level?" />
  <bpmn:userTask id="human_review" name="Human Review Required">
    <bpmn:humanPerformer><bpmn:resourceAssignmentExpression>
      <bpmn:formalExpression>Doctor</bpmn:formalExpression>
    </bpmn:resourceAssignmentExpression></bpmn:humanPerformer>
  </bpmn:userTask>
  <bpmn:serviceTask id="update_record" name="Update Patient Record"
    implementation="##WebService" />
  <bpmn:serviceTask id="trigger_escalation" name="Trigger Escalation"
    implementation="##WebService" />
  <bpmn:endEvent id="end" name="Evaluation Complete" />

  <bpmn:sequenceFlow from="start" to="collect_data" />
  <bpmn:sequenceFlow from="collect_data" to="symptom_analysis" />
  <bpmn:sequenceFlow from="symptom_analysis" to="history_review" />
  <bpmn:sequenceFlow from="history_review" to="classify_risk" />
  <bpmn:sequenceFlow from="classify_risk" to="risk_gateway" />
  <bpmn:sequenceFlow from="risk_gateway" to="human_review">
    <bpmn:conditionExpression>riskLevel == 'high' || riskLevel == 'medium'</bpmn:conditionExpression>
  </bpmn:sequenceFlow>
  <bpmn:sequenceFlow from="risk_gateway" to="update_record">
    <bpmn:conditionExpression>riskLevel == 'low'</bpmn:conditionExpression>
  </bpmn:sequenceFlow>
  <bpmn:sequenceFlow from="human_review" to="update_record" />
  <bpmn:sequenceFlow from="update_record" to="trigger_escalation">
    <bpmn:conditionExpression>riskLevel == 'high' || riskLevel == 'emergency'</bpmn:conditionExpression>
  </bpmn:sequenceFlow>
  <bpmn:sequenceFlow from="update_record" to="end">
    <bpmn:conditionExpression>riskLevel == 'low' || riskLevel == 'medium'</bpmn:conditionExpression>
  </bpmn:sequenceFlow>
  <bpmn:sequenceFlow from="trigger_escalation" to="end" />
</bpmn:process>
```

**Decision Matrix:**

| Condition | Action |
|-----------|--------|
| Low Risk | Auto-update record, routine follow-up |
| Medium Risk | Human review required, schedule follow-up |
| High Risk | Human review + escalation to specialist |
| Emergency | Immediate escalation, trigger emergency protocol |

---

## 3. Referral Approval Workflow

**BPMN Process ID:** `referral_approval`

**Workflow Steps:**

1. **Generate Referral** (AI Agent) — Coordinator agent creates referral document
2. **Find Matching Facility** (AI Agent) — Check facility availability and specialization
3. **Check Service Availability** (API) — Real-time capacity check
4. **Route for Human Approval** (Human Task) — Assign to appropriate reviewer
5. **Approve or Reject** (Human Decision) — Doctor/Admin makes decision
6. **Notify Stakeholders** (Automation) — Multi-channel notifications
7. **Schedule Follow-up** (AI Agent) — Auto-schedule next appointment

**Human-in-the-Loop Gates:**
- High-risk referrals require doctor approval
- Emergency referrals require immediate administrator override
- All referrals have 48-hour SLA for approval

---

## 4. Appointment Scheduling Workflow

**BPMN Process ID:** `appointment_scheduling`

**Workflow Steps:**

1. **Determine Follow-up Interval** (AI Agent) — Based on risk level
2. **Check Provider Availability** (API) — Calendar integration
3. **Schedule Appointment** (Automation) — Create calendar entry
4. **Send Confirmation** (Automation) — Patient notification
5. **Schedule Reminders** (Automation) — 72h, 24h, 2h before
6. **Monitor Attendance** (Automation) — Check-in verification
7. **Handle Missed Appointment** (Workflow) — Re-engagement process

**Exception Handling:**
- Provider unavailable → Find alternative, notify patient
- Patient no-show → Trigger re-engagement workflow, increment missed counter
- Multiple misses → Escalate to social worker

---

## 5. Emergency Escalation Workflow

**BPMN Process ID:** `emergency_escalation`

**Workflow Steps:**

1. **Detect Emergency Symptoms** (AI Agent) — Real-time symptom monitoring
2. **Assess Severity** (AI Agent) — EmergencyResponse assessment
3. **Trigger Emergency Protocol** (Workflow) — Parallel execution branch
4. **Dispatch Ambulance** (API) — Emergency services integration
5. **Notify Emergency Staff** (Automation) — Multi-channel alert
6. **Human Review & Confirmation** (Human Task) — Doctor acknowledgment
7. **Document Intervention** (Automation) — Record all actions

**Parallel Branches:**
- **Branch A:** Patient care coordination (ambulance, hospital prep)
- **Branch B:** Stakeholder notification (family, primary doctor)
- **Branch C:** Documentation (legal, clinical records)

**Exception Escalation:**
- Unacknowledged alert after 5 minutes → Escalate to medical director
- Ambulance unavailable → Activate backup transport protocol
- System failure → Manual override with SMS fallback

---

## 6. Follow-up Monitoring Workflow

**BPMN Process ID:** `follow_up_monitoring`

**Workflow Steps:**

1. **Check Appointment Adherence** (Automation) — Verify attendance
2. **Analyze Patient Progress** (AI Agent) — Trend analysis
3. **Detect Missed Follow-ups** (AI Agent) — Pattern detection
4. **Trigger Re-engagement** (Workflow) — Outreach process
5. **Update Risk Assessment** (AI Agent) — Recalculate risk score
6. **Escalate if Deteriorating** (Workflow) — Risk-based escalation

**Monitoring Metrics:**
- Appointment adherence rate
- Symptom progression/regression
- Medication compliance
- Vital sign trends
- Risk score changes over time

---

## BPMN Diagram Visual Representation

The BPMN 2.0 XML above can be imported into:

- **UiPath Maestro** — Direct BPMN import and execution
- **Camunda Modeler** — Visual BPMN editing
- **BPMN.io** — Online BPMN viewer and editor
- **Signavio** — Enterprise BPMN modeling

### Workflow Orchestration Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    UIPATH MAESTRO                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Patient  │  │  Risk    │  │ Referral │  │Emergency │  │
│  │Register  │─▶│Evaluate  │─▶│ Approve  │─▶│Escalate  │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
│        │             │             │             │         │
│        ▼             ▼             ▼             ▼         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              AI AGENT ORCHESTRATION                   │  │
│  │  [Risk Agent] [Coordinator] [Scheduler] [Escalation]  │  │
│  └──────────────────────────────────────────────────────┘  │
│        │             │             │             │         │
│        ▼             ▼             ▼             ▼         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           HUMAN APPROVAL GATES                        │  │
│  │  [Nurse Review] [Doctor Approval] [Admin Confirm]     │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```
