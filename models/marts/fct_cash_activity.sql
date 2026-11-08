select
    payments.payment_id,
    payments.order_id,
    payments.payment_date,
    cast(date_trunc('month', payments.payment_date) as date) as cash_month,
    payments.payment_type,
    payments.amount_cents,
    case payments.payment_type
        when 'charge' then payments.amount_cents
        when 'refund' then -payments.amount_cents
    end as signed_amount_cents
from {{ ref('stg_payments') }} as payments
inner join {{ ref('stg_orders') }} as orders
    on payments.order_id = orders.order_id
where orders.order_status = 'complete'
