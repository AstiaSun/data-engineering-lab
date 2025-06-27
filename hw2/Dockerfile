FROM python:3.13.3

RUN pip install pipenv
WORKDIR /data-engineering-lab
COPY Pipfile Pipfile.lock ./
RUN pipenv sync

COPY hw2/src/*.py hw2/src/
