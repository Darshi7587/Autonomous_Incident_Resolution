import logging
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from backend.database.models import Alert, Incident, IncidentEvent, ServiceDependency

logger = logging.getLogger("nexus.correlation")

class IncidentCorrelator:
    """
    Intelligent Alert Correlation and Incident Synthesis Engine.
    Correlates disparate metric anomalies across services by:
    1. Temporal proximity (sliding time window correlation).
    2. Topological graph dependency tracing.
    3. Resource co-locality.
    """
    def __init__(self, correlation_window_seconds: int = 180):
        self.correlation_window_seconds = correlation_window_seconds

    def correlate_alert(self, alert_data: Dict[str, Any], session: Session) -> Dict[str, Any]:
        """
        Process a newly detected anomaly.
        Determines whether to attach to an existing active Incident or initiate a new one.
        """
        now = datetime.now(timezone.utc)
        cutoff_time = now - timedelta(seconds=self.correlation_window_seconds)

        # 1. Fetch active incidents within the correlation window
        active_incidents = session.query(Incident).filter(
            Incident.status.in_(["NEW", "INVESTIGATING", "RCA_COMPLETED", "AWAITING_APPROVAL"]),
            Incident.detection_time >= cutoff_time
        ).order_by(Incident.detection_time.desc()).all()

        target_service = alert_data.get("service") or alert_data.get("resource", "cluster")
        correlated_incident = None

        # 2. Check topological dependencies
        dependencies = session.query(ServiceDependency).all()
        related_services = {target_service}
        for dep in dependencies:
            if dep.upstream_service == target_service:
                related_services.add(dep.downstream_service)
            elif dep.downstream_service == target_service:
                related_services.add(dep.upstream_service)

        for inc in active_incidents:
            inc_resources = set(inc.affected_resources or [])
            if inc_resources.intersection(related_services):
                correlated_incident = inc
                break

        # 3. If correlated, attach alert to existing incident
        if correlated_incident:
            alert = Alert(
                fingerprint=alert_data.get("fingerprint", str(uuid.uuid4())),
                incident_id=correlated_incident.id,
                title=alert_data.get("title", f"Anomaly detected in {target_service}"),
                severity=alert_data.get("severity", "WARNING"),
                metric_name=alert_data.get("metric_name", "unknown_metric"),
                current_value=float(alert_data.get("current_value", 0.0)),
                baseline_value=float(alert_data.get("baseline_value", 0.0)) if alert_data.get("baseline_value") is not None else None,
                anomaly_score=float(alert_data.get("anomaly_score", 0.0)) if alert_data.get("anomaly_score") is not None else None,
                source=alert_data.get("source", "Prometheus"),
                status="CORRELATED"
            )
            session.add(alert)

            current_resources = list(correlated_incident.affected_resources or [])
            if target_service not in current_resources:
                current_resources.append(target_service)
                correlated_incident.affected_resources = current_resources

            if alert_data.get("severity") == "CRITICAL" and correlated_incident.severity != "CRITICAL":
                correlated_incident.severity = "CRITICAL"
                correlated_incident.priority = "P1"

            event = IncidentEvent(
                incident_id=correlated_incident.id,
                event_type="CORRELATED_ALERT_ATTACHED",
                message=f"Correlated related alert '{alert.title}' to incident ({target_service} in dependency chain).",
                agent_name="Incident Correlation Agent",
                payload_json={"alert_id": alert.id, "metric": alert.metric_name, "value": alert.current_value}
            )
            session.add(event)
            session.commit()
            session.refresh(correlated_incident)

            return {
                "action": "ATTACHED_TO_EXISTING_INCIDENT",
                "incident_id": correlated_incident.id,
                "incident_title": correlated_incident.title,
                "severity": correlated_incident.severity,
                "affected_resources": correlated_incident.affected_resources
            }

        # 4. Otherwise, construct a new correlated incident
        new_incident_id = str(uuid.uuid4())
        severity = alert_data.get("severity", "MEDIUM")
        priority = "P1" if severity == "CRITICAL" else ("P2" if severity in ["HIGH", "WARNING"] else "P3")

        title = f"Correlated Incident: Multi-metric Anomaly on {target_service}"
        desc = (
            f"Statistically significant metric deviation detected on {target_service}. "
            f"Metric: {alert_data.get('metric_name')} at {alert_data.get('current_value')}. "
            f"Dynamic baseline deviation: {alert_data.get('z_score', 'N/A')} sigma."
        )

        new_incident = Incident(
            id=new_incident_id,
            title=title,
            description=desc,
            severity=severity,
            priority=priority,
            status="NEW",
            source="Statistical Anomaly Detector",
            affected_resources=[target_service],
            detection_time=now,
            assigned_agent="Incident Correlation Agent"
        )
        session.add(new_incident)

        alert = Alert(
            id=str(uuid.uuid4()),
            fingerprint=alert_data.get("fingerprint", str(uuid.uuid4())),
            incident_id=new_incident_id,
            title=alert_data.get("title", f"Initial Anomaly: {target_service}"),
            severity=severity,
            metric_name=alert_data.get("metric_name", "unknown_metric"),
            current_value=float(alert_data.get("current_value", 0.0)),
            baseline_value=float(alert_data.get("baseline_value", 0.0)) if alert_data.get("baseline_value") is not None else None,
            anomaly_score=float(alert_data.get("anomaly_score", 0.0)) if alert_data.get("anomaly_score") is not None else None,
            source=alert_data.get("source", "Prometheus"),
            status="ACTIVE"
        )
        session.add(alert)

        event = IncidentEvent(
            incident_id=new_incident_id,
            event_type="INCIDENT_INITIALIZED",
            message=f"Incident synthesized from initial anomaly trigger on {target_service}.",
            agent_name="Incident Correlation Agent",
            payload_json={"initial_alert": alert.title, "resources": [target_service]}
        )
        session.add(event)

        session.commit()
        session.refresh(new_incident)

        return {
            "action": "CREATED_NEW_INCIDENT",
            "incident_id": new_incident.id,
            "incident_title": new_incident.title,
            "severity": new_incident.severity,
            "affected_resources": new_incident.affected_resources
        }
