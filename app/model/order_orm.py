import uuid

from sqlalchemy import Boolean, DateTime, Float, String, UUID
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql.schema import Column

Base = declarative_base()


def order_to_order_orm(order):
	order_orm = OrderORM()
	order_orm.order_id = order.order_id
	order_orm.order_desc = order.order_desc
	order_orm.order_create_date = order.order_create_date
	order_orm.order_update_date = order.order_update_date
	order_orm.delivery_date = order.delivery_date
	order_orm.order_price = order.order_price
	order_orm.order_origin = order.order_origin
	order_orm.order_availability = order.order_availability
	order_orm.order_barcode = order.order_barcode
	order_orm.order_discount = order.order_discount
	order_orm.customer_id = order.customer_id
	order_orm.carrier_id = order.carrier_id
	order_orm.weight = order.weight
	order_orm.volume = order.volume
	order_orm.package_type = order.package_type
	order_orm.order_status = order.order_status
	return order_orm


class OrderORM(Base):
	__tablename__ = "order"
	__table_args__ = {"schema": "orders"}

	order_id = Column(String, primary_key=True, default=uuid.uuid4, nullable=False)
	order_desc = Column(String, nullable=True)
	order_create_date = Column(DateTime, nullable=True)
	order_update_date = Column(DateTime, nullable=True)
	order_price = Column(Float, nullable=True)
	order_origin = Column(String, nullable=True)
	order_availability = Column(Boolean, nullable=True)
	carrier_id = Column(String, nullable=True)
	delivery_date = Column(DateTime, nullable=True)
	order_barcode = Column(UUID, nullable=True)
	order_discount = Column(Float, nullable=True)
	customer_id = Column(String, nullable=True)
	weight = Column(Float, nullable=True)
	volume = Column(Float, nullable=True)
	package_type = Column(String, nullable=True)
	order_status = Column(String, nullable=True)

	def __str__(self):
		return (f"""\nOrder::
		        order_id: {self.order_id} ,
		        delivery_date:: {self.delivery_date},
		        order_create_date:: {self.order_create_date},
		        order_availability:: {self.order_availability},
		        order_price:: {self.order_price},
		        customer_id:: {self.customer_id},
		        order_barcode:: {self.order_barcode},
		        order_desc:: {self.order_desc},
		        order_carrier_id:: {self.carrier_id},
		        """)

	class Config:
		orm_mode = True
