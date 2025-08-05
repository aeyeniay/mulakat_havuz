FROM python:3.11-slim

# Sistem güncellemeleri ve gerekli paketler
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Çalışma dizini oluştur
WORKDIR /app

# Python bağımlılıklarını kopyala ve yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama kodunu kopyala
COPY . .

# Data dizinini oluştur (volume mount için)
RUN mkdir -p /app/data/job_descriptions \
    /app/data/generated_questions \
    /app/data/word_exports

# Entry point scriptini çalıştırılabilir yap
RUN chmod +x docker/entrypoint.sh

# Non-root user oluştur (güvenlik için)
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Port expose (gerekirse web interface için)
EXPOSE 8000

# Entry point
ENTRYPOINT ["docker/entrypoint.sh"]
CMD ["--help"]