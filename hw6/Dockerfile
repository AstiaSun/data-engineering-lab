FROM python:3.13.3

# Install Java
RUN apt-get update && apt-get install -y openjdk-17-jdk curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Setup python environment
ENV POETRY_VERSION=2.0.0 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /data-engineering-lab

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root

ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-arm64
ENV PATH="$JAVA_HOME/bin:$PATH"

COPY src/ src/
