import json
from abc import ABC, abstractmethod

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

from src.schemas import Segment


class TextSegmenter(ABC):
    @abstractmethod
    def run(self, text: str) -> list[Segment]: ...


class OpenAISegmenter(TextSegmenter):
    def __init__(self, client: OpenAI, system_message: str | None = None):
        self.client = client
        self.messages: list[ChatCompletionMessageParam] = []
        if system_message:
            self.messages.append({"role": "system", "content": system_message})

    def run(self, text: str) -> list[Segment]:
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=self.messages + [{"role": "user", "content": text}],
            n=1,
            stop=None,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        if content is None:
            raise RuntimeError("No content in response")
        segments = json.loads(content)["segments"]
        return segments
