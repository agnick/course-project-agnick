FROM python:3.11-slim AS build

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements*.txt ./
RUN --mount=type=cache,target=/root/.cache \
    pip install --upgrade pip && \
    pip wheel -r requirements.txt -w /wheels

COPY app app

FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN groupadd -r app -g 10001 && useradd -r -g app -u 10001 app
WORKDIR /app

COPY --from=build /wheels /wheels
RUN pip install --no-cache-dir /wheels/*

COPY app app
COPY requirements*.txt ./
RUN chown -R app:app /app

USER app
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD ["python","-c","import http.client,sys; c=http.client.HTTPConnection('127.0.0.1',8000,timeout=2); c.request('GET','/health'); r=c.getresponse(); sys.exit(0 if r.status==200 else 1)"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
