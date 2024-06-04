import logging
import os
from uuid import UUID

from fastapi import FastAPI, HTTPException
from pydantic import ValidationError

from aion.connectors.circular_objs.dynamodb_connector import (
    DynamoDBConnector as CODynamoDBConnector,
)
from aion.connectors.utils_connectors import AWSCredentials

logger = logging.getLogger("uvicorn.error")
app = FastAPI()


@app.post("/get_circles")
async def get_circular_objs(str_uri_image: str) -> dict:
    # AWS S3 configuration using environment variables
    AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
    AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
    AWS_SESSION_TOKEN = os.environ["AWS_SESSION_TOKEN"]

    # Gather credentials
    credentials = AWSCredentials(
        access_key_id=AWS_ACCESS_KEY_ID,
        secret_access_key=AWS_SECRET_ACCESS_KEY,
        session_token=AWS_SESSION_TOKEN,
    )

    # Validate UUID
    try:
        uri_image = UUID(str_uri_image)
    except ValueError:
        logger.error(f"Invalid UUID format: {uri_image}")
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    # Retrieve item from remote and type it
    try:
        co_dynamodb_connector = CODynamoDBConnector(credentials=credentials)
        circular_objs = co_dynamodb_connector.load_by_image(uri_image=uri_image)
    except ValidationError as e:
        logger.error(f"Response validation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Error validating response format")

    return circular_objs.model_dump()
