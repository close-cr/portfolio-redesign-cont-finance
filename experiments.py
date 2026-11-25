"""Document experiments: which conclusions change if I change one assumption?

Usage: python3 experiments.py
"""
import contextlib
import io

import estimates as e

ROWS = ["Invoices per month", "Requests/s at peak hour", "Gmail cron in a single run (s)",
        "Gmail cron per office (s)", "Database growth (MB per month)", "New files (GB per month)"]


def table(title):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        e.run()
    lines = buf.getvalue().splitlines()
    print(f"### {title}\n")
    print(lines[0]); print(lines[1])
    for line in lines[2:]:
        if any(line.startswith(f"| {r}") for r in ROWS):
            print(line)
    print()


base_inv, base_gmail = e.ASSUMPTIONS["invoices_per_client_month"], e.GMAIL_S_PER_CONNECTION
table("Baseline (40 invoices per client, 10 s per Gmail connection)")
e.ASSUMPTIONS["invoices_per_client_month"] = 120
table("120 invoices per client per month")
e.ASSUMPTIONS["invoices_per_client_month"] = 10
table("10 invoices per client per month")
e.ASSUMPTIONS["invoices_per_client_month"] = base_inv
e.GMAIL_S_PER_CONNECTION = 60
table("60 s per Gmail connection (instead of 10)")
