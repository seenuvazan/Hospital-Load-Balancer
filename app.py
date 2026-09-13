from __future__ import annotations

import json
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from hospital_lb.engine import NoAvailableServerError
from hospital_lb.models import Request, Server
from hospital_lb.store import LoadBalancerStore


BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"
STORE = LoadBalancerStore()


class HospitalRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)

        if parsed.path == "/api/servers":
            self._send_json({"servers": [item.to_dict() for item in STORE.list_servers()]})
            return

        if parsed.path == "/api/requests":
            self._send_json({"requests": [item.to_dict() for item in STORE.list_requests()]})
            return

        if parsed.path == "/api/patients":
            self._send_json({"patients": [item.to_dict() for item in STORE.list_patients()]})
            return

        if parsed.path == "/api/logs":
            self._send_json({"logs": [item.to_dict() for item in STORE.list_logs()]})
            return

        if parsed.path == "/api/health":
            self._send_json({"status": "ok", "summary": STORE.system_health()})
            return

        if parsed.path == "/":
            self.path = "/index.html"

        super().do_GET()

    def do_POST(self) -> None:
        parsed = urlparse(self.path)

        if parsed.path == "/api/servers":
            payload = self._read_json()
            server = Server(
                server_id=payload["server_id"],
                name=payload["name"],
                server_type=payload["server_type"],
                max_capacity=int(payload["max_capacity"]),
                current_load=int(payload["current_load"]),
                status=payload["status"],
                avg_response_ms=int(payload["avg_response_ms"]),
            )
            STORE.add_server(server)
            self._send_json({"server": server.to_dict()}, status=HTTPStatus.CREATED)
            return

        if parsed.path == "/api/route":
            payload = self._read_json()
            request = Request(
                request_id=payload["request_id"],
                request_type=payload["request_type"],
                source_name=payload["source_name"],
                target_module=payload["target_module"],
                condition_level=payload.get("condition_level", "normal"),
            )
            try:
                result = STORE.submit_request(request)
            except NoAvailableServerError as exc:
                self._send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return

            self._send_json(result, status=HTTPStatus.CREATED)
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Not found")

    def log_message(self, format: str, *args) -> None:
        return

    def _read_json(self) -> dict[str, object]:
        content_length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(content_length).decode("utf-8")
        return json.loads(raw) if raw else {}

    def _send_json(self, payload: dict[str, object], status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run_server(port: int = 8000) -> None:
    server = ThreadingHTTPServer(("127.0.0.1", port), HospitalRequestHandler)
    print(f"Hospital load balancer running at http://127.0.0.1:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    run_server()
