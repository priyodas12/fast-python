from pydantic import BaseModel


class OrderCreate(BaseModel):
	order_desc: str
	order_price: str
	customer_id: str
	carrier_id: str
