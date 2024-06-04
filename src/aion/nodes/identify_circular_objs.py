import cv2
import numpy as np
from cv2.typing import MatLike
from pydantic import BaseModel, Field


class HoughCirclesConfig(BaseModel):
    method: int = Field(default=cv2.HOUGH_GRADIENT, description="Detection method.")
    dp: float = Field(
        gt=0,
        default=1.1,
        description="Inverse ratio of the accumulator resolution to the image resolution.",
    )
    minDist: float = Field(
        gt=0,
        default=30,
        description="Minimum distance between the centers of the detected circles.",
    )
    param1: float = Field(
        gt=0,
        default=150,
        description="Higher threshold of the two passed to the Canny edge detector.",
    )
    param2: float = Field(
        gt=0,
        default=20,
        description="Accumulator threshold for the circle centers at the detection stage.",
    )
    minRadius: int = Field(ge=0, default=50, description="Minimum circle radius.")
    maxRadius: int = Field(ge=0, default=70, description="Maximum circle radius.")


def preprocess_img(image: MatLike) -> MatLike:
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    return gray


def identify_circles(gray: MatLike) -> MatLike:
    # Identify circles in a grayscaled image
    config = HoughCirclesConfig()
    circles = cv2.HoughCircles(
        image=gray,
        method=config.method,
        minDist=config.minDist,
        dp=config.dp,
        param1=config.param1,
        param2=config.param2,
        minRadius=config.minRadius,
        maxRadius=config.maxRadius,
    )

    # Round coordinates and radiuses into integers
    circles = np.round(np.array(circles[0, :])).astype("int")

    return circles
