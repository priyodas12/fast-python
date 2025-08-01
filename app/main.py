import logging
import os
import random
import uuid
from datetime import datetime, timedelta
from typing import Any

import coloredlogs
from dotenv import load_dotenv
from faker import Faker
from fastapi import FastAPI, Query
from fastapi.exceptions import ResponseValidationError
from scalar_fastapi import get_scalar_api_reference
from sqlalchemy import text
from sqlalchemy.dialects import registry
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from starlette.responses import JSONResponse

from app.dao.database import session
from app.dao.order_dao import *
from app.model.order import Order
from app.model.order_orm import OrderORM
from app.model.order_package import OrderPackage
from app.model.order_status import OrderStatus

load_dotenv(dotenv_path=".env")
app = FastAPI(title=os.getenv("APP_NAME"),
              version=os.getenv("APP_VERSION"),
              server_description=[{"url": "http://localhost:8000", "description": "dev server"}],
              debug=True)
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
		"timestamp": datetime.now(),
		"trace_id": str(uuid.uuid4()),
		"http_response_code": 200,
		"thought_of_the_day": faker.paragraph(),
	}


@app.get("/orders/customer", response_model=None)
def get_order_by_customer_id(customer_id: str | None = Query(default=None, max_length=20)) -> dict[str, Any] | dict[
	str, str] | set[str | Any] | JSONResponse:
	try:
		db = session()
		if not customer_id:
			log.info("no customer id provided")
			order_latest = get_order_latest(db)
			log.info(f"latest order : {order_latest} returned!")
			return {"order": order_latest,
			        "timestamp": datetime.now().isoformat(),
			        "trace_id": str(uuid.uuid4()),
			        "http_response_code": 200,
			        }
		order_orm = get_order_by_cust_id(db, customer_id)
		log.info(f"order with customer_id {customer_id} from cockroachdb: {order_orm.__str__()}")
		if not order_orm:
			log.debug(f"error while getting order with customer_id {customer_id} from db")
			return JSONResponse(status_code=404, content={"order": None,
			                                              "timestamp": datetime.now().isoformat(),
			                                              "trace_id": str(uuid.uuid4()),
			                                              "http_response_code": 404,
			                                              })
		return {"order": order_orm,
		        "timestamp": datetime.now().isoformat(),
		        "trace_id": str(uuid.uuid4()),
		        "http_response_code": 200,
		        }
	except (SQLAlchemyError, AssertionError, OperationalError, Exception) as e:
		log.error(f"FetchOrderByCustomerId:: Exception:: {e.args[0]}, type: {type(e)}")
		return JSONResponse(status_code=500, content={"error": str(e),
		                                              "timestamp": datetime.now().isoformat(),
		                                              "trace_id": str(uuid.uuid4()),
		                                              "http_response_code": 500,
		                                              })


@app.get("/orders/{order_id}", response_model=None)
def get_order_by_order_id(order_id: str) -> dict[str, str] | JSONResponse:
	try:
		db = session()
		order_orm = get_order_by_id(db, order_id)
		log.info(f"order {order_id} from cockroachdb: {order_orm.__str__()}")
		if not order_orm:
			log.debug(f"error while getting order {order_id} from db")
			return JSONResponse(status_code=404, content={"order": None,
			                                              "timestamp": datetime.now().isoformat(),
			                                              "trace_id": str(uuid.uuid4()),
			                                              "http_response_code": 404,
			                                              })
		return {"order": order_orm,
		        "timestamp": datetime.now().isoformat(),
		        "trace_id": str(uuid.uuid4()),
		        "http_response_code": 200,
		        }
	except (SQLAlchemyError, AssertionError, OperationalError, Exception) as e:
		log.error(f"FetchOrderByOrderId:: Exception:: {e}, type: {type(e)}")
		return JSONResponse(status_code=500, content={"error": str(e),
		                                              "timestamp": datetime.now().isoformat(),
		                                              "trace_id": str(uuid.uuid4()),
		                                              "http_response_code": 500,
		                                              })


@app.get("/orders")
def get_orders():
	try:
		db = session()
		orders = get_all_orders(db)
		for order in orders:
			log.info(f"fetched orders: {order.__str__()}")
		return {"orders": orders,
		        "timestamp": datetime.now().isoformat(),
		        "trace_id": str(uuid.uuid4()),
		        "http_response_code": 200,
		        }
	except (SQLAlchemyError, AssertionError, OperationalError, Exception) as e:
		log.error(f"FetchOrders:: Exception:: {e.args[0]}, type: {type(e)}")
		return JSONResponse(status_code=500, content={"error": str(e),
		                                              "timestamp": datetime.now().isoformat(),
		                                              "trace_id": str(uuid.uuid4()),
		                                              "http_response_code": 500,
		                                              })


@app.post("/v1/orders", response_model=None)
def post_order(order_desc: str, order_price: float, carrier_id: str, customer_id: str) -> dict[
	                                                                                          str, Order | str | int] | JSONResponse:
	try:
		db = session()
		random_date = faker.date_time_between(start_date=faker.past_date(), end_date=faker.date_time().now())
		order = OrderORM(order_id=str(uuid.uuid4()),
		                 order_desc=f"{order_desc}{faker.company()}",
		                 order_price=float(order_price + faker.random_int()),
		                 carrier_id=f"{carrier_id}{faker.random_int(10000, 910000)}",
		                 customer_id=f"{customer_id}{faker.random_int(10000, 90000)}",
		                 order_barcode=uuid.uuid4(),
		                 order_create_date=random_date + timedelta(days=-5),
		                 order_update_date=random_date,
		                 order_origin=faker.country(),
		                 delivery_date=faker.date_time(),
		                 order_discount=float(faker.random_number(4)) / 100,
		                 order_availability=float(faker.random_number()) > 7,
		                 weight=float(faker.random_number()) / 100,
		                 volume=float(faker.random_number()) / 100,
		                 order_status=random.choice(list(OrderStatus)),
		                 package_type=random.choice(list(OrderPackage)), )
		create_order(db, order)
		order_return = Order.order_orm_to_order(order)
		return {"order": order_return,
		        "timestamp": datetime.now().isoformat(),
		        "trace_id": str(uuid.uuid4()),
		        "http_response_code": 201,
		        }
	except (SQLAlchemyError, AssertionError, ResponseValidationError, OperationalError, Exception) as e:
		log.error(f"CreateOrder:: Exception:: {e}, type: {type(e)} for order_id: {order.order_id}")
		return JSONResponse(status_code=500, content={"error": str(e),
		                                              "timestamp": datetime.now().isoformat(),
		                                              "trace_id": str(uuid.uuid4()),
		                                              "http_response_code": 500,
		                                              })


@app.post("/v2/orders", response_model=None)
def post_order_with_request_body(order: Order) -> dict[str, Order | str | int] | JSONResponse:
	try:
		db = session()
		random_date = faker.date_time_between(start_date=faker.past_date(), end_date=faker.date_time().now())
		log.info(f"received order data: {order}")
		order = OrderORM(order_id=str(uuid.uuid4()),
		                 order_desc=f"{order.order_desc}{faker.company()}",
		                 order_price=float(order.order_price + faker.random_int()),
		                 carrier_id=f"{order.carrier_id}{faker.random_int(10000, 910000)}",
		                 customer_id=f"{order.customer_id}{faker.random_int(10000, 90000)}",
		                 order_barcode=uuid.uuid4(),
		                 order_create_date=random_date + timedelta(days=-5),
		                 order_update_date=random_date,
		                 order_origin=faker.country(),
		                 delivery_date=faker.date_time(),
		                 order_discount=float(faker.random_number(4)) / 100,
		                 order_availability=float(faker.random_number()) > 0.7,
		                 weight=float(faker.random_number()) / 100,
		                 volume=float(faker.random_number()) / 100,
		                 order_status=random.choice(list(OrderStatus)),
		                 package_type=random.choice(list(OrderPackage)), )
		order_created = Order.order_orm_to_order(create_order(db, order))
		log.info(f"created order: {order_created}")
		return {
			"order": order_created,
			"timestamp": datetime.now().isoformat(),
			"trace_id": str(uuid.uuid4()),
			"http_response_code": 201,
		}
	except (SQLAlchemyError, AssertionError, ResponseValidationError, OperationalError, Exception) as e:
		log.error(f"CreateOrder:: Exception:: {e}, type: {type(e)} for order_id: {order.order_id}")
		return JSONResponse(status_code=500, content={"error": str(e),
		                                              "timestamp": datetime.now().isoformat(),
		                                              "trace_id": str(uuid.uuid4()),
		                                              "http_response_code": 500,
		                                              })


@app.put("/v1/orders", response_model=None)
def put_order(order: Order) -> dict[str, Order | str | int] | JSONResponse:
	try:
		db = session()
		log.info(f"received order data: {order}")
		order = OrderORM(
			order_id=order.order_id,
			order_desc=order.order_desc,
			order_price=order.order_price,
			carrier_id=order.carrier_id,
			customer_id=order.customer_id,
			order_barcode=order.order_barcode,
			order_create_date=order.order_update_date,
			order_update_date=datetime.now(),
			delivery_date=order.delivery_date,
			order_availability=order.order_availability,
			weight=order.weight,
			volume=order.volume,
			order_status=order.order_status,
			package_type=order.package_type, )

		order_updated = update_order(db, order)
		order = Order.order_orm_to_order(order_updated)
		log.info(f"updated order: {order}")
		return {
			"order": order,
			"timestamp": datetime.now().isoformat(),
			"trace_id": str(uuid.uuid4()),
			"http_response_code": 200,
		}
	except (SQLAlchemyError, AssertionError, ResponseValidationError, OperationalError, Exception) as e:
		log.error(f"UpdateOrder:: Exception:: {e}, type: {type(e)} for order_id: {order.order_id}")
		return JSONResponse(status_code=500, content={"error": str(e),
		                                              "timestamp": datetime.now().isoformat(),
		                                              "trace_id": str(uuid.uuid4()),
		                                              "http_response_code": 500,
		                                              })


@app.delete("/v1/orders/{order_id}", response_model=None)
def delete_order(order_id: str) -> dict[str, any] | dict[str, str]:
	try:
		db = session()
		log.info(f"deleting order data: {order_id}")
		deleted_order = delete_order_by_order_id(db, order_id)
		log.info(f"updated order: {deleted_order}")
		return {f"{order_id}": "deleted"}
	except (SQLAlchemyError, AssertionError, ResponseValidationError, OperationalError, Exception) as e:
		log.error(f"DeleteOrder:: Exception:: {e}, type: {type(e)} for order_id: {order_id}")
		return {"error": str(e),
		        "timestamp": datetime.now().isoformat(),
		        "trace_id": str(uuid.uuid4()),
		        "http_response_code": 500,
		        }


# documentation purpose
# http://0.0.0.0:8000/redoc
@app.get("/scalar", include_in_schema=False)
def get_scalar_docs(self):
	return get_scalar_api_reference(
		openapi_url="/openapi.json",
		title=f"Scalar API",
	)
