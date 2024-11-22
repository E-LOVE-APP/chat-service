FROM python:3.10-slim AS builder

ARG INSTALL_DEV=true

WORKDIR /app

# linux stuff that must be installed 
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libssl-dev \
    libffi-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false

RUN if [ "$INSTALL_DEV" = "true" ] ; then \
        poetry install --no-interaction --no-ansi ; \
    else \
        poetry install --no-dev --no-interaction --no-ansi ; \
    fi

RUN apt-get purge -y --auto-remove gcc libssl-dev libffi-dev build-essential

FROM python:3.10-slim

WORKDIR /app

# copying a "light" version of a project
COPY --from=builder /usr/local /usr/local
COPY --from=builder /app /app

COPY . /app

EXPOSE 8081

# for the nearest future
# CMD ["bash", "-c", "poetry run alembic upgrade head && python -m scripts.db_scripts.populate_db && poetry run uvicorn main:app --host 0.0.0.0 --port 8080"]

CMD ["bash", "-c", "poetry run uvicorn main:app --host 0.0.0.0 --port 8081"]