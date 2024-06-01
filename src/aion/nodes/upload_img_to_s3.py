from fastapi import FastAPI, File, UploadFile
import boto3
import os
from dotenv import load_dotenv
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from mangum import Mangum

from aion.nodes.config import BUCKET_NAME, REGION

load_dotenv()

app = FastAPI()

# AWS S3 configuration using environment variables
AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
AWS_SESSION_TOKEN=os.environ["AWS_SESSION_TOKEN"]

# Initialize the S3 client
s3_client = boto3.client(
    's3',
    region_name=REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN
)

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    try:
        s3_client.upload_fileobj(file.file, BUCKET_NAME, file.filename)
        return {"filename": file.filename}
    except NoCredentialsError:
        return {"error": "Credentials not available"}
    except PartialCredentialsError:
        return {"error": "Incomplete credentials provided"}
    except Exception as e:
        return {"error": str(e)}

handler = Mangum(app)
