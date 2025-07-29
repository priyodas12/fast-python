### FAST API WITH PYTHON

Tech Stack:

```
python
fast-api
cockroach-db(docker)
```

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
    weight float not null,
    volume float not null,
    package_type string,
    order_status string,
    order_create_date timestamptz,
    order_update_date timestamptz,
    order_price float,
    order_origin string,
    order_availability bool,
    customer_id string,
    delivery_date date,
    order_barcode uuid,
    order_discount float,
    carrier_id string
);
```

