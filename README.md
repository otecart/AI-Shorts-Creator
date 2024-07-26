# AI-Shorts-Creator! 🎥✂️

AI-Shorts-Creator is a powerful tool designed for content creators, podcasters, and video enthusiasts to effortlessly extract captivating segments from their videos. Leveraging the advanced language model GPT-4, this innovative solution intelligently analyzes video transcripts to identify the most viral and exciting moments. By harnessing the capabilities of FFmpeg and OpenCV, AI-Shorts-Creator automatically crops videos, allowing you to focus on the key highlights and provide an enhanced viewing experience.

## AI-Shorts-Creator is a powerful tool designed to:

- Automatically extract captivating segments from videos.
- Identify the most viral and exciting moments using GPT-4.
- Crop videos to emphasize key highlights with precise face detection. (*Doesn't work*)
- Streamline video editing and save time by eliminating manual searching.
- Work seamlessly with various video formats for maximum compatibility. (*Only works with .mp4*)
- Enhance the viewing experience for your audience with perfectly cropped highlights. (*Cropping doesn't work*)


## Examples: 

<details>
  <summary>Fake examples</summary>

Source Video : https://www.youtube.com/watch?v=NHaczOsMQ20
![thumbnail](https://github.com/NisaarAgharia/AI-Video-Cropper/assets/22457544/7dbf9b92-2a08-4948-bb49-e41350ae4a02)

## Output Shorts:

<div align="center">
  <img src="https://github.com/NisaarAgharia/AI-Video-Cropper/assets/22457544/81b0759b-7cc9-4622-9440-3ccf9400ede2" alt="Demo GIF 1" width="280"/>
  <img src="https://github.com/NisaarAgharia/AI-Video-Cropper/assets/22457544/f3ea6e7d-f999-4597-87fc-0166c1be7840" alt="Demo GIF 2" width="280"/>
  <img src="https://github.com/NisaarAgharia/AI-Video-Cropper/assets/22457544/8aeeb666-cff0-493a-8a9a-18780badd79f" alt="Demo GIF 3" width="280"/>
</div>

https://github.com/NisaarAgharia/AI-Shorts-Creator/assets/22457544/318c8cf1-bcc3-4ed7-a979-7af17e545e6e

</details>

## Requirements
- Python 3.12+
- poetry
- FFmpeg
- Redis
- RabbitMQ

## Usage

1. Install the required libraries by running the following command:

```shell
poetry install
```

2. Make sure the `ffmpeg` command is accessible from the command line.

3. Rename `.env.example` to `.env` and set all necessary variables.

4. Make sure your Redis and RabbitMQ instances are running.

5. Run taskiq worker

```shell
poetry run taskiq worker src.worker:broker src.tasks
```

6. Run taskiq scheduler

```shell
poetry run taskiq scheduler --skip-first-run src.worker:scheduler src.tasks
```

7. Run fastapi server

```shell
poetry run fastapi run src/main.py
```

This will run AI-Shorts-Creator server on port `8000` (by default). It's API could be found on `http://localhost:8000/docs` (by default).
