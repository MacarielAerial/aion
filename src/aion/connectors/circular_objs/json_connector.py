import logging
from pathlib import Path
from typing import List, Tuple
from uuid import UUID

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class CircularObj(BaseModel):
    uri_image: UUID  # URI of the parent image
    uri_circle: UUID
    centroid: Tuple[int, int]
    radius: int
    # Only include top left and bottom right corners of the rectangle
    bbox: Tuple[Tuple[int, int], Tuple[int, int]]


class CircularObjs(BaseModel):
    list_obj: List[CircularObj]


class JSONConnector:
    def __init__(self, filepath: Path) -> None:
        self.filepath = filepath

    def save(self, circular_objs: CircularObjs) -> None:
        # Only used for local dev purpose
        # File truncation on purpose
        with open(self.filepath, "w+") as f:
            f.write(circular_objs.model_dump_json(indent=2))
            logger.info(f"Saved a {type(circular_objs)} object to {self.filepath}")

    def load(self) -> CircularObjs:
        with open(self.filepath, "r") as f:
            circular_objs = CircularObjs.model_validate_json(f.read())
            logger.info(f"Loaded a {type(circular_objs)} object from {self.filepath}")

            return circular_objs
