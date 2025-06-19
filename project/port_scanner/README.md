# Modular Port Scanner with Plugin Support

A fast, multithreaded port scanner built in Python with support for custom plugins, banner grabbing, colored output, and IPv6 scanning. Designed for extensibility and performance, this tool is ideal for developers, sysadmins, and pentesters.

---

## Features

- Multithreaded scanning (default 100 threads)
- Supports IPv4 and IPv6 (`--ipv6`)
- Banner grabbing with SHA256 hashing
- Plugin system for custom post-processing per open port
- CIDR and dash-range IP parsing
- JSON output with structured results
- Optional silent mode and open-port-only output

---

## Usage

```bash
python port_scanner.py 192.168.1.0/24 --start-port 20 --end-port 1024 --threads 200
