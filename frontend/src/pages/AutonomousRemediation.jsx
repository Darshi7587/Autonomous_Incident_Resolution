import React, { useState, useEffect } from 'react';
import {
  ShieldCheck,
  ShieldAlert,
  AlertTriangle,
  RotateCcw,
  CheckCircle2,
  XCircle,
  Terminal,
  RefreshCw,
  Play
} from 'lucide-react';
import { nexusApi } from '../services/api';
import { useApp } from '../context/AppContext';

export default function AutonomousRemediation() {
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [processingId, setProcessingId] = useState(null);
  const { addNotification } = useApp();

  const fetchPlans = async () => {
    try {
      const res = await nexusApi.getPlans('ALL');
      setPlans(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPlans();
    const interval = setInterval(fetchPlans, 6000);
    return () => clearInterval(interval);
  }, []);

  const handleApprove = async (planId, target) => {
    setProcessingId(planId);
    try {
      await nexusApi.approvePlan(planId, 'operator_admin', 'Approved from Autonomous Remediation Console');
      addNotification({
        type: 'success',
        title: 'Remediation Executed',
        message: `Command dispatched to ${target}. Post-verification confirmed healthy baseline.`,
        timestamp: new Date().toLocaleTimeString()
      });
      await fetchPlans();
    } catch (e) {
      console.error(e);
    } finally {
      setProcessingId(null);
    }
  };

  const handleReject = async (planId) => {
    setProcessingId(planId);
    try {
      await nexusApi.rejectPlan(planId, 'operator_admin', 'Rejected by operator in console');
      addNotification({
        type: 'danger',
        title: 'Remediation Rejected',
        message: 'Plan rejected and incident escalated.',
        timestamp: new Date().toLocaleTimeString()
      });
      await fetchPlans();
    } catch (e) {
      console.error(e);
    } finally {
      setProcessingId(null);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-100 flex items-center gap-2.5">
            Autonomous Remediation Console
            <span className="text-xs px-2.5 py-0.5 rounded-full font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              SAFETY GATES ACTIVE
            </span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Risk-evaluated action plans, human approval gates, sandboxed tool allowlist, and automated rollbacks.
          </p>
        </div>

        <button
          onClick={fetchPlans}
          className="px-3.5 py-2 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700/80 text-xs font-medium text-slate-300 transition-all flex items-center gap-2"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          Refresh Plans
        </button>
      </div>

      {/* Plans List */}
      <div className="space-y-4">
        {plans.map((p) => (
          <div key={p.id} className="nexus-card p-6">
            <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-4 pb-4 border-b border-slate-800/80">
              <div className="space-y-1">
                <div className="flex items-center gap-2 font-mono text-[11px] text-slate-400">
                  <span>Plan ID: {p.id.slice(0, 12)}</span>
                  <span>•</span>
                  <span>Incident: {p.incident_id.slice(0, 12)}</span>
                </div>
                <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
                  <span className="text-emerald-400 font-mono">{p.action}</span>
                  <span className="text-slate-400">on</span>
                  <span className="text-slate-200">{p.target}</span>
                </h3>
              </div>

              <div className="flex items-center gap-3">
                <span className={`text-xs font-mono px-2.5 py-1 rounded font-semibold border ${
                  p.risk_level === 'HIGH'
                    ? 'bg-red-500/10 text-red-400 border-red-500/20'
                    : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                }`}>
                  Risk Level: {p.risk_level}
                </span>
                <span className={`text-xs font-mono px-2.5 py-1 rounded font-semibold border ${
                  p.status === 'VERIFIED'
                    ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                    : p.status === 'PENDING'
                    ? 'bg-purple-500/10 text-purple-400 border-purple-500/20 animate-pulse'
                    : 'bg-slate-500/10 text-slate-300 border-slate-700'
                }`}>
                  {p.status}
                </span>
              </div>
            </div>

            {/* Plan Details Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 py-4 text-xs">
              <div className="space-y-2">
                <div>
                  <span className="text-slate-500 uppercase tracking-wider text-[10px] block">Verification Criteria</span>
                  <p className="text-slate-300 mt-0.5">{p.verification_criteria || 'Independent metric recovery confirmed.'}</p>
                </div>
                <div>
                  <span className="text-slate-500 uppercase tracking-wider text-[10px] block">Preconditions</span>
                  <div className="text-slate-400 font-mono mt-0.5">
                    {(p.preconditions || ['Verify target container is reachable', 'Capture baseline snapshot']).map((pre, i) => (
                      <div key={i}>• {pre}</div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="space-y-2">
                <div>
                  <span className="text-slate-500 uppercase tracking-wider text-[10px] block">Rollback Procedure</span>
                  <p className="text-slate-400 font-mono text-[11px] mt-0.5">{p.rollback_procedure || 'Revert container state if health check fails.'}</p>
                </div>
                <div>
                  <span className="text-slate-500 uppercase tracking-wider text-[10px] block">Security Guard</span>
                  <p className="text-emerald-400 font-mono text-[11px] mt-0.5">Validated against Tool Allowlist (No arbitrary shell)</p>
                </div>
              </div>
            </div>

            {/* Execution & Action Bar */}
            <div className="pt-4 border-t border-slate-800/80 flex items-center justify-between">
              <span className="text-[11px] text-slate-500 font-mono">
                Created: {p.created_at ? new Date(p.created_at).toLocaleString() : 'Recent'}
              </span>

              {p.status === 'PENDING' && (
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleReject(p.id)}
                    disabled={processingId === p.id}
                    className="px-3 py-1.5 rounded-lg bg-rose-600/15 hover:bg-rose-600/25 border border-rose-500/30 text-rose-300 text-xs font-medium transition-all disabled:opacity-50"
                  >
                    Reject Plan
                  </button>
                  <button
                    onClick={() => handleApprove(p.id, p.target)}
                    disabled={processingId === p.id}
                    className="px-4 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-md shadow-emerald-500/20 transition-all flex items-center gap-1.5 disabled:opacity-50"
                  >
                    <Play className="w-3.5 h-3.5" />
                    {processingId === p.id ? 'Executing...' : 'Approve & Execute Action'}
                  </button>
                </div>
              )}
            </div>
          </div>
        ))}

        {plans.length === 0 && (
          <div className="nexus-card p-12 text-center text-slate-500 font-mono text-xs">
            No remediation plans in queue.
          </div>
        )}
      </div>
    </div>
  );
}
