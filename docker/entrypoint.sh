#!/bin/bash
set -e

# OpenAI API key kontrolü - sadece soru üretimi komutları için
NON_API_COMMANDS="list-roles|list-categories|--help|-h"
if [[ ! "$*" =~ $NON_API_COMMANDS ]] && [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ HATA: OPENAI_API_KEY environment variable tanımlı değil!"
    echo "💡 Çözüm: .env dosyasında OPENAI_API_KEY=your-key-here ekleyin"
    exit 1
fi

# Data klasörü izinlerini ayarla
chmod -R 755 /app/data/ 2>/dev/null || true

# Python path ayarla
export PYTHONPATH=/app:$PYTHONPATH

# Main script'i çalıştır
exec python main.py "$@"