"""Build the local dbt project, reconcile it to raw data, and export report files."""

import csv
import json
import os
import subprocess
from collections import defaultdict
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
REPORT_COLUMNS = ("cash_month", "event_count", "charges_cents", "refunds_cents", "net_cash_cents")


def run_dbt(project, *args, check=True):
    return subprocess.run(
        ["dbt", *args, "--profiles-dir", ".", "--target", "local"],
        cwd=project,
        check=check,
        env={**os.environ, "DBT_SEND_ANONYMOUS_USAGE_STATS": "false"},
    )


def dbt_test_results(project):
    results = json.loads((project / "target" / "run_results.json").read_text(encoding="utf-8"))
    return {
        result["unique_id"].split(".")[2]: result["status"]
        for result in results["results"]
        if result["unique_id"].startswith("test.")
    }


def totals_from_source():
    monthly = defaultdict(lambda: {"charge": 0, "refund": 0, "count": 0})
    with (ROOT / "seeds" / "payments.csv").open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            month = row["payment_date"][:7] + "-01"
            monthly[month][row["payment_type"]] += int(row["amount_cents"])
            monthly[month]["count"] += 1
    return [
        (month, data["count"], data["charge"], data["refund"], data["charge"] - data["refund"])
        for month, data in sorted(monthly.items())
    ]


def main():
    run_dbt(ROOT, "build")
    test_results = dbt_test_results(ROOT)
    if not test_results or any(status != "pass" for status in test_results.values()):
        raise RuntimeError(f"Expected all dbt tests to pass, got {test_results}")

    with duckdb.connect(str(ROOT / "finance.duckdb"), read_only=True) as connection:
        rows = connection.execute("""
            select cast(cash_month as varchar), event_count, charges_cents, refunds_cents, net_cash_cents
            from analytics.monthly_cash_summary
            order by cash_month
        """).fetchall()
    if rows != totals_from_source():
        raise RuntimeError("The monthly cash mart differs from the independent Python totals")

    reports = ROOT / "reports"
    reports.mkdir(exist_ok=True)
    with (reports / "monthly_cash_summary.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(REPORT_COLUMNS)
        writer.writerows(rows)

    validation = {
        "dataset": "synthetic",
        "dbt_data_tests_passed": len(test_results),
        "independent_monthly_reconciliation": "passed",
        "months": len(rows),
        **{
            column: sum(row[index] for row in rows)
            for index, column in enumerate(REPORT_COLUMNS[1:], start=1)
        },
    }
    output = json.dumps(validation, indent=2) + "\n"
    (reports / "validation.json").write_text(output, encoding="utf-8")
    print(output, end="")


if __name__ == "__main__":
    main()
