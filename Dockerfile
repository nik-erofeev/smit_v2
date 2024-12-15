FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=10 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=false \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    LC_ALL=C.UTF-8 \
    LANG=C.UTF-8

WORKDIR /app_example

RUN apt-get update && apt-get install -y curl netcat-openbsd && apt-get clean

COPY app /app_example/app
COPY docker /app_example/docker
COPY migrations /app_example/migrations
COPY pyproject.toml /app_example
COPY alembic.ini /app_example
#COPY pyproject.toml ./
COPY pyproject.toml poetry.lock* ./

RUN pip install --upgrade pip && \
    pip install poetry && \
    poetry install --no-dev


RUN chmod +x /app_example/docker/app.sh


EXPOSE 8000