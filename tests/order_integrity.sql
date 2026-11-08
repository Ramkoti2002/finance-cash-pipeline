select *
from {{ ref('stg_orders') }}
where order_date is null
   or order_amount_cents is null
   or order_amount_cents <= 0
   or order_status is null
   or order_status not in ('complete', 'cancelled')
