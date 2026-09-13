from __future__ import annotations

from dataclasses import dataclass

from hospital_lb.models import PRIORITY_ORDER, Request, Server


REQUEST_LOAD_COST = {
    "emergency": 20,
    "doctor": 12,
    "patient": 8,
}

TARGET_PREFERENCE = {
    "emergency": {"emergency-routing": 18, "shared-services": 8},
    "doctor": {"doctor-services": 18, "shared-services": 10},
    "patient": {"patient-services": 18, "shared-services": 10},
}


@dataclass(slots=True)
class RoutingResult:
    server: Server
    score: float
    reason: str
    breakdown: dict[str, float]

    def to_dict(self) -> dict[str, object]:
        return {
            "server": self.server.to_dict(),
            "score": round(self.score, 2),
            "reason": self.reason,
            "breakdown": {key: round(value, 2) for key, value in self.breakdown.items()},
        }


class NoAvailableServerError(RuntimeError):
    """Raised when no server is fit to accept a request."""


def calculate_priority(request_type: str) -> int:
    return PRIORITY_ORDER.get(request_type.lower(), 1)


def request_load_cost(request_type: str) -> int:
    return REQUEST_LOAD_COST.get(request_type.lower(), 8)


def score_server(server: Server, request: Request) -> tuple[float, dict[str, float]]:
    projected_load = server.current_load + request_load_cost(request.request_type)

    if server.status.lower() == "down":
        raise NoAvailableServerError(f"{server.name} is down.")

    if projected_load > server.max_capacity:
        raise NoAvailableServerError(f"{server.name} would exceed safe capacity.")

    priority = calculate_priority(request.request_type)
    preferred_bonus = TARGET_PREFERENCE.get(request.request_type.lower(), {}).get(server.server_type, 0)
    health_bonus = 12 if server.status.lower() == "healthy" else 5
    available_capacity_score = ((server.max_capacity - projected_load) / server.max_capacity) * 40
    latency_score = max(0.0, 22 - (server.avg_response_ms / 5))
    priority_score = priority * 20

    if request.request_type.lower() == "emergency":
        latency_score += 10
        preferred_bonus += 8

    total = available_capacity_score + latency_score + priority_score + preferred_bonus + health_bonus

    return total, {
        "available_capacity": available_capacity_score,
        "latency": latency_score,
        "priority_weight": priority_score,
        "target_fit": preferred_bonus,
        "health": health_bonus,
    }


def choose_server(servers: list[Server], request: Request) -> RoutingResult:
    candidates: list[RoutingResult] = []
    rejection_reasons: list[str] = []

    for server in servers:
        try:
            score, breakdown = score_server(server, request)
        except NoAvailableServerError as exc:
            rejection_reasons.append(str(exc))
            continue

        reason = (
            f"{server.name} was selected for this {request.request_type} request because it is "
            f"{server.status}, has {server.available_capacity} capacity units free, and responds "
            f"in about {server.avg_response_ms} ms."
        )
        candidates.append(RoutingResult(server=server, score=score, reason=reason, breakdown=breakdown))

    if not candidates:
        details = "; ".join(rejection_reasons) if rejection_reasons else "No servers were configured."
        raise NoAvailableServerError(f"No suitable server found. {details}")

    candidates.sort(
        key=lambda item: (
            item.score,
            item.server.status.lower() == "healthy",
            item.server.available_capacity,
        ),
        reverse=True,
    )
    return candidates[0]
