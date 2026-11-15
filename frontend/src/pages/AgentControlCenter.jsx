import React, { useState, useEffect } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap
} from 'reactflow';
import 'reactflow/dist/style.css';
import {
  Bot,
  Activity,
  CheckCircle2,
  Cpu,
  Clock,
  Layers,
  RefreshCw,
  Zap,
  ArrowRight
} from 'lucide-react';
import { nexusApi } from '../services/api';

const initialNodes = [
  { id: '1', position: { x: 50, y: 50 }, data: { label: '1. Discovery Agent' }, style: { background: '#1E293B', color: '#93C5FD', border: '1px solid #3B82F6', borderRadius: '8px', fontSize: '11px', padding: '8px' } },
  { id: '2', position: { x: 230, y: 50 }, data: { label: '2. Monitoring Agent' }, style: { background: '#1E293B', color: '#93C5FD', border: '1px solid #3B82F6', borderRadius: '8px', fontSize: '11px', padding: '8px' } },
  { id: '3', position: { x: 410, y: 50 }, data: { label: '3. Anomaly Detection' }, style: { background: '#1E293B', color: '#A5B4FC', border: '1px solid #6366F1', borderRadius: '8px', fontSize: '11px', padding: '8px' } },
  { id: '4', position: { x: 590, y: 50 }, data: { label: '4. Log Intelligence' }, style: { background: '#1E293B', color: '#67E8F9', border: '1px solid #06B6D4', borderRadius: '8px', fontSize: '11px', padding: '8px' } },

  { id: '8', position: { x: 50, y: 160 }, data: { label: '8. Service Dependency' }, style: { background: '#1E293B', color: '#CBD5E1', border: '1px solid #475569', borderRadius: '8px', fontSize: '11px', padding: '8px' } },
  { id: '9', position: { x: 230, y: 160 }, data: { label: '9. Deployment Analysis' }, style: { background: '#1E293B', color: '#CBD5E1', border: '1px solid #475569', borderRadius: '8px', fontSize: '11px', padding: '8px' } },
  { id: '5', position: { x: 410, y: 160 }, data: { label: '5. Correlation Agent' }, style: { background: '#1E293B', color: '#FDE047', border: '1px solid #EAB308', borderRadius: '8px', fontSize: '11px', padding: '8px' } },
  { id: '7', position: { x: 590, y: 160 }, data: { label: '7. Knowledge RAG' }, style: { background: '#1E293B', color: '#C4B5FD', border: '1px solid #8B5CF6', borderRadius: '8px', fontSize: '11px', padding: '8px' } },

  { id: '6', position: { x: 140, y: 270 }, data: { label: '6. Root Cause (RCA)' }, style: { background: '#1E293B', color: '#F472B6', border: '1px solid #EC4899', borderRadius: '8px', fontSize: '11px', padding: '8px' } },
  { id: '10', position: { x: 320, y: 270 }, data: { label: '10. Security & Risk' }, style: { background: '#1E293B', color: '#FB923C', border: '1px solid #F97316', borderRadius: '8px', fontSize: '11px', padding: '8px' } },
  { id: '11', position: { x: 500, y: 270 }, data: { label: '11. Remediation Plan' }, style: { background: '#1E293B', color: '#34D399', border: '1px solid #10B981', borderRadius: '8px', fontSize: '11px', padding: '8px' } },

  { id: '12', position: { x: 230, y: 380 }, data: { label: '12. Autonomous Execution' }, style: { background: '#1E293B', color: '#6EE7B7', border: '1px solid #059669', borderRadius: '8px', fontSize: '11px', padding: '8px' } },
  { id: '13', position: { x: 410, y: 380 }, data: { label: '13. Validation & Recovery' }, style: { background: '#1E293B', color: '#38BDF8', border: '1px solid #0284C7', borderRadius: '8px', fontSize: '11px', padding: '8px' } }
];

const initialEdges = [
  { id: 'e1-2', source: '1', target: '2', animated: true },
  { id: 'e2-3', source: '2', target: '3', animated: true },
  { id: 'e3-4', source: '3', target: '4', animated: true },
  { id: 'e4-8', source: '4', target: '8', animated: true },
  { id: 'e8-9', source: '8', target: '9', animated: true },
  { id: 'e9-5', source: '9', target: '5', animated: true },
  { id: 'e5-7', source: '5', target: '7', animated: true },
  { id: 'e7-6', source: '7', target: '6', animated: true },
  { id: 'e6-10', source: '6', target: '10', animated: true },
  { id: 'e10-11', source: '10', target: '11', animated: true },
  { id: 'e11-12', source: '11', target: '12', animated: true, label: 'Approval Gate' },
  { id: 'e12-13', source: '12', target: '13', animated: true }
];

export default function AgentControlCenter() {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchAgents = async () => {
    try {
      const res = await nexusApi.getAgents();
      setAgents(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAgents();
  }, []);

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-100 flex items-center gap-2.5">
            AI Agent Control Center
            <span className="text-xs px-2.5 py-0.5 rounded-full font-mono bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              13 AGENTS ACTIVE
            </span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Specialized multi-agent cognitive architecture orchestrated with LangGraph state machine.
          </p>
        </div>

        <button
          onClick={fetchAgents}
          className="px-3.5 py-2 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700/80 text-xs font-medium text-slate-300 transition-all flex items-center gap-2"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          Refresh Agents
        </button>
      </div>

      {/* Interactive LangGraph React Flow Canvas */}
      <div className="nexus-card p-4">
        <div className="flex items-center justify-between mb-2 px-2">
          <span className="text-xs font-bold text-slate-200 uppercase tracking-wider">
            Live Cognitive Workflow Orchestration (LangGraph State Machine)
          </span>
          <span className="text-[11px] font-mono text-slate-400">Drag & Zoom to Explore Topology</span>
        </div>
        <div className="h-96 rounded-lg bg-slate-950/70 border border-slate-800/80 overflow-hidden">
          <ReactFlow nodes={initialNodes} edges={initialEdges} fitView>
            <Background color="#1E293B" gap={16} />
            <Controls className="fill-slate-400" />
            <MiniMap nodeColor="#3B82F6" maskColor="rgba(11, 15, 25, 0.8)" style={{ background: '#0F172A' }} />
          </ReactFlow>
        </div>
      </div>

      {/* Agents Catalog Grid */}
      <div>
        <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-4">
          Autonomous Agents Roster
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {agents.map((agent) => (
            <div key={agent.id} className="nexus-card p-5 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2.5">
                    <div className="w-8 h-8 rounded-lg bg-indigo-500/10 text-indigo-400 flex items-center justify-center">
                      <Bot className="w-4 h-4" />
                    </div>
                    <div>
                      <h3 className="text-sm font-bold text-slate-100">{agent.name}</h3>
                      <div className="text-[10px] text-slate-500 font-mono">{agent.id.toUpperCase()}</div>
                    </div>
                  </div>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    {agent.status}
                  </span>
                </div>

                <p className="text-xs text-slate-400 leading-relaxed">
                  {agent.responsibility}
                </p>

                <div className="mt-3 p-2 rounded bg-slate-900/60 border border-slate-800/60 text-[11px] font-mono text-slate-300">
                  <span className="text-slate-500 block text-[10px] uppercase">Current Task:</span>
                  {agent.current_task}
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-[11px] font-mono text-slate-400">
                <span>Avg: {agent.avg_duration_ms}ms</span>
                <span>Errors: {agent.errors_count}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
