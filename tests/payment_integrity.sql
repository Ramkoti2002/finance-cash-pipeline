select *
from {{ ref('stg_payments') }}
where payment_date is null
   or amount_cents is null
   or amount_cents <= 0
   or payment_type is null
   or payment_type not in ('charge', 'refund')
