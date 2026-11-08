with source_totals as (
    select
        cast(date_trunc('month', cast(payment_date as date)) as date) as cash_month,
        count(*) as event_count,
        sum(case when lower(trim(payment_type)) = 'charge' then amount_cents else 0 end) as charges_cents,
        sum(case when lower(trim(payment_type)) = 'refund' then amount_cents else 0 end) as refunds_cents
    from {{ ref('payments') }}
    group by 1
)
select source.cash_month as source_month, report.cash_month as report_month
from source_totals as source
full outer join {{ ref('monthly_cash_summary') }} as report on source.cash_month = report.cash_month
where source.cash_month is null
   or report.cash_month is null
   or source.event_count <> report.event_count
   or source.charges_cents <> report.charges_cents
   or source.refunds_cents <> report.refunds_cents
   or source.charges_cents - source.refunds_cents <> report.net_cash_cents
