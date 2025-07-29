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


def create_order(db: Session, order: OrderORM):
	db.add(order)
	db.commit()
	return db.refresh(order)


def update_order_field(db_order, order):
	db_order.order_id = order.order_id
	db_order.order_desc = order.order_desc
	db_order.carrier_id = order.carrier_id
	db_order.order_price = order.order_price
	db_order.order_availability = order.order_availability
	db_order.order_create_date = order.order_create_date
	db_order.order_update_date = order.order_update_date
	return db_order


def update_order(db: Session, order: OrderORM):
	db_order = get_order_by_id(db, order.order_id)
	if not db_order:
		log.info(f"Exception while fetching new order: {db_order}")
		raise HTTPException(status_code=404, detail=f"Order: {order.order_id} not found")
	update_order_field(db_order, order)
	db.commit()
	db.refresh(db_order)
	return db_order


def delete_order_by_order_id(db: Session, order_id: str):
	db_order = get_order_by_id(db, order_id)
	if not db_order:
		log.info(f"Exception while fetching new order: {db_order}")
		raise HTTPException(status_code=404, detail=f"Order: {order_id} not found")
	db.delete(db_order)
	db.commit()
	return db_order
