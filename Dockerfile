# syntax=docker/dockerfile:1
FROM python:3.10-slim-buster
RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
ENV PYTHONPATH "${PYTHONPATH}:."
EXPOSE 8080/tcp
ENTRYPOINT [ "python3", "./src/main.py"]