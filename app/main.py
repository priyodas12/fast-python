from fastapi import FastAPI
from markdown_it.rules_block import fence
from scalar_fastapi import scalar_fastapi, get_scalar_api_reference
import uuid
from datetime import datetime

app = FastAPI()


@app.get("/")
def get_app():
    return {"uuid": uuid.uuid4(), "time": datetime.now()}


@app.get("/order/{order_id}")
def get_order_data(order_id: int):
    return {
        "order_id": order_id,
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
