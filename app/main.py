from fastapi import FastAPI
from scalar_fastapi import scalar_fastapi, get_scalar_api_reference
import uuid
from datetime import datetime
from random import random
from faker import *

app = FastAPI()

from faker import Faker

faker = Faker()
print(faker.name())
print(faker.email())


@app.get("/")
def get_app():
    return {"uuid": uuid.uuid4(), "time": datetime.now()}


@app.get("/order/{order_id}")
def get_order_data(
    order_id: int | str,
) -> dict[str, str | int | float | bool | datetime]:
    return {
        "order_id": order_id,
        "is_available": random() < 0.7,
        "origin_country": "India",
        "price": round(random() * 10000, 2),
        "order_delivery_address": f"{faker.address()}",
        "order_placed_at": datetime.now(),
    }


# documentation purpose
@app.get("/scalar")
def get_scalar_docs(self):
    return get_scalar_api_reference(
        openapi_url="/openapi.json",
        title=f"Scalar API",
    )
