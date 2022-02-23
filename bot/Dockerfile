# syntax=docker/dockerfile:1

FROM python:3.9-slim-buster

ENV PYTHONUNBUFFERED True

WORKDIR /bot

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD ["python3", "-m", "bot"]
