import React, { createContext, useContext, useState, useEffect } from 'react';
import { wsClient, nexusApi } from '../services/api';

const AppContext = createContext();

export const AppProvider = ({ children }) => {
  const [wsConnected, setWsConnected] = useState(false);
  const [liveIncidents, setLiveIncidents] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [integrationsHealth, setIntegrationsHealth] = useState([]);

  useEffect(() => {
    wsClient.connect();

    const unsubscribe = wsClient.subscribe((msg) => {
      if (msg.event === 'system_connection') {
        setWsConnected(msg.payload.connected);
      } else if (msg.event === 'new_incident') {
        addNotification({
          type: 'danger',
          title: 'New Incident Detected',
          message: msg.payload.title,
          timestamp: new Date().toLocaleTimeString()
        });
      } else if (msg.event === 'incident_resolved') {
        addNotification({
          type: 'success',
          title: 'Incident Resolved',
          message: `Incident ${msg.payload.incident_id.slice(0, 8)}... verified & resolved.`,
          timestamp: new Date().toLocaleTimeString()
        });
      }
    });

    // Initial integrations check
    nexusApi.getIntegrationsStatus()
      .then(res => setIntegrationsHealth(res.data))
      .catch(err => console.debug('Failed to fetch integrations:', err));

    return () => unsubscribe();
  }, []);

  const addNotification = (notif) => {
    const id = Date.now();
    setNotifications((prev) => [{ id, ...notif }, ...prev.slice(0, 7)]);
    setTimeout(() => {
      setNotifications((prev) => prev.filter((n) => n.id !== id));
    }, 6000);
  };

  return (
    <AppContext.Provider
      value={{
        wsConnected,
        notifications,
        addNotification,
        integrationsHealth,
        setIntegrationsHealth
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => useContext(AppContext);
