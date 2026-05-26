# MaternaI CareFlow

AI-powered maternal healthcare coordination platform — built for **UiPath AgentHack 2026**.

MaternaI CareFlow orchestrates the full lifecycle of maternal/postnatal patient care: from registration and AI-driven risk assessment, through referral coordination and appointment scheduling, to emergency escalation workflows — all with **human-in-the-loop** approval gates.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.10+ / FastAPI / Uvicorn |
| Database | MongoDB (Motor + Beanie ODM) |
| AI/LLM | LangChain, Google Gemini Pro, CrewAI |
| Frontend | Next.js 14, React 18, TypeScript, Tailwind CSS, Recharts |
| Workflows | UiPath Maestro (BPMN 2.0) |
| Notifications | Twilio (SMS), SendGrid (Email) |
| License | MIT |
| Agent Type | Coded (Python + TypeScript, UiPath Maestro API integration) |

## Key Features

- **Patient Registration & Management** — Register mothers, track demographics, pregnancy details, medical history, vital signs, and symptoms.
- **AI Risk Assessment** — Hybrid rule-based + LLM (Gemini Pro) system with CrewAI multi-agent collaboration. Classifies patients into `low`, `medium`, `high`, or `emergency` risk levels.
- **Referral Coordination** — AI-powered facility matching. Full lifecycle: create, approve (human-in-the-loop), reject, assign worker, complete.
- **Appointment Scheduling** — Schedule, reschedule, cancel, confirm attendance. AI-suggested follow-up intervals. Multi-channel reminders (SMS/Email/In-app).
- **Emergency Escalation** — Real-time detection of critical symptoms. Automatic ambulance coordination and stakeholder notification with full audit trail.
- **Real-Time Analytics Dashboard** — Patient counts by risk, referral status, adherence metrics, risk trends, workflow performance, facility load.
- **BPMN Workflow Orchestration** — 6 BPMN 2.0 workflows for patient registration, risk evaluation, referral approval, appointment scheduling, emergency escalation, and follow-up monitoring.
- **Human-in-the-Loop** — All critical decisions require explicit human acknowledgment by designated roles (nurse, doctor, admin).

## Project Structure

```
maternaicareflow/
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI app entry, CORS, router includes
│   │   ├── config.py             # Pydantic settings (env vars)
│   │   ├── models/               # Beanie ODM documents (Patient, Referral, Appointment, Alert)
│   │   ├── schemas/              # Pydantic request/response schemas
│   │   ├── routers/              # Patients, Referrals, Appointments, Alerts, Analytics
│   │   ├── services/             # Workflow orchestrator, Notification service
│   │   └── agents/               # AI agents (Risk assessment, Referral, Scheduling, Emergency)
│   ├── .env.example
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   └── app/
│   │       ├── page.tsx          # Landing page
│   │       ├── dashboard/        # Clinical dashboard (Recharts)
│   │       ├── patients/         # Patient list & registration
│   │       ├── referrals/        # Referral list & actions
│   │       ├── appointments/     # Appointment management
│   │       └── alerts/           # Alerts & escalations
│   └── package.json
├── bpmn/
│   └── workflows.md              # BPMN 2.0 XML definitions
├── docs/
│   ├── api.md                    # Full REST API documentation
│   └── architecture.md           # System architecture & data flow
├── scripts/
│   ├── setup.sh                  # macOS/Linux setup
│   └── setup.ps1                 # Windows setup
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- MongoDB (local or Atlas)

### Backend Setup

```bash
cd backend
python -m venv venv
# Windows: .\venv\Scripts\Activate.ps1
# macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env    # Edit with your API keys
uvicorn app.main:app --reload
```

Backend runs on **http://localhost:8000** — interactive docs at `/docs`.

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on **http://localhost:3000**.

### Environment Variables (`.env`)

| Variable | Description |
|----------|-------------|
| `MONGODB_URI` | MongoDB connection string |
| `GEMINI_API_KEY` | Google Gemini Pro API key |
| `TWILIO_ACCOUNT_SID` | Twilio SMS account SID |
| `TWILIO_AUTH_TOKEN` | Twilio auth token |
| `TWILIO_PHONE_NUMBER` | Twilio sender phone number |
| `SENDGRID_API_KEY` | SendGrid email API key |
| `FROM_EMAIL` | Sender email address |
| `UIPATH_MAESTRO_API_URL` | UiPath Maestro API URL |
| `UIPATH_MAESTRO_API_KEY` | UiPath Maestro API key |

### Automated Setup

```bash
# macOS/Linux
bash scripts/setup.sh
# Windows PowerShell
.\scripts\setup.ps1
```

### API Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check |
| `GET/POST` | `/api/patients` | List / Register patients |
| `POST` | `/api/patients/{id}/symptoms` | Report symptom (triggers AI risk assessment) |
| `POST` | `/api/patients/{id}/vitals` | Record vital signs |
| `POST` | `/api/patients/{id}/assess-risk` | Run AI risk assessment |
| `GET/POST` | `/api/referrals` | List / Create referrals |
| `POST` | `/api/referrals/{id}/approve` | Approve referral (human-in-the-loop) |
| `GET/POST` | `/api/appointments` | List / Create appointments |
| `POST` | `/api/appointments/{id}/reschedule` | Reschedule appointment |
| `POST` | `/api/alerts/escalations` | Create emergency escalation |
| `GET` | `/api/analytics/dashboard` | Dashboard overview |

Full API documentation: `docs/api.md`

## Architecture

The system uses a hybrid AI architecture where deterministic rule-based engines and LLM-based agents (Gemini Pro via LangChain) work together. Results are merged with a weighted formula — every LLM integration falls back to rule-based logic if the API is unavailable. The UiPath Maestro workflow orchestrator similarly falls back to local simulation when the service is unreachable.

See `docs/architecture.md` for detailed component diagrams and data flow.
