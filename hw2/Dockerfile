FROM python:3.13.3

ENV POETRY_VERSION=2.0.0 \
 PYTHONUNBUFFERED=1 \
 POETRY_VIRTUALENVS_CREATE=false \
 POETRY_NO_INTERACTION=1

RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /data-engineering-lab
COPY poetry.lock pyproject.toml ./
RUN poetry install --no-root

COPY hw2/src/*.py hw2/src/
