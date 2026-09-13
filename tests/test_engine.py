import unittest

from hospital_lb.data import SAMPLE_SERVERS
from hospital_lb.engine import NoAvailableServerError, calculate_priority, choose_server
from hospital_lb.models import Request, Server


class LoadBalancerTests(unittest.TestCase):
    def test_emergency_prefers_emergency_server(self) -> None:
        request = Request(
            request_id="req-test-1",
            request_type="emergency",
            source_name="Ambulance Desk",
            target_module="icu-monitoring",
            condition_level="critical",
        )

        result = choose_server(SAMPLE_SERVERS, request)

        self.assertEqual(result.server.name, "Emergency Edge Node")

    def test_rejects_overloaded_servers(self) -> None:
        servers = [
            Server(
                server_id="srv-a",
                name="Pinned Node",
                server_type="patient-services",
                max_capacity=100,
                current_load=96,
                status="healthy",
                avg_response_ms=45,
            )
        ]
        request = Request(
            request_id="req-test-2",
            request_type="patient",
            source_name="Patient Portal",
            target_module="appointment-booking",
            condition_level="normal",
        )

        with self.assertRaises(NoAvailableServerError):
            choose_server(servers, request)

    def test_priority_mapping(self) -> None:
        self.assertEqual(calculate_priority("emergency"), 3)
        self.assertEqual(calculate_priority("doctor"), 2)
        self.assertEqual(calculate_priority("patient"), 1)


if __name__ == "__main__":
    unittest.main()
