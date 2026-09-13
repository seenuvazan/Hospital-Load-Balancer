from __future__ import annotations

from hospital_lb.models import PatientRecord, Request, RoutingLog, Server


SAMPLE_SERVERS: list[Server] = [
    Server(
        server_id="srv-1",
        name="Emergency Edge Node",
        server_type="emergency-routing",
        max_capacity=120,
        current_load=42,
        status="healthy",
        avg_response_ms=40,
    ),
    Server(
        server_id="srv-2",
        name="Clinical Applications Node",
        server_type="doctor-services",
        max_capacity=150,
        current_load=78,
        status="healthy",
        avg_response_ms=66,
    ),
    Server(
        server_id="srv-3",
        name="Patient Portal Cluster",
        server_type="patient-services",
        max_capacity=200,
        current_load=132,
        status="warning",
        avg_response_ms=95,
    ),
    Server(
        server_id="srv-4",
        name="Analytics Failover Node",
        server_type="shared-services",
        max_capacity=170,
        current_load=64,
        status="healthy",
        avg_response_ms=58,
    ),
]

SAMPLE_REQUESTS: list[Request] = [
    Request(
        request_id="req-1001",
        request_type="emergency",
        source_name="Ambulance Alert",
        target_module="icu-monitoring",
        priority=3,
        status="routed",
        condition_level="critical",
    ),
    Request(
        request_id="req-1002",
        request_type="doctor",
        source_name="Dr. Mehta",
        target_module="lab-reports",
        priority=2,
        status="routed",
        condition_level="stable",
    ),
    Request(
        request_id="req-1003",
        request_type="patient",
        source_name="Neha Singh",
        target_module="appointment-booking",
        priority=1,
        status="queued",
        condition_level="normal",
    ),
]

SAMPLE_PATIENTS: list[PatientRecord] = [
    PatientRecord(
        patient_id="pat-01",
        patient_name="Rahul Verma",
        condition_level="critical",
        assigned_module="emergency",
    ),
    PatientRecord(
        patient_id="pat-02",
        patient_name="Anika Shah",
        condition_level="stable",
        assigned_module="doctor",
    ),
]

SAMPLE_LOGS: list[RoutingLog] = [
    RoutingLog(
        request_id="req-1001",
        server_id="srv-1",
        decision="Emergency override routed to lowest-latency healthy server",
        priority=3,
        request_type="emergency",
    ),
    RoutingLog(
        request_id="req-1002",
        server_id="srv-2",
        decision="Doctor request assigned by least-load + specialty server fit",
        priority=2,
        request_type="doctor",
    ),
]
