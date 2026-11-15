import React, { useState, useEffect } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap
} from 'reactflow';
import 'reactflow/dist/style.css';
import { Network, RefreshCw, Layers, ShieldAlert, CheckCircle2 } from 'lucide-react';
import { nexusApi } from '../services/api';

export default function ServiceDependencyMap() {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchTopology = async () => {
    try {
      const res = await nexusApi.getTopology();
      setNodes(res.data.nodes || []);
      setEdges(res.data.edges || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTopology();
    const interval = setInterval(fetchTopology, 8000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-100 flex items-center gap-2.5">
            Service Dependency Map
            <span className="text-xs px-2.5 py-0.5 rounded-full font-mono bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
              BLAST RADIUS TOPOLOGY
            </span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Dynamic service-to-service graph highlighting upstream dependencies and downstream cascading blast radius.
          </p>
        </div>

        <button
          onClick={fetchTopology}
          className="px-3.5 py-2 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700/80 text-xs font-medium text-slate-300 transition-all flex items-center gap-2"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          Refresh Graph
        </button>
      </div>

      {/* Main React Flow Graph Canvas */}
      <div className="nexus-card p-4">
        <div className="flex items-center justify-between mb-3 px-2 text-xs">
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1.5 text-slate-300">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-400" /> Healthy Nodes
            </span>
            <span className="flex items-center gap-1.5 text-red-400">
              <span className="w-2.5 h-2.5 rounded-full bg-red-400 animate-ping" /> Degraded / Blast Radius
            </span>
          </div>
          <span className="font-mono text-slate-400">Interactive Canvas • Drag, Pan & Zoom</span>
        </div>

        <div className="h-[550px] rounded-xl bg-slate-950/80 border border-slate-800/80 overflow-hidden relative">
          <ReactFlow nodes={nodes} edges={edges} fitView>
            <Background color="#1E293B" gap={20} />
            <Controls className="fill-slate-400" />
            <MiniMap
              nodeColor={(node) => (node.data?.status === 'CRITICAL' ? '#EF4444' : '#10B981')}
              maskColor="rgba(11, 15, 25, 0.85)"
              style={{ background: '#0F172A' }}
            />
          </ReactFlow>
        </div>
      </div>
    </div>
  );
}
