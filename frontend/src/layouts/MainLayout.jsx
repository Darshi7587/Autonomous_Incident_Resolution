import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import {
  LayoutDashboard,
  Server,
  AlertOctagon,
  Cpu,
  Bot,
  Network,
  ShieldCheck,
  BookOpen,
  BarChart3,
  FileText,
  Layers,
  Radio,
  CheckCircle2,
  AlertTriangle,
  XCircle
} from 'lucide-react';
import { useApp } from '../context/AppContext';

const NAV_ITEMS = [
  { path: '/', label: 'Command Center', icon: LayoutDashboard },
  { path: '/infrastructure', label: 'Live Infrastructure', icon: Server },
  { path: '/incidents', label: 'Incident Management', icon: AlertOctagon },
  { path: '/intelligence', label: 'Incident Intelligence', icon: Cpu },
  { path: '/agents', label: 'AI Agent Control', icon: Bot },
  { path: '/topology', label: 'Service Dependency', icon: Network },
  { path: '/remediation', label: 'Remediation & Approval', icon: ShieldCheck },
  { path: '/knowledge', label: 'Knowledge & RAG', icon: BookOpen },
  { path: '/analytics', label: 'AIOps Analytics', icon: BarChart3 },
  { path: '/audit', label: 'Audit Trail', icon: FileText },
  { path: '/integrations', label: 'Integrations', icon: Layers },
];

export default function MainLayout() {
  const { wsConnected, notifications, integrationsHealth } = useApp();

  return (
    <div className="flex h-screen bg-[#0B0F19] text-slate-100 overflow-hidden font-sans">
      {/* Sidebar Navigation */}
      <aside className="w-64 bg-[#0E1322] border-r border-slate-800/80 flex flex-col z-20 select-none">
        {/* Brand Header */}
        <div className="h-16 flex items-center px-6 border-b border-slate-800/80 gap-3">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-blue-600 via-indigo-600 to-cyan-500 flex items-center justify-center shadow-lg shadow-blue-500/20">
            <Radio className="w-5 h-5 text-white animate-pulse" />
          </div>
          <div>
            <span className="font-bold text-lg tracking-wider bg-gradient-to-r from-blue-400 via-cyan-300 to-indigo-300 bg-clip-text text-transparent">
              NEXUS AI
            </span>
            <div className="text-[10px] tracking-widest text-slate-400 font-mono">AUTONOMOUS AIOPS</div>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-1">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                end={item.path === '/'}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 ${
                    isActive
                      ? 'bg-blue-600/15 text-blue-400 border border-blue-500/30 shadow-sm shadow-blue-500/10'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                  }`
                }
              >
                <Icon className="w-4 h-4 flex-shrink-0" />
                <span className="truncate">{item.label}</span>
              </NavLink>
            );
          })}
        </nav>

        {/* Workspace Health Indicator */}
        <div className="p-4 border-t border-slate-800/80 bg-slate-900/40">
          <div className="flex items-center justify-between text-xs mb-2">
            <span className="text-slate-400">Stream Connection</span>
            <span className="flex items-center gap-1.5 font-mono text-[11px]">
              <span
                className={`w-2 h-2 rounded-full ${
                  wsConnected ? 'bg-emerald-400 animate-pulse' : 'bg-rose-500'
                }`}
              />
              <span className={wsConnected ? 'text-emerald-400' : 'text-rose-400'}>
                {wsConnected ? 'LIVE' : 'STANDBY'}
              </span>
            </span>
          </div>
          <div className="text-[11px] text-slate-500 font-mono truncate">
            Core: 13 Autonomous Agents
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Header Bar */}
        <header className="h-16 bg-[#0E1322]/80 backdrop-blur-md border-b border-slate-800/80 px-8 flex items-center justify-between z-10">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 px-3 py-1 bg-slate-800/60 rounded-full border border-slate-700/60 text-xs font-mono text-slate-300">
              <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
              <span>Real-Time Observability Engine</span>
            </div>
            <div className="hidden md:flex items-center gap-3 text-xs text-slate-400 font-mono">
              <span className="flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-blue-400" /> PromQL: Active
              </span>
              <span className="flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-indigo-400" /> Loki: LogQL
              </span>
              <span className="flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" /> Docker: Online
              </span>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="text-right">
              <div className="text-sm font-semibold text-slate-200">Darshitha S R</div>
              <div className="text-[11px] text-blue-400 font-mono">Senior AIOps Engineer</div>
            </div>
            <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center font-bold text-sm text-white shadow-md border border-slate-700">
              DS
            </div>
          </div>
        </header>

        {/* Page Content Viewport */}
        <main className="flex-1 overflow-y-auto p-8 relative">
          <Outlet />

          {/* Toast Notification Stack */}
          <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-2 max-w-sm pointer-events-none">
            {notifications.map((notif) => (
              <div
                key={notif.id}
                className={`pointer-events-auto p-4 rounded-xl border backdrop-blur-lg shadow-xl transition-all duration-300 flex items-start gap-3 ${
                  notif.type === 'danger'
                    ? 'bg-rose-950/80 border-rose-800/80 text-rose-200'
                    : notif.type === 'success'
                    ? 'bg-emerald-950/80 border-emerald-800/80 text-emerald-200'
                    : 'bg-slate-900/90 border-slate-700 text-slate-200'
                }`}
              >
                {notif.type === 'danger' ? (
                  <AlertTriangle className="w-5 h-5 text-rose-400 flex-shrink-0 mt-0.5" />
                ) : notif.type === 'success' ? (
                  <CheckCircle2 className="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" />
                ) : (
                  <Radio className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
                )}
                <div>
                  <div className="font-semibold text-xs tracking-wide">{notif.title}</div>
                  <div className="text-xs text-slate-300 mt-0.5">{notif.message}</div>
                  <div className="text-[10px] text-slate-400 mt-1 font-mono">{notif.timestamp}</div>
                </div>
              </div>
            ))}
          </div>
        </main>
      </div>
    </div>
  );
}
