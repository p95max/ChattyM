FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
      bash build-essential curl git libpq-dev postgresql-client \
    && rm -rf /var/lib/apt/lists/*

ARG POETRY_VERSION=1.6.1
RUN curl -sSL https://install.python-poetry.org | python3 - --version $POETRY_VERSION \
 && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

COPY pyproject.toml poetry.lock* /app/
RUN poetry config virtualenvs.create false \
 && poetry install --no-interaction --no-ansi --no-dev

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

COPY . /app

RUN mkdir -p /app/staticfiles /app/media

EXPOSE 8000
