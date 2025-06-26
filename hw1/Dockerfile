FROM python:3.13.3

# Set up environment
RUN pip install pipenv
WORKDIR /data-engineering-lab
COPY Pipfile Pipfile.lock ./
RUN pipenv sync

COPY alembic/ alembic/
COPY alembic.ini constants.py ./

COPY hw1/*.py hw1/
COPY hw2/*.py hw2/
