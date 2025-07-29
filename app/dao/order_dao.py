from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.model.order_model import Order


def get_order_by_id(db: Session, order_id: str):
	return db.query(Order).filter(Order.order_id == order_id).one()


def get_order_by_cust_id(db: Session, customer_id: str):
	return db.query(Order).filter(Order.customer_id == customer_id).one()


def get_order_latest(db: Session):
	return db.query(Order).order_by(Order.order_create_date.desc()).first()


def get_all_orders(db: Session):
	return db.query(Order).all()


def create_order(db: Session, order: Order):
	return db.add(order)


def update_order(db: Session, order: Order):
	db_user = get_order_by_id(db, order.order_id)
	if not Order.order_id:
		raise HTTPException(status_code=404, detail=f"Order: {order.order_id} not found")
	db.commit()
	db.refresh(db_user)
	return db_user


def delete_order(db: Session, order: Order):
	return db.delete(order)
