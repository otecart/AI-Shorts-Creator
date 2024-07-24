import re


def has_valid_pattern(pattern: str, value: str) -> bool:
    match = re.match(pattern, value)
    return bool(match)


YOUTUBE_VIDEO_URL_PATTERN = (
    r"(?:https?://)?(?:www\.)?(?:youtube\.com|youtu\.be)/watch\?v=[\w-]+"
)


def get_video_id(video_url: str) -> str:
    return re.search(r"watch\?v=([\w-]+)", video_url).group(1)  # type: ignore
