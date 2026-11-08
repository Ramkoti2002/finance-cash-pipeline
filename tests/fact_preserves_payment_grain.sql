select
    source.payment_id as source_payment_id,
    fact.payment_id as fact_payment_id
from {{ ref('stg_payments') }} as source
full outer join {{ ref('fct_cash_activity') }} as fact on source.payment_id = fact.payment_id
where source.payment_id is null
   or fact.payment_id is null
   or source.order_id <> fact.order_id
   or source.payment_date <> fact.payment_date
   or source.payment_type <> fact.payment_type
   or source.amount_cents <> fact.amount_cents
