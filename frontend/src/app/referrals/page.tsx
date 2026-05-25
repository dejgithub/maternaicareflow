'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { api, type Referral } from '@/lib/api';
import { ArrowRight, ArrowLeft, Plus, Activity, CheckCircle, XCircle, UserCheck } from 'lucide-react';

const statusBadge: Record<string, string> = {
  pending_approval: 'badge-pending', approved: 'badge-approved',
  assigned: 'badge-medium', completed: 'badge-completed', rejected: 'badge-emergency',
};
const riskBadge: Record<string, string> = {
  low: 'badge-low', medium: 'badge-medium', high: 'badge-high', emergency: 'badge-emergency',
};

export default function ReferralsPage() {
  const [referrals, setReferrals] = useState<Referral[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({ patient_id: '', referral_reason: '', priority: 'normal' });

  useEffect(() => { loadReferrals(); }, []);

  async function loadReferrals() {
    try {
      setLoading(true);
      const result = await api.getReferrals();
      setReferrals(result);
    } catch {
      setReferrals(getMockReferrals());
    } finally {
      setLoading(false);
    }
  }

  function getMockReferrals(): Referral[] {
    return [
      { referral_id: 'REF-001', patient_id: 'PAT-001', patient_name: 'Maria Santos', risk_level: 'high', referral_reason: 'Preeclampsia monitoring', status: 'pending_approval', target_facility_name: 'St. Mary\'s Maternity Hospital', priority: 'high', is_emergency: false, created_at: new Date().toISOString() },
      { referral_id: 'REF-002', patient_id: 'PAT-002', patient_name: 'Jane Doe', risk_level: 'emergency', referral_reason: 'Severe postpartum hemorrhage', status: 'approved', target_facility_name: 'State University Teaching Hospital', priority: 'emergency', is_emergency: true, created_at: new Date().toISOString() },
      { referral_id: 'REF-003', patient_id: 'PAT-003', patient_name: 'Sarah Johnson', risk_level: 'low', referral_reason: 'Routine postnatal check', status: 'completed', target_facility_name: 'City Women\'s Health Center', priority: 'normal', is_emergency: false, created_at: new Date().toISOString() },
    ];
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    try {
      await api.createReferral(formData);
      setShowForm(false);
      loadReferrals();
    } catch { alert('Referral created (mock)'); setShowForm(false); }
  }

  async function handleApprove(id: string) {
    try {
      await api.approveReferral(id, 'dr-sarah-chen', 'MAT-001');
      loadReferrals();
    } catch { alert('Referral approved (mock)'); }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 px-4 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href="/dashboard" className="text-gray-500 hover:text-gray-700"><ArrowLeft className="h-5 w-5" /></Link>
          <h1 className="text-lg font-semibold">Referral Coordination</h1>
        </div>
        <button onClick={() => setShowForm(!showForm)} className="btn-primary text-sm flex items-center gap-2">
          <Plus className="h-4 w-4" /> New Referral
        </button>
      </header>

      <main className="p-4 lg:p-8 max-w-7xl mx-auto">
        {showForm && (
          <form onSubmit={handleSubmit} className="stat-card mb-6">
            <h3 className="font-semibold mb-4">Create New Referral</h3>
            <div className="grid md:grid-cols-3 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Patient ID</label>
                <input className="input-field" required value={formData.patient_id} onChange={e => setFormData({...formData, patient_id: e.target.value})} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Referral Reason</label>
                <input className="input-field" required value={formData.referral_reason} onChange={e => setFormData({...formData, referral_reason: e.target.value})} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
                <select className="input-field" value={formData.priority} onChange={e => setFormData({...formData, priority: e.target.value})}>
                  <option value="normal">Normal</option>
                  <option value="high">High</option>
                  <option value="emergency">Emergency</option>
                </select>
              </div>
            </div>
            <div className="flex gap-3">
              <button type="submit" className="btn-primary">Create Referral</button>
              <button type="button" onClick={() => setShowForm(false)} className="btn-secondary">Cancel</button>
            </div>
          </form>
        )}

        {loading ? (
          <div className="flex items-center justify-center py-12"><Activity className="h-6 w-6 text-primary-500 animate-spin" /></div>
        ) : (
          <div className="space-y-4">
            {referrals.map((ref) => (
              <div key={ref.referral_id} className="stat-card">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="font-mono text-xs text-gray-400">{ref.referral_id}</span>
                      <span className={`badge ${riskBadge[ref.risk_level] || 'badge-medium'}`}>{ref.risk_level}</span>
                      <span className={`badge ${statusBadge[ref.status] || 'badge-pending'}`}>{ref.status.replace(/_/g, ' ')}</span>
                      {ref.is_emergency && <span className="badge badge-emergency">EMERGENCY</span>}
                    </div>
                    <h3 className="font-semibold">{ref.patient_name}</h3>
                    <p className="text-sm text-gray-600 mt-1">{ref.referral_reason}</p>
                    {ref.target_facility_name && (
                      <p className="text-sm text-gray-500 mt-1">
                        <ArrowRight className="h-3 w-3 inline mr-1" />
                        {ref.target_facility_name}
                      </p>
                    )}
                  </div>
                  <div className="flex items-center gap-2 ml-4">
                    {ref.status === 'pending_approval' && (
                      <>
                        <button onClick={() => handleApprove(ref.referral_id)} className="btn-primary text-xs flex items-center gap-1">
                          <CheckCircle className="h-3 w-3" /> Approve
                        </button>
                        <button className="btn-secondary text-xs flex items-center gap-1">
                          <XCircle className="h-3 w-3" /> Reject
                        </button>
                      </>
                    )}
                    {ref.status === 'approved' && (
                      <button className="btn-secondary text-xs flex items-center gap-1">
                        <UserCheck className="h-3 w-3" /> Assign Worker
                      </button>
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
