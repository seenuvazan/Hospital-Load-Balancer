from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


PRIORITY_ORDER = {
    "emergency": 3,
    "doctor": 2,
    "patient": 1,
}


@dataclass(slots=True)
class Server:
    server_id: str
    name: str
    server_type: str
    max_capacity: int
    current_load: int
    status: str
    avg_response_ms: int

    @property
    def load_ratio(self) -> float:
        return self.current_load / self.max_capacity if self.max_capacity else 1.0

    @property
    def available_capacity(self) -> int:
        return max(self.max_capacity - self.current_load, 0)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["load_ratio"] = round(self.load_ratio, 3)
        payload["available_capacity"] = self.available_capacity
        return payload


@dataclass(slots=True)
class Request:
    request_id: str
    request_type: str
    source_name: str
    target_module: str
    status: str = "queued"
    priority: int = 1
    condition_level: str = "normal"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class PatientRecord:
    patient_id: str
    patient_name: str
    condition_level: str
    assigned_module: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class RoutingLog:
    request_id: str
    server_id: str
    decision: str
    priority: int
    request_type: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
