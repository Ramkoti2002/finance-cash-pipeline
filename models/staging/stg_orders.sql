select
    order_id,
    cast(order_date as date) as order_date,
    lower(trim(order_status)) as order_status,
    order_amount_cents
from {{ ref('orders') }}
