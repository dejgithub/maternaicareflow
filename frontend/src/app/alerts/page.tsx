'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { api, type Escalation } from '@/lib/api';
import { Bell, ArrowLeft, Activity, AlertTriangle, CheckCircle, UserCheck, Clock } from 'lucide-react';

const severityBadge: Record<string, string> = {
  low: 'badge-low', medium: 'badge-medium', high: 'badge-high', critical: 'badge-emergency',
};
const statusBadge: Record<string, string> = {
  open: 'badge-emergency', acknowledged: 'badge-medium', approved: 'badge-approved', resolved: 'badge-completed', rejected: 'badge-emergency',
};

export default function AlertsPage() {
  const [escalations, setEscalations] = useState<Escalation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { loadEscalations(); }, []);

  async function loadEscalations() {
    try {
      setLoading(true);
      const result = await api.getEscalations();
      setEscalations(result);
    } catch {
      setEscalations(getMockEscalations());
    } finally {
      setLoading(false);
    }
  }

  function getMockEscalations(): Escalation[] {
    return [
      { escalation_id: 'ESC-001', patient_id: 'PAT-002', patient_name: 'Jane Doe', severity: 'critical', status: 'open', description: 'Severe postpartum hemorrhage with loss of consciousness', created_at: new Date().toISOString() },
      { escalation_id: 'ESC-002', patient_id: 'PAT-005', patient_name: 'Lisa Chen', severity: 'high', status: 'acknowledged', description: 'Preeclampsia symptoms with severe headache', created_at: new Date(Date.now() - 3600000).toISOString() },
      { escalation_id: 'ESC-003', patient_id: 'PAT-001', patient_name: 'Maria Santos', severity: 'high', status: 'resolved', description: 'Abnormal vital signs detected', created_at: new Date(Date.now() - 86400000).toISOString() },
    ];
  }

  async function handleAcknowledge(id: string) {
    try {
      await api.acknowledgeEscalation(id, 'dr-sarah-chen');
      loadEscalations();
    } catch { alert('Escalation acknowledged (mock)'); }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 px-4 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href="/dashboard" className="text-gray-500 hover:text-gray-700"><ArrowLeft className="h-5 w-5" /></Link>
          <h1 className="text-lg font-semibold">Alerts & Escalations</h1>
        </div>
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <Bell className="h-4 w-4" />
          <span>{escalations.filter(e => e.status === 'open').length} open</span>
        </div>
      </header>

      <main className="p-4 lg:p-8 max-w-7xl mx-auto">
        {loading ? (
          <div className="flex items-center justify-center py-12"><Activity className="h-6 w-6 text-primary-500 animate-spin" /></div>
        ) : (
          <div className="space-y-4">
            {escalations.map((esc) => (
              <div key={esc.escalation_id} className={`stat-card border-l-4 ${esc.severity === 'critical' ? 'border-l-red-500' : esc.severity === 'high' ? 'border-l-orange-500' : 'border-l-yellow-500'}`}>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="font-mono text-xs text-gray-400">{esc.escalation_id}</span>
                      <span className={`badge ${severityBadge[esc.severity] || 'badge-medium'}`}>{esc.severity}</span>
                      <span className={`badge ${statusBadge[esc.status] || 'badge-pending'}`}>{esc.status}</span>
                      {esc.severity === 'critical' && (
                        <span className="badge badge-emergency flex items-center gap-1">
                          <AlertTriangle className="h-3 w-3" /> CRITICAL
                        </span>
                      )}
                    </div>
                    <h3 className="font-semibold">{esc.patient_name}</h3>
                    <p className="text-sm text-gray-600 mt-1">{esc.description}</p>
                    <div className="flex items-center gap-2 mt-2 text-xs text-gray-500">
                      <Clock className="h-3 w-3" />
                      <span>{new Date(esc.created_at).toLocaleString()}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 ml-4">
                    {esc.status === 'open' && (
                      <button onClick={() => handleAcknowledge(esc.escalation_id)} className="btn-primary text-xs flex items-center gap-1">
                        <UserCheck className="h-3 w-3" /> Acknowledge
                      </button>
                    )}
                    {esc.status === 'acknowledged' && (
                      <>
                        <button className="btn-primary text-xs flex items-center gap-1">
                          <CheckCircle className="h-3 w-3" /> Approve
                        </button>
                        <button className="btn-secondary text-xs flex items-center gap-1">
                          <AlertTriangle className="h-3 w-3" /> Escalate
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
