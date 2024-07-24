FROM python:3.12-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=1.8.3 \
    POETRY_VIRTUALENVS_IN_PROJECT=true

RUN pip install poetry==$POETRY_VERSION

WORKDIR /app
COPY pyproject.toml poetry.lock ./

RUN poetry install --without dev

# Runtime image

FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app
COPY --from=builder /app/.venv .venv
COPY src src

CMD fastapi run --host 0.0.0.0 --port 8000 src/main.py