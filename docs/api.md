# MaternAI CareFlow API Documentation

## Base URL

```
http://localhost:8000
```

Interactive API docs available at `/docs` (Swagger UI) when the server is running.

---

## Authentication

All API requests require the `Authorization` header:

```
Authorization: Bearer <your-api-key>
```

---

## Endpoints

### Health Check

```http
GET /api/health
```

Response:
```json
{
  "status": "healthy",
  "service": "MaternAI CareFlow",
  "version": "1.0.0",
  "environment": "development"
}
```

### Patients

#### List Patients
```http
GET /api/patients?risk_level=high&skip=0&limit=50
```

#### Register Patient
```http
POST /api/patients
Content-Type: application/json

{
  "first_name": "Maria",
  "last_name": "Santos",
  "date_of_birth": "1996-03-15",
  "age": 28,
  "phone": "+1234567890",
  "email": "maria@example.com",
  "pregnancy_week": 34,
  "expected_delivery_date": "2026-06-20",
  "allergies": ["penicillin"]
}
```

#### Get Patient
```http
GET /api/patients/{patient_id}
```

#### Report Symptom
```http
POST /api/patients/{patient_id}/symptoms
Content-Type: application/json

{"symptom": "severe headache", "severity": "severe"}
```

Response includes AI risk assessment:
```json
{
  "patient_id": "PAT-...",
  "risk_assessment": {
    "risk_level": "high",
    "risk_score": 72.5,
    "recommendation": "Urgent specialist referral needed",
    "requires_escalation": true,
    "danger_signs_detected": ["severe_headache"],
    "recommended_actions": ["Refer to specialist within 24 hours"]
  }
}
```

#### Run AI Risk Assessment
```http
POST /api/patients/{patient_id}/assess-risk
```

#### Record Vital Signs
```http
POST /api/patients/{patient_id}/vitals
Content-Type: application/json

{
  "blood_pressure_systolic": 150,
  "blood_pressure_diastolic": 95,
  "heart_rate": 88,
  "temperature": 37.2,
  "oxygen_saturation": 97
}
```

#### Get Patient Timeline
```http
GET /api/patients/{patient_id}/timeline
```

### Referrals

#### List Facilities
```http
GET /api/referrals/facilities?facility_type=maternity_hospital
```

#### Create Referral
```http
POST /api/referrals
Content-Type: application/json

{
  "patient_id": "PAT-001",
  "referral_reason": "Preeclampsia monitoring",
  "priority": "high"
}
```

#### Approve Referral
```http
POST /api/referrals/{referral_id}/approve
Content-Type: application/json

{
  "approved_by": "dr-sarah-chen",
  "target_facility_id": "MAT-001"
}
```

#### Reject Referral
```http
POST /api/referrals/{referral_id}/reject
Content-Type: application/json

{
  "rejected_by": "dr-sarah-chen",
  "rejection_reason": "Insufficient specialist availability"
}
```

### Appointments

#### Create Appointment
```http
POST /api/appointments
Content-Type: application/json

{
  "patient_id": "PAT-001",
  "appointment_type": "High-Risk Follow-up",
  "facility_name": "St. Mary's Maternity Hospital",
  "scheduled_date": "2026-05-28T10:00:00Z",
  "healthcare_provider": "dr-jones"
}
```

#### Confirm Attendance
```http
POST /api/appointments/{appointment_id}/confirm-attendance?attended=true
```

#### Send Reminder
```http
POST /api/appointments/{appointment_id}/send-reminder
```

#### Get Analytics
```http
GET /api/appointments/analytics/overview
```

### Alerts & Escalations

#### Create Escalation
```http
POST /api/alerts/escalations?patient_id=PAT-001&description=Severe+postpartum+symptoms
```

#### List Escalations
```http
GET /api/alerts/escalations?status=open&severity=critical
```

#### Acknowledge Escalation (Human-in-the-Loop)
```http
POST /api/alerts/escalations/{escalation_id}/acknowledge?acknowledged_by=dr-sarah-chen
```

#### Approve Escalation
```http
POST /api/alerts/escalations/{escalation_id}/approve
Content-Type: application/json

{
  "approved_by": "dr-smith",
  "approve": true,
  "notes": "Emergency surgery prep initiated"
}
```

#### Resolve Escalation
```http
POST /api/alerts/escalations/{escalation_id}/resolve
Content-Type: application/json

{
  "resolved_by": "dr-sarah-chen",
  "resolution_notes": "Patient stabilized, transferred to ICU"
}
```

### Analytics

#### Dashboard Overview
```http
GET /api/analytics/dashboard
```

#### Risk Trends
```http
GET /api/analytics/risk-trends?days=30
```

#### Workflow Performance
```http
GET /api/analytics/workflow-performance
```

#### Facility Load
```http
GET /api/analytics/facility-load
```

---

## Error Responses

```json
{
  "detail": "Patient not found"
}
```

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 404 | Not Found |
| 409 | Conflict |
| 422 | Validation Error |
| 500 | Internal Server Error |

## Data Models

### Patient
```json
{
  "patient_id": "PAT-20260525123456-1234",
  "first_name": "Maria",
  "last_name": "Santos",
  "age": 28,
  "risk_level": "high",
  "risk_score": 65.0,
  "pregnancy_week": 34,
  "is_emergency": false,
  "missed_appointments": 2,
  "symptoms": [],
  "vital_signs": [],
  "created_at": "2026-05-25T00:00:00"
}
```

### Referral
```json
{
  "referral_id": "REF-20260525123456-1234",
  "patient_id": "PAT-001",
  "patient_name": "Maria Santos",
  "risk_level": "high",
  "status": "pending_approval",
  "target_facility_name": "St. Mary's Maternity Hospital",
  "ai_recommendation": "Best available maternity facility",
  "ai_confidence_score": 0.85,
  "is_emergency": false,
  "created_at": "2026-05-25T00:00:00"
}
```
