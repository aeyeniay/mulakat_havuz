FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

RUN mkdir -p /app/data/job_descriptions /app/data/generated_questions /app/data/word_exports
RUN chmod +x docker/entrypoint.sh || true

# Non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

ENV PYTHONPATH=/app

ENTRYPOINT ["docker/entrypoint.sh"]
CMD ["--help"]
