import axios from 'axios';

const API_BASE = '/api';

export const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
});

export const nexusApi = {
  // Command Center Overview
  getOverview: () => api.get('/overview/'),

  // Live Infrastructure
  getNodes: () => api.get('/infrastructure/nodes'),
  getContainers: () => api.get('/infrastructure/containers'),
  getContainerStats: (id) => api.get(`/infrastructure/containers/${id}/stats`),
  getLiveMetrics: () => api.get('/infrastructure/metrics/live'),

  // Incidents
  getIncidents: (params) => api.get('/incidents/', { params }),
  getIncident: (id) => api.get(`/incidents/${id}`),
  triggerInvestigation: (id) => api.post(`/incidents/trigger-investigation/${id}`),
  simulateIncident: (params) => api.post('/incidents/simulate', null, { params }),

  // AI Agent Control Center
  getAgents: () => api.get('/agents/'),

  // Service Topology
  getTopology: () => api.get('/topology/'),

  // Remediation & Approvals
  getPlans: (status = 'PENDING') => api.get('/remediation/plans', { params: { status } }),
  approvePlan: (planId, approvedBy, comments) =>
    api.post(`/remediation/approve/${planId}`, { approved_by: approvedBy, comments }),
  rejectPlan: (planId, rejectedBy, reason) =>
    api.post(`/remediation/reject/${planId}`, { rejected_by: rejectedBy, reason }),

  // Knowledge & RAG
  getRunbooks: () => api.get('/knowledge/runbooks'),
  searchKnowledge: (query, category) => api.post('/knowledge/search', { query, category }),

  // Analytics
  getAnalytics: () => api.get('/analytics/'),

  // Audit Trail
  getAuditTrail: (params) => api.get('/audit/', { params }),

  // Integrations Status
  getIntegrationsStatus: () => api.get('/integrations/status'),
};

// WebSocket Service with Auto-Reconnect
class WebSocketClient {
  constructor() {
    this.ws = null;
    this.subscribers = new Set();
    this.reconnectTimer = null;
    this.isConnected = false;
  }

  connect() {
    if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) {
      return;
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/events`;

    try {
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        this.isConnected = true;
        this.notifySubscribers({ event: 'system_connection', payload: { connected: true } });
        if (this.reconnectTimer) {
          clearInterval(this.reconnectTimer);
          this.reconnectTimer = null;
        }
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.notifySubscribers(data);
        } catch (e) {
          console.debug('Raw WS message:', event.data);
        }
      };

      this.ws.onclose = () => {
        this.isConnected = false;
        this.notifySubscribers({ event: 'system_connection', payload: { connected: false } });
        this.scheduleReconnect();
      };

      this.ws.onerror = (err) => {
        console.warn('WebSocket connection error:', err);
        this.ws.close();
      };
    } catch (e) {
      console.warn('Failed to initiate WebSocket:', e);
      this.scheduleReconnect();
    }
  }

  scheduleReconnect() {
    if (!this.reconnectTimer) {
      this.reconnectTimer = setInterval(() => {
        this.connect();
      }, 5000);
    }
  }

  subscribe(callback) {
    this.subscribers.add(callback);
    return () => this.subscribers.delete(callback);
  }

  notifySubscribers(data) {
    this.subscribers.forEach((cb) => {
      try {
        cb(data);
      } catch (e) {
        console.error('Subscriber callback error:', e);
      }
    });
  }
}

export const wsClient = new WebSocketClient();
