FROM python:3.13.3

# Set up environment
RUN pip install pipenv
WORKDIR /data-engineering-lab
COPY Pipfile Pipfile.lock ./
RUN pipenv sync

# Run data loader
COPY hw1/*.py hw1/
CMD ["pipenv", "run", "python", "-m", "hw1.data_loader"]