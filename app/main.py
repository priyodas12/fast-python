import logging
import os
import uuid
from datetime import datetime, timedelta

import coloredlogs
from dotenv import load_dotenv
from faker import Faker
from fastapi import FastAPI, Query
from fastapi.exceptions import ResponseValidationError
from scalar_fastapi import get_scalar_api_reference
from sqlalchemy import text
from sqlalchemy.dialects import registry
from sqlalchemy.exc import SQLAlchemyError

from app.dao.database import session
from app.dao.order_dao import create_order, get_all_orders, get_order_by_cust_id, get_order_by_id, get_order_latest, \
	update_order
from app.model.order_model import Order

load_dotenv(dotenv_path=".env")
app = FastAPI(title=os.getenv("APP_NAME"),
              version=os.getenv("APP_VERSION"),
              server_description=[{"url": "http://localhost:8000", "description": "dev server"}]
              )
faker = Faker()
registry.register("cockroach.psycopg2", "cockroach_dialect", "CockroachDBDialect")
log = logging.getLogger("sqlalchemy.engine")
coloredlogs.install(level="INFO", logger=log)


@app.on_event("startup")
def on_start():
	try:
		db = session()
		db.execute(text("SELECT 1"))
		log.info(f"Database connection tested at {datetime.now()}")
		db.close()
	except Exception as e:
		log.error(f"Exception while connecting database:: {e}")


@app.get("/")
def get_app_status():
	return {
		"time": datetime.now(),
		"request_id": uuid.uuid4(),
		"thought_of_the_day": faker.paragraph(),
	}


@app.get("/orders/customer", response_model=None)
def get_order_by_customer_id(customer_id: str | None = Query(default=None, max_length=20)) -> dict[str, any] | dict[
	str, str]:
	try:
		db = session()
		if not customer_id:
			log.info("no customer id provided")
			order_latest = get_order_latest(db)
			log.info(f"latest order : {order_latest} returned!")
			return {"order": order_latest}
		order_orm = get_order_by_cust_id(db, customer_id)
		log.info(f"order with customer_id {customer_id} from cockroachdb: {order_orm.__str__()}")
		if not order_orm:
			log.debug(f"error while getting order with customer_id {customer_id} from db")
			return {"error": f"customer_id:: {customer_id} not found"}
		return dict("order", order_orm)
	except SQLAlchemyError as e:
		log.error(e.args[0])
		return {"error": str(e.args[0])}
	except AssertionError as e:
		log.error(e.args[0])
		return {"error": str(e.args[0])}
	except ResponseValidationError as e:
		log.error(e.args[0])
		return {"error": str(e.args[0])}


@app.get("/orders/{order_id}", response_model=None)
def get_order_by_order_id(order_id: str) -> dict[str, any] | dict[str, str]:
	try:
		db = session()
		order_orm = get_order_by_id(db, order_id)
		log.info(f"order {order_id} from cockroachdb: {order_orm.__str__()}")
		if not order_orm:
			log.debug(f"error while getting order {order_id} from db")
			return {"error": f"order_id:: {order_id} not found"}
		return {"orders": order_orm}
	except SQLAlchemyError as e:
		log.error(e.args[0])
		return {"error": str(e.args[0])}
	except AssertionError as e:
		log.error(e.args[0])
		return {"error": str(e.args[0])}
	except ResponseValidationError as e:
		log.error(e.args[0])
		return {"error": str(e.args[0])}


@app.get("/orders")
def get_orders():
	try:
		db = session()
		orders = get_all_orders(db)
		for order in orders:
			log.info(f"fetched orders: {order.__str__()}")
		return {"orders": orders}
	except SQLAlchemyError as e:
		log.error(e.args[0])
		return {"error": str(e.args[0])}
	except AssertionError as e:
		log.error(e.args[0])
		return {"error": str(e.args[0])}


@app.post("/v1/orders", response_model=None)
def post_order(order_desc: str, order_price: float, order_carrier_id: str, customer_id: str) -> dict[str, any] | dict[
	str, str]:
	try:
		db = session()
		random_date = faker.date_time_between(start_date=faker.past_date(), end_date=faker.date_time().now())
		order = Order(order_id=str(uuid.uuid4()),
		              order_desc=f"{order_desc}{faker.company()}",
		              order_price=float(order_price + faker.random_int()),
		              order_carrier_id=f"{order_carrier_id}{faker.random_int(10000, 910000)}",
		              customer_id=f"{customer_id}{faker.random_int(10000, 90000)}",
		              order_barcode=uuid.uuid4(),
		              order_create_date=random_date + timedelta(days=-5),
		              order_update_date=random_date,
		              order_origin=faker.country(),
		              delivery_date=faker.date_time(),
		              order_discount=float(faker.random_number(4)) / 100,
		              order_availability=float(faker.random_number()) > 7, )
		create_order(db, order)
		return {"order": order}
	except SQLAlchemyError as e:
		log.error(e.args[0])
		return {"error": str(e.args[0])}
	except AssertionError as e:
		log.error(e.args[0])
		return {"error": str(e.args[0])}
	except ResponseValidationError as e:
		log.error(e.args[0])
		return {"error": str(e.args[0])}


@app.post("/v2/orders", response_model=None)
def post_order_with_request_body(data: dict[str, str | float]) -> dict[str, any] | dict[str, str]:
	try:
		db = session()
		random_date = faker.date_time_between(start_date=faker.past_date(), end_date=faker.date_time().now())
		log.info(f"received order data: {data}")
		order = Order(order_id=str(uuid.uuid4()),
		              order_desc=f"{data.get("order_desc")}{faker.company()}",
		              order_price=float(data.get("order_price") + faker.random_int()),
		              order_carrier_id=f"{data.get("order_carrier_id")}{faker.random_int(10000, 910000)}",
		              customer_id=f"{data.get("customer_id")}{faker.random_int(10000, 90000)}",
		              order_barcode=uuid.uuid4(),
		              order_create_date=random_date + timedelta(days=-5),
		              order_update_date=random_date,
		              order_origin=faker.country(),
		              delivery_date=faker.date_time(),
		              order_discount=float(faker.random_number(4)) / 100,
		              order_availability=float(faker.random_number()) > 7, )
		create_order(db, order)
		return {"order": order}
	except SQLAlchemyError as e:
		log.error(e.args[0])
		return {"error": str(e.args[0])}
	except AssertionError as e:
		log.error(e.args[0])
		return {"error": str(e.args[0])}
	except ResponseValidationError as e:
		log.error(e.args[0])
		return {"error": str(e.args[0])}


@app.put("/v1/orders", response_model=None)
def put_order(data: dict[str, str | float | bool | datetime]) -> dict[str, any] | dict[str, str]:
	try:
		db = session()
		random_date = faker.date_time_between(start_date=faker.past_date(), end_date=faker.date_time().now())
		log.info(f"received order data: {data}")
		order = Order(
			order_id=f"{data.get("order_id")}",
			order_desc=f"{data.get("order_desc")}",
			order_price=float(data.get("order_price")),
			order_carrier_id=f"{data.get("order_carrier_id")}",
			customer_id=f"{data.get("customer_id")}",
			order_barcode=f"{data.get("order_barcode")}",
			order_update_date=datetime.now(),
			delivery_date=data.get("order_delivery_date"),
			order_availability=data.get("order_availability"), )
		order_updated = update_order(db, order)
		log.info(f"updated order: {order_updated}")
		return {"order": order_updated}
	except SQLAlchemyError as e:
		log.error(e.args[0])
		return {"error": str(e.args[0])}
	except AssertionError as e:
		log.error(e.args[0])
		return {"error": str(e.args[0])}
	except ResponseValidationError as e:
		log.error(e.args[0])
		return {"error": str(e.args[0])}
	except Exception as e:
		log.error(e.args[0])


# documentation purpose
# http://0.0.0.0:8000/redoc
@app.get("/scalar", include_in_schema=False)
def get_scalar_docs(self):
	return get_scalar_api_reference(
		openapi_url="/openapi.json",
		title=f"Scalar API",
	)
