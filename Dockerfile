# syntax=docker/dockerfile:1

FROM python:3.8-buster

RUN apt-get update -y && \
    apt-get install -y curl git && \
    curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python -

ARG WORKDIR=/home/bookk-bookk
ARG WORKDIR

WORKDIR $WORKDIR

COPY pyproject.toml $WORKDIR/pyproject.toml
COPY poetry.lock $WORKDIR/poetry.lock

ENV PATH="/root/.local/bin:$PATH"
RUN poetry config virtualenvs.create false && \
    poetry install --no-dev

COPY apps $WORKDIR/apps
COPY gunicorn.ini.py $WORKDIR/gunicorn.ini.py
COPY entrypoint.sh $WORKDIR/entrypoint.sh

ENV WORKERS=4 \
    PORT=8003

RUN --mount=type=secret,id=notion_token cat /run/secrets/notion_token | tee /notion_token.txt

EXPOSE 8000

ENTRYPOINT ./entrypoint.sh
