import React, { useState, useEffect } from 'react';
import {
  Layers,
  Activity,
  CheckCircle2,
  XCircle,
  RefreshCw,
  ExternalLink,
  Sliders,
  Server
} from 'lucide-react';
import { nexusApi } from '../services/api';
import { useApp } from '../context/AppContext';

export default function IntegrationsConfig() {
  const [integrations, setIntegrations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [testingId, setTestingId] = useState(null);
  const { addNotification } = useApp();

  const fetchIntegrations = async () => {
    try {
      const res = await nexusApi.getIntegrationsStatus();
      setIntegrations(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIntegrations();
  }, []);

  const handleTestConnection = async (item) => {
    setTestingId(item.id);
    try {
      await fetchIntegrations();
      addNotification({
        type: item.connected ? 'success' : 'danger',
        title: `${item.name} Health Check`,
        message: `Status: ${item.status}. Connection probe complete.`,
        timestamp: new Date().toLocaleTimeString()
      });
    } catch (e) {
      console.error(e);
    } finally {
      setTestingId(null);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-100 flex items-center gap-2.5">
            Observability & Infrastructure Integrations
            <span className="text-xs px-2.5 py-0.5 rounded-full font-mono bg-blue-500/10 text-blue-400 border border-blue-500/20">
              REAL CONNECTORS
            </span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Configure live endpoints for Prometheus, Grafana Loki, Docker Daemon, and OpenTelemetry.
          </p>
        </div>

        <button
          onClick={fetchIntegrations}
          className="px-3.5 py-2 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700/80 text-xs font-medium text-slate-300 transition-all flex items-center gap-2"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          Run Health Probes
        </button>
      </div>

      {/* Integrations Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {integrations.map((item) => (
          <div key={item.id} className="nexus-card p-6 flex flex-col justify-between">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-lg bg-slate-800 border border-slate-700 flex items-center justify-center font-bold text-xs text-blue-400">
                    {item.type.slice(0, 3)}
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-slate-100">{item.name}</h3>
                    <div className="text-[11px] text-slate-400 font-mono">{item.type}</div>
                  </div>
                </div>

                <span className={`text-[10px] font-mono px-2 py-0.5 rounded font-semibold border ${
                  item.connected
                    ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                    : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                }`}>
                  {item.status}
                </span>
              </div>

              <p className="text-xs text-slate-400">{item.description}</p>

              <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800/80 text-xs font-mono space-y-1">
                <span className="text-slate-500 text-[10px] uppercase block">Configured Endpoint</span>
                <div className="text-slate-300 truncate">{item.endpoint}</div>
              </div>
            </div>

            <div className="mt-5 pt-4 border-t border-slate-800/80 flex items-center justify-between">
              <span className="text-[11px] text-slate-500 font-mono">
                {item.connected ? 'Scraping Active' : 'Standby / Local Fallback'}
              </span>

              <button
                onClick={() => handleTestConnection(item)}
                disabled={testingId === item.id}
                className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs font-medium text-slate-200 transition-all flex items-center gap-1.5 disabled:opacity-50"
              >
                <Activity className={`w-3.5 h-3.5 ${testingId === item.id ? 'animate-spin' : ''}`} />
                {testingId === item.id ? 'Testing...' : 'Test Endpoint'}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
