# Reproduce the cash report in Power BI

1. In Power BI Desktop, select **Get data → Text/CSV** and open [monthly_cash_summary.csv](../reports/monthly_cash_summary.csv).
2. Select **Transform Data**. Name the table `monthly_cash_summary`. Set `cash_month` to **Date** and the remaining columns to **Whole Number**. Select **Close & Apply**.
3. Add these measures one at a time and format each as USD with two decimal places.

```dax
Gross Collections = DIVIDE(SUM(monthly_cash_summary[charges_cents]), 100)
```

```dax
Refunds = DIVIDE(SUM(monthly_cash_summary[refunds_cents]), 100)
```

```dax
Net Cash = DIVIDE(SUM(monthly_cash_summary[net_cash_cents]), 100)
```

4. Add three cards for the measures and a line chart with `cash_month` on the X-axis and **Net Cash** on the Y-axis. Use the date field directly to show one point per month. Add a table with the month, event count, and three measures to inspect each month's totals.
5. Clear filters and confirm gross collections of **$183,150.20**, refunds of **$4,583.04**, and net cash of **$178,567.16**. The chart should have 12 monthly points. Compare the monthly amounts with the CSV before sharing the report.
