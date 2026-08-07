#!/usr/bin/env python3
"""
Network Port Scanner — Portfolio Edition

Usage:
    python main.py <host> [--start N] [--end N] [--profile quick|common|full]
                    [--workers N] [--timeout SEC] [--format json,csv,html]

Example:
    python main.py 192.168.1.10 --profile common --format json,html
"""

import argparse
import logging
import sys

from scanner import config, fingerprint
from scanner.core import PortScanner
from scanner import reporting


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Professional TCP port scanner")
    p.add_argument("host", help="Target hostname or IPv4 address")
    p.add_argument("--start", type=int, help="First port")
    p.add_argument("--end", type=int, help="Last port")
    p.add_argument("--profile", choices=config.PORT_RANGES.keys(),
                   default="common", help="Scan profile")
    p.add_argument("--workers", type=int, default=config.DEFAULT_MAX_WORKERS)
    p.add_argument("--timeout", type=float, default=config.DEFAULT_TIMEOUT)
    p.add_argument("--format", default="json,html",
                   help="Output formats: json,csv,html")
    return p


def main() -> int:
    args = build_parser().parse_args()

    logging.basicConfig(
        level=logging.INFO,
        filename=config.LOG_FILE,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    # Resolve profile or explicit range
    if args.start and args.end:
        start, end = args.start, args.end
    else:
        start, end = config.PORT_RANGES[args.profile]

    print(f"[*] Target : {args.host}")
    print(f"[*] Range  : {start}–{end}")
    print(f"[*] Workers: {args.workers} | Timeout: {args.timeout}s\n")

    scanner = PortScanner(args.host,
                          timeout=args.timeout,
                          max_workers=args.workers)
    results = scanner.scan(start, end)
    results = fingerprint.enrich_results(args.host, results)

    print(f"[+] Scan complete. Open ports: {len(results)}\n")
    for r in results:
        print(f"    {r.port:<6}{r.service:<12}{r.banner or ''}")
    print()

    # Emit requested report formats
    for fmt in args.format.split(","):
        path = {
            "json": lambda: reporting.write_json(results, args.host),
            "csv":  lambda: reporting.write_csv(results, args.host),
            "html": lambda: reporting.write_html(results, args.host),
        }[fmt.strip()]()
        print(f"[+] {fmt.upper()} report -> {path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
