'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { api, type Patient } from '@/lib/api';
import { Users, Plus, Search, Activity, ArrowLeft } from 'lucide-react';

const riskBadge: Record<string, string> = {
  low: 'badge-low', medium: 'badge-medium', high: 'badge-high', emergency: 'badge-emergency',
};

export default function PatientsPage() {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    first_name: '', last_name: '', age: 25, phone: '', email: '',
    pregnancy_week: '', date_of_birth: '',
  });

  useEffect(() => { loadPatients(); }, []);

  async function loadPatients() {
    try {
      setLoading(true);
      const result = await api.getPatients();
      setPatients(result);
    } catch {
      setPatients(getMockPatients());
    } finally {
      setLoading(false);
    }
  }

  function getMockPatients(): Patient[] {
    return [
      { patient_id: 'PAT-001', first_name: 'Maria', last_name: 'Santos', age: 28, risk_level: 'high', risk_score: 65, pregnancy_week: 34, is_emergency: false, is_active: true, missed_appointments: 2, created_at: new Date().toISOString() },
      { patient_id: 'PAT-002', first_name: 'Jane', last_name: 'Doe', age: 32, risk_level: 'emergency', risk_score: 88, pregnancy_week: 28, is_emergency: true, is_active: true, missed_appointments: 3, created_at: new Date().toISOString() },
      { patient_id: 'PAT-003', first_name: 'Sarah', last_name: 'Johnson', age: 25, risk_level: 'low', risk_score: 15, pregnancy_week: 20, is_emergency: false, is_active: true, missed_appointments: 0, created_at: new Date().toISOString() },
      { patient_id: 'PAT-004', first_name: 'Amara', last_name: 'Okafor', age: 30, risk_level: 'medium', risk_score: 35, is_emergency: false, is_active: true, missed_appointments: 1, created_at: new Date().toISOString() },
      { patient_id: 'PAT-005', first_name: 'Lisa', last_name: 'Chen', age: 35, risk_level: 'high', risk_score: 72, pregnancy_week: 36, is_emergency: false, is_active: true, missed_appointments: 4, created_at: new Date().toISOString() },
    ];
  }

  const filtered = patients.filter(p =>
    `${p.first_name} ${p.last_name}`.toLowerCase().includes(search.toLowerCase()) ||
    p.patient_id.toLowerCase().includes(search.toLowerCase())
  );

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    try {
      await api.createPatient({
        ...formData,
        date_of_birth: formData.date_of_birth || '1995-01-01',
        pregnancy_week: formData.pregnancy_week ? parseInt(formData.pregnancy_week) : undefined,
      });
      setShowForm(false);
      loadPatients();
    } catch (err) {
      alert('Patient registered (mock)');
      setShowForm(false);
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 px-4 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href="/dashboard" className="text-gray-500 hover:text-gray-700"><ArrowLeft className="h-5 w-5" /></Link>
          <h1 className="text-lg font-semibold">Patient Management</h1>
        </div>
        <button onClick={() => setShowForm(!showForm)} className="btn-primary text-sm flex items-center gap-2">
          <Plus className="h-4 w-4" /> Register Patient
        </button>
      </header>

      <main className="p-4 lg:p-8 max-w-7xl mx-auto">
        {showForm && (
          <form onSubmit={handleSubmit} className="stat-card mb-6">
            <h3 className="font-semibold mb-4">Register New Patient</h3>
            <div className="grid md:grid-cols-3 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">First Name</label>
                <input className="input-field" required value={formData.first_name} onChange={e => setFormData({...formData, first_name: e.target.value})} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
                <input className="input-field" required value={formData.last_name} onChange={e => setFormData({...formData, last_name: e.target.value})} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Age</label>
                <input className="input-field" type="number" required value={formData.age} onChange={e => setFormData({...formData, age: parseInt(e.target.value) || 0})} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                <input className="input-field" value={formData.phone} onChange={e => setFormData({...formData, phone: e.target.value})} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                <input className="input-field" type="email" value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Pregnancy Week</label>
                <input className="input-field" type="number" value={formData.pregnancy_week} onChange={e => setFormData({...formData, pregnancy_week: e.target.value})} />
              </div>
            </div>
            <div className="flex gap-3">
              <button type="submit" className="btn-primary">Register</button>
              <button type="button" onClick={() => setShowForm(false)} className="btn-secondary">Cancel</button>
            </div>
          </form>
        )}

        <div className="stat-card mb-6">
          <div className="flex items-center gap-3">
            <Search className="h-5 w-5 text-gray-400" />
            <input
              className="input-field border-0 bg-gray-50"
              placeholder="Search patients by name or ID..."
              value={search}
              onChange={e => setSearch(e.target.value)}
            />
          </div>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-12"><Activity className="h-6 w-6 text-primary-500 animate-spin" /></div>
        ) : (
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-100 bg-gray-50">
                    <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Patient ID</th>
                    <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Name</th>
                    <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Age</th>
                    <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Risk Level</th>
                    <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Risk Score</th>
                    <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Pregnancy</th>
                    <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Missed</th>
                    <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((p) => (
                    <tr key={p.patient_id} className="border-b border-gray-50 hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4 text-sm font-mono text-gray-500">{p.patient_id}</td>
                      <td className="px-6 py-4 text-sm font-medium">{p.first_name} {p.last_name}</td>
                      <td className="px-6 py-4 text-sm">{p.age}</td>
                      <td className="px-6 py-4"><span className={`badge ${riskBadge[p.risk_level] || 'badge-medium'}`}>{p.risk_level}</span></td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <div className="h-2 bg-gray-100 rounded-full w-20 overflow-hidden">
                            <div className={`h-full rounded-full ${p.risk_score > 70 ? 'bg-red-500' : p.risk_score > 40 ? 'bg-orange-500' : p.risk_score > 20 ? 'bg-yellow-500' : 'bg-green-500'}`}
                              style={{ width: `${p.risk_score}%` }} />
                          </div>
                          <span className="text-xs text-gray-500">{p.risk_score}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-sm">{p.pregnancy_week ? `Week ${p.pregnancy_week}` : 'N/A'}</td>
                      <td className="px-6 py-4 text-sm">{p.missed_appointments}</td>
                      <td className="px-6 py-4">
                        {p.is_emergency ? (
                          <span className="badge badge-emergency flex items-center gap-1 w-fit">
                            <Activity className="h-3 w-3" /> Emergency
                          </span>
                        ) : (
                          <span className="badge badge-completed">{p.is_active === false ? 'Inactive' : 'Active'}</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {filtered.length === 0 && (
              <div className="text-center py-12 text-gray-500">
                <Users className="h-12 w-12 mx-auto mb-3 text-gray-300" />
                <p>No patients found</p>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
