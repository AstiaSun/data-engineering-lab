FROM python:3.13.3

RUN pip install pipenv
WORKDIR /data-engineering-lab
COPY Pipfile Pipfile.lock ./
RUN pipenv sync

COPY hw1/alembic/ alembic/
COPY hw1/alembic.ini .

COPY hw1/src/*.py hw1/src/
