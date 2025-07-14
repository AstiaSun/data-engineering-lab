FROM python:3.13.3

ENV POETRY_VERSION=2.0.0 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /data-engineering-lab-hw3
COPY pyproject.toml poetry.lock ./
COPY src/ src/

RUN poetry install --no-root
