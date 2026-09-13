from __future__ import annotations

from copy import deepcopy

from hospital_lb.data import SAMPLE_LOGS, SAMPLE_PATIENTS, SAMPLE_REQUESTS, SAMPLE_SERVERS
from hospital_lb.engine import calculate_priority, choose_server, request_load_cost
from hospital_lb.models import PatientRecord, Request, RoutingLog, Server


class LoadBalancerStore:
    def __init__(self) -> None:
        self._servers: list[Server] = deepcopy(SAMPLE_SERVERS)
        self._requests: list[Request] = deepcopy(SAMPLE_REQUESTS)
        self._patients: list[PatientRecord] = deepcopy(SAMPLE_PATIENTS)
        self._logs: list[RoutingLog] = deepcopy(SAMPLE_LOGS)

    def list_servers(self) -> list[Server]:
        return self._servers

    def list_requests(self) -> list[Request]:
        return self._requests

    def list_patients(self) -> list[PatientRecord]:
        return self._patients

    def list_logs(self) -> list[RoutingLog]:
        return self._logs

    def add_server(self, server: Server) -> Server:
        self._servers.append(server)
        return server

    def submit_request(self, request: Request) -> dict[str, object]:
        request.priority = calculate_priority(request.request_type)
        result = choose_server(self._servers, request)
        server = result.server
        server.current_load = min(server.current_load + request_load_cost(request.request_type), server.max_capacity)
        server.avg_response_ms = min(server.avg_response_ms + (8 if request.request_type == "emergency" else 5), 250)
        if server.load_ratio >= 0.88:
            server.status = "warning"

        request.status = "routed"
        self._requests.insert(0, request)

        log = RoutingLog(
            request_id=request.request_id,
            server_id=server.server_id,
            decision=result.reason,
            priority=request.priority,
            request_type=request.request_type,
        )
        self._logs.insert(0, log)

        if request.request_type == "patient":
            self._patients.insert(
                0,
                PatientRecord(
                    patient_id=f"pat-{request.request_id}",
                    patient_name=request.source_name,
                    condition_level=request.condition_level,
                    assigned_module="patient",
                ),
            )

        return {
            "routing": result.to_dict(),
            "request": request.to_dict(),
            "log": log.to_dict(),
        }

    def system_health(self) -> dict[str, object]:
        healthy = sum(1 for server in self._servers if server.status == "healthy")
        warning = sum(1 for server in self._servers if server.status == "warning")
        down = sum(1 for server in self._servers if server.status == "down")
        average_load = (
            round(sum(server.load_ratio for server in self._servers) / len(self._servers), 3)
            if self._servers
            else 0
        )
        return {
            "healthy_servers": healthy,
            "warning_servers": warning,
            "down_servers": down,
            "average_load": average_load,
            "queued_or_processed_requests": len(self._requests),
        }
