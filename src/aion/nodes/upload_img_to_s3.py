import os

from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile

from aion.connectors.raw_img.s3_connector import S3Connector as RawImgS3Connector
from aion.connectors.utils_connectors import AWSCredentials

load_dotenv()

app = FastAPI()


@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)) -> dict:
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

    # Upload to s3
    raw_img_s3_connector = RawImgS3Connector(credentials=credentials)
    response = raw_img_s3_connector.save(raw_img=file.file, filename=str(file.filename))

    return response
