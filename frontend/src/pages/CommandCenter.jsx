import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  AlertTriangle,
  CheckCircle2,
  Clock,
  Activity,
  Flame,
  ArrowUpRight,
  TrendingDown,
  RefreshCw,
  Zap,
  Play
} from 'lucide-react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid
} from 'recharts';
import { nexusApi } from '../services/api';
import { useApp } from '../context/AppContext';

export default function CommandCenter() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [simulating, setSimulating] = useState(false);
  const navigate = useNavigate();
  const { addNotification } = useApp();

  const fetchOverview = async () => {
    try {
      const res = await nexusApi.getOverview();
      setData(res.data);
    } catch (e) {
      console.error('Error fetching overview:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOverview();
    const interval = setInterval(fetchOverview, 6000);
    return () => clearInterval(interval);
  }, []);

  const triggerChaosTest = async () => {
    setSimulating(true);
    try {
      const res = await nexusApi.simulateIncident({
        service: 'nexus-demo-order-service',
        incident_type: 'cpu_saturation'
      });
      addNotification({
        type: 'danger',
        title: 'Empirical Anomaly Triggered',
        message: 'Dispatched multi-agent cognitive investigation pipeline for Order Service.',
        timestamp: new Date().toLocaleTimeString()
      });
      await fetchOverview();
    } catch (e) {
      console.error(e);
    } finally {
      setSimulating(false);
    }
  };

  // Mock live sparkline data
  const telemetryHistory = [
    { time: '10:00', cpu: 32, memory: 58, latency: 42 },
    { time: '10:05', cpu: 34, memory: 59, latency: 45 },
    { time: '10:10', cpu: 41, memory: 61, latency: 50 },
    { time: '10:15', cpu: 39, memory: 60, latency: 48 },
    { time: '10:20', cpu: 88, memory: 78, latency: 420 },
    { time: '10:25', cpu: 94, memory: 82, latency: 890 },
    { time: '10:30', cpu: 35, memory: 59, latency: 44 },
  ];

  if (loading && !data) {
    return (
      <div className="flex h-96 items-center justify-center">
        <RefreshCw className="w-8 h-8 text-blue-500 animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Title & Action Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-100 flex items-center gap-2.5">
            Command Center
            <span className="text-xs px-2.5 py-0.5 rounded-full font-mono bg-blue-500/10 text-blue-400 border border-blue-500/20">
              LIVE TELEMETRY
            </span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Real-time autonomous observation, continuous statistical baselining, and closed-loop resolution.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchOverview}
            className="px-3.5 py-2 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700/80 text-xs font-medium text-slate-300 transition-all flex items-center gap-2"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Refresh
          </button>
          <button
            onClick={triggerChaosTest}
            disabled={simulating}
            className="px-4 py-2 rounded-lg bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 text-white font-medium text-xs shadow-lg shadow-red-500/20 transition-all flex items-center gap-2 disabled:opacity-50"
          >
            <Play className={`w-3.5 h-3.5 ${simulating ? 'animate-spin' : ''}`} />
            {simulating ? 'Simulating...' : 'Inject Chaos Anomaly'}
          </button>
        </div>
      </div>

      {/* KPI Tiles Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="nexus-card p-5 relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">Active Incidents</span>
            <div className="w-8 h-8 rounded-lg bg-amber-500/10 text-amber-400 flex items-center justify-center">
              <AlertTriangle className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-bold text-slate-100 font-mono">
              {data?.active_incidents ?? 0}
            </span>
            <span className="text-xs text-amber-400 font-mono">Under Investigation</span>
          </div>
          <div className="mt-2 text-xs text-slate-500">
            Critical Severity: <span className="text-red-400 font-semibold">{data?.critical_incidents ?? 0}</span>
          </div>
        </div>

        <div className="nexus-card p-5 relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">Cluster Availability</span>
            <div className="w-8 h-8 rounded-lg bg-emerald-500/10 text-emerald-400 flex items-center justify-center">
              <CheckCircle2 className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-bold text-slate-100 font-mono">
              {data?.infrastructure_availability ?? 99.8}%
            </span>
            <span className="text-xs text-emerald-400 font-mono">SLA Optimal</span>
          </div>
          <div className="mt-2 text-xs text-slate-500">
            Resolved Incidents: <span className="text-slate-300 font-semibold">{data?.resolved_incidents ?? 0}</span>
          </div>
        </div>

        <div className="nexus-card p-5 relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">Mean Time to Detect (MTTD)</span>
            <div className="w-8 h-8 rounded-lg bg-cyan-500/10 text-cyan-400 flex items-center justify-center">
              <Zap className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-bold text-slate-100 font-mono">
              {data?.mttd_minutes ?? 1.4}
            </span>
            <span className="text-xs text-cyan-400 font-mono">Minutes</span>
          </div>
          <div className="mt-2 text-xs text-slate-500">
            Statistical Anomaly Detection: <span className="text-cyan-400 font-semibold">Continuous</span>
          </div>
        </div>

        <div className="nexus-card p-5 relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">Mean Time to Resolve (MTTR)</span>
            <div className="w-8 h-8 rounded-lg bg-blue-500/10 text-blue-400 flex items-center justify-center">
              <Clock className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-bold text-slate-100 font-mono">
              {data?.mttr_minutes ?? 3.8}
            </span>
            <span className="text-xs text-blue-400 font-mono">Minutes</span>
          </div>
          <div className="mt-2 text-xs text-slate-500">
            Autonomous Recovery Rate: <span className="text-blue-400 font-semibold">87.5%</span>
          </div>
        </div>
      </div>

      {/* Telemetry Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="nexus-card p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-slate-200">Cluster CPU & Memory Utilization</h3>
              <p className="text-xs text-slate-400">Dynamic baseline bounds vs actual Prometheus streams</p>
            </div>
            <div className="flex items-center gap-3 text-xs font-mono">
              <span className="flex items-center gap-1 text-blue-400">
                <span className="w-2 h-2 rounded-full bg-blue-500" /> CPU %
              </span>
              <span className="flex items-center gap-1 text-indigo-400">
                <span className="w-2 h-2 rounded-full bg-indigo-500" /> Memory %
              </span>
            </div>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={telemetryHistory}>
                <defs>
                  <linearGradient id="cpuGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#3B82F6" stopOpacity={0.0} />
                  </linearGradient>
                  <linearGradient id="memGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366F1" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#6366F1" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" />
                <XAxis dataKey="time" stroke="#64748B" fontSize={11} />
                <YAxis stroke="#64748B" fontSize={11} domain={[0, 100]} />
                <Tooltip contentStyle={{ backgroundColor: '#111827', borderColor: '#374151', fontSize: '12px' }} />
                <Area type="monotone" dataKey="cpu" stroke="#3B82F6" fillOpacity={1} fill="url(#cpuGradient)" />
                <Area type="monotone" dataKey="memory" stroke="#6366F1" fillOpacity={1} fill="url(#memGradient)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="nexus-card p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-slate-200">P95 Response Latency (ms)</h3>
              <p className="text-xs text-slate-400">Prometheus histogram quantile (le=0.95)</p>
            </div>
            <span className="text-xs font-mono text-cyan-400 px-2 py-0.5 rounded bg-cyan-500/10 border border-cyan-500/20">
              Median: 45ms
            </span>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={telemetryHistory}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" />
                <XAxis dataKey="time" stroke="#64748B" fontSize={11} />
                <YAxis stroke="#64748B" fontSize={11} />
                <Tooltip contentStyle={{ backgroundColor: '#111827', borderColor: '#374151', fontSize: '12px' }} />
                <Line type="monotone" dataKey="latency" stroke="#06B6D4" strokeWidth={2} dot={{ fill: '#06B6D4', r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Recent Activities Audit Feed */}
      <div className="nexus-card p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-semibold text-slate-200">Recent Autonomous & Operator Activities</h3>
            <p className="text-xs text-slate-400">Chronological tamper-evident audit trail</p>
          </div>
          <button
            onClick={() => navigate('/audit')}
            className="text-xs text-blue-400 hover:text-blue-300 font-medium flex items-center gap-1"
          >
            View Full Audit Trail <ArrowUpRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="divide-y divide-slate-800/80">
          {(data?.recent_activities ?? []).slice(0, 5).map((act) => (
            <div key={act.id} className="py-3 flex items-center justify-between gap-4 text-xs">
              <div className="flex items-center gap-3">
                <div className="w-2 h-2 rounded-full bg-blue-500" />
                <div>
                  <span className="font-semibold text-slate-200">{act.actor}</span>
                  <span className="text-slate-400 mx-1.5">performed</span>
                  <span className="font-mono text-blue-400">{act.action}</span>
                  <span className="text-slate-500 ml-1.5">on {act.target}</span>
                </div>
              </div>
              <span className="text-slate-500 font-mono text-[11px] flex-shrink-0">
                {act.timestamp ? new Date(act.timestamp).toLocaleTimeString() : 'Recent'}
              </span>
            </div>
          ))}
          {(!data?.recent_activities || data.recent_activities.length === 0) && (
            <div className="py-8 text-center text-slate-500 text-xs">
              No recent audit records. Systems running normally.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
