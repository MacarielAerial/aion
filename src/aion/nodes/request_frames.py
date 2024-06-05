import logging
import os

from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from pydantic import ValidationError

from aion.connectors.frames.dynamodb_connector import (
    DynamoDBConnector as FDynamoDBConnector,
)
from aion.connectors.utils_connectors import AWSCredentials

logger = logging.getLogger("uvicorn.error")
app = FastAPI()


@app.post("/request_frames")
async def request_frames(depth_min: int, depth_max: int) -> dict:
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

    # Query frames by depth range
    try:
        f_dynamodb_connector = FDynamoDBConnector(credentials=credentials)
        frames = f_dynamodb_connector.load_by_depth_range(
            depth_min=depth_min, depth_max=depth_max
        )
    except ValidationError as e:
        logger.error(f"Response validation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Error validating response format")

    return frames.model_dump()
