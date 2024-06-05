import logging
from decimal import Decimal
from typing import Any, List

import boto3
import cv2
import numpy as np
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import HTTPException
from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource
from pydantic import BaseModel

from aion.connectors.utils_connectors import AWSCredentials
from aion.nodes.config import REGION

logger = logging.getLogger("uvicorn.error")


class Frame(BaseModel):
    frame_id: int
    # Coloured images have one extra dimension
    image_data: List[List[int]] | List[List[List[int]]]


class Frames(BaseModel):
    list_frame: List[Frame]


def convert_decimals(obj: Any) -> Any:
    if isinstance(obj, list):
        return [convert_decimals(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    return obj


def apply_colour_map(
    frame: np.ndarray, color_map: int = cv2.COLORMAP_JET
) -> np.ndarray:
    # Combine the rows of the frame into a single image array
    combined_frame = np.vstack(frame).astype(np.uint8)  # type: ignore[call-overload]
    # Apply the color map using OpenCV
    coloured_frame = cv2.applyColorMap(combined_frame, color_map)

    return coloured_frame  # type: ignore[no-any-return]


class DynamoDBConnector:
    def __init__(self, credentials: AWSCredentials) -> None:
        client: DynamoDBServiceResource = boto3.resource(
            "dynamodb",
            region_name=REGION,
            aws_access_key_id=credentials.access_key_id,
            aws_secret_access_key=credentials.secret_access_key,
            aws_session_token=credentials.session_token,
        )
        self.table = client.Table("ResizedFramesTable")

    def save(self, frames: Frames) -> dict:
        try:
            # Convert Pydantic model to dictionary
            items = frames.model_dump()["list_frame"]

            # Put items into DynamoDB table
            with self.table.batch_writer() as batch:
                for item in items:
                    batch.put_item(Item=item)

            return {
                "message": f"{len(items)} frames are successfully uploaded to a dynamodb table"
            }
        except (BotoCoreError, ClientError) as e:
            logger.error(f"Error uploading item to DynamoDB: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise HTTPException(status_code=500, detail="Unexpected Error")

    def load_by_depth_range(self, depth_min: int, depth_max: int) -> Frames:
        if depth_min > depth_max:
            raise HTTPException(
                status_code=500,
                detail=f"depth_min {depth_min} is larger than depth_max {depth_max}",
            )

        try:
            # Retrieve all frames within a depth range
            response: dict = self.table.scan(  # type: ignore[assignment]
                FilterExpression=Attr("frame_id").between(depth_min, depth_max),
            )
            items = convert_decimals(response.get("Items", []))
            if not items:
                raise HTTPException(
                    status_code=404,
                    detail=f"Depth range between {depth_min} and {depth_max} returned no items",
                )

            # Validate typed data
            frames = Frames.model_validate({"list_frame": items})

            # Apply colour map to queried frames
            coloured_frames = Frames(list_frame=[])
            for frame in frames.list_frame:
                coloured_frame = apply_colour_map(frame=np.array(frame.image_data))
                coloured_frames.list_frame.append(
                    Frame(frame_id=frame.frame_id, image_data=coloured_frame.tolist())
                )

            return coloured_frames

        except (BotoCoreError, ClientError) as e:
            logger.error(f"Error downloading items from DynamoDB: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise HTTPException(status_code=500, detail="Unexpected Error")
