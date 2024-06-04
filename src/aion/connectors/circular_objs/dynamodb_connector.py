import logging
from typing import Set
from uuid import UUID

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import HTTPException
from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource

from aion.connectors.circular_objs.json_connector import CircularObj, CircularObjs
from aion.connectors.utils_connectors import AWSCredentials
from aion.nodes.config import REGION

logger = logging.getLogger("uvicorn.error")


class DynamoDBConnector:
    def __init__(self, credentials: AWSCredentials) -> None:
        client: DynamoDBServiceResource = boto3.resource(
            "dynamodb",
            region_name=REGION,
            aws_access_key_id=credentials.access_key_id,
            aws_secret_access_key=credentials.secret_access_key,
            aws_session_token=credentials.session_token,
        )
        self.table = client.Table("CircularObjsTable")

    def save(self, circular_objs: CircularObjs) -> dict:
        uri_image: Set[str] = set(str(obj.uri_image) for obj in circular_objs.list_obj)

        try:
            # Convert Pydantic model to dictionary
            items = circular_objs.model_dump()["list_obj"]

            # Convert UUIDs to strings
            for item in items:
                item["uri_image"] = str(item["uri_image"])
                item["uri_circle"] = str(item["uri_circle"])

            # Put items into DynamoDB table
            with self.table.batch_writer() as batch:
                for item in items:
                    batch.put_item(Item=item)

            return {
                "message": f"Items associated with image URI {uri_image} successfully uploaded"
            }
        except (BotoCoreError, ClientError) as e:
            logger.error(f"Error uploading item to DynamoDB: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise HTTPException(status_code=500, detail="Unexpected Error")

    def load_by_image(self, uri_image: UUID) -> CircularObjs:
        try:
            # Retrieve all circles associated with an image from remote
            response: dict = self.table.query(  # type: ignore[assignment]
                IndexName="UriImageIndex",
                KeyConditionExpression=Key("uri_image").eq(str(uri_image)),
            )
            items = response.get("Items", [])
            if not items:
                raise HTTPException(
                    status_code=404, detail=f"Image with URI {uri_image} not found"
                )

            # Convert the retrieved item to match Pydantic model
            for item in items:
                item["uri_image"] = UUID(item["uri_image"])
                item["uri_circle"] = UUID(item["uri_circle"])
                item["radius"] = int(item["radius"])
                item["centroid"] = tuple(int(x) for x in item["centroid"])
                item["bbox"] = tuple(
                    tuple(int(x) for x in bbox_point) for bbox_point in item["bbox"]
                )

            # Validate typed data
            circular_objs = CircularObjs.model_validate({"list_obj": items})

            return circular_objs

        except (BotoCoreError, ClientError) as e:
            logger.error(f"Error downloading items from DynamoDB: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise HTTPException(status_code=500, detail="Unexpected Error")

    def load_by_circle(self, uri_circle: UUID) -> CircularObj:
        try:
            # Request the item from remote
            item: dict = self.table.get_item(Key={"uri_circle": str(uri_circle)})[
                "Item"
            ]

            # Type fields to match the pydantic model
            item["uri_image"] = UUID(item["uri_image"])
            item["uri_circle"] = UUID(item["uri_circle"])
            item["radius"] = int(item["radius"])
            item["centroid"] = tuple(int(x) for x in item["centroid"])
            item["bbox"] = tuple(
                tuple(int(x) for x in bbox_point) for bbox_point in item["bbox"]
            )

            # Validate typed data
            circular_obj = CircularObj.model_validate(item)

            return circular_obj

        except (BotoCoreError, ClientError) as e:
            logger.error(f"Error downloading item from DynamoDB: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise HTTPException(status_code=500, detail="Unexpected Error")
