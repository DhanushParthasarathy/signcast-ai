FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/home/app/.local/bin:${PATH}"

WORKDIR /app

RUN apt-get update \
  && apt-get install -y --no-install-recommends ffmpeg curl \
  && rm -rf /var/lib/apt/lists/* \
  && adduser --disabled-password --gecos "" app

COPY backend/pyproject.toml .
RUN pip install --no-cache-dir .

COPY backend/app ./app
COPY backend/tests ./tests
COPY backend/.env.example ./.env.example
COPY database/migrations ./database/migrations
RUN chown -R app:app /app

USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD curl -fsS http://127.0.0.1:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
