"""
Service and version fingerprinting for open ports.

Implements banner grabbing (RFC-compliant peel-and-read) for
text-based protocols, plus a static IANA-derived lookup table.
This is the first step in the vulnerability-mapping stage of a
penetration testing methodology.
"""

import socket
from typing import Optional

# Common service table (IANA-oriented). Extend programmatically
# from /etc/services in production deployments.
SERVICE_DB = {
    20:"FTP-data", 21:"FTP", 22:"SSH", 23:"Telnet", 25:"SMTP",
    53:"DNS", 80:"HTTP", 110:"POP3", 111:"rpcbind", 135:"MSRPC",
    139:"NetBIOS-SSN", 143:"IMAP", 161:"SNMP", 389:"LDAP",
    443:"HTTPS", 445:"SMB", 993:"IMAPS", 995:"POP3S",
    1433:"MSSQL", 1521:"Oracle-DB", 3306:"MySQL", 3389:"RDP",
    5432:"PostgreSQL", 5900:"VNC", 6379:"Redis", 8000:"HTTP-alt",
    8080:"HTTP-alt", 8443:"HTTPS-alt", 27017:"MongoDB",
}


def identify_service(port: int) -> str:
    return SERVICE_DB.get(port, "unknown")


def grab_banner(host: str, port: int, timeout: float = 3.0) -> Optional[str]:
    """
    Reads the initial banner some services advertise on connect
    (e.g., SSH demonstrates 'SSH-2.0-OpenSSH_9.x'). Best-effort;
    many services send nothing without a client hello.
    """
    try:
        with socket.create_connection((host, port), timeout=timeout) as sock:
            banner = sock.recv(1024).decode(errors="ignore").strip()
            return banner if banner else None
    except Exception:
        return None


def enrich_results(host: str, results: list) -> list:
    """Attach service name and banner to each open-port record."""
    for res in results:
        res.service = identify_service(res.port)
        if res.service == "unknown":
            res.banner = grab_banner(host, res.port)
    return results
