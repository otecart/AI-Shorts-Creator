import math
import os
import subprocess
from pathlib import Path
from time import time

import youtube_dl
from openai import OpenAI
from taskiq import TaskiqDepends
from youtube_transcript_api import YouTubeTranscriptApi

from src.logger import get_logger
from src.schemas import MakeShortsInput, Segment, response_obj
from src.text_segmenters import OpenAISegmenter, TextSegmenter
from src.worker import broker

logger = get_logger("app.tasks")


@broker.task
def download_video(url: str, filename: Path):
    opts = {
        "format": "mp4",
        "outtmpl": str(filename),
    }
    youtube_dl.YoutubeDL(opts).download([url])


def get_transcript(video_id: str):
    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=("en", "ru"))

    formatted_transcript = ""
    for entry in transcript:
        start_time = "{:.2f}".format(entry["start"])
        end_time = "{:.2f}".format(entry["start"] + entry["duration"])
        text = entry["text"]
        formatted_transcript += f"{start_time} --> {end_time} : {text}\n"

    return transcript


def get_segments(
    text_segmenter: TextSegmenter, transcript: str, n: int
) -> list[Segment]:
    prompt = f"This is a transcript of a video. Please identify the {n} most viral sections from the whole, make sure they are more than 30 seconds in duration,Make Sure you provide extremely accurate timestamps respond only with JSON in this format {response_obj}  \n Here is the Transcription:\n{transcript}"
    return text_segmenter.run(prompt)


def segment_video(
    video_path: Path, segments: list[Segment], video_id: str
) -> list[str]:
    segment_paths = []
    output_prefix = hash(os.environ["SALT"] + video_id + str(time()))
    for i, segment in enumerate(segments, start=1):
        start_time = math.floor(float(segment.get("start_time", 0)))
        end_time = math.ceil(float(segment.get("end_time", 0))) + 2
        output_file = Path("static", "output", f"{output_prefix}_{i:03d}.mp4")
        command = f"ffmpeg -i {video_path} -ss {start_time} -to {end_time} -c copy {output_file}"
        logger.info("Running command: %s", command)
        subprocess.call(
            command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        segment_paths.append(f"/{output_file}")
        logger.info(
            "Segment %s of video %s saved to %s", f"{i:03d}", video_id, output_file
        )
    return segment_paths


def get_openai_client():
    if not hasattr(get_openai_client, "client"):
        logger.info("Creating OpenAI client in task")
        setattr(get_openai_client, "client", OpenAI())
    return getattr(get_openai_client, "client")


@broker.task
def make_shorts(
    data: MakeShortsInput, openai_client: OpenAI = TaskiqDepends(get_openai_client)
):
    transcript = get_transcript(data.video_id)
    logger.info("Transcript for video %s fetched", data.video_id)
    logger.debug("Transcript for video %s: %s", data.video_id, transcript)

    filename = Path("static", "input", f"{data.video_id}.mp4")
    download_video(data.video_url, filename)
    logger.info("Video %s downloaded", data.video_id)

    system_prompt = "You are a ViralGPT helpful assistant. You are master at reading youtube transcripts and identifying the most Interesting and Viral Content"
    text_segmenter = OpenAISegmenter(openai_client, system_prompt)
    segments = get_segments(text_segmenter, transcript, data.n)
    logger.info("Content analyzed for video %s", data.video_id)
    logger.debug("Analyzed content for video %s: %s", data.video_id, segments)
    output_paths = segment_video(filename, segments, data.video_id)
    logger.info("Segments for video %s saved", data.video_id)

    return {"video_urls": output_paths}
