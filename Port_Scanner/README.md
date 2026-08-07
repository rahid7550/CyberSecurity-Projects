# Network Port Scanner — A Concurrency-Aware Reconnaissance Tool

## Abstract
A production-quality TCP port scanner built in Python that combines
bounded-concurrency engineering with standardized network forensics
techniques. The tool performs connect-based port enumeration, service
fingerprinting, and banner extraction, and exports structured reports
in JSON, CSV, and HTML formats. It is architected as a modular,
testable library rather than a monolithic script, following OWASP
reconnaissance and PTES enumeration guidelines.

## Motivation & Background
Network enumeration is the foundation of both offensive security and
defensive hygiene. Scanning reveals the *attack surface* of a host —
the set of exposed services. When a port is open, it indicates a
listening application, which becomes a candidate for version
discovery and vulnerability correlation (e.g., CVEs). This project
implements that first, critical measurement step in a safe,
observable, and extensible manner.

## Methodology
1. **Port probing** — TCP three-way-handshake connect attempts
   (`connect_ex`), governed by per-attempt timeouts.
2. **Concurrency control** — A bounded `ThreadPoolExecutor` (default
   200 workers) yields high throughput while preventing resource
   exhaustion — a deliberate trade-off between speed and host load.
3. **Service fingerprinting** — IANA-derived static table plus
   best-effort protocol banner grabbing.
4. **Reporting** — Deterministic, sorted results exported to machine-
   and human-readable formats.

## Design Decisions
| Decision | Justification |
|----------|---------------|
| Dataclass model | Immutable, typed, testable result records |
| Config module | No hard-coded magic numbers; behavior is data-driven |
| Logging module | Auditable execution history (good practice + R&D portfolio) |
| CLI via `argparse` | Consistent with professional Python tool UX |
| ThreadPoolExecutor | Safer concurrency pattern than raw threads |

## Limitations & Future Work
- **TCP-only** currently; UDP scanning (ICMP port-unreachable
  detection) is a planned extension.
- **SYN (stealth) scan** requires raw sockets / elevated privileges
  and is roadmaped with packet-crafting via `scapy`.
- **OS fingerprinting** (TTL-based) can be layered on a future release.

## Testing
```bash
pip install -r requirements.txt
pytest tests/
