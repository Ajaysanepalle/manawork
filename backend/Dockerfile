FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=180 --retries=5 -r requirements.txt
COPY app ./app
COPY alembic.ini ./alembic.ini
COPY alembic ./alembic
RUN groupadd --system --gid 10001 manaworks && useradd --system --uid 10001 --gid manaworks --home-dir /app manaworks && chown -R manaworks:manaworks /app
USER manaworks
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]