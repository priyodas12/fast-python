import logging as log

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.model.order_orm import OrderORM


def get_order_by_id(db: Session, order_id: str):
	return db.query(OrderORM).filter(OrderORM.order_id == order_id).one()


def get_order_by_cust_id(db: Session, customer_id: str):
	return db.query(OrderORM).filter(OrderORM.customer_id == customer_id).first()


def get_order_latest(db: Session):
	return db.query(OrderORM).order_by(OrderORM.order_create_date.desc()).first()


def get_all_orders(db: Session):
	return db.query(OrderORM).all()


def create_order(db: Session, order: OrderORM) -> OrderORM:
	db.add(order)
	db.commit()
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


def update_order(db: Session, order_orm: OrderORM):
	order_exists = get_order_by_id(db, order_orm.order_id)
	if not order_exists:
		log.info(f"Exception while fetching new order: {order_exists}")
		raise HTTPException(status_code=404, detail=f"Order: {order_exists.order_id} not found")
	update_order_field(order_exists, order_orm)
	db.commit()
	db.refresh(order_exists)
	return order_exists


def delete_order_by_order_id(db: Session, order_id: str):
	db_order = get_order_by_id(db, order_id)
	if not db_order:
		log.info(f"Exception while fetching new order: {db_order}")
		raise HTTPException(status_code=404, detail=f"Order: {order_id} not found")
	db.delete(db_order)
	db.commit()
	return db_order
