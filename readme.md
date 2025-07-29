### FAST API WITH PYTHON

CMD

``
pip install fastapi[all]
pip install scalar_fastapi
``

Create Table:

```
CREATE TABLE orders.order (
    order_id string PRIMARY KEY not null,
    order_desc string not null,
    order_create_date timestamptz,
    order_update_date timestamptz,
    order_price float,
    order_origin string,
    order_availability bool,
    customer_id string,
    order_carrier_id string,
    delivery_date date,
    order_barcode uuid,
    order_discount float
);
```