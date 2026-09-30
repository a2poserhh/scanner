import errno
import json
import logging
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from func.logger import setup_logging
from func.webport import check_port, is_alive, subnet_scan


MAIN = Path(__file__).resolve().parents[1] / "main.py"


class ResultTests(unittest.TestCase):
    def run_cli(self, *args):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [sys.executable, str(MAIN), *args], cwd=directory,
                capture_output=True, text=True, timeout=30,
            )
            log_path = Path(directory) / "data.log"
            log = log_path.read_text() if log_path.exists() else ""
        return result, log

    def test_real_open_and_closed_ports(self):
        with socket.socket() as server:
            server.bind(("127.0.0.1", 0))
            server.listen()
            port = server.getsockname()[1]
            result = check_port("127.0.0.1", port)
            self.assertEqual(result[:3], (port, "open", None))
            self.assertGreaterEqual(result[3], 0)
        with socket.socket() as closed:
            closed.bind(("127.0.0.1", 0))
            result = check_port("127.0.0.1", closed.getsockname()[1])
            self.assertEqual(result[1:3], ("closed", None))

    def test_socket_failure_is_not_counted_as_closed(self):
        with patch("func.webport.socket.socket") as factory:
            factory.return_value.__enter__.return_value.connect_ex.return_value = errno.EHOSTUNREACH
            result = check_port("127.0.0.1", 80)
        self.assertEqual(result[1], "error")
        self.assertTrue(result[2])

    def test_scan_cli_returns_counts_and_timing(self):
        with socket.socket() as server:
            server.bind(("127.0.0.1", 1024))
            server.listen(128)
            completed, log = self.run_cli("scan", "127.0.0.1")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertEqual(result["ports_scanned"], 1024)
        self.assertIn(1024, result["open_ports"])
        self.assertEqual(
            len(result["open_ports"]) + result["closed_count"] + result["error_count"], 1024,
        )
        self.assertEqual(result["error_count"], len(result["errors"]))
        self.assertGreaterEqual(result["elapsed_seconds"], 0)
        self.assertIn("1024 ports checked", log)
        self.assertIn("completed in", completed.stderr)

    def test_scanport_cli_accepts_a_port_and_returns_json(self):
        with socket.socket() as server:
            server.bind(("127.0.0.1", 0))
            server.listen()
            port = server.getsockname()[1]
            completed, log = self.run_cli("sP", "127.0.0.1", str(port))
        self.assertEqual(completed.returncode, 0, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertEqual(result["port"], port)
        self.assertEqual(result["status"], "open")
        self.assertIsNone(result["error"])
        self.assertIn("completed in", log)

    def test_cli_rejects_invalid_ports(self):
        for value in ("0", "65536", "abc"):
            with self.subTest(value=value):
                completed, log = self.run_cli("scanport", "127.0.0.1", value)
                self.assertEqual(completed.returncode, 2)
                self.assertIn("port must", completed.stderr)
                self.assertEqual(log, "")

    def test_invalid_subnet_logs_failure_and_time(self):
        completed, log = self.run_cli("subnet", "127.0.0.1/24")
        self.assertEqual(completed.returncode, 1)
        self.assertIn("failed after", log)
        self.assertEqual(completed.stdout, "")

    def test_ping_reports_permission_failure(self):
        response = subprocess.CompletedProcess([], 2, stdout="", stderr="socket: Operation not permitted")
        with patch("func.webport.subprocess.run", return_value=response):
            with self.assertLogs("func.webport", level="ERROR") as logs:
                self.assertFalse(is_alive("127.0.0.1"))
        self.assertIn("Operation not permitted", logs.output[0])
        self.assertIn("failed after", logs.output[0])

    def test_ping_alive_and_no_response_have_timed_outcomes(self):
        for exit_code in (0, 1):
            with self.subTest(exit_code=exit_code):
                response = subprocess.CompletedProcess([], exit_code, stdout="", stderr="")
                with patch("func.webport.subprocess.run", return_value=response):
                    with self.assertLogs("func.webport", level="INFO") as logs:
                        self.assertEqual(is_alive("127.0.0.1"), exit_code == 0)
                self.assertIn("completed in", logs.output[0])
                self.assertIn("alive" if exit_code == 0 else "no response", logs.output[0])

    def test_missing_ping_and_timeout_log_errors(self):
        for error in (FileNotFoundError("ping not installed"), subprocess.TimeoutExpired("ping", 5)):
            with self.subTest(error=error):
                with patch("func.webport.subprocess.run", side_effect=error):
                    with self.assertLogs("func.webport", level="ERROR") as logs:
                        self.assertFalse(is_alive("127.0.0.1"))
                self.assertIn("failed after", logs.output[0])

    def test_subnet_returns_host_totals(self):
        with patch("func.webport.is_alive", side_effect=[True, False]) as ping:
            with self.assertLogs("func.webport", level="INFO") as logs:
                result = subnet_scan("127.0.0.0/30")
        self.assertEqual([call.args[0] for call in ping.call_args_list], ["127.0.0.1", "127.0.0.2"])
        self.assertEqual(result["hosts_scanned"], 2)
        self.assertEqual(result["alive_hosts"], ["127.0.0.1"])
        self.assertEqual(result["alive_count"], 1)
        self.assertEqual(result["not_detected_count"], 1)
        self.assertGreaterEqual(result["elapsed_seconds"], 0)
        self.assertIn("2 hosts checked, 1 alive, 1 not detected", logs.output[-1])

    def test_logging_setup_does_not_duplicate_entries(self):
        root = logging.getLogger()
        previous_level = root.level
        try:
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "result.log"
                setup_logging(path)
                setup_logging(path)
                logging.getLogger("scanner.test").info("unique result")
                self.assertEqual(path.read_text().count("unique result"), 1)
                self.assertIn("INFO - scanner.test", path.read_text())
        finally:
            for handler in root.handlers[:]:
                if getattr(handler, "_scanner_handler", False):
                    root.removeHandler(handler)
                    handler.close()
            root.setLevel(previous_level)


if __name__ == "__main__":
    unittest.main()
