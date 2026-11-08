"""Generate reproducible synthetic orders and payment events without personal data."""

import csv
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def write_seed(name, columns, rows):
    with (ROOT / "seeds" / f"{name}.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(columns)
        writer.writerows(rows)


def main():
    orders, payments = [], []
    year_end = date(2025, 12, 31)

    def add_payment(order_id, paid_on, event, amount):
        payments.append((len(payments) + 1, order_id, paid_on, event, amount))

    for month in range(1, 13):
        for number in range(1, 101):
            order_id = 100 * (month - 1) + number
            ordered_on = date(2025, month, 1) + timedelta(days=(number * 7 + month) % 24)
            amount = 4200 + (order_id * 1733 + month * 911) % 29500
            cancelled = number % 10 == 0
            orders.append((order_id, ordered_on, "cancelled" if cancelled else "complete", amount))
            if cancelled or number % 13 == 0:
                continue
            collected = amount // 2 if number % 17 == 0 else amount
            if number % 4 == 0:
                first_charge = collected // 2
                add_payment(order_id, ordered_on, "charge", first_charge)
                add_payment(order_id, ordered_on + timedelta(days=2), "charge", collected - first_charge)
            else:
                add_payment(order_id, ordered_on + timedelta(days=1), "charge", collected)
            if number % 9 == 0:
                refunded_on = min(ordered_on + timedelta(days=12), year_end)
                add_payment(order_id, refunded_on, "refund", collected // 5)

    write_seed("orders", ("order_id", "order_date", "order_status", "order_amount_cents"), orders)
    write_seed("payments", ("payment_id", "order_id", "payment_date", "payment_type", "amount_cents"), payments)


if __name__ == "__main__":
    main()
