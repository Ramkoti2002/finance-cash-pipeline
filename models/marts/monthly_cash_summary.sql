select
    cash_month,
    count(*) as event_count,
    sum(case when payment_type = 'charge' then amount_cents else 0 end) as charges_cents,
    sum(case when payment_type = 'refund' then amount_cents else 0 end) as refunds_cents,
    sum(signed_amount_cents) as net_cash_cents
from {{ ref('fct_cash_activity') }}
group by cash_month
