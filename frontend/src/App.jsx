import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppProvider } from './context/AppContext';
import MainLayout from './layouts/MainLayout';

import CommandCenter from './pages/CommandCenter';
import LiveInfrastructure from './pages/LiveInfrastructure';
import IncidentManagement from './pages/IncidentManagement';
import IncidentIntelligence from './pages/IncidentIntelligence';
import AgentControlCenter from './pages/AgentControlCenter';
import ServiceDependencyMap from './pages/ServiceDependencyMap';
import AutonomousRemediation from './pages/AutonomousRemediation';
import KnowledgeIntelligence from './pages/KnowledgeIntelligence';
import AnalyticsDashboard from './pages/AnalyticsDashboard';
import AuditTrail from './pages/AuditTrail';
import IntegrationsConfig from './pages/IntegrationsConfig';

export default function App() {
  return (
    <AppProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<MainLayout />}>
            <Route path="/" element={<CommandCenter />} />
            <Route path="/infrastructure" element={<LiveInfrastructure />} />
            <Route path="/incidents" element={<IncidentManagement />} />
            <Route path="/intelligence" element={<IncidentIntelligence />} />
            <Route path="/agents" element={<AgentControlCenter />} />
            <Route path="/topology" element={<ServiceDependencyMap />} />
            <Route path="/remediation" element={<AutonomousRemediation />} />
            <Route path="/knowledge" element={<KnowledgeIntelligence />} />
            <Route path="/analytics" element={<AnalyticsDashboard />} />
            <Route path="/audit" element={<AuditTrail />} />
            <Route path="/integrations" element={<IntegrationsConfig />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AppProvider>
  );
}
