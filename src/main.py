import math
import subprocess
from pathlib import Path

import dotenv
import openai
import youtube_dl
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from youtube_transcript_api import YouTubeTranscriptApi

from src.logger import get_logger
from src.schemas import MakeShortsInput, Segment, response_obj
from src.text_segmenters import OpenAISegmenter

dotenv.load_dotenv()

logger = get_logger("app")


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


def segment_video(
    video_path: Path, segments: list[Segment], video_id: str
) -> list[str]:
    segment_paths = []
    for i, segment in enumerate(segments, start=1):
        start_time = math.floor(float(segment.get("start_time", 0)))
        end_time = math.ceil(float(segment.get("end_time", 0))) + 2
        output_file = Path("static", "output", f"{video_id}_{i:03d}.mp4")
        command = f"ffmpeg -i {video_path} -ss {start_time} -to {end_time} -c copy {output_file}"
        logger.debug("Running command: %s", command)
        subprocess.call(
            command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        segment_paths.append(f"/{output_file}")
        logger.debug(
            "Segment %s of video %s saved to %s", f"{i:03d}", video_id, output_file
        )
    return segment_paths


app = FastAPI(
    title="Shorts cutter",
    description="This is a simple API to cut long YouTube video into multiple YouTube shorts.",
    version="0.1.0",
    debug=True,
)

Path("static", "input").mkdir(parents=True, exist_ok=True)
Path("static", "output").mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")

openai_client = openai.Client()


@app.post("/")
def make_shorts(data: MakeShortsInput):
    transcript = get_transcript(data.video_id)
    logger.info("Transcript for video %s fetched", data.video_id)
    logger.debug("Transcript for video %s: %s", data.video_id, transcript)

    filename = Path("static", "input", f"{data.video_id}.mp4")
    download_video(data.video_url, filename)
    logger.info("Video %s downloaded", data.video_id)

    system_prompt = "You are a ViralGPT helpful assistant. You are master at reading youtube transcripts and identifying the most Interesting and Viral Content"
    text_segmenter = OpenAISegmenter(openai_client, system_prompt)
    prompt = f"This is a transcript of a video. Please identify the {data.n} most viral sections from the whole, make sure they are more than 30 seconds in duration,Make Sure you provide extremely accurate timestamps respond only with JSON in this format {response_obj}  \n Here is the Transcription:\n{transcript}"
    segments = text_segmenter.run(prompt)
    logger.info("Content analyzed for video %s", data.video_id)
    logger.debug("Analyzed content for video %s: %s", data.video_id, segments)
    output_paths = segment_video(filename, segments, data.video_id)

    return {"video_urls": output_paths}
