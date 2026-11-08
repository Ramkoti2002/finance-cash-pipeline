select orders.order_id, orders.order_amount_cents, sum(payments.amount_cents) as charged_cents
from {{ ref('stg_orders') }} as orders
inner join {{ ref('stg_payments') }} as payments on orders.order_id = payments.order_id
where payments.payment_type = 'charge'
group by orders.order_id, orders.order_amount_cents
having sum(payments.amount_cents) > orders.order_amount_cents
