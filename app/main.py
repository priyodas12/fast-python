import logging
import os
import sys
import uuid
from datetime import datetime
from http.client import HTTPException

from dotenv import load_dotenv
from faker import Faker
from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference
from sqlalchemy import Boolean, create_engine, DateTime, Float, String, UUID
from sqlalchemy.dialects import registry
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql.schema import Column

app = FastAPI()
faker = Faker()

logging.basicConfig(
	# filename="app.log",
	stream=sys.stdout,
	level=logging.INFO,
)

registry.register("cockroach.psycopg2", "cockroach_dialect", "CockroachDBDialect")

load_dotenv(dotenv_path=".env")

database_url = os.getenv("COCKROACH_POSTGRESQL_URL")
logging.info(f"db_url: {database_url}\n\n")

engine = create_engine(database_url, echo=True, future=True, hide_parameters=False)
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


def get_db_connection():
	db = session()
	try:
		logging.info(f"connecting to db: {database_url} at {datetime.now()}")
		yield db
	except ():
		logging.error("error  while connecting to db")
	finally:
		db.close()


@app.get("/")
def get_app():
	return {"uuid": uuid.uuid4(), "time": datetime.now()}


@app.get("/order/{order_id}")
def get_order_data(order_id: str):
	try:
		db = session()
		order = db.query(Order).filter(Order.order_id == order_id).first()
		logging.info(f"******************get order {order_id} from db: {order}\n\n")
		if not order:
			raise HTTPException(detail="Order not found")
		return {"order": order}
	except SQLAlchemyError as e:
		logging.error(e.args[0])
		return {"error": str(e.args[0])}
	except AssertionError as e:
		logging.error(e.args[0])
		return {"error": str(e.args[0])}


@app.get("/orders")
def get_order_data_v2():
	try:
		db = session()
		orders = db.query(Order).all()
		logging.info(f"**************get orders v2 in db: {orders}")
		return {"orders": orders}
	except SQLAlchemyError as e:
		logging.error(e.args[0])
		return {"error": str(e.args[0])}
	except AssertionError as e:
		logging.error(e.args[0])
		return {"error": str(e.args[0])}


# documentation purpose
@app.get("/scalar")
def get_scalar_docs(self):
	return get_scalar_api_reference(
		openapi_url="/openapi.json",
		title=f"Scalar API",
	)
