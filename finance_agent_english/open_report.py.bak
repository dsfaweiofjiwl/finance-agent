#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
On-demand report viewer - Serve HTML reports via local HTTP server.

Usage:
    python open_report.py                  # List all reports, pick one to serve
    python open_report.py <filename>       # Serve a specific report
    python open_report.py --latest         # Serve the most recent report
"""

import sys
import os

from web_renderer import list_reports, serve_report, get_http_url


def main():
    output_dir = "output"
    args = [a for a in sys.argv[1:] if a != "--open"]

    if args:
        arg = args[0]

        if arg == "--latest":
            reports = list_reports(output_dir)
            if reports:
                url = get_http_url(reports[0])
                print(f"Latest report: {url}")
                print("Starting server...")
                serve_report(reports[0])
            else:
                print(f"No HTML reports found in {output_dir}/")
            return

        # Treat argument as filename
        path = arg if os.path.isfile(arg) else os.path.join(output_dir, arg)
        if os.path.isfile(path):
            url = get_http_url(path)
            print(f"Report: {url}")
            print("Starting server...")
            serve_report(path)
        else:
            print(f"File not found: {arg}")
            sys.exit(1)
        return

    # No arguments — list all reports
    reports = list_reports(output_dir)
    if not reports:
        print(f"No HTML reports found in {output_dir}/")
        print("Run 'python run_analysis.py' first to generate a report.")
        return

    print("\nAvailable Reports:")
    print("-" * 60)
    for i, path in enumerate(reports, 1):
        name = os.path.basename(path)
        size_kb = os.path.getsize(path) / 1024
        print(f"  [{i}] {name}  ({size_kb:.0f} KB)")
    print("-" * 60)

    try:
        choice = input("\nEnter number to serve (or q to quit): ").strip()
        if choice.lower() == "q":
            return
        idx = int(choice) - 1
        if 0 <= idx < len(reports):
            serve_report(reports[idx])
        else:
            print("Invalid choice.")
    except (ValueError, EOFError):
        print("Cancelled.")


if __name__ == "__main__":
    main()
