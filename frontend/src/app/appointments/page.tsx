'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { api, type Appointment } from '@/lib/api';
import { Calendar, ArrowLeft, Plus, Activity, CheckCircle, XCircle, Clock } from 'lucide-react';

const statusBadge: Record<string, string> = {
  scheduled: 'badge-pending', completed: 'badge-approved',
  missed: 'badge-emergency', cancelled: 'badge-medium', rescheduled: 'badge-medium',
};

export default function AppointmentsPage() {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    patient_id: '', appointment_type: 'Follow-up Visit', facility_name: '',
    scheduled_date: '', healthcare_provider: '',
  });

  useEffect(() => { loadAppointments(); }, []);

  async function loadAppointments() {
    try {
      setLoading(true);
      const result = await api.getAppointments();
      setAppointments(result);
    } catch {
      setAppointments(getMockAppointments());
    } finally {
      setLoading(false);
    }
  }

  function getMockAppointments(): Appointment[] {
    return [
      { appointment_id: 'APT-001', patient_id: 'PAT-001', patient_name: 'Maria Santos', appointment_type: 'High-Risk Follow-up', facility_name: 'St. Mary\'s Maternity Hospital', scheduled_date: new Date(Date.now() + 86400000).toISOString(), status: 'scheduled' },
      { appointment_id: 'APT-002', patient_id: 'PAT-002', patient_name: 'Jane Doe', appointment_type: 'Emergency Check', facility_name: 'State University Teaching Hospital', scheduled_date: new Date().toISOString(), status: 'completed', attended: true },
      { appointment_id: 'APT-003', patient_id: 'PAT-003', patient_name: 'Sarah Johnson', appointment_type: 'Routine Postnatal', facility_name: 'City Women\'s Health Center', scheduled_date: new Date(Date.now() - 86400000).toISOString(), status: 'missed', attended: false },
      { appointment_id: 'APT-004', patient_id: 'PAT-004', patient_name: 'Amara Okafor', appointment_type: 'Follow-up Visit', facility_name: 'Riverside Community Clinic', scheduled_date: new Date(Date.now() + 172800000).toISOString(), status: 'scheduled' },
    ];
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    try {
      await api.createAppointment({ ...formData, scheduled_date: new Date(formData.scheduled_date).toISOString() });
      setShowForm(false);
      loadAppointments();
    } catch { alert('Appointment created (mock)'); setShowForm(false); }
  }

  async function handleAttendance(id: string, attended: boolean) {
    try {
      await api.confirmAttendance(id, attended);
      loadAppointments();
    } catch { alert(`Attendance ${attended ? 'confirmed' : 'marked missed'} (mock)`); }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 px-4 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href="/dashboard" className="text-gray-500 hover:text-gray-700"><ArrowLeft className="h-5 w-5" /></Link>
          <h1 className="text-lg font-semibold">Appointments</h1>
        </div>
        <button onClick={() => setShowForm(!showForm)} className="btn-primary text-sm flex items-center gap-2">
          <Plus className="h-4 w-4" /> Schedule
        </button>
      </header>

      <main className="p-4 lg:p-8 max-w-7xl mx-auto">
        {showForm && (
          <form onSubmit={handleSubmit} className="stat-card mb-6">
            <h3 className="font-semibold mb-4">Schedule Appointment</h3>
            <div className="grid md:grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Patient ID</label>
                <input className="input-field" required value={formData.patient_id} onChange={e => setFormData({...formData, patient_id: e.target.value})} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
                <select className="input-field" value={formData.appointment_type} onChange={e => setFormData({...formData, appointment_type: e.target.value})}>
                  <option>Follow-up Visit</option>
                  <option>Emergency Check</option>
                  <option>Routine Postnatal</option>
                  <option>High-Risk Follow-up</option>
                  <option>Specialist Referral</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Facility</label>
                <input className="input-field" required value={formData.facility_name} onChange={e => setFormData({...formData, facility_name: e.target.value})} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Date & Time</label>
                <input className="input-field" type="datetime-local" required value={formData.scheduled_date} onChange={e => setFormData({...formData, scheduled_date: e.target.value})} />
              </div>
            </div>
            <div className="flex gap-3">
              <button type="submit" className="btn-primary">Schedule</button>
              <button type="button" onClick={() => setShowForm(false)} className="btn-secondary">Cancel</button>
            </div>
          </form>
        )}

        {loading ? (
          <div className="flex items-center justify-center py-12"><Activity className="h-6 w-6 text-primary-500 animate-spin" /></div>
        ) : (
          <div className="space-y-4">
            {appointments.map((apt) => (
              <div key={apt.appointment_id} className="stat-card">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="font-mono text-xs text-gray-400">{apt.appointment_id}</span>
                      <span className={`badge ${statusBadge[apt.status] || 'badge-pending'}`}>{apt.status}</span>
                    </div>
                    <h3 className="font-semibold">{apt.patient_name}</h3>
                    <p className="text-sm text-gray-600">{apt.appointment_type}</p>
                    <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                      <span className="flex items-center gap-1"><Calendar className="h-3 w-3" /> {new Date(apt.scheduled_date).toLocaleDateString()}</span>
                      <span className="flex items-center gap-1"><Clock className="h-3 w-3" /> {new Date(apt.scheduled_date).toLocaleTimeString()}</span>
                      <span>{apt.facility_name}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 ml-4">
                    {apt.status === 'scheduled' && (
                      <>
                        <button onClick={() => handleAttendance(apt.appointment_id, true)} className="btn-primary text-xs flex items-center gap-1">
                          <CheckCircle className="h-3 w-3" /> Attended
                        </button>
                        <button onClick={() => handleAttendance(apt.appointment_id, false)} className="btn-secondary text-xs flex items-center gap-1">
                          <XCircle className="h-3 w-3" /> Missed
                        </button>
                      </>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
