# syntax=docker/dockerfile:1

FROM python:3.9-slim-buster

ENV PYTHONUNBUFFERED True

RUN apt update && apt install libffi-dev libnacl-dev python3-dev

WORKDIR /bot
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD ["python3", "-m", "bot"]
