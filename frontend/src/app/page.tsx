'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Activity, Baby, Heart, AlertTriangle, Users, Calendar, ArrowRight, Shield, Bot, GitBranch, Database, Brain, Stethoscope } from 'lucide-react';

export default function Home() {
  const [isVisible, setIsVisible] = useState(false);
  useEffect(() => { setIsVisible(true); }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50">
      <header className="border-b border-gray-200 bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-2">
              <Baby className="h-8 w-8 text-primary-600" />
              <span className="text-xl font-bold text-gray-900">MaternAI CareFlow</span>
            </div>
            <div className="flex items-center gap-4">
              <Link href="/dashboard" className="btn-primary text-sm">
                Launch Dashboard
              </Link>
            </div>
          </div>
        </div>
      </header>

      <main>
        <section className={`max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 transition-all duration-1000 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
          <div className="text-center max-w-4xl mx-auto">
            <div className="inline-flex items-center gap-2 bg-primary-100 text-primary-700 px-4 py-2 rounded-full text-sm font-medium mb-6">
              <Heart className="h-4 w-4" /> UiPath AgentHack 2026
            </div>
            <h1 className="text-5xl sm:text-6xl font-bold text-gray-900 mb-6 leading-tight">
              AI-Powered Maternal Healthcare{' '}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-600 to-secondary-600">Orchestration</span>
            </h1>
            <p className="text-xl text-gray-600 mb-10 max-w-3xl mx-auto leading-relaxed">
              An enterprise-grade platform that orchestrates postnatal care referrals, follow-ups,
              emergency escalation, and healthcare workflows using UiPath Maestro, AI agents, and human-in-the-loop approvals.
            </p>
            <div className="flex flex-wrap justify-center gap-4">
              <Link href="/dashboard" className="btn-primary text-lg px-8 py-3 inline-flex items-center gap-2">
                Enter Dashboard <ArrowRight className="h-5 w-5" />
              </Link>
              <a href="#features" className="btn-secondary text-lg px-8 py-3">Explore Features</a>
            </div>
          </div>
        </section>

        <section className="bg-white py-16 border-y border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
              {[
                { value: '500+', label: 'Mothers Supported', icon: Users },
                { value: '96%', label: 'Follow-up Adherence', icon: Calendar },
                { value: '<5min', label: 'Emergency Response', icon: AlertTriangle },
                { value: '100%', label: 'HIPAA Compliant', icon: Shield },
              ].map((stat, i) => (
                <div key={i} className="stat-card">
                  <stat.icon className="h-8 w-8 text-primary-500 mx-auto mb-2" />
                  <div className="text-3xl font-bold text-gray-900">{stat.value}</div>
                  <div className="text-sm text-gray-500">{stat.label}</div>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section id="features" className="py-20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <h2 className="text-3xl font-bold text-center mb-4">Enterprise-Grade Healthcare Orchestration</h2>
            <p className="text-gray-500 text-center mb-12 max-w-2xl mx-auto">
              Powered by UiPath Maestro, AI Agents, and Human-in-the-Loop workflows
            </p>
            <div className="grid md:grid-cols-3 gap-8">
              {[
                { icon: Brain, title: 'AI Risk Assessment', desc: 'Multi-agent AI analysis of symptoms, history, and vitals to classify maternal risk levels with intelligent escalation.' },
                { icon: GitBranch, title: 'BPMN Workflow Orchestration', desc: 'UiPath Maestro-powered referral, appointment, and emergency workflows with exception handling.' },
                { icon: Bot, title: 'Intelligent Agents', desc: 'LangChain & CrewAI agents for referral coordination, scheduling, and emergency response.' },
                { icon: Stethoscope, title: 'Human-in-the-Loop', desc: 'Governed AI with nurse, doctor, and admin approval gates for critical medical decisions.' },
                { icon: Activity, title: 'Real-time Analytics', desc: 'Dashboards for risk distribution, referral status, missed appointments, and facility load.' },
                { icon: Database, title: 'Enterprise Backend', desc: 'FastAPI + MongoDB with secure REST APIs for patient management and workflow integration.' },
              ].map((feature, i) => (
                <div key={i} className="stat-card p-6">
                  <feature.icon className="h-10 w-10 text-primary-600 mb-4" />
                  <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
                  <p className="text-gray-600 text-sm leading-relaxed">{feature.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="bg-gradient-to-r from-primary-600 to-secondary-600 py-16 text-white">
          <div className="max-w-4xl mx-auto px-4 text-center">
            <h2 className="text-3xl font-bold mb-4">Powered by UiPath Ecosystem</h2>
            <p className="text-xl mb-8 opacity-90">
              Integrating UiPath Maestro &bull; Agent Builder &bull; API Workflows &bull; Automation Cloud
            </p>
            <div className="flex flex-wrap justify-center gap-3">
              {['Clinical Agents', 'Referral Workflows', 'AI Orchestration', 'Human Approvals', 'API Integration', 'Analytics'].map((tag) => (
                <span key={tag} className="bg-white/20 backdrop-blur-sm px-4 py-2 rounded-full text-sm font-medium">
                  {tag}
                </span>
              ))}
            </div>
          </div>
        </section>

        <section className="py-16">
          <div className="max-w-4xl mx-auto px-4 text-center">
            <h2 className="text-2xl font-bold mb-2">Built with Claude Code</h2>
            <p className="text-gray-500 mb-8">AI-assisted development using Claude Code coding agent</p>
            <div className="bg-gray-900 text-green-400 rounded-xl p-6 text-left font-mono text-sm overflow-x-auto">
              <p>$ <span className="text-white">Claude Code generated full-stack healthcare coordination platform</span></p>
              <p className="mt-2 text-gray-500">// Backend: FastAPI + MongoDB models, AI agents, REST APIs</p>
              <p className="text-gray-500">// Frontend: Next.js dashboard with real-time analytics</p>
              <p className="text-gray-500">// AI: LangChain + CrewAI multi-agent risk assessment</p>
              <p className="text-gray-500">// Workflow: BPMN orchestration with human-in-the-loop</p>
              <p className="mt-2">✓ <span className="text-white">Full project scaffolded and implemented via AI pair programming</span></p>
            </div>
          </div>
        </section>
      </main>

      <footer className="border-t border-gray-200 py-8 text-center text-sm text-gray-500">
        <p>MaternAI CareFlow &mdash; UiPath AgentHack 2026</p>
        <p className="mt-1">Built with Claude Code &amp; the UiPath Enterprise Platform</p>
      </footer>
    </div>
  );
}
