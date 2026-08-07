"""Unit tests for the Port_Scanner framework.

Run with:  pytest tests/ -v
"""

import csv
import json
import socket
import threading

import pytest

from scanner import config, fingerprint, reporting
from scanner.core import PortScanner, ScanResult


# ---------------------------------------------------------------------------
# ScanResult model
# ---------------------------------------------------------------------------

class TestScanResult:
    def test_as_dict_returns_all_fields(self):
        r = ScanResult(port=22, service="SSH",
                       banner="SSH-2.0-OpenSSH_9.0", latency_ms=1.5)
        d = r.as_dict()
        assert d["port"] == 22
        assert d["service"] == "SSH"
        assert d["banner"].startswith("SSH-2.0")
        assert d["latency_ms"] == 1.5

    def test_defaults(self):
        r = ScanResult(port=80)
        assert r.service == "unknown"
        assert r.banner is None
        assert r.latency_ms == 0.0


# ---------------------------------------------------------------------------
# PortScanner engine
# ---------------------------------------------------------------------------

class TestPortScanner:
    def test_no_open_ports_on_unassigned_high_range(self):
        s = PortScanner("127.0.0.1", timeout=0.2, max_workers=50)
        assert s.scan(60000, 60005) == []

    def test_results_are_sorted_by_port(self):
        s = PortScanner("127.0.0.1", timeout=0.2, max_workers=50)
        ports = [r.port for r in s.scan(1, 30)]
        assert ports == sorted(ports)

    def test_scan_returns_scanresult_objects(self):
        s = PortScanner("127.0.0.1", timeout=0.2, max_workers=50)
        for r in s.scan(1, 25):
            assert isinstance(r, ScanResult)


# ---------------------------------------------------------------------------
# Service fingerprinting
# ---------------------------------------------------------------------------

class TestFingerprinting:
    def test_well_known_service_mappings(self):
        assert fingerprint.identify_service(22) == "SSH"
        assert fingerprint.identify_service(443) == "HTTPS"
        assert fingerprint.identify_service(3306) == "MySQL"
        assert fingerprint.identify_service(5432) == "PostgreSQL"

    def test_unknown_port_maps_to_unknown(self):
        assert fingerprint.identify_service(59999) == "unknown"

    def test_grab_banner_returns_none_for_closed_port(self):
        assert fingerprint.grab_banner("127.0.0.1", 1, timeout=0.2) is None

    def test_grab_banner_reads_server_greeting(self):
        """Spins up a real local server that advertises a banner."""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(("127.0.0.1", 0))
        server.listen(1)
        port = server.getsockname()[1]

        def serve():
            conn, _ = server.accept()
            conn.sendall(b"TEST-BANNER-1.0\r\n")
            conn.close()

        threading.Thread(target=serve, daemon=True).start()
        try:
            banner = fingerprint.grab_banner("127.0.0.1", port, timeout=2.0)
            assert banner == "TEST-BANNER-1.0"
        finally:
            server.close()


# ---------------------------------------------------------------------------
# Configuration sanity
# ---------------------------------------------------------------------------

class TestConfig:
    def test_port_ranges_are_valid(self):
        for name, (start, end) in config.PORT_RANGES.items():
            assert 1 <= start <= end <= 65535

    def test_default_workers_is_positive(self):
        assert config.DEFAULT_MAX_WORKERS > 0

    def test_timeout_is_reasonable(self):
        assert 0.01 <= config.DEFAULT_TIMEOUT <= 10


# ---------------------------------------------------------------------------
# Reporting (uses pytest tmp_path fixture + monkeypatch)
# ---------------------------------------------------------------------------

class TestReporting:
    def test_write_json_creates_valid_file(self, tmp_path, monkeypatch):
        monkeypatch.setattr(reporting.config, "REPORT_DIR", tmp_path)
        results = [ScanResult(port=22, service="SSH", banner="SSH-2.0"),
                   ScanResult(port=443, service="HTTPS")]
        path = reporting.write_json(results, "localhost")
        assert path.exists()
        data = json.loads(path.read_text())
        assert data["host"] == "localhost"
        assert len(data["open_ports"]) == 2
        assert data["open_ports"][0]["port"] == 22

    def test_write_csv_creates_valid_file(self, tmp_path, monkeypatch):
        monkeypatch.setattr(reporting.config, "REPORT_DIR", tmp_path)
        results = [ScanResult(port=80, service="HTTP")]
        path = reporting.write_csv(results, "localhost")
        assert path.exists()
        with path.open() as f:
            rows = list(csv.DictReader(f))
        assert len(rows) == 1
        assert rows[0]["port"] == "80"
        assert rows[0]["service"] == "HTTP"

    def test_write_html_contains_results(self, tmp_path, monkeypatch):
        monkeypatch.setattr(reporting.config, "REPORT_DIR", tmp_path)
        results = [ScanResult(port=443, service="HTTPS")]
        path = reporting.write_html(results, "example.com")
        html = path.read_text(encoding="utf-8")
        assert "example.com" in html
        assert "443" in html
        assert "HTTPS" in html
