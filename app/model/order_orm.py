import uuid

from sqlalchemy import Boolean, DateTime, Float, String, UUID
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql.schema import Column

Base = declarative_base()


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
