import logging as log

from fastapi import HTTPException

from app.dao.database import get_db
from app.model.order_orm import OrderORM


def get_order_by_id(order_id: str):
	with get_db() as db:
		return db.query(OrderORM).filter(OrderORM.order_id == order_id).first()


def get_order_by_cust_id(customer_id: str):
	with get_db() as db:
		return db.query(OrderORM).filter(OrderORM.customer_id == customer_id).one()


def get_order_latest():
	with get_db() as db:
		return db.query(OrderORM).order_by(OrderORM.order_id.desc()).first()


def get_all_orders():
	with get_db() as db:
		return db.query(OrderORM).all()


def create_order(order: OrderORM) -> OrderORM:
	with get_db() as db:
		db.add(order)
		return order


def update_order_field(order_exists, order):
	order_exists.order_id = order.order_id
	order_exists.customer_id = order.customer_id
	order_exists.weight = order.weight
	order_exists.volume = order.volume
	order_exists.customer_id = order.customer_id
	order_exists.order_discount = order.order_discount
	order_exists.package_type = order.package_type
	order_exists.order_desc = order.order_desc
	order_exists.carrier_id = order.carrier_id
	order_exists.order_price = order.order_price
	order_exists.order_availability = order.order_availability
	order_exists.order_create_date = order.order_create_date
	order_exists.order_update_date = order.order_update_date
	return order_exists


def update_order(order_orm: OrderORM):
	order_exists = get_order_by_id(order_orm.order_id)
	if not order_exists:
		log.info(f"Exception while fetching new order: {order_exists}")
		raise HTTPException(status_code=404, detail=f"Order: {order_exists.order_id} not found")
	update_order_field(order_exists, order_orm)
	with get_db() as db:
		db.add(order_orm)
		return order_orm


def delete_order_by_order_id(order_id: str):
	db_order = get_order_by_id(order_id)
	if not db_order:
		log.info(f"Exception while fetching new order: {db_order}")
		raise HTTPException(status_code=404, detail=f"Order: {order_id} not found")
	with get_db() as db:
		db.delete(db_order)
		return db_order
