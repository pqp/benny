#FROM ubuntu:20.04
FROM python:3-slim

RUN apt update \
    && apt -y install python3 python3-venv libopus0 ffmpeg

WORKDIR /app

COPY . .

RUN python3 -m venv venv \
    && venv/bin/python3 -m pip install wheel \
    && venv/bin/python3 -m pip install -r requirements.txt

ENTRYPOINT ["/app/venv/bin/python3", "/app/benny.py"]
