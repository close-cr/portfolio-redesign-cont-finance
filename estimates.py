"""Back-of-envelope estimates for a multi-office accounting app in three size scenarios.

Everything that is not a measured fact is an explicit ASSUMPTION (see ASSUMPTIONS). Change a number and re-run:
the tables in DESIGN.md can then be refreshed.

Usage:  python3 estimates.py
"""

# --- Limits of the example platform and of Google (documented by their providers) ---
CRON_MAX_S = 300           # maximum run time of a cron job on the current platform
GMAIL_PARALLEL = 15        # Gmail connections the bot processes in parallel
GMAIL_S_PER_CONNECTION = 10  # approximate seconds per connection (estimated, not measured)
POOL_PER_INSTANCE = 5      # database connections per app instance
DB_LIMIT_MB = 512          # ASSUMPTION: size of a small database plan
GMAIL_UNVERIFIED_CAP = 100  # user cap of an unverified Google app

# --- Scenarios ---
SCENARIOS = {
    "Small scenario":          dict(offices=1,   active_clients=10),    # ASSUMPTION: one office just starting
    "Medium scenario":         dict(offices=20,  active_clients=1000),  # ASSUMPTION: ~50 clients per office
    "Design scenario (×100)":  dict(offices=100, active_clients=5000),  # ASSUMPTION: ~100 times the small one in offices
}

ASSUMPTIONS = dict(
    invoices_per_client_month=40,   # "tens or hundreds" according to the guides; 40 is used
    kb_files_per_invoice=150,       # XML (~20 KB) + PDF (~130 KB)
    kb_db_per_invoice=5,            # invoice row + lines + journal entry
    users_per_office=3,
    requests_per_user_hour=120,     # normal browsing: 2 a minute
    peak_concurrency_share=0.3,     # share of users active at once in the peak hour
    peak_factor=3,                  # peak = 3 × average
    request_latency_s=0.2,          # average time a request holds a database connection (ASSUMPTION)
    pdf_only_share=0.10,            # invoices without XML that need AI reading
)


def fmt(n, d=0):
    return f"{n:,.{d}f}"


def run():
    s = ASSUMPTIONS
    print("| Quantity | " + " | ".join(SCENARIOS) + " |")
    print("|---|" + "---|" * len(SCENARIOS))
    rows = {}
    for name, e in SCENARIOS.items():
        invoices = e["active_clients"] * s["invoices_per_client_month"]
        users = e["offices"] * s["users_per_office"]
        active = users * s["peak_concurrency_share"]
        peak_rps = active * (s["requests_per_user_hour"] / 3600) * s["peak_factor"]
        bot_s = e["active_clients"] / GMAIL_PARALLEL * GMAIL_S_PER_CONNECTION  # one single cron run for everyone
        bot_s_office = (e["active_clients"] / e["offices"]) / GMAIL_PARALLEL * GMAIL_S_PER_CONNECTION  # one office
        db_mb = invoices * s["kb_db_per_invoice"] / 1024
        files_gb = invoices * s["kb_files_per_invoice"] / 1024 / 1024
        rows.setdefault("Active clients per month", []).append(fmt(e["active_clients"]))
        rows.setdefault("Invoices per month", []).append(fmt(invoices))
        rows.setdefault("Invoices per day (30 days)", []).append(fmt(invoices / 30))
        rows.setdefault("Total users", []).append(fmt(users))
        rows.setdefault("Requests/s at peak hour", []).append(fmt(peak_rps, 1))
        rows.setdefault("DB connections in use at once (Little's law: requests/s × latency)", []).append(fmt(peak_rps * s["request_latency_s"], 1))
        rows.setdefault("Gmail cron in a single run (s)", []).append(f"{fmt(bot_s)} ({'EXCEEDS' if bot_s > CRON_MAX_S else 'fits'} {CRON_MAX_S} s)")
        rows.setdefault("Gmail cron per office (s)", []).append(f"{fmt(bot_s_office)} ({'exceeds' if bot_s_office > CRON_MAX_S else 'fits'})")
        rows.setdefault("Connected Gmail accounts (≈ 1 per client)", []).append(f"{fmt(e['active_clients'])} ({'above' if e['active_clients'] > GMAIL_UNVERIFIED_CAP else 'below'} the cap of {GMAIL_UNVERIFIED_CAP})")
        rows.setdefault("Database growth (MB per month)", []).append(f"{fmt(db_mb)} ({'exceeds' if db_mb > DB_LIMIT_MB else 'below'} {DB_LIMIT_MB} MB assumed)")
        rows.setdefault("New files (GB per month)", []).append(fmt(files_gb, 1))
        rows.setdefault("Invoices needing AI (PDF only) per month", []).append(fmt(invoices * s["pdf_only_share"]))
    for k, v in rows.items():
        print(f"| {k} | " + " | ".join(v) + " |")


if __name__ == "__main__":
    run()
