select
    payment_id,
    order_id,
    cast(payment_date as date) as payment_date,
    lower(trim(payment_type)) as payment_type,
    amount_cents
from {{ ref('payments') }}
