# Pull base image
FROM python:3.9-slim-buster
# Set environment variable
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create a new folder for the the locally saved code, change cwd, copy code
WORKDIR /code
COPY . /code/

# Upgrade pip and install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt