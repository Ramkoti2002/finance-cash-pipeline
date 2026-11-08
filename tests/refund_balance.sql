with balances as (
    select
        payment_id,
        order_id,
        sum(case when payment_type = 'charge' then amount_cents else -amount_cents end)
            over (
                partition by order_id order by payment_date, payment_id
                rows between unbounded preceding and current row
            ) as collected_balance_cents
    from {{ ref('stg_payments') }}
)
select *
from balances
where collected_balance_cents < 0
