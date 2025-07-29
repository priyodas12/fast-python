from datetime import datetime
from typing import Optional

from pydantic import *


class Order(BaseModel):
	order_id: Optional[str] = None
	# validations
	order_desc: str = Field(alias='order_desc', max_length=100)
	order_price: float
	weight: Optional[float] = None
	package_type: Optional[str] = None
	volume: Optional[float] = None
	order_status: Optional[str] = None
	order_create_date: Optional[datetime] = None
	order_update_date: Optional[datetime] = None
	delivery_date: Optional[datetime] = None
	customer_id: str = Field(alias='customer_id', max_length=12)
	carrier_id: str
	order_discount: Optional[float] = None
	order_availability: Optional[bool] = None
	order_origin: Optional[str] = None
	order_barcode: Optional[str] = None

	class Config:
		orm_mode = True
