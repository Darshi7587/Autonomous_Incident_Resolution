import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  AlertOctagon,
  Search,
  Filter,
  RefreshCw,
  ArrowRight,
  ShieldAlert,
  Clock,
  Sparkles
} from 'lucide-react';
import { nexusApi } from '../services/api';

const SEVERITIES = ['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];
const STATUSES = ['ALL', 'NEW', 'INVESTIGATING', 'RCA_COMPLETED', 'AWAITING_APPROVAL', 'REMEDIATING', 'VERIFYING', 'RESOLVED', 'ESCALATED'];

export default function IncidentManagement() {
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedSeverity, setSelectedSeverity] = useState('ALL');
  const [selectedStatus, setSelectedStatus] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();

  const fetchIncidents = async () => {
    try {
      const params = {};
      if (selectedSeverity !== 'ALL') params.severity = selectedSeverity;
      if (selectedStatus !== 'ALL') params.status = selectedStatus;
      if (searchQuery.trim()) params.search = searchQuery.trim();

      const res = await nexusApi.getIncidents(params);
      setIncidents(res.data);
    } catch (e) {
      console.error('Error fetching incidents:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIncidents();
    const interval = setInterval(fetchIncidents, 6000);
    return () => clearInterval(interval);
  }, [selectedSeverity, selectedStatus, searchQuery]);

  const getSeverityBadge = (sev) => {
    switch (sev) {
      case 'CRITICAL':
        return 'bg-red-500/10 text-red-400 border-red-500/20';
      case 'HIGH':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/20';
      case 'MEDIUM':
        return 'bg-blue-500/10 text-blue-400 border-blue-500/20';
      default:
        return 'bg-slate-500/10 text-slate-400 border-slate-500/20';
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'RESOLVED':
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
      case 'AWAITING_APPROVAL':
        return 'bg-purple-500/10 text-purple-400 border-purple-500/20 animate-pulse';
      case 'REMEDIATING':
      case 'VERIFYING':
        return 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20 animate-pulse';
      case 'ESCALATED':
        return 'bg-rose-500/10 text-rose-400 border-rose-500/20 font-bold';
      default:
        return 'bg-slate-500/10 text-slate-300 border-slate-700';
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-100 flex items-center gap-2.5">
            Incident Management
            <span className="text-xs px-2.5 py-0.5 rounded-full font-mono bg-blue-500/10 text-blue-400 border border-blue-500/20">
              {incidents.length} TOTAL
            </span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Centrally correlated incidents across distributed infrastructure and microservices.
          </p>
        </div>

        <button
          onClick={fetchIncidents}
          className="px-3.5 py-2 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700/80 text-xs font-medium text-slate-300 transition-all flex items-center gap-2"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="nexus-card p-4 space-y-3">
        <div className="flex flex-col md:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search incidents by title, description or resource..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-slate-900/80 border border-slate-700/80 rounded-lg pl-10 pr-4 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors"
            />
          </div>

          <div className="flex items-center gap-2 overflow-x-auto pb-1 md:pb-0">
            <span className="text-xs text-slate-400 flex items-center gap-1 flex-shrink-0">
              <Filter className="w-3.5 h-3.5" /> Severity:
            </span>
            {SEVERITIES.map((sev) => (
              <button
                key={sev}
                onClick={() => setSelectedSeverity(sev)}
                className={`px-2.5 py-1 rounded text-[11px] font-mono transition-all ${
                  selectedSeverity === sev
                    ? 'bg-blue-600 text-white font-semibold shadow-sm'
                    : 'bg-slate-800/60 text-slate-400 hover:text-slate-200 hover:bg-slate-700/60'
                }`}
              >
                {sev}
              </button>
            ))}
          </div>
        </div>

        {/* Status Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto pt-2 border-t border-slate-800/60">
          <span className="text-[11px] text-slate-400 mr-2 flex-shrink-0">Status:</span>
          {STATUSES.map((st) => (
            <button
              key={st}
              onClick={() => setSelectedStatus(st)}
              className={`px-2 py-0.5 rounded text-[10px] font-mono whitespace-nowrap transition-all ${
                selectedStatus === st
                  ? 'bg-indigo-600/30 text-indigo-300 border border-indigo-500/40 font-semibold'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {st}
            </button>
          ))}
        </div>
      </div>

      {/* Incidents Table */}
      <div className="nexus-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/60 border-b border-slate-800 text-slate-400 font-medium">
              <tr>
                <th className="py-3 px-4">Severity</th>
                <th className="py-3 px-4">Incident Title & Details</th>
                <th className="py-3 px-4">Affected Resources</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Confidence</th>
                <th className="py-3 px-4">Detected</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {incidents.map((inc) => (
                <tr
                  key={inc.id}
                  onClick={() => navigate(`/intelligence?id=${inc.id}`)}
                  className="hover:bg-slate-800/40 transition-colors cursor-pointer group"
                >
                  <td className="py-3 px-4">
                    <span className={`inline-block px-2 py-0.5 rounded font-mono text-[10px] font-semibold border ${getSeverityBadge(inc.severity)}`}>
                      {inc.severity}
                    </span>
                  </td>
                  <td className="py-3 px-4 max-w-md">
                    <div className="font-semibold text-slate-100 group-hover:text-blue-400 transition-colors">
                      {inc.title}
                    </div>
                    <div className="text-[11px] text-slate-400 mt-0.5 line-clamp-1">
                      {inc.description}
                    </div>
                  </td>
                  <td className="py-3 px-4 font-mono text-[11px] text-slate-300">
                    <div className="flex flex-wrap gap-1">
                      {(inc.affected_resources || []).map((res) => (
                        <span key={res} className="px-1.5 py-0.5 rounded bg-slate-800 border border-slate-700/60 text-slate-300">
                          {res}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="py-3 px-4">
                    <span className={`inline-block px-2 py-0.5 rounded font-mono text-[10px] border ${getStatusBadge(inc.status)}`}>
                      {inc.status}
                    </span>
                  </td>
                  <td className="py-3 px-4 font-mono text-cyan-400">
                    {inc.confidence_score ? `${Math.round(inc.confidence_score * 100)}%` : '85%'}
                  </td>
                  <td className="py-3 px-4 font-mono text-slate-400 whitespace-nowrap">
                    {inc.detection_time ? new Date(inc.detection_time).toLocaleTimeString() : 'N/A'}
                  </td>
                  <td className="py-3 px-4 text-right">
                    <button className="px-2.5 py-1 rounded bg-blue-600/10 hover:bg-blue-600/20 text-blue-400 border border-blue-500/20 text-xs font-medium inline-flex items-center gap-1 transition-all">
                      Investigate <ArrowRight className="w-3 h-3" />
                    </button>
                  </td>
                </tr>
              ))}
              {incidents.length === 0 && (
                <tr>
                  <td colSpan="7" className="py-12 text-center text-slate-500 font-mono">
                    No incidents match the active filters. Cluster healthy.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
