# syntax=docker/dockerfile:1
FROM python:3.10-slim-buster
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY ./src .
EXPOSE 8080/tcp
ENTRYPOINT [ "python3", "./main.py"]