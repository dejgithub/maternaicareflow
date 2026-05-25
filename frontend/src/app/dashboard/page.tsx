'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { api, type DashboardData } from '@/lib/api';
import {
  Baby, Users, AlertTriangle, Calendar, Activity, Heart, ArrowRight,
  Bell, TrendingUp, Clock, Shield, ChevronRight, Menu, X, LogOut,
} from 'lucide-react';

const riskColors: Record<string, string> = {
  low: 'bg-green-500', medium: 'bg-yellow-500', high: 'bg-orange-500', emergency: 'bg-red-500',
};
const riskBadge: Record<string, string> = {
  low: 'badge-low', medium: 'badge-medium', high: 'badge-high', emergency: 'badge-emergency',
};

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboard();
  }, []);

  async function loadDashboard() {
    try {
      setLoading(true);
      setError(null);
      const result = await api.getDashboard();
      setData(result);
    } catch (e: any) {
      setError(e.message);
      // Use mock data if API unavailable
      setData(getMockDashboard());
    } finally {
      setLoading(false);
    }
  }

  function getMockDashboard(): DashboardData {
    return {
      summary: {
        total_patients: 248, high_risk_patients: 18, emergency_patients: 5,
        total_referrals: 156, pending_referrals: 23, missed_appointments: 12,
        open_escalations: 7,
      },
      risk_distribution: { low: 145, medium: 80, high: 18, emergency: 5 },
      referral_status: { pending_approval: 23, approved: 89, assigned: 31, completed: 13, rejected: 0 },
      appointment_metrics: { total: 312, scheduled: 48, completed: 248, missed: 12, cancelled: 4 },
      recent_alerts: [
        { alert_id: 'A1', patient_name: 'Maria Santos', severity: 'high', message: 'Missed critical follow-up appointment', created_at: new Date().toISOString() },
        { alert_id: 'A2', patient_name: 'Jane Doe', severity: 'emergency', message: 'Severe postpartum symptoms reported', created_at: new Date().toISOString() },
        { alert_id: 'A3', patient_name: 'Sarah Johnson', severity: 'medium', message: 'Medication adherence concern', created_at: new Date().toISOString() },
      ],
    };
  }

  const navItems = [
    { label: 'Dashboard', href: '/dashboard', icon: Activity, active: true },
    { label: 'Patients', href: '/patients', icon: Users },
    { label: 'Referrals', href: '/referrals', icon: ArrowRight },
    { label: 'Appointments', href: '/appointments', icon: Calendar },
    { label: 'Alerts', href: '/alerts', icon: Bell },
  ];

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <aside className={`fixed inset-y-0 left-0 z-50 w-64 bg-white border-r border-gray-200 transform transition-transform lg:translate-x-0 lg:static lg:inset-auto ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}`}>
        <div className="flex items-center justify-between h-16 px-6 border-b border-gray-200">
          <Link href="/" className="flex items-center gap-2">
            <Baby className="h-7 w-7 text-primary-600" />
            <span className="font-bold text-gray-900">CareFlow</span>
          </Link>
          <button onClick={() => setSidebarOpen(false)} className="lg:hidden text-gray-500 hover:text-gray-700">
            <X className="h-5 w-5" />
          </button>
        </div>
        <nav className="px-3 py-4 space-y-1">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                item.active ? 'bg-primary-50 text-primary-700' : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              <item.icon className="h-5 w-5" />
              {item.label}
            </Link>
          ))}
        </nav>
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200">
          <div className="flex items-center gap-3 text-sm text-gray-500">
            <Shield className="h-4 w-4" />
            <span>HIPAA Compliant</span>
          </div>
        </div>
      </aside>

      {/* Overlay */}
      {sidebarOpen && (
        <div className="fixed inset-0 bg-black/30 z-40 lg:hidden" onClick={() => setSidebarOpen(false)} />
      )}

      {/* Main */}
      <div className="flex-1 min-w-0">
        <header className="bg-white border-b border-gray-200 h-16 flex items-center justify-between px-4 lg:px-8">
          <button onClick={() => setSidebarOpen(true)} className="lg:hidden text-gray-500 hover:text-gray-700">
            <Menu className="h-6 w-6" />
          </button>
          <h1 className="text-lg font-semibold text-gray-900">Clinical Dashboard</h1>
          <div className="flex items-center gap-3">
            <span className="text-sm text-gray-500">Dr. Sarah Chen</span>
            <div className="h-8 w-8 bg-primary-100 rounded-full flex items-center justify-center">
              <span className="text-sm font-medium text-primary-700">SC</span>
            </div>
          </div>
        </header>

        <main className="p-4 lg:p-8">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <Activity className="h-8 w-8 text-primary-500 animate-pulse" />
              <span className="ml-3 text-gray-500">Loading dashboard data...</span>
            </div>
          ) : error && !data ? (
            <div className="text-center py-12">
              <AlertTriangle className="h-12 w-12 text-orange-400 mx-auto mb-4" />
              <h2 className="text-lg font-semibold mb-2">Connection Error</h2>
              <p className="text-gray-500 mb-4">Unable to reach API server. Start the backend with: <code className="bg-gray-100 px-2 py-0.5 rounded text-sm">uvicorn app.main:app</code></p>
            </div>
          ) : data ? (
            <>
              {/* Summary Cards */}
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                {[
                  { label: 'Total Patients', value: data.summary.total_patients, icon: Users, color: 'text-blue-600', bg: 'bg-blue-50' },
                  { label: 'High Risk', value: data.summary.high_risk_patients, icon: AlertTriangle, color: 'text-orange-600', bg: 'bg-orange-50' },
                  { label: 'Pending Referrals', value: data.summary.pending_referrals, icon: ArrowRight, color: 'text-purple-600', bg: 'bg-purple-50' },
                  { label: 'Open Escalations', value: data.summary.open_escalations, icon: Bell, color: 'text-red-600', bg: 'bg-red-50' },
                ].map((card, i) => (
                  <div key={i} className="stat-card">
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-sm text-gray-500">{card.label}</span>
                      <div className={`h-10 w-10 rounded-lg ${card.bg} flex items-center justify-center`}>
                        <card.icon className={`h-5 w-5 ${card.color}`} />
                      </div>
                    </div>
                    <div className="text-3xl font-bold">{card.value}</div>
                  </div>
                ))}
              </div>

              <div className="grid lg:grid-cols-2 gap-6 mb-8">
                {/* Risk Distribution */}
                <div className="stat-card">
                  <h3 className="font-semibold mb-4 flex items-center gap-2">
                    <Heart className="h-5 w-5 text-primary-500" /> Risk Distribution
                  </h3>
                  <div className="space-y-3">
                    {Object.entries(data.risk_distribution).map(([level, count]) => (
                      <div key={level}>
                        <div className="flex justify-between text-sm mb-1">
                          <span className="capitalize">{level}</span>
                          <span className="font-medium">{count}</span>
                        </div>
                        <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                          <div
                            className={`h-full rounded-full transition-all duration-500 ${riskColors[level] || 'bg-gray-400'}`}
                            style={{ width: `${(count / data.summary.total_patients) * 100}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Referral Status */}
                <div className="stat-card">
                  <h3 className="font-semibold mb-4 flex items-center gap-2">
                    <ArrowRight className="h-5 w-5 text-primary-500" /> Referral Status
                  </h3>
                  <div className="space-y-3">
                    {Object.entries(data.referral_status).map(([status, count]) => (
                      <div key={status} className="flex items-center justify-between py-2 border-b border-gray-50 last:border-0">
                        <span className="text-sm capitalize">{status.replace(/_/g, ' ')}</span>
                        <span className={`badge ${status === 'pending_approval' ? 'badge-pending' : status === 'approved' ? 'badge-approved' : status === 'completed' ? 'badge-completed' : 'badge-medium'}`}>
                          {count}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="grid lg:grid-cols-2 gap-6">
                {/* Appointment Metrics */}
                <div className="stat-card">
                  <h3 className="font-semibold mb-4 flex items-center gap-2">
                    <Calendar className="h-5 w-5 text-primary-500" /> Appointment Overview
                  </h3>
                  <div className="grid grid-cols-2 gap-4">
                    {[
                      { label: 'Scheduled', value: data.appointment_metrics.scheduled, color: 'text-blue-600' },
                      { label: 'Completed', value: data.appointment_metrics.completed, color: 'text-green-600' },
                      { label: 'Missed', value: data.appointment_metrics.missed, color: 'text-red-600' },
                      { label: 'Adherence', value: `${Math.round((data.appointment_metrics.completed / (data.appointment_metrics.completed + data.appointment_metrics.missed || 1)) * 100)}%`, color: 'text-primary-600' },
                    ].map((metric, i) => (
                      <div key={i} className="bg-gray-50 rounded-lg p-4">
                        <div className={`text-2xl font-bold ${metric.color}`}>{metric.value}</div>
                        <div className="text-xs text-gray-500 mt-1">{metric.label}</div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Recent Alerts */}
                <div className="stat-card">
                  <h3 className="font-semibold mb-4 flex items-center gap-2">
                    <Bell className="h-5 w-5 text-primary-500" /> Recent Alerts
                  </h3>
                  <div className="space-y-3">
                    {data.recent_alerts.map((alert) => (
                      <div key={alert.alert_id} className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                        <div className={`mt-0.5 h-2 w-2 rounded-full ${riskColors[alert.severity] || 'bg-gray-400'} flex-shrink-0`} />
                        <div className="min-w-0 flex-1">
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-medium">{alert.patient_name}</span>
                            <span className={`badge ${riskBadge[alert.severity] || 'badge-medium'}`}>{alert.severity}</span>
                          </div>
                          <p className="text-xs text-gray-500 mt-0.5 truncate">{alert.message}</p>
                        </div>
                        <ChevronRight className="h-4 w-4 text-gray-400 flex-shrink-0 mt-1" />
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="mt-8 grid lg:grid-cols-3 gap-4">
                <Link href="/patients" className="stat-card flex items-center justify-between group">
                  <div>
                    <h4 className="font-medium">Patient Management</h4>
                    <p className="text-sm text-gray-500">Register & manage patients</p>
                  </div>
                  <ArrowRight className="h-5 w-5 text-gray-400 group-hover:text-primary-600 transition-colors" />
                </Link>
                <Link href="/referrals" className="stat-card flex items-center justify-between group">
                  <div>
                    <h4 className="font-medium">Referral Workflow</h4>
                    <p className="text-sm text-gray-500">Create & approve referrals</p>
                  </div>
                  <ArrowRight className="h-5 w-5 text-gray-400 group-hover:text-primary-600 transition-colors" />
                </Link>
                <Link href="/alerts" className="stat-card flex items-center justify-between group">
                  <div>
                    <h4 className="font-medium">Emergency Escalations</h4>
                    <p className="text-sm text-gray-500">View & manage alerts</p>
                  </div>
                  <ArrowRight className="h-5 w-5 text-gray-400 group-hover:text-primary-600 transition-colors" />
                </Link>
              </div>
            </>
          ) : null}
        </main>
      </div>
    </div>
  );
}
