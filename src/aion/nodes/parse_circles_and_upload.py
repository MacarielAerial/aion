import logging
import os
import tempfile
from pathlib import Path
from typing import Tuple
from uuid import UUID

import cv2
from fastapi import FastAPI
from s3path import S3Path

from aion.connectors.circular_objs.dynamodb_connector import (
    DynamoDBConnector as CODynamoDBConnector,
)
from aion.connectors.circular_objs.json_connector import CircularObj, CircularObjs
from aion.connectors.raw_img.s3_connector import S3Connector as RawImgS3Connector
from aion.connectors.utils_connectors import AWSCredentials
from aion.nodes.identify_circular_objs import identify_circles, preprocess_img
from aion.nodes.utils_upload import generate_uuid_from_uuid_xyz

logger = logging.getLogger("uvicorn.error")
app = FastAPI()


# AWS S3 configuration using environment variables
AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
AWS_SESSION_TOKEN = os.environ["AWS_SESSION_TOKEN"]


@app.post("/parse_and_upload")
async def parse_circles_and_upload(str_s3_path: str) -> dict:
    # Gather credentials
    credentials = AWSCredentials(
        access_key_id=AWS_ACCESS_KEY_ID,
        secret_access_key=AWS_SECRET_ACCESS_KEY,
        session_token=AWS_SESSION_TOKEN,
    )

    # Identify circles in the image
    with tempfile.TemporaryDirectory() as tmpdir:
        s3_path = S3Path.from_uri(str_s3_path)
        uri_image = UUID(s3_path.stem)  # Assume file stem is used to store UUID
        filepath = Path(tmpdir) / s3_path.name

        # Download the image
        raw_img_s3_connector = RawImgS3Connector(credentials=credentials)
        raw_img_s3_connector.load(s3_path=s3_path, filepath=filepath)

        # Identify circular objects
        image = cv2.imread(str(filepath))
        gray = preprocess_img(image=image)
        circles = identify_circles(gray=gray)

    # Compile pydantic objects
    circular_objs = CircularObjs(uri_image=uri_image, list_obj=[])
    for x, y, r in circles:
        # Parse reproducible UUIDs
        uri = generate_uuid_from_uuid_xyz(existing_uuid=uri_image, int_tuple=(x, y, r))
        # Parse bounding boxes based on centroid and radius information
        top_left: Tuple[int, int] = ((x - r), (y - r))
        bottom_right: Tuple[int, int] = ((x + r), (y + r))
        circular_obj = CircularObj(
            uri=uri, centroid=(x, y), radius=r, bbox=(top_left, bottom_right)
        )
        circular_objs.list_obj.append(circular_obj)

    # Upload result object
    co_dynamo_db_connector = CODynamoDBConnector(credentials=credentials)
    response = co_dynamo_db_connector.save(circular_objs=circular_objs)

    return response
