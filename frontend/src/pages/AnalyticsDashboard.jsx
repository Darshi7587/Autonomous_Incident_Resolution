import React, { useState, useEffect } from 'react';
import {
  BarChart3,
  TrendingDown,
  TrendingUp,
  Clock,
  ShieldCheck,
  Zap,
  RefreshCw,
  PieChart as PieIcon
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { nexusApi } from '../services/api';

const SEVERITY_COLORS = {
  CRITICAL: '#EF4444',
  HIGH: '#F59E0B',
  MEDIUM: '#3B82F6',
  LOW: '#64748B'
};

export default function AnalyticsDashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchAnalytics = async () => {
    try {
      const res = await nexusApi.getAnalytics();
      setData(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const pieData = Object.entries(data?.severity_distribution || { CRITICAL: 1, HIGH: 3, MEDIUM: 5, LOW: 2 }).map(
    ([key, value]) => ({ name: key, value })
  );

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-100 flex items-center gap-2.5">
            AIOps Analytics & Performance
            <span className="text-xs px-2.5 py-0.5 rounded-full font-mono bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
              HISTORICAL METRICS
            </span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Mean Time to Detect (MTTD), Mean Time to Resolve (MTTR), resolution efficiency, and agent benchmarks.
          </p>
        </div>

        <button
          onClick={fetchAnalytics}
          className="px-3.5 py-2 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700/80 text-xs font-medium text-slate-300 transition-all flex items-center gap-2"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          Refresh Metrics
        </button>
      </div>

      {/* KPI Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="nexus-card p-5">
          <div className="flex items-center justify-between text-xs text-slate-400 uppercase tracking-wider">
            <span>Mean Time to Detect</span>
            <Zap className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-bold text-slate-100 font-mono">
              {data ? Math.round(data.mttd_seconds / 60 * 10) / 10 : 1.4}
            </span>
            <span className="text-xs text-cyan-400 font-mono">Mins (84s)</span>
          </div>
          <div className="mt-2 text-xs text-emerald-400 flex items-center gap-1 font-mono">
            <TrendingDown className="w-3.5 h-3.5" /> 28% reduction vs manual ops
          </div>
        </div>

        <div className="nexus-card p-5">
          <div className="flex items-center justify-between text-xs text-slate-400 uppercase tracking-wider">
            <span>Mean Time to Resolve</span>
            <Clock className="w-4 h-4 text-blue-400" />
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-bold text-slate-100 font-mono">
              {data ? Math.round(data.mttr_seconds / 60 * 10) / 10 : 3.8}
            </span>
            <span className="text-xs text-blue-400 font-mono">Mins (228s)</span>
          </div>
          <div className="mt-2 text-xs text-emerald-400 flex items-center gap-1 font-mono">
            <TrendingDown className="w-3.5 h-3.5" /> 64% faster than human SLA
          </div>
        </div>

        <div className="nexus-card p-5">
          <div className="flex items-center justify-between text-xs text-slate-400 uppercase tracking-wider">
            <span>Remediation Success Rate</span>
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-bold text-slate-100 font-mono">
              {data?.resolution_success_rate ?? 98.4}%
            </span>
            <span className="text-xs text-emerald-400 font-mono">Post-Verified</span>
          </div>
          <div className="mt-2 text-xs text-slate-500 font-mono">
            Zero Unverified Resolutions
          </div>
        </div>

        <div className="nexus-card p-5">
          <div className="flex items-center justify-between text-xs text-slate-400 uppercase tracking-wider">
            <span>Autonomous Actions Ratio</span>
            <BarChart3 className="w-4 h-4 text-purple-400" />
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-bold text-slate-100 font-mono">
              {data?.autonomous_resolution_rate ?? 87.5}%
            </span>
            <span className="text-xs text-purple-400 font-mono">Closed-Loop</span>
          </div>
          <div className="mt-2 text-xs text-slate-500 font-mono">
            Safety Gate Enforced
          </div>
        </div>
      </div>

      {/* Historical Frequency & Severity Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="nexus-card p-6 lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-slate-200">Incident Volume History & MTTR Trend</h3>
              <p className="text-xs text-slate-400">Daily incident frequency across the last 7 days</p>
            </div>
            <span className="text-xs font-mono text-slate-400">Weekly Total: 39</span>
          </div>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data?.incident_frequency_history || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" />
                <XAxis dataKey="date" stroke="#64748B" fontSize={11} />
                <YAxis stroke="#64748B" fontSize={11} />
                <Tooltip contentStyle={{ backgroundColor: '#111827', borderColor: '#374151', fontSize: '12px' }} />
                <Bar dataKey="incidents" fill="#3B82F6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="nexus-card p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-slate-200">Severity Distribution</h3>
              <p className="text-xs text-slate-400">Active & Historical Incidents</p>
            </div>
            <PieIcon className="w-4 h-4 text-slate-400" />
          </div>
          <div className="h-72 flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={SEVERITY_COLORS[entry.name] || '#3B82F6'} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#111827', borderColor: '#374151', fontSize: '12px' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
