from datetime import datetime
from typing import Optional

from pydantic import *
from sqlalchemy.testing.pickleable import Order

from app.model.order_orm import OrderORM


class Order(BaseModel):
	order_id: Optional[str] = None
	# validations
	order_desc: Optional[str] = None
	order_price: Optional[float] = None
	weight: Optional[float] = None
	package_type: Optional[str] = None
	volume: Optional[float] = None
	order_status: Optional[str] = None
	order_create_date: Optional[datetime] = None
	order_update_date: Optional[datetime] = None
	delivery_date: Optional[datetime] = None
	customer_id: Optional[str] = None
	carrier_id: Optional[str] = None
	order_discount: Optional[float] = None
	order_availability: Optional[bool] = None
	order_origin: Optional[str] = None
	order_barcode: Optional[str] = None

	class Config:
		arbitrary_types_allowed = True
		from_arbitrary_types = True

	def order_orm_to_order(order_orm: OrderORM) -> Order:
		return Order(
			order_id=order_orm.order_id,
			order_desc=order_orm.order_desc,
			order_status=order_orm.order_status,
			package_type=order_orm.package_type,
			weight=order_orm.weight,
			volume=order_orm.volume,
			order_create_date=str(order_orm.order_create_date),
			order_update_date=str(order_orm.order_update_date),
			order_availability=order_orm.order_availability,
			order_origin=order_orm.order_origin,
			order_barcode=str(order_orm.order_barcode),
			order_price=order_orm.order_price,
			carrier_id=order_orm.carrier_id,
			customer_id=order_orm.customer_id,
			delivery_date=str(order_orm.delivery_date),
			order_discount=order_orm.order_discount,
		)
