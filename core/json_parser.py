"""
GELİŞMİŞ JSON PARSE SİSTEMİ
===========================

OpenAI API yanıtlarını temizleyip JSON formatına çeviren gelişmiş sistem.
Diğer projeden adapte edilmiş gelişmiş regex temizleme mekanizmaları.
"""

import json
import logging
import re
from typing import Dict, Any

logger = logging.getLogger(__name__)

def extract_question_data(generated_text: str) -> Dict[str, Any]:
    """
    OpenAI API yanıtından soru ve cevap verilerini çıkarır.
    Gelişmiş JSON temizleme ve parse sistemi.
    """
    try:
        # Markdown code block'ları ve diğer formatları temizle
        cleaned_text = generated_text.strip()
        
        # Farklı JSON başlangıçlarını temizle - REGEX ile güçlendirildi
        
        # ```json { ... } ``` formatını temizle
        if '```json' in cleaned_text and '```' in cleaned_text:
            # Regex ile ```json ile ``` arasındaki kısmı çıkar
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', cleaned_text, re.DOTALL)
            if json_match:
                cleaned_text = json_match.group(1).strip()
        elif cleaned_text.startswith('```json'):
            cleaned_text = cleaned_text.replace('```json', '').replace('```', '').strip()
        elif cleaned_text.startswith('```'):
            cleaned_text = cleaned_text.replace('```', '').strip()
        elif cleaned_text.startswith('json ('):
            cleaned_text = cleaned_text.replace('json (', '{', 1).strip()
        elif cleaned_text.startswith('"json ('):
            cleaned_text = cleaned_text.replace('"json (', '{', 1).strip()
        
        # JSON içinde başlangıç/bitiş karakterlerini düzelt
        if not cleaned_text.startswith('{') and '{' in cleaned_text:
            # İlk { karakterinden başla
            start_idx = cleaned_text.find('{')
            cleaned_text = cleaned_text[start_idx:]
        
        if not cleaned_text.endswith('}') and '}' in cleaned_text:
            # Son } karakterinde bitir
            end_idx = cleaned_text.rfind('}')
            cleaned_text = cleaned_text[:end_idx+1]
        
        # JSON içindeki yanlış anahtar kelimeler formatını düzelt - SÜPER GÜÇLENDİRİLDİ
        # AI'ın ürettiği en yaygın hatalı formatları yakala ve düzelt:
        
        # Format 1: "expected_answer": "text", "\n\nAnahtar kelimeler: words" }
        pattern1 = r'("expected_answer":\s*"[^"]*"),\s*"(\\n\\nAnahtar kelimeler:[^"]*)"(\s*\})'
        if re.search(pattern1, cleaned_text):
            cleaned_text = re.sub(pattern1, r'\1\2"\3', cleaned_text)
            logger.info("JSON Format 1 düzeltildi")
        
        # Format 2: "text", "\n\nAnahtar kelimeler: words" 
        pattern2 = r'",\s*"(\\n\\nAnahtar kelimeler:[^"]*)"'
        if re.search(pattern2, cleaned_text):
            cleaned_text = re.sub(pattern2, r'\1"', cleaned_text)
            logger.info("JSON Format 2 düzeltildi")
            
        # Format 3: Çift quotes düzeltme
        cleaned_text = cleaned_text.replace('""', '"')
        
        # Format 4: Anahtar kelimeler için özel düzeltme - yanlış virgül yerleşimi
        pattern4 = r'",\s*\n\s*"(\\n\\nAnahtar kelimeler:[^"]*)"'
        if re.search(pattern4, cleaned_text):
            cleaned_text = re.sub(pattern4, r'\1"', cleaned_text)
            logger.info("JSON Format 4 düzeltildi")
            
        # Format 5: Satır sonu ve anahtar kelimeler düzeltmesi
        pattern5 = r'",\s*\n\s*\n\s*"(\\n\\nAnahtar kelimeler:[^"]*)"'
        if re.search(pattern5, cleaned_text):
            cleaned_text = re.sub(pattern5, r'\1"', cleaned_text)
            logger.info("JSON Format 5 düzeltildi")
        
        # Eğer JSON formatında geldiyse parse et
        if cleaned_text.startswith('{') and cleaned_text.endswith('}'):
            question_data = json.loads(cleaned_text)
            question_text = question_data.get('question', cleaned_text)
            expected_answer = question_data.get('expected_answer', '')
            
            # Eğer question alanı tekrar JSON ise, onu da parse et
            if isinstance(question_text, str):
                # Nested JSON'ı daha agresif parse et
                question_text = question_text.strip()
                
                # ```json blokları içindeki nested JSON'ı temizle
                if '```json' in question_text:
                    json_match = re.search(r'```json\s*(\{.*?\})\s*```', question_text, re.DOTALL)
                    if json_match:
                        question_text = json_match.group(1).strip()
                
                # JSON formatında mı kontrol et
                if question_text.startswith('{') and question_text.endswith('}'):
                    try:
                        # JSON temizleme işlemleri
                        clean_question = question_text
                        # Anahtar kelimeler kısmını düzelt
                        clean_question = re.sub(r'",\s*\n\s*"(\\n\\nAnahtar kelimeler:[^"]*)"', r'\1"', clean_question)
                        clean_question = re.sub(r'",\s*"(\\n\\nAnahtar kelimeler:[^"]*)"', r'\1"', clean_question)
                        
                        nested_json = json.loads(clean_question)
                        question_text = nested_json.get('question', question_text)
                        if not expected_answer:  # expected_answer boşsa nested'dan al
                            expected_answer = nested_json.get('expected_answer', '')
                        logger.info("Nested JSON başarıyla parse edildi")
                    except Exception as nested_error:
                        logger.warning(f"Nested JSON parse edilemedi: {nested_error}")
                        # JSON string'i düz metne çevir
                        try:
                            nested_data = eval(question_text)  # Son çare olarak eval kullan
                            if isinstance(nested_data, dict):
                                question_text = nested_data.get('question', question_text)
                                if not expected_answer:
                                    expected_answer = nested_data.get('expected_answer', '')
                                logger.info("Nested JSON eval ile parse edildi")
                        except:
                            logger.warning("Eval ile de parse edilemedi, raw string kullanılacak")
            
            return {
                "success": True,
                "question": question_text,
                "expected_answer": expected_answer,
                "raw_response": generated_text
            }
        else:
            # Düz metin olarak gelirse direkt kullan
            logger.warning(f"JSON parse edilemedi, düz metin kullanılıyor: {cleaned_text[:100]}...")
            return {
                "success": True,
                "question": cleaned_text,
                "expected_answer": '',
                "raw_response": generated_text
            }
            
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse hatası: {e}")
        # JSON parse hatası durumunda düz metin olarak kullan
        return {
            "success": True,
            "question": generated_text.strip(),
            "expected_answer": '',
            "raw_response": generated_text,
            "parse_error": str(e)
        }
    except Exception as e:
        logger.error(f"JSON extract hatası: {e}")
        return {
            "success": False,
            "error": str(e),
            "raw_response": generated_text
        }