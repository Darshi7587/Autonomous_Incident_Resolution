import React, { useState, useEffect } from 'react';
import {
  FileText,
  Search,
  Filter,
  RefreshCw,
  Shield,
  Bot,
  User,
  ExternalLink
} from 'lucide-react';
import { nexusApi } from '../services/api';

export default function AuditTrail() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchAction, setSearchAction] = useState('');
  const [selectedLog, setSelectedLog] = useState(null);

  const fetchAuditLogs = async () => {
    try {
      const params = {};
      if (searchAction.trim()) params.action = searchAction.trim();
      const res = await nexusApi.getAuditTrail(params);
      setLogs(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAuditLogs();
  }, [searchAction]);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-100 flex items-center gap-2.5">
            Audit Trail
            <span className="text-xs px-2.5 py-0.5 rounded-full font-mono bg-blue-500/10 text-blue-400 border border-blue-500/20">
              TAMPER-EVIDENT
            </span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Immutable log of all autonomous agent decisions, tool invocations, human approvals, and configuration changes.
          </p>
        </div>

        <button
          onClick={fetchAuditLogs}
          className="px-3.5 py-2 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700/80 text-xs font-medium text-slate-300 transition-all flex items-center gap-2"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          Refresh Audit
        </button>
      </div>

      {/* Search Input */}
      <div className="nexus-card p-4">
        <div className="relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search audit trail by action (e.g. 'APPROVE', 'RESTART', 'DISCOVER')..."
            value={searchAction}
            onChange={(e) => setSearchAction(e.target.value)}
            className="w-full bg-slate-900/80 border border-slate-700 rounded-lg pl-10 pr-4 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors"
          />
        </div>
      </div>

      {/* Audit Log Table */}
      <div className="nexus-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/60 border-b border-slate-800 text-slate-400 font-medium">
              <tr>
                <th className="py-3 px-4">Timestamp</th>
                <th className="py-3 px-4">Actor</th>
                <th className="py-3 px-4">Action</th>
                <th className="py-3 px-4">Target Resource</th>
                <th className="py-3 px-4">Origin IP</th>
                <th className="py-3 px-4 text-right">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {logs.map((log) => {
                const isAgent = log.actor.includes('Agent');
                return (
                  <tr key={log.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="py-3 px-4 text-slate-400 text-[11px] whitespace-nowrap">
                      {log.timestamp ? new Date(log.timestamp).toLocaleString() : 'Recent'}
                    </td>
                    <td className="py-3 px-4 font-sans font-semibold">
                      <div className="flex items-center gap-1.5">
                        {isAgent ? (
                          <Bot className="w-3.5 h-3.5 text-indigo-400" />
                        ) : (
                          <User className="w-3.5 h-3.5 text-blue-400" />
                        )}
                        <span className={isAgent ? 'text-indigo-300' : 'text-blue-300'}>{log.actor}</span>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-emerald-400 font-semibold text-[11px]">
                      {log.action}
                    </td>
                    <td className="py-3 px-4 text-slate-300 text-[11px] truncate max-w-xs">
                      {log.target_type}:{log.target_id || ''}
                    </td>
                    <td className="py-3 px-4 text-slate-500 text-[11px]">
                      {log.ip_address || '127.0.0.1'}
                    </td>
                    <td className="py-3 px-4 text-right font-sans">
                      <button
                        onClick={() => setSelectedLog(log)}
                        className="px-2 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 text-[10px]"
                      >
                        Inspect
                      </button>
                    </td>
                  </tr>
                );
              })}
              {logs.length === 0 && (
                <tr>
                  <td colSpan="6" className="py-12 text-center text-slate-500">
                    No audit records matching query.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Details Modal */}
      {selectedLog && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="nexus-card p-6 max-w-lg w-full space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <Shield className="w-4 h-4 text-blue-400" />
                Audit Record Payload Inspection
              </h3>
              <button
                onClick={() => setSelectedLog(null)}
                className="text-slate-400 hover:text-white text-xs font-bold px-2 py-1 rounded bg-slate-800"
              >
                ✕
              </button>
            </div>

            <div className="space-y-2 text-xs font-mono">
              <div><span className="text-slate-500">Record ID:</span> <span className="text-slate-300">{selectedLog.id}</span></div>
              <div><span className="text-slate-500">Actor:</span> <span className="text-blue-400">{selectedLog.actor}</span></div>
              <div><span className="text-slate-500">Action:</span> <span className="text-emerald-400">{selectedLog.action}</span></div>
              <div><span className="text-slate-500">Timestamp:</span> <span className="text-slate-300">{selectedLog.timestamp}</span></div>
            </div>

            <div>
              <span className="text-[10px] text-slate-500 uppercase font-mono block mb-1">Payload JSON</span>
              <pre className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-[11px] font-mono text-cyan-300 overflow-x-auto max-h-48">
                {JSON.stringify(selectedLog.details, null, 2)}
              </pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
