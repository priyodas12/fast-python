import logging
import os
from contextlib import contextmanager
from datetime import datetime

import coloredlogs
from dotenv import load_dotenv
from sentry_sdk.session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def init_db():
	load_dotenv(dotenv_path=".env")
	database_url = os.getenv("COCKROACH_POSTGRESQL_URL")
	engine = create_engine(database_url, echo=True, future=True, hide_parameters=False, )
	session_local = sessionmaker(bind=engine, autocommit=False, expire_on_commit=False)
	log = logging.getLogger("sqlalchemy-logger")
	coloredlogs.install(level="DEBUG")
	return engine, session_local, log


@contextmanager
def get_db():
	engine, session_local, log = init_db()
	db: Session = session_local()
	log.info(
		"\n\n--------------------------------Connecting to database at:: {}-----------------------------------".format(
			datetime.now()))
	try:
		yield db
		db.commit()
	except Exception as e:
		db.rollback()
		raise e
	finally:
		log.info(
			"\n\n--------------------------------Closing connection to database at:: {}--------------------------".format(
				datetime.now()))
		db.close()
