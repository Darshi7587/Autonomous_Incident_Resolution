import React, { useState, useEffect } from 'react';
import {
  Server,
  Cpu,
  HardDrive,
  RefreshCw,
  Power,
  RotateCcw,
  CheckCircle2,
  AlertCircle,
  ExternalLink
} from 'lucide-react';
import { nexusApi } from '../services/api';
import { useApp } from '../context/AppContext';

export default function LiveInfrastructure() {
  const [nodes, setNodes] = useState([]);
  const [containers, setContainers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [restarting, setRestarting] = useState(null);
  const { addNotification } = useApp();

  const fetchInfrastructure = async () => {
    try {
      const [nodesRes, containersRes] = await Promise.all([
        nexusApi.getNodes(),
        nexusApi.getContainers()
      ]);
      setNodes(nodesRes.data);
      setContainers(containersRes.data);
    } catch (e) {
      console.error('Error fetching infrastructure:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInfrastructure();
    const interval = setInterval(fetchInfrastructure, 8000);
    return () => clearInterval(interval);
  }, []);

  const handleRestart = async (containerName) => {
    setRestarting(containerName);
    try {
      await nexusApi.approvePlan('manual', 'operator_admin', `Manual container restart for ${containerName}`);
      addNotification({
        type: 'success',
        title: 'Restart Signal Sent',
        message: `Restart dispatched to container ${containerName}.`,
        timestamp: new Date().toLocaleTimeString()
      });
      await fetchInfrastructure();
    } catch (e) {
      console.error(e);
    } finally {
      setRestarting(null);
    }
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-100 flex items-center gap-2.5">
            Live Infrastructure
            <span className="text-xs px-2.5 py-0.5 rounded-full font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              DISCOVERY ACTIVE
            </span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Real-time topology inventory: monitored hosts, containers, and live resource utilization.
          </p>
        </div>

        <button
          onClick={fetchInfrastructure}
          className="px-3.5 py-2 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700/80 text-xs font-medium text-slate-300 transition-all flex items-center gap-2"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          Refresh Inventory
        </button>
      </div>

      {/* Host Nodes Section */}
      <div>
        <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-3">Host Nodes</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {nodes.map((node) => (
            <div key={node.id} className="nexus-card p-5">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2.5">
                  <div className="w-8 h-8 rounded-lg bg-blue-500/10 text-blue-400 flex items-center justify-center">
                    <Server className="w-4 h-4" />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-slate-100">{node.name}</h3>
                    <div className="text-[11px] text-slate-400 font-mono">{node.type.toUpperCase()} • {node.ip_address || '127.0.0.1'}</div>
                  </div>
                </div>
                <span className={`text-[10px] font-mono px-2 py-0.5 rounded-full border ${
                  node.status === 'ONLINE'
                    ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                    : 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                }`}>
                  {node.status}
                </span>
              </div>
              <div className="text-xs text-slate-500 mt-4 flex items-center justify-between">
                <span>Last heartbeat</span>
                <span className="font-mono text-slate-400">
                  {node.last_seen ? new Date(node.last_seen).toLocaleTimeString() : 'Just now'}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Connected Containers Section */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">
            Docker Containers ({containers.length})
          </h2>
          <span className="text-xs text-slate-500 font-mono">Scraped via cAdvisor / Docker Engine API</span>
        </div>

        <div className="nexus-card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-900/60 border-b border-slate-800 text-slate-400 font-medium">
                <tr>
                  <th className="py-3 px-4">Container</th>
                  <th className="py-3 px-4">Image</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Restarts</th>
                  <th className="py-3 px-4">Ports</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {containers.map((c) => (
                  <tr key={c.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="py-3 px-4 font-mono font-medium text-slate-200">
                      {c.name}
                    </td>
                    <td className="py-3 px-4 text-slate-400 font-mono text-[11px] truncate max-w-xs">
                      {c.image}
                    </td>
                    <td className="py-3 px-4">
                      <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full font-mono text-[10px] border ${
                        c.status.startsWith('up') || c.status === 'running'
                          ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                          : 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                      }`}>
                        <span className={`w-1.5 h-1.5 rounded-full ${c.status.startsWith('up') || c.status === 'running' ? 'bg-emerald-400' : 'bg-rose-400'}`} />
                        {c.status}
                      </span>
                    </td>
                    <td className="py-3 px-4 font-mono text-slate-300">
                      <span className={c.restart_count > 0 ? 'text-amber-400 font-semibold' : 'text-slate-400'}>
                        {c.restart_count}
                      </span>
                    </td>
                    <td className="py-3 px-4 font-mono text-[11px] text-slate-400 truncate max-w-xs">
                      {Object.keys(c.ports || {}).join(', ') || 'internal'}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={() => handleRestart(c.name)}
                        disabled={restarting === c.name}
                        className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 hover:text-white transition-all text-[11px] font-medium inline-flex items-center gap-1.5 disabled:opacity-50"
                      >
                        <RotateCcw className={`w-3 h-3 ${restarting === c.name ? 'animate-spin' : ''}`} />
                        Restart
                      </button>
                    </td>
                  </tr>
                ))}
                {containers.length === 0 && (
                  <tr>
                    <td colSpan="6" className="py-8 text-center text-slate-500 font-mono">
                      No Docker containers discovered or Docker daemon standby.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
