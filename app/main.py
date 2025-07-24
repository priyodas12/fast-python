from datetime import time

from fastapi import FastAPI
from scalar_fastapi import scalar_fastapi, get_scalar_api_reference
import uuid
from datetime import datetime
app = FastAPI()

@app.get("/")
def get_app():
    return {"uuid": uuid.uuid4(),"time": datetime.now()}

@app.get("/scalar")
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url="/openapi.json",
        title=f"Scalar API",
    )

