"""
Concurrent TCP scanning engine.

Implements two techniques from RFC 793 connection semantics:
  - CONNECT scan: completes the three-way handshake (accurate,
    easily logged by the target — good for controlled environments).
Uses ThreadPoolExecutor for bounded, safe concurrency instead of
raw threads to avoid GIL contention and unbounded thread creation.
"""

import logging
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import List, Optional

from . import config

log = logging.getLogger("port_scanner")


@dataclass
class ScanResult:
    """Immutable record of one open port observation."""
    port: int
    service: str = "unknown"
    banner: Optional[str] = None
    latency_ms: float = 0.0

    def as_dict(self) -> dict:
        return {
            "port": self.port,
            "service": self.service,
            "banner": self.banner,
            "latency_ms": round(self.latency_ms, 2),
        }


class PortScanner:
    """
    Encapsulates the scanning lifecycle: TCP connect probe,
    optional banner grab, and aggregation of results.
    """

    def __init__(self,
                 host: str,
                 timeout: float = config.DEFAULT_TIMEOUT,
                 max_workers: int = config.DEFAULT_MAX_WORKERS):
        self.host = host
        self.timeout = timeout
        self.max_workers = max_workers
        self._open_ports: List[ScanResult] = []

    # ---- Private helpers ----
    def _probe(self, port: int) -> Optional[ScanResult]:
        """Attempt a TCP connect to a single port."""
        start = __import__("time").perf_counter()
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(self.timeout)
                if sock.connect_ex((self.host, port)) != 0:
                    return None
                elapsed_ms = (__import__("time").perf_counter() - start) * 1000
                return ScanResult(port=port, latency_ms=elapsed_ms)
        except (socket.timeout, OSError):
            return None

    # ---- Public API ----
    def scan(self, start: int, end: int) -> List[ScanResult]:
        """
        Concurrently probe the inclusive [start, end] port range.

        Results are returned sorted by port number to guarantee
        deterministic output for reporting and unit testing.
        """
        log.info("Scanning %s ports %d-%d", self.host, start, end)
        with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            futures = {
                pool.submit(self._probe, p): p
                for p in range(start, end + 1)
            }
            for future in as_completed(futures):
                res = future.result()
                if res is not None:
                    self._open_ports.append(res)
        self._open_ports.sort(key=lambda r: r.port)
        return self._open_ports

    @property
    def results(self) -> List[ScanResult]:
        return self._open_ports
