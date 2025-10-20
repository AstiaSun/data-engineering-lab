FROM python:3.11.13

RUN apt-get update && apt-get install -y \
    gcc \
    make \
    libev-dev \
    && rm -rf /var/lib/apt/lists/*

ENV POETRY_VERSION=2.0.0 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /data-engineering-lab

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root

COPY src/ src/
COPY logging.ini logging.ini
