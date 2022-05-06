# syntax=docker/dockerfile:1
FROM python:3.8.13-slim-buster AS python-base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VIRTUAL_ENV="/opt/pysetup/.venv"

ENV PATH="$POETRY_HOME/bin:$VIRTUAL_ENV/bin:$PATH"

# less: Python help() use it
# make: Use of make with Makefile
# git: pre-commit checks during testing
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        less \
        make \
        sqlite \
        git && \
    apt-get autoremove -y && \
    apt-get clean autoclean && \
    rm -rf /var/lib/apt/lists/*


### STAGE builder-base is used to build dependencies
FROM python-base AS builder-base

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        build-essential

RUN mkdir $POETRY_HOME $PYSETUP_PATH

RUN chown -R 1000:1000 $POETRY_HOME $PYSETUP_PATH

USER 1000

# Install Poetry - respects $POETRY_VERSION & $POETRY_HOME
ENV POETRY_VERSION=1.1.13
RUN curl -sSL https://install.python-poetry.org | python3 -

# We copy our Python requirements here to cache them
# and install only runtime deps using poetry
WORKDIR $PYSETUP_PATH
COPY ./poetry.lock ./pyproject.toml ./

# POETRY_CACHE_DIR is not recognised by Poetry
RUN XDG_CACHE_HOME="/opt/poetry/.cache" poetry install --no-dev


### STAGE development installs all dev deps and can be used to develop code
# For example using docker-compose to mount local volume under /code
FROM python-base AS development

USER 1000

# Copying poetry and venv into image
COPY --from=builder-base $POETRY_HOME $POETRY_HOME
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH

# venv already has runtime deps installed we get a quicker install
WORKDIR $PYSETUP_PATH

RUN XDG_CACHE_HOME="/opt/poetry/.cache" poetry install

WORKDIR /code


### STAGE testing
FROM development AS testing

COPY . ./
