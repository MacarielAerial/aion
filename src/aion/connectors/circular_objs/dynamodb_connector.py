import logging

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import HTTPException
from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource

from aion.connectors.circular_objs.json_connector import CircularObjs
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
        try:
            # Convert Pydantic model to dictionary
            item = circular_objs.model_dump()

            # Convert UUIDs to strings
            item["uri_image"] = str(item["uri_image"])
            for obj in item["list_obj"]:
                obj["uri"] = str(obj["uri"])
            # Put the entire item into DynamoDB table
            self.table.put_item(Item=item)
            return {
                "message": f"Item associated with image URI {item['uri_image']} successfully uploaded"
            }
        except (BotoCoreError, ClientError) as e:
            logger.error(f"Error uploading item to DynamoDB: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise HTTPException(status_code=500, detail="Unexpected Error")
