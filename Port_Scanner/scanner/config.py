"""
Configuration and static knowledge base.

Centralizing constants here ensures the scanner's behavior is
data-driven and auditable — a key design consideration highlighted
in the Open Web Application Security Project (OWASP) testing guides.
"""

from pathlib import Path

# --- Executor settings ---
DEFAULT_TIMEOUT = 1.0          # Seconds per connection attempt
DEFAULT_MAX_WORKERS = 200       # Bound the thread pool (resource control)
CONNECT_RETRIES = 2             # Resilience for dropped packets

# --- Scan profile presets ---
# IANA Service Name and Transport Protocol Port Number Registry categories
PORT_RANGES = {
    "quick":   (1, 1000),      # Well-known ports + studied range
    "common":  (1, 1024),      # Well-known system ports (RFC 6335)
    "full":    (1, 65535),     # All TCP ports
}

# --- Reporting ---
REPORT_DIR = Path("reports")
LOG_FILE = Path("scanner.log")
