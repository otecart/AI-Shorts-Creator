import os
from datetime import timedelta

import dotenv
from taskiq import TaskiqScheduler
from taskiq.schedule_sources import LabelScheduleSource
from taskiq_aio_pika import AioPikaBroker
from taskiq_redis import RedisAsyncResultBackend

dotenv.load_dotenv()

redis_url = f"redis://:{os.environ["REDIS_PASSWORD"]}@{os.environ["REDIS_HOST"]}:{os.environ["REDIS_PORT"]}"
result_backend = RedisAsyncResultBackend(
    redis_url + "/0",
    result_ex_time=int(timedelta(hours=1).total_seconds()),
)

rabbitmq_url = f"amqp://{os.environ["RABBITMQ_USER"]}:{os.environ["RABBITMQ_PASS"]}@{os.environ["RABBITMQ_HOST"]}:{os.environ["RABBITMQ_PORT"]}"
broker = AioPikaBroker(rabbitmq_url).with_result_backend(result_backend)

source = LabelScheduleSource(broker)
scheduler = TaskiqScheduler(broker, sources=[source])
