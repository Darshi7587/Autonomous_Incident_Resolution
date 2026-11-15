import React, { useState, useEffect } from 'react';
import {
  BookOpen,
  Search,
  Sparkles,
  RefreshCw,
  Tag,
  Shield,
  CheckCircle2,
  Database
} from 'lucide-react';
import { nexusApi } from '../services/api';

export default function KnowledgeIntelligence() {
  const [runbooks, setRunbooks] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState(null);
  const [searching, setSearching] = useState(false);
  const [loading, setLoading] = useState(true);

  const fetchRunbooks = async () => {
    try {
      const res = await nexusApi.getRunbooks();
      setRunbooks(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRunbooks();
  }, []);

  const handleSemanticSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    setSearching(true);
    try {
      const res = await nexusApi.searchKnowledge(searchQuery.trim());
      setSearchResults(res.data.matches || []);
    } catch (e) {
      console.error(e);
    } finally {
      setSearching(false);
    }
  };

  const displayedList = searchResults !== null ? searchResults : runbooks;

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-100 flex items-center gap-2.5">
            Knowledge Intelligence (ChromaDB RAG)
            <span className="text-xs px-2.5 py-0.5 rounded-full font-mono bg-purple-500/10 text-purple-400 border border-purple-500/20">
              COLLECTION: it_runbooks
            </span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Semantic vector embeddings (Sentence Transformers) over IT operations runbooks, historical RCAs, and SOPs.
          </p>
        </div>

        <button
          onClick={() => { setSearchResults(null); setSearchQuery(''); fetchRunbooks(); }}
          className="px-3.5 py-2 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700/80 text-xs font-medium text-slate-300 transition-all flex items-center gap-2"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          Reset Search
        </button>
      </div>

      {/* Semantic Vector Search Box */}
      <div className="nexus-card p-6 border-t-2 border-t-purple-500">
        <form onSubmit={handleSemanticSearch} className="space-y-3">
          <div className="flex items-center gap-2 text-xs text-purple-400 font-semibold uppercase tracking-wider">
            <Sparkles className="w-4 h-4" />
            Semantic Similarity Vector Query
          </div>
          <div className="flex gap-3">
            <div className="relative flex-1">
              <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Enter symptoms or scenario e.g. 'high cpu thread lock', 'database out of connection pool', 'memory leak'..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-slate-900/80 border border-slate-700 rounded-lg pl-10 pr-4 py-2.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-purple-500 transition-colors font-mono"
              />
            </div>
            <button
              type="submit"
              disabled={searching}
              className="px-5 py-2.5 rounded-lg bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-medium text-xs shadow-md shadow-purple-500/20 transition-all flex items-center gap-2 disabled:opacity-50"
            >
              <Sparkles className={`w-3.5 h-3.5 ${searching ? 'animate-spin' : ''}`} />
              {searching ? 'Querying...' : 'Semantic Search'}
            </button>
          </div>
          <div className="text-[11px] text-slate-500 font-mono">
            Powered by ChromaDB cosine similarity ranking against it_runbooks vector space.
          </div>
        </form>
      </div>

      {/* Runbook Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {displayedList.map((rb) => (
          <div key={rb.id} className="nexus-card p-6 flex flex-col justify-between">
            <div className="space-y-3">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <div className="flex items-center gap-2 font-mono text-[11px] text-slate-400">
                    <span>ID: {rb.id}</span>
                    <span>•</span>
                    <span className="uppercase text-purple-400">{rb.category}</span>
                  </div>
                  <h3 className="text-base font-bold text-slate-100 mt-1">{rb.title}</h3>
                </div>

                <div className="flex flex-col items-end gap-1 flex-shrink-0">
                  <span className={`text-[10px] font-mono px-2 py-0.5 rounded uppercase font-semibold border ${
                    rb.risk_level === 'HIGH'
                      ? 'bg-red-500/10 text-red-400 border-red-500/20'
                      : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                  }`}>
                    {rb.risk_level} RISK
                  </span>
                  {rb.similarity_score && (
                    <span className="text-[10px] font-mono text-cyan-400">
                      Match: {Math.round(rb.similarity_score * 100)}%
                    </span>
                  )}
                </div>
              </div>

              <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800 text-xs text-slate-300 leading-relaxed font-mono whitespace-pre-line">
                {rb.content || rb.document}
              </div>

              <div className="space-y-1.5 text-xs pt-2">
                <div className="flex items-center gap-2">
                  <span className="text-slate-500 font-medium">Action:</span>
                  <span className="font-mono text-emerald-400 font-semibold">{rb.recommended_action}</span>
                </div>
                <div className="flex items-start gap-2">
                  <span className="text-slate-500 font-medium flex-shrink-0">Verification:</span>
                  <span className="text-slate-300 text-[11px]">{rb.verification_criteria}</span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
