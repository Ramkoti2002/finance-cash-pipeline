"""Inject three errors in a temporary build and verify that dbt catches them."""

import json
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

import duckdb

from run_demo import ROOT, dbt_test_results, run_dbt


def expect_failures(project, *test_names):
    result = run_dbt(project, "test", "--select", *test_names, check=False)
    statuses = dbt_test_results(project)
    if result.returncode != 1 or statuses != dict.fromkeys(test_names, "fail"):
        raise RuntimeError(f"Expected {test_names} to fail, got {statuses}")


def main():
    with TemporaryDirectory(prefix="finance-cash-controls-") as directory:
        project = Path(directory)
        for name in ("dbt_project.yml", "profiles.yml"):
            shutil.copy2(ROOT / name, project / name)
        for name in ("models", "seeds", "tests"):
            shutil.copytree(ROOT / name, project / name)
        run_dbt(project, "build")

        with duckdb.connect(str(project / "finance.duckdb")) as connection:
            connection.execute("""
                update analytics.monthly_cash_summary
                set net_cash_cents = net_cash_cents + 1
                where cash_month = (select min(cash_month) from analytics.monthly_cash_summary)
            """)
        expect_failures(project, "monthly_cash_reconciles")

        with duckdb.connect(str(project / "finance.duckdb")) as connection:
            connection.execute("insert into analytics.payments select * from analytics.payments where payment_id = 1")
            connection.execute("update analytics.payments set order_id = -1 where payment_id = 2")
        expect_failures(project, "unique_stg_payments_payment_id", "payment_order_consistency")

    output = json.dumps({
        "one_cent_net_cash_error": "monthly_cash_reconciles",
        "duplicate_payment_id": "unique_stg_payments_payment_id",
        "payment_without_matching_order": "payment_order_consistency",
    }, indent=2) + "\n"
    (ROOT / "reports").mkdir(exist_ok=True)
    (ROOT / "reports" / "control_results.json").write_text(output, encoding="utf-8")
    print(output, end="")


if __name__ == "__main__":
    main()
