import uuid

from sqlalchemy import Boolean, DateTime, Float, String, UUID
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql.schema import Column

Base = declarative_base()


class Order(Base):
	__tablename__ = "order"
	__table_args__ = {"schema": "orders"}

	order_id = Column(String, primary_key=True, default=uuid.uuid4, nullable=False)
	order_desc = Column(String, nullable=False)
	order_create_date = Column(DateTime, nullable=False)
	order_update_date = Column(DateTime, nullable=False)
	order_price = Column(Float, nullable=False)
	order_origin = Column(String, nullable=False)
	order_availability = Column(Boolean, nullable=False)
	order_carrier_id = Column(String, nullable=False)
	delivery_date = Column(DateTime, nullable=False)
	order_barcode = Column(UUID, nullable=False)
	order_discount = Column(Float, nullable=False)
	customer_id = Column(String, nullable=False)

	def __str__(self):
		return (f"""\nOrder::
		        order_id: {self.order_id} ,
		        delivery_date:: {self.delivery_date},
		        order_create_date:: {self.order_create_date},
		        order_availability:: {self.order_availability},
		        order_price:: {self.order_price},
		        customer_id:: {self.customer_id},
		        order_barcode:: {self.order_barcode}
		        """)
