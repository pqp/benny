FROM ubuntu:20.04

RUN apt update
RUN apt -y install python3 python3-venv libopus0 ffmpeg

RUN mkdir /app

COPY . /app

WORKDIR /app

RUN python3 -m venv venv
RUN venv/bin/python3 -m pip install wheel
RUN venv/bin/python3 -m pip install -r requirements.txt

CMD venv/bin/python3 /app/benny.py
