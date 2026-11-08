select payments.payment_id, payments.order_id
from {{ ref('stg_payments') }} as payments
left join {{ ref('stg_orders') }} as orders
    on payments.order_id = orders.order_id
where orders.order_id is null
   or orders.order_status <> 'complete'
   or payments.payment_date < orders.order_date
