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
from sqlalchemy.dialects import registry
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from starlette.responses import JSONResponse

from app.dao.database import init_db
from app.dao.order_dao import *
from app.model.enums.order_package import OrderPackage
from app.model.enums.order_status import OrderStatus
from app.model.order_create import OrderCreate
from app.model.order_orm import Base, OrderORM
from app.model.order_update import OrderUpdate

load_dotenv(dotenv_path=".env")
app = FastAPI(title=os.getenv("APP_NAME"),
              version=os.getenv("APP_VERSION"))
faker = Faker()
registry.register("cockroach.psycopg2", "cockroach_dialect", "CockroachDBDialect")
log = logging.getLogger("sqlalchemy.engine")
coloredlogs.install(level="INFO", logger=log)


def on_application_boot_up():
	engine, session_local, log = init_db()
	Base.metadata.create_all(engine)


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
		if not customer_id:
			log.info("no customer id provided")
			order_latest = get_order_latest()
			log.info(f"latest order : {order_latest} returned!")
			return {"order": order_latest,
			        "timestamp": datetime.now().isoformat(),
			        "trace_id": str(uuid.uuid4()),
			        "http_response_code": 200,
			        }
		order_orm = get_order_by_cust_id(customer_id)
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
		order_orm = get_order_by_id(order_id)
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
		orders = get_all_orders()
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
	                                                                                          str, OrderORM | str | int] | JSONResponse:
	try:
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
		order_returned = create_order(order)
		return {"order": order_returned,
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
def post_order_with_request_body(order_create: OrderCreate) -> dict[str, OrderORM | str | int] | JSONResponse:
	try:
		random_date = faker.date_time_between(start_date=faker.past_date(), end_date=faker.date_time().now())
		log.info(f"received order data: {order_create}")
		order_db = OrderORM(**order_create.dict())

		if "test" in order_db.order_desc:
			order_db.order_desc = faker.company() + "-" + faker.sentence()
		if float(order_db.order_price) < 100.00:
			order_db.order_price = faker.random_number() * 99.999
		if "test" in order_db.customer_id:
			order_db.customer_id = "CUSTOMER-" + str(faker.random_number())
		if "test" in order_db.carrier_id:
			order_db.carrier_id = "CARRIER-" + str(faker.random_number())
		order_db.order_discount = float(faker.random_number(4)) / 100
		order_db.order_availability = float(faker.random_number()) > 0.7
		order_db.weight = float(faker.random_number()) / 100
		order_db.volume = float(faker.random_number()) / 100
		order_db.order_status = random.choice(list(OrderStatus))
		order_db.order_package = random.choice(list(OrderPackage))
		order_db.order_origin = faker.country()
		order_db.delivery_date = faker.date_time()
		order_db.order_barcode = uuid.uuid4()
		order_db.order_create_date = random_date
		order_db.order_update_date = random_date
		order_db.order_id = str(uuid.uuid4())

		order_created = create_order(order_db)
		log.info(f"created order: {order_created}")
		return {
			"order": order_created,
			"timestamp": datetime.now().isoformat(),
			"trace_id": str(uuid.uuid4()),
			"http_response_code": 201,
		}
	except (SQLAlchemyError, AssertionError, ResponseValidationError, OperationalError, Exception) as e:
		log.error(f"CreateOrder:: Exception:: {e}, type: {type(e)} for order_id: {order_db.order_id}")
		return JSONResponse(status_code=500, content={"error": str(e),
		                                              "timestamp": datetime.now().isoformat(),
		                                              "trace_id": str(uuid.uuid4()),
		                                              "http_response_code": 500,
		                                              })


@app.put("/v1/orders", response_model=None)
def put_order(order_update: OrderUpdate) -> dict[str, OrderORM | str | int] | JSONResponse:
	try:
		log.info(f"\n\nreceived order data: {order_update}")
		order_update = OrderORM(**order_update.dict())
		order_updated = update_order(order_update)
		log.info(f"updated order: {order_updated}")
		return {
			"order": order_updated,
			"timestamp": datetime.now().isoformat(),
			"trace_id": str(uuid.uuid4()),
			"http_response_code": 200,
		}
	except (SQLAlchemyError, AssertionError, ResponseValidationError, OperationalError, Exception) as e:
		log.error(f"UpdateOrder:: Exception:: {e}, type: {type(e)} for order_id: {order_update.order_id}")
		return JSONResponse(status_code=500, content={"error": str(e),
		                                              "timestamp": datetime.now().isoformat(),
		                                              "trace_id": str(uuid.uuid4()),
		                                              "http_response_code": 500,
		                                              })


@app.delete("/v1/orders/{order_id}", response_model=None)
def delete_order(order_id: str) -> dict[str, any] | dict[str, str]:
	try:

		log.info(f"deleting order data: {order_id}")
		deleted_order = delete_order_by_order_id(order_id)
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
