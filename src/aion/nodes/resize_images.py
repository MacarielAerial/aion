import logging
import os
from typing import Any, List

import numpy as np
import pandas as pd
from fastapi import FastAPI, File, UploadFile
from PIL import Image

from aion.connectors.frames.dynamodb_connector import (
    DynamoDBConnector as FDynamoDBConnector,
)
from aion.connectors.frames.dynamodb_connector import Frame, Frames
from aion.connectors.utils_connectors import AWSCredentials

logger = logging.getLogger("uvicorn.error")
app = FastAPI()


def group_rows_by_depth(df: pd.DataFrame, rows_per_frame: int = 10) -> List[Any]:
    grouped_frames: List[Any] = []
    num_frames = len(df) // rows_per_frame
    for i in range(num_frames):
        start = i * rows_per_frame
        end = start + rows_per_frame
        frame = df.iloc[start:end].drop(columns=["depth"]).to_numpy()
        grouped_frames.append(frame)

    return grouped_frames


def resize_image(data: np.ndarray, new_width: int) -> np.ndarray:
    height, _ = data.shape
    image = Image.fromarray(data)
    resized_image = image.resize((new_width, height), Image.LANCZOS)  # type: ignore[attr-defined]

    return np.array(resized_image)


@app.post("/resize_images")
async def resize_images(file: UploadFile = File(...)) -> dict:
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

    # Preprocess input dataframe
    df = pd.read_csv(file.file).dropna()
    grouped_frames = group_rows_by_depth(df)
    preprocessed_frames: List[np.ndarray] = []
    for frame_data in grouped_frames:
        combined_frame = np.vstack(frame_data)
        normalized_frame = (combined_frame / 255.0) * 255.0
        preprocessed_frames.append(normalized_frame.astype(np.uint8))

    # Obtain frame ids
    frame_ids: List[int] = list(
        set(df["depth"].astype(str).str.split(".").str[0].astype(int))
    )

    # Resize frames
    processed_frames: List[np.ndarray] = []
    new_width = 150
    for frame in preprocessed_frames:
        resized_frame = resize_image(frame, new_width)
        processed_frames.append(resized_frame)

    # Form the pydantic data structure
    frames = Frames(
        list_frame=[
            Frame(frame_id=frame_ids[i], image_data=processed_frames[i].tolist())
            for i in range(len(processed_frames))
        ]
    )

    # Upload the typed structure
    f_dynamo_db_connector = FDynamoDBConnector(credentials=credentials)
    response = f_dynamo_db_connector.save(frames=frames)

    return response
