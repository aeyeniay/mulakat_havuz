"""
OPENAI API AYARLARI VE KONFİGÜRASYON
===================================

OpenAI API bağlantısı ve parametreleri için konfigürasyon dosyası.
"""

import os
from typing import Optional

# OpenAI API konfigürasyonu
DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_TIMEOUT = 60.0
DEFAULT_MAX_RETRIES = 3
DEFAULT_TEMPERATURE = 0.8
DEFAULT_MAX_TOKENS = 16000  # GPT-4o-mini max output (100+ soru için)

def get_openai_config() -> dict:
    """
    Çevre değişkenlerinden OpenAI konfigürasyonunu al.
    
    Returns:
        dict: OpenAI API konfigürasyon bilgileri
    """
    return {
        "api_key": os.getenv("OPENAI_API_KEY"),
        "model": os.getenv("OPENAI_MODEL", DEFAULT_MODEL),
        "timeout": float(os.getenv("OPENAI_TIMEOUT", DEFAULT_TIMEOUT)),
        "max_retries": int(os.getenv("OPENAI_MAX_RETRIES", DEFAULT_MAX_RETRIES)),
        "temperature": float(os.getenv("OPENAI_TEMPERATURE", DEFAULT_TEMPERATURE)),
        "max_tokens": int(os.getenv("OPENAI_MAX_TOKENS", DEFAULT_MAX_TOKENS))
    }

def validate_api_key() -> bool:
    """
    OpenAI API anahtarının tanımlı olup olmadığını kontrol et.
    
    Returns:
        bool: API key tanımlı ise True
    """
    api_key = os.getenv("OPENAI_API_KEY")
    return api_key is not None and len(api_key.strip()) > 0

def get_model_info() -> dict:
    """
    Kullanılacak model bilgilerini döndür.
    
    Returns:
        dict: Model bilgileri
    """
    return {
        "name": DEFAULT_MODEL,
        "display_name": f"{DEFAULT_MODEL} - OpenAI API",
        "speed_category": "🚀 API Hızlı",
        "recommended": True,
        "description": "OpenAI'ın optimize edilmiş, hızlı ve ekonomik modeli"
    }