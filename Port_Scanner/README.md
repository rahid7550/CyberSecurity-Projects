# Network Port Scanner

## Overview

A modular, multi-threaded TCP port scanner built with Python for cybersecurity learning and authorized network reconnaissance. The tool performs fast TCP port scanning, basic service fingerprinting, banner grabbing, and generates reports in multiple formats.

The project follows a clean, modular architecture and demonstrates practical concepts including concurrent programming, socket programming, network enumeration, and automated reporting.

---

## Features

- Fast multi-threaded TCP port scanning
- Configurable scan profiles (Quick, Common, Full)
- Service detection using common port mappings
- Banner grabbing for supported services
- Configurable timeout and worker threads
- Export scan results to:
  - JSON
  - CSV
  - HTML
- Modular project structure
- Command-line interface using `argparse`
- Unit tested with **Pytest**

---

## Project Structure

```text
Port_Scanner/
│
├── scanner/
│   ├── __init__.py
│   ├── config.py
│   ├── core.py
│   ├── fingerprint.py
│   └── reporting.py
│
├── tests/
│   └── test_core.py
│
├── reports/
├── README.md
├── main.py
├── requirements.txt
├── requirements-dev.txt
└── .gitignore
```

---

## Technologies Used

- Python 3
- Socket Programming
- ThreadPoolExecutor
- argparse
- JSON
- CSV
- HTML
- Pytest

---

## Usage

```bash
python3 main.py example.com --profile quick
```

Generate reports:

```bash
python3 main.py example.com --format json,csv,html
```

---

## Testing

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

Run all tests:

```bash
python3 -m pytest
```

Example output:

```
=====================
15 passed in 0.04s
=====================
```

---

## Limitations

- Supports TCP scanning only
- UDP scanning is not implemented
- SYN (Stealth) scan is not implemented
- OS fingerprinting is not implemented

---

## Future Improvements

- UDP Port Scanner
- SYN Scan
- OS Fingerprinting
- IPv6 Support
- Service Version Detection
- Progress Bar
- XML/Nmap compatible output

---

## Disclaimer

This project is intended for educational purposes and authorized security testing only. Always obtain proper permission before scanning systems that you do not own or manage.

## License

This project is licensed under the MIT License.
