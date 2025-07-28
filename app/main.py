import logging
import os
import uuid
from datetime import datetime

import coloredlogs
from dotenv import load_dotenv
from faker import Faker
from fastapi import FastAPI
from fastapi.exceptions import ResponseValidationError
from scalar_fastapi import get_scalar_api_reference
from sqlalchemy import Boolean, create_engine, DateTime, Float, String, UUID
from sqlalchemy.dialects import registry
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql.schema import Column

app = FastAPI()
faker = Faker()

registry.register("cockroach.psycopg2", "cockroach_dialect", "CockroachDBDialect")

load_dotenv(dotenv_path=".env")

log = logging.getLogger("sqlalchemy.engine")
database_url = os.getenv("COCKROACH_POSTGRESQL_URL")

coloredlogs.install(level="INFO", logger=log)
log.info(f"db_url: {database_url}\n\n")

engine = create_engine(database_url, echo=True, future=True, hide_parameters=False, )
session = sessionmaker(bind=engine, autocommit=False, expire_on_commit=False)
Base = declarative_base()


class Order(Base):
	__tablename__ = "order"
	__table_args__ = {"schema": "orders"}

	order_id = Column(String, primary_key=True, default=uuid.uuid4, nullable=False)
	order_desc = Column(String, nullable=False)
	order_create_date = Column(DateTime, nullable=False)
	order_update_date = Column(DateTime, nullable=False)
	order_price = Column(Float, nullable=False)
	order_origin = Column(String, nullable=False)
	order_availability = Column(Boolean, nullable=False)
	order_carrier_id = Column(String, nullable=False)
	delivery_date = Column(DateTime, nullable=False)
	order_barcode = Column(UUID, nullable=False)
	order_discount = Column(Float, nullable=False)
	customer_id = Column(String, nullable=False)

	def __str__(self):
		return (f"""\nOrder::
		        order_id: {self.order_id} ,
		        delivery_date:: {self.delivery_date},
		        order_create_date:: {self.order_create_date},
		        order_availability:: {self.order_availability},
		        order_price:: {self.order_price},
		        customer_id:: {self.customer_id},
		        order_barcode:: {self.order_barcode}
		        """)


def get_db_connection():
	db = session()
	try:
		log.info(f"connecting to db: {database_url} at {datetime.now()}")
		yield db
	except ():
		log.error("error  while connecting to db")
	finally:
		db.close()


@app.get("/")
def get_app_status():
	return {"uuid": uuid.uuid4(), "time": datetime.now()}


@app.get("/order/customer", response_model=None)
def get_order_by_customer_id(customer_id: str) -> dict[str, Order] | dict[str, str]:
	try:
		db = session()
		order_orm = db.query(Order).filter(Order.customer_id == str(customer_id)).first()
		log.info(f"order with customer_id {customer_id} from cockroachdb: {order_orm.__str__()}")
		if not order_orm:
			log.debug(f"error while getting order with customer_id {customer_id} from db")
			return {"error": f"customer_id:: {customer_id} not found"}
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


@app.get("/order/{order_id}", response_model=None)
def get_order_by_order_id(order_id: str) -> dict[str, Order] | dict[str, str]:
	try:
		db = session()
		order_orm = db.query(Order).filter(Order.order_id == str(order_id)).first()
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
		orders = db.query(Order).all()
		for order in orders:
			log.info(f"fetched orders: {order.__str__()}")
		return {"orders": orders}
	except SQLAlchemyError as e:
		log.error(e.args[0])
		return {"error": str(e.args[0])}
	except AssertionError as e:
		log.error(e.args[0])
		return {"error": str(e.args[0])}


# documentation purpose
# http://0.0.0.0:8000/redoc
@app.get("/scalar", include_in_schema=False)
def get_scalar_docs(self):
	return get_scalar_api_reference(
		openapi_url="/openapi.json",
		title=f"Scalar API",
	)
