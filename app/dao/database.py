import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv(dotenv_path=".env")
database_url = os.getenv("COCKROACH_POSTGRESQL_URL")
engine = create_engine(database_url, echo=True, future=True, hide_parameters=False, )
session = sessionmaker(bind=engine, autocommit=False, expire_on_commit=False)
