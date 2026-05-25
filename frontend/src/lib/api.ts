const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const error = await res.text();
    throw new Error(`API Error ${res.status}: ${error}`);
  }
  return res.json();
}

export interface Patient {
  patient_id: string;
  first_name: string;
  last_name: string;
  age: number;
  risk_level: string;
  risk_score: number;
  phone?: string;
  email?: string;
  pregnancy_week?: number;
  is_emergency: boolean;
  is_active: boolean;
  missed_appointments: number;
  created_at: string;
}

export interface Referral {
  referral_id: string;
  patient_id: string;
  patient_name: string;
  risk_level: string;
  referral_reason: string;
  status: string;
  target_facility_name?: string;
  priority: string;
  is_emergency: boolean;
  created_at: string;
}

export interface Appointment {
  appointment_id: string;
  patient_id: string;
  patient_name: string;
  appointment_type: string;
  facility_name: string;
  scheduled_date: string;
  status: string;
  attended?: boolean;
}

export interface Escalation {
  escalation_id: string;
  patient_id: string;
  patient_name: string;
  severity: string;
  status: string;
  description: string;
  created_at: string;
}

export interface DashboardData {
  summary: {
    total_patients: number;
    high_risk_patients: number;
    emergency_patients: number;
    total_referrals: number;
    pending_referrals: number;
    missed_appointments: number;
    open_escalations: number;
  };
  risk_distribution: Record<string, number>;
  referral_status: Record<string, number>;
  appointment_metrics: Record<string, number>;
  recent_alerts: Array<{
    alert_id: string;
    patient_name: string;
    severity: string;
    message: string;
    created_at: string;
  }>;
}

export const api = {
  // Patients
  getPatients: (params?: Record<string, string>) =>
    fetchAPI<Patient[]>(`/api/patients?${new URLSearchParams(params)}`),
  getPatient: (id: string) => fetchAPI<Patient>(`/api/patients/${id}`),
  createPatient: (data: Record<string, unknown>) =>
    fetchAPI<Patient>('/api/patients', { method: 'POST', body: JSON.stringify(data) }),
  assessRisk: (id: string) =>
    fetchAPI<{ assessment: Record<string, unknown> }>(`/api/patients/${id}/assess-risk`, { method: 'POST' }),
  reportSymptom: (id: string, symptom: string, severity: string) =>
    fetchAPI<Record<string, unknown>>(`/api/patients/${id}/symptoms`, {
      method: 'POST',
      body: JSON.stringify({ symptom, severity }),
    }),

  // Referrals
  getReferrals: (params?: Record<string, string>) =>
    fetchAPI<Referral[]>(`/api/referrals?${new URLSearchParams(params)}`),
  createReferral: (data: Record<string, unknown>) =>
    fetchAPI<Referral>('/api/referrals', { method: 'POST', body: JSON.stringify(data) }),
  approveReferral: (id: string, approvedBy: string, facilityId: string) =>
    fetchAPI<Referral>(`/api/referrals/${id}/approve`, {
      method: 'POST',
      body: JSON.stringify({ approved_by: approvedBy, target_facility_id: facilityId }),
    }),

  // Appointments
  getAppointments: (params?: Record<string, string>) =>
    fetchAPI<Appointment[]>(`/api/appointments?${new URLSearchParams(params)}`),
  createAppointment: (data: Record<string, unknown>) =>
    fetchAPI<Appointment>('/api/appointments', { method: 'POST', body: JSON.stringify(data) }),
  confirmAttendance: (id: string, attended: boolean) =>
    fetchAPI<Appointment>(`/api/appointments/${id}/confirm-attendance?attended=${attended}`, { method: 'POST' }),

  // Escalations
  getEscalations: (params?: Record<string, string>) =>
    fetchAPI<Escalation[]>(`/api/alerts/escalations?${new URLSearchParams(params)}`),
  acknowledgeEscalation: (id: string, user: string) =>
    fetchAPI<Escalation>(`/api/alerts/escalations/${id}/acknowledge?acknowledged_by=${user}`, { method: 'POST' }),

  // Analytics
  getDashboard: () => fetchAPI<DashboardData>('/api/analytics/dashboard'),
};
