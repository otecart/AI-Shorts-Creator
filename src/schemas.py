import re
from typing import Any, TypedDict

from pydantic import BaseModel, field_validator
from pydantic_core import PydanticCustomError

from src.utils import YOUTUBE_VIDEO_URL_PATTERN, has_valid_pattern


class MakeShortsInput(BaseModel):
    video_url: str
    n: int

    @field_validator("video_url")
    def validate_video_url(cls, value: str) -> str:
        if not has_valid_pattern(YOUTUBE_VIDEO_URL_PATTERN, value):
            raise PydanticCustomError(
                "wrong_url",
                'The URL "{video_url}" is not a valid YouTube video URL.',
                {"video_url": value},
            )
        return value

    @field_validator("n")
    def validate_n(cls, value: int) -> int:
        if not (1 <= value <= 10):
            raise PydanticCustomError(
                "wrong_range",
                "The value of n must be between 1 and 10.",
                {"n": value},
            )
        return value

    @property
    def video_id(self) -> str:
        return re.search(r"watch\?v=([\w-]+)", self.video_url).group(1)  # type: ignore


class Segment(TypedDict):
    start_time: float
    end_time: float
    text: str
    duration: int


response_obj = """{
  segments: [
    {
        "start_time": 97.19, 
        "end_time": 127.43,
        "text": "Full segment text",
        "duration":36 #Length in seconds
    },
    {
        "start_time": 169.58,
        "end_time": 199.10,
        "text": "Full segment text",
        "duration":33 
    },
  ]
}"""


class AsyncResponse(BaseModel):
    is_err: bool
    return_value: Any
    execution_time: float


class FaceDetectionTaskInput(BaseModel):
    video_url: str
