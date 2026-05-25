# MaternAI CareFlow Architecture

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (Next.js)                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│  │Dashboard │ │Patients  │ │Referrals │ │Alerts    │        │
│  │ Page     │ │ Page     │ │ Page     │ │ Page     │        │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘        │
│       └──────────────┬──────────┴──────────────┘             │
│                      │ HTTP/REST                             │
└──────────────────────┼───────────────────────────────────────┘
                       │
┌──────────────────────┼───────────────────────────────────────┐
│              BACKEND (FastAPI - Python)                       │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                   API ROUTERS                           │  │
│  │  /api/patients  /api/referrals  /api/appointments       │  │
│  │  /api/alerts    /api/analytics  /api/workflows          │  │
│  └──────────────────────┬──────────────────────────────────┘  │
│                         │                                     │
│  ┌──────────────────────┼──────────────────────────────────┐  │
│  │              AI AGENT LAYER                              │  │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐           │  │
│  │  │   Risk     │ │  Referral  │ │Appointment │           │  │
│  │  │Assessment  │ │Coordinator │ │ Scheduler  │           │  │
│  │  └────────────┘ └────────────┘ └────────────┘           │  │
│  │  ┌────────────┐ ┌────────────────────────┐              │  │
│  │  │ Emergency  │ │   CrewAI Multi-Agent   │              │  │
│  │  │Escalation  │ │   Risk Assessment Team │              │  │
│  │  └────────────┘ └────────────────────────┘              │  │
│  └──────────────────────┬──────────────────────────────────┘  │
│                         │                                     │
│  ┌──────────────────────┼──────────────────────────────────┐  │
│  │            SERVICE LAYER                                 │  │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐          │  │
│  │  │Workflow    │ │Notification│ │  External  │          │  │
│  │  │Orchestrator│ │  Service   │ │   APIs     │          │  │
│  │  └────────────┘ └────────────┘ └────────────┘          │  │
│  └──────────────────────┬──────────────────────────────────┘  │
│                         │                                     │
│  ┌──────────────────────┼──────────────────────────────────┐  │
│  │              DATA LAYER (MongoDB)                        │  │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐          │  │
│  │  │  Patients  │ │  Referrals │ │Appointments│          │  │
│  │  └────────────┘ └────────────┘ └────────────┘          │  │
│  │  ┌────────────┐ ┌────────────┐                          │  │
│  │  │   Alerts   │ │Facilities  │                          │  │
│  │  └────────────┘ └────────────┘                          │  │
│  └─────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
                               │
┌──────────────────────────────┼───────────────────────────────┐
│                 UIPATH ECOSYSTEM                               │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐               │
│  │   Maestro  │ │   Agent    │ │    API     │               │
│  │Orchestrator│ │  Builder   │ │ Workflows  │               │
│  └────────────┘ └────────────┘ └────────────┘               │
└───────────────────────────────────────────────────────────────┘
```

## Component Description

### Frontend (Next.js + Tailwind CSS)
- **Dashboard**: Real-time analytics and monitoring
- **Patient Management**: Registration, risk assessment, timeline
- **Referral Coordination**: Create, approve, track referrals
- **Appointment Management**: Schedule, remind, confirm
- **Alert Center**: Emergency escalations and notifications

### Backend (Python FastAPI)
- **RESTful API**: Secure endpoints for all healthcare operations
- **Authentication**: Token-based API security
- **Validation**: Pydantic schema validation
- **Documentation**: Auto-generated OpenAPI/Swagger docs

### AI Agent Layer
- **LangChain**: Prompt chaining and LLM integration
- **CrewAI**: Multi-agent collaboration for risk assessment
- **Gemini CLI**: Google's generative AI integration
- **Rule Engine**: Deterministic fallback for reliability

### Data Layer (MongoDB via Beanie ODM)
- **Document Models**: Patient, Referral, Appointment, Alert, Escalation, Facility
- **Indexed Queries**: Optimized for healthcare workload
- **Schema Validation**: Beanie document validation

### UiPath Integration
- **Maestro**: BPMN workflow orchestration
- **Agent Builder**: Custom AI agent deployment
- **API Workflows**: REST integration points
- **Automation Cloud**: Enterprise deployment

## Security Architecture

| Layer | Security Measure |
|-------|-----------------|
| API | Token-based authentication, rate limiting |
| Data | MongoDB encrypted at rest, field-level encryption |
| Network | HTTPS, CORS configuration |
| Audit | Full action logging, audit trails |
| Compliance | HIPAA-compliant data handling |

## Key Integration Points

### REST API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/patients` | GET/POST | List/Create patients |
| `/api/patients/{id}/assess-risk` | POST | AI risk assessment |
| `/api/patients/{id}/symptoms` | POST | Report symptom |
| `/api/referrals` | GET/POST | List/Create referrals |
| `/api/referrals/{id}/approve` | POST | Human approval |
| `/api/appointments` | GET/POST | List/Create appointments |
| `/api/appointments/{id}/confirm-attendance` | POST | Attendance tracking |
| `/api/alerts/escalations` | GET | List escalations |
| `/api/alerts/escalations/{id}/acknowledge` | POST | Human acknowledgment |
| `/api/analytics/dashboard` | GET | Dashboard data |

## Data Flow Example: Emergency Escalation

```
1. Patient reports "severe headache" via frontend
2. POST /api/patients/{id}/symptoms
3. RiskAssessmentAgent.assess() → Rule + AI hybrid analysis
4. Risk level = "high", requires_escalation = true
5. EmergencyEscalationAgent.assess_emergency()
6. WorkflowOrchestrator.start_workflow("emergency_escalation")
7. Parallel execution:
   a. Ambulance dispatch (API call)
   b. Stakeholder notification (SMS/Email)
   c. Alert created in database
8. Human acknowledgment required (doctor)
9. POST /api/alerts/escalations/{id}/acknowledge
10. Resolution and documentation
```
