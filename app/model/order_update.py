from datetime import datetime

from pydantic import *


class OrderUpdate(BaseModel):
	order_id: str
	order_desc: str
	order_price: str
	weight: float
	package_type: str
	volume: float
	order_status: str
	order_create_date: datetime
	order_update_date: datetime
	delivery_date: datetime
	customer_id: str
	carrier_id: str
	order_discount: float
	order_availability: float
	order_origin: str
	order_barcode: str

	class Config:
		arbitrary_types_allowed = True
		from_arbitrary_types = True
