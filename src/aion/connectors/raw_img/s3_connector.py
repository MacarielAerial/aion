import io
import logging
import shutil
from enum import Enum
from pathlib import Path
from typing import IO

import boto3
from botocore.exceptions import (
    BotoCoreError,
    ClientError,
    NoCredentialsError,
    PartialCredentialsError,
)
from fastapi import HTTPException
from mypy_boto3_s3 import S3Client
from s3path import S3Path

from aion.connectors.utils_connectors import AWSCredentials
from aion.nodes.config import BUCKET_NAME, REGION
from aion.nodes.utils_upload import generate_uuid_from_file

logger = logging.getLogger("uvicorn.error")


class ImageFileSuffix(str, Enum):
    png = ".png"
    jpeg = ".jpeg"


class S3Connector:
    def __init__(self, credentials: AWSCredentials) -> None:
        self.s3_client: S3Client = boto3.client(
            "s3",
            region_name=REGION,
            aws_access_key_id=credentials.access_key_id,
            aws_secret_access_key=credentials.secret_access_key,
            aws_session_token=credentials.session_token,
        )

    def save(self, raw_img: IO, filename: str) -> dict:
        # Check the file suffix is as expected
        suffix = ImageFileSuffix(Path(filename).suffix).value

        # Read the image data into a byte buffer
        buffer = io.BytesIO()
        shutil.copyfileobj(raw_img, buffer)
        buffer.seek(0)  # Reset buffer position to the beginning

        # Parse a new file name for the file in s3 with uuid
        file_uuid = generate_uuid_from_file(file=buffer)
        buffer.seek(0)  # Reset buffer position to the beginning again
        s3_filename = f"{file_uuid}{suffix}"

        try:
            # Upload the file to S3
            self.s3_client.upload_fileobj(buffer, BUCKET_NAME, s3_filename)
            return {"original_filename": filename, "s3_filename": s3_filename}
        except NoCredentialsError:
            raise HTTPException(status_code=403, detail="Credentials not available")
        except PartialCredentialsError:
            raise HTTPException(
                status_code=403, detail="Incomplete credentials provided"
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def load(self, s3_path: S3Path, filepath: Path) -> None:  # type: ignore[no-any-unimported]
        try:
            # Download the image from S3
            self.s3_client.download_file(s3_path.bucket, s3_path.key, str(filepath))

        except (BotoCoreError, ClientError) as e:
            logger.error(f"Error accessing S3: {e}")
            raise HTTPException(status_code=500, detail="Error accessing S3")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise HTTPException(status_code=500, detail="Unexpected Error")
