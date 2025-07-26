from fastapi import FastAPI
from scalar_fastapi import scalar_fastapi, get_scalar_api_reference
import uuid
from datetime import datetime
from random import random

app = FastAPI()


@app.get("/")
def get_app():
    return {"uuid": uuid.uuid4(), "time": datetime.now()}


@app.get("/order/{order_id}")
def get_order_data(order_id: int | str) -> dict[str, str | int | datetime | bool]:
    return {
        "order_id": order_id,
        "is_available": random() < 0.7,
        "origin_country": "India",
        "product_description": f"AI TV - {uuid.uuid4()}",
        "order_placed_at": datetime.now(),
    }


# documentation purpose
@app.get("/scalar")
def get_scalar_docs(self):
    return get_scalar_api_reference(
        openapi_url="/openapi.json",
        title=f"Scalar API",
    )
