"""
ANA SORU ÜRETİM MOTORU
=====================

Mevcut projeden uyarlanan OpenAI API entegrasyonu ile soru üretimi.
"""

import json
import logging
import re
from typing import Dict, Any, List, Optional
from openai import OpenAI

from core.prompt_templates import SYSTEM_MESSAGE, MAIN_PROMPT_TEMPLATE, BATCH_PROMPT_TEMPLATE
from core.json_parser import extract_question_data
from config.rubric_system import get_difficulty_distribution_by_multiplier
from config.openai_settings import get_openai_config, validate_api_key
from config.question_categories import get_active_question_categories

logger = logging.getLogger(__name__)

class QuestionGenerator:
    """Ana soru üretim sınıfı - OpenAI API ile entegre"""
    
    def __init__(self):
        """Soru üretici başlatıcı"""
        self.openai_config = get_openai_config()
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """OpenAI client'ını başlat"""
        if not validate_api_key():
            raise ValueError("OPENAI_API_KEY environment variable tanımlı değil!")
        
        try:
            self.client = OpenAI(
                api_key=self.openai_config["api_key"],
                timeout=self.openai_config["timeout"],
                max_retries=self.openai_config["max_retries"]
            )
            logger.info("OpenAI client başarıyla başlatıldı")
        except Exception as e:
            logger.error(f"OpenAI client başlatma hatası: {e}")
            raise
    
    def check_api_status(self) -> Dict[str, Any]:
        """API durumunu kontrol et"""
        try:
            response = self.client.chat.completions.create(
                model=self.openai_config["model"],
                messages=[{"role": "user", "content": "test"}],
                max_tokens=10
            )
            
            return {
                "api_available": True,
                "model": self.openai_config["model"],
                "status": "connected",
                "test_response": response.choices[0].message.content
            }
            
        except Exception as e:
            logger.error(f"API durumu kontrol hatası: {e}")
            return {
                "api_available": False,
                "error": str(e),
                "details": "API bağlantı hatası"
            }
    
    def generate_single_question(
        self,
        role_name: str,
        job_context: str,
        description: str,
        salary_coefficient: int,
        question_type: str,
        type_name: str,
        question_number: int = 1
    ) -> Dict[str, Any]:
        """
        Tek bir soru üret.
        
        Args:
            role_name: Pozisyon ismi
            job_context: İlan bağlamı
            description: İş tanımı
            salary_coefficient: Maaş katsayısı (zorluk seviyesi)
            question_type: Soru tipi kodu
            type_name: Soru tipi ismi
            question_number: Soru numarası
            
        Returns:
            dict: Üretilen soru verisi
        """
        try:
            # Zorluk dağılımını hesapla
            difficulty_distribution = get_difficulty_distribution_by_multiplier(salary_coefficient)
            
            # Prompt'u oluştur
            prompt = MAIN_PROMPT_TEMPLATE.format(
                job_context=job_context,
                role_name=role_name,
                salary_coefficient=salary_coefficient,
                description=description,
                type_name=type_name,
                question_number=question_number,
                K1=difficulty_distribution["K1_Temel_Bilgi"],
                K2=difficulty_distribution["K2_Uygulamali"],
                K3=difficulty_distribution["K3_Hata_Cozumleme"],
                K4=difficulty_distribution["K4_Tasarim"],
                K5=difficulty_distribution["K5_Stratejik"]
            )
            
            # OpenAI API çağrısı
            response = self.client.chat.completions.create(
                model=self.openai_config["model"],
                messages=[
                    {"role": "system", "content": SYSTEM_MESSAGE},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.openai_config["temperature"],
                max_tokens=self.openai_config["max_tokens"]
            )
            
            logger.info(f"{type_name} sorusu {question_number} için API yanıtı alındı")
            
            # Yanıtı parse et
            raw_response = response.choices[0].message.content
            question_data = extract_question_data(raw_response)
            
            # Sonuç verisini hazırla
            result = {
                "success": True,
                "question": question_data["question"],
                "expected_answer": question_data["expected_answer"],
                "question_type": question_type,
                "type_name": type_name,
                "role": role_name,
                "salary_coefficient": salary_coefficient,
                "difficulty_distribution": difficulty_distribution,
                "api_used": "openai",
                "raw_response": raw_response if not question_data["success"] else None
            }
            
            logger.info(f"{type_name} sorusu {question_number} başarıyla üretildi")
            return result
            
        except Exception as e:
            logger.error(f"Soru üretim hatası ({type_name} {question_number}): {e}")
            return {
                "success": False,
                "error": str(e),
                "question_type": question_type,
                "type_name": type_name,
                "api_used": "openai"
            }
    
    def _parse_questions_array(self, generated_text: str) -> List[Dict[str, Any]]:
        """JSON Array formatındaki soruları parse et"""
        try:
            # JSON temizleme işlemleri
            cleaned_text = generated_text.strip()
            
            # Markdown code block'larını temizle
            if '```json' in cleaned_text:
                json_match = re.search(r'```json\s*(\[.*?\])\s*```', cleaned_text, re.DOTALL)
                if json_match:
                    cleaned_text = json_match.group(1).strip()
            elif cleaned_text.startswith('```'):
                cleaned_text = cleaned_text.replace('```', '').strip()
            
            # JSON array'in başlangıç ve bitişini kontrol et
            if not cleaned_text.startswith('['):
                start_idx = cleaned_text.find('[')
                if start_idx != -1:
                    cleaned_text = cleaned_text[start_idx:]
            
            if not cleaned_text.endswith(']'):
                end_idx = cleaned_text.rfind(']')
                if end_idx != -1:
                    cleaned_text = cleaned_text[:end_idx+1]
            
            # JSON parse et
            questions_array = json.loads(cleaned_text)
            
            if not isinstance(questions_array, list):
                logger.warning("Yanıt array formatında değil, tek soru olarak işleniyor")
                if isinstance(questions_array, dict):
                    return [questions_array]
                else:
                    return []
            
            # Her soruyu kontrol et ve temizle
            cleaned_questions = []
            for i, question_data in enumerate(questions_array):
                if isinstance(question_data, dict):
                    question_result = {
                        "success": True,
                        "question": question_data.get("question", ""),
                        "expected_answer": question_data.get("expected_answer", "")
                    }
                    cleaned_questions.append(question_result)
                else:
                    logger.warning(f"Soru {i+1} geçersiz format: {question_data}")
            
            logger.info(f"Array parse başarılı: {len(cleaned_questions)} soru")
            return cleaned_questions
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON Array parse hatası: {e}")
            # Hata durumunda extract_question_data'yı dene
            try:
                single_result = extract_question_data(generated_text)
                return [single_result] if single_result.get("success") else []
            except:
                return []
        except Exception as e:
            logger.error(f"Array parse genel hatası: {e}")
            return []
    
    def _parse_questions_array_robust(self, generated_text: str) -> List[Dict[str, Any]]:
        """
        SÜPER GÜÇLENDİRİLMİŞ JSON Parser - Tüm AI format'larını handle eder
        """
        logger.info(f"🚀 Süper parser başlıyor: {len(generated_text)} karakter")
        
        # Strateji 1: Direkt JSON Array parse
        result = self._try_direct_json_array(generated_text)
        if result:
            logger.info(f"✅ Strateji 1 başarılı: {len(result)} soru")
            return result
        
        # Strateji 2: Markdown temizleyerek parse
        result = self._try_markdown_cleanup_parse(generated_text)
        if result:
            logger.info(f"✅ Strateji 2 başarılı: {len(result)} soru")
            return result
        
        # Strateji 3: Regex ile JSON Array çıkarma
        result = self._try_regex_extract_parse(generated_text)
        if result:
            logger.info(f"✅ Strateji 3 başarılı: {len(result)} soru")
            return result
        
        # Strateji 4: Nested JSON parse (AI tek object döndürürse)
        result = self._try_nested_json_robust(generated_text)
        if result:
            logger.info(f"✅ Strateji 4 başarılı: {len(result)} soru")
            return result
        
        logger.error("❌ Tüm parse stratejileri başarısız!")
        return []
    
    def _try_direct_json_array(self, text: str) -> List[Dict[str, Any]]:
        """Strateji 1: Direkt JSON Array parse"""
        try:
            cleaned = text.strip()
            if cleaned.startswith('[') and cleaned.endswith(']'):
                data = json.loads(cleaned)
                if isinstance(data, list):
                    return self._format_questions_array(data)
        except:
            pass
        return []
    
    def _try_markdown_cleanup_parse(self, text: str) -> List[Dict[str, Any]]:
        """Strateji 2: Markdown temizleyerek parse"""
        try:
            # ```json ... ``` blokları temizle
            patterns = [
                r'```json\s*(\[.*?\])\s*```',
                r'```\s*(\[.*?\])\s*```',
                r'json\s*(\[.*?\])',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text, re.DOTALL)
                if match:
                    json_content = match.group(1).strip()
                    data = json.loads(json_content)
                    if isinstance(data, list):
                        return self._format_questions_array(data)
        except:
            pass
        return []
    
    def _try_regex_extract_parse(self, text: str) -> List[Dict[str, Any]]:
        """Strateji 3: Regex ile JSON Array çıkarma"""
        try:
            # İlk [ ile son ] arasını al
            start = text.find('[')
            end = text.rfind(']')
            
            if start != -1 and end != -1 and start < end:
                json_content = text[start:end+1]
                # JSON hatalarını düzelt
                json_content = self._fix_common_json_errors(json_content)
                data = json.loads(json_content)
                if isinstance(data, list):
                    return self._format_questions_array(data)
        except:
            pass
        return []
    
    def _try_nested_json_robust(self, text: str) -> List[Dict[str, Any]]:
        """Strateji 4: AI tek object döndürürse (nested JSON)"""
        try:
            # Önce tek object parse et
            single_obj = extract_question_data(text)
            if not single_obj.get("success"):
                return []
            
            question_field = single_obj.get("question", "")
            
            # Question field'ında JSON Array var mı?
            if '[' in question_field and ']' in question_field:
                # JSON Array çıkar
                start = question_field.find('[')
                end = question_field.rfind(']')
                
                if start != -1 and end != -1:
                    json_str = question_field[start:end+1]
                    json_str = self._fix_common_json_errors(json_str)
                    data = json.loads(json_str)
                    if isinstance(data, list):
                        return self._format_questions_array(data)
        except:
            pass
        return []
    
    def _format_questions_array(self, data: List[Dict]) -> List[Dict[str, Any]]:
        """JSON Array'i standard format'a çevir"""
        result = []
        for item in data:
            if isinstance(item, dict) and "question" in item:
                result.append({
                    "success": True,
                    "question": str(item.get("question", "")),
                    "expected_answer": str(item.get("expected_answer", ""))
                })
        return result
    
    def _fix_common_json_errors(self, json_text: str) -> str:
        """JSON'daki yaygın hataları düzelt"""
        # Fazla virgül temizle
        json_text = re.sub(r',(\s*[}\]])', r'\1', json_text)
        
        # Çift virgül temizle
        json_text = re.sub(r',,+', ',', json_text)
        
        # Escape edilmemiş newline'ları düzelt
        json_text = re.sub(r'(?<!\\)\n', '\\n', json_text)
        
        # Escape edilmemiş quote'ları düzelt (basit versiyon)
        json_text = re.sub(r'(?<!\\)"(?=\w)', '\\"', json_text)
        
        return json_text
    
    def _try_parse_nested_json(self, generated_text: str) -> List[Dict[str, Any]]:
        """
        AI'ın question field'ında JSON Array döndürdüğü durum için parser
        """
        try:
            logger.info("Nested JSON parse deneniyor...")
            
            # Önce tek soru olarak parse etmeyi dene
            single_result = extract_question_data(generated_text)
            
            if not single_result.get("success"):
                return []
            
            question_content = single_result.get("question", "")
            
            # Question içinde JSON Array var mı kontrol et
            if not ('[' in question_content and ']' in question_content):
                return []
            
            # Question içindeki JSON'u çıkar
            # Markdown temizle
            if '```json' in question_content:
                json_match = re.search(r'```json\s*(\[.*?\])\s*```', question_content, re.DOTALL)
                if json_match:
                    question_content = json_match.group(1).strip()
            
            # JSON Array sınırlarını bul
            start_idx = question_content.find('[')
            end_idx = question_content.rfind(']')
            
            if start_idx == -1 or end_idx == -1:
                return []
            
            json_content = question_content[start_idx:end_idx+1]
            
            # JSON'u temizle ve parse et
            json_content = self._fix_common_json_errors(json_content)
            questions_array = json.loads(json_content)
            
            if not isinstance(questions_array, list):
                return []
            
            # Sonuçları hazırla
            result = []
            for item in questions_array:
                if isinstance(item, dict) and "question" in item:
                    result.append({
                        "success": True,
                        "question": str(item.get("question", "")),
                        "expected_answer": str(item.get("expected_answer", ""))
                    })
            
            logger.info(f"Nested JSON parse başarılı: {len(result)} soru")
            return result
            
        except Exception as e:
            logger.error(f"Nested JSON parse hatası: {e}")
            return []
    
    def _fallback_parse(self, generated_text: str) -> List[Dict[str, Any]]:
        """Parse başarısız olursa fallback"""
        try:
            # Eski extract_question_data'yı dene
            single_result = extract_question_data(generated_text)
            if single_result.get("success"):
                return [single_result]
        except:
            pass
        
        # Son çare: Boş liste
        logger.error("Fallback parse de başarısız")
        return []
    
    def _parse_all_questions(self, generated_text: str, question_counts: Dict[str, int]) -> Dict[str, List[Dict[str, Any]]]:
        """Tek istekten gelen tüm kategorilerdeki soruları parse et"""
        try:
            # JSON temizleme işlemleri
            cleaned_text = generated_text.strip()
            
            # Markdown code block'larını temizle
            if '```json' in cleaned_text:
                json_match = re.search(r'```json\s*(\{.*?\})\s*```', cleaned_text, re.DOTALL)
                if json_match:
                    cleaned_text = json_match.group(1).strip()
            elif cleaned_text.startswith('```'):
                cleaned_text = cleaned_text.replace('```', '').strip()
            
            # JSON object'in başlangıç ve bitişini kontrol et
            if not cleaned_text.startswith('{'):
                start_idx = cleaned_text.find('{')
                if start_idx != -1:
                    cleaned_text = cleaned_text[start_idx:]
            
            if not cleaned_text.endswith('}'):
                end_idx = cleaned_text.rfind('}')
                if end_idx != -1:
                    cleaned_text = cleaned_text[:end_idx+1]
            
            # JSON parse et
            all_data = json.loads(cleaned_text)
            
            if not isinstance(all_data, dict):
                logger.warning("Yanıt object formatında değil")
                return {}
            
            # Her kategoriyi işle
            result = {}
            for category_code in question_counts.keys():
                if category_code in all_data and isinstance(all_data[category_code], list):
                    category_questions = []
                    for question_data in all_data[category_code]:
                        if isinstance(question_data, dict):
                            # Metadata ekle
                            question_result = {
                                "success": True,
                                "question": question_data.get("question", ""),
                                "expected_answer": question_data.get("expected_answer", ""),
                                "question_type": category_code,
                                "type_name": self._get_category_name(category_code),
                                "role": "",  # Daha sonra doldurulacak
                                "salary_coefficient": 0,  # Daha sonra doldurulacak
                                "difficulty_distribution": {},  # Daha sonra doldurulacak
                                "api_used": "openai",
                                "raw_response": None
                            }
                            category_questions.append(question_result)
                    
                    result[category_code] = category_questions
                    logger.info(f"{category_code} kategorisi parse edildi: {len(category_questions)} soru")
                else:
                    result[category_code] = []
                    logger.warning(f"{category_code} kategorisi bulunamadı veya geçersiz")
            
            total_parsed = sum(len(qs) for qs in result.values())
            logger.info(f"Toplam parse edilen soru sayısı: {total_parsed}")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"All questions JSON parse hatası: {e}")
            return {}
        except Exception as e:
            logger.error(f"All questions parse genel hatası: {e}")
            return {}
    
    def _get_category_name(self, category_code: str) -> str:
        """Kategori kodundan kategori ismini al"""
        category_map = {
            "professional_experience": "Mesleki Deneyim Soruları",
            "theoretical_knowledge": "Teorik Bilgi Soruları", 
            "practical_application": "Pratik Uygulama Soruları"
        }
        return category_map.get(category_code, category_code)
    
    def generate_all_questions_single_request(
        self,
        role_name: str,
        job_context: str,
        description: str,
        salary_coefficient: int,
        question_counts: Dict[str, int]
    ) -> Dict[str, Any]:
        """
        Tek API isteği ile tüm kategorilerde sorular üret (EN VERİMLİ)
        
        Args:
            role_name: Pozisyon ismi
            job_context: İlan bağlamı  
            description: İş tanımı
            salary_coefficient: Maaş katsayısı
            question_counts: {kategori_kodu: soru_sayısı} formatında
            
        Returns:
            dict: Tüm kategorilerdeki sorular
        """
        try:
            # Zorluk dağılımını hesapla
            difficulty_distribution = get_difficulty_distribution_by_multiplier(salary_coefficient)
            
            # Kategori bilgilerini hazırla
            from config.question_categories import get_active_question_categories
            active_categories = get_active_question_categories()
            category_details = []
            total_questions = 0
            
            for category_code, category_name in active_categories:
                count = question_counts.get(category_code, 0)
                if count > 0:
                    category_details.append(f"- {category_name}: {count} adet soru")
                    total_questions += count
            
            categories_text = "\n".join(category_details)
            
            # Özel tek istek prompt'u
            prompt = f"""İlan Başlığı: {job_context}
Pozisyon: {role_name}
Maaş Katsayısı: {salary_coefficient}x
Özel Şartlar: {description}

Bu pozisyon için toplam {total_questions} adet soru üret. Sorular şu kategorilerde dağılsın:

{categories_text}

🚨 KONU ÇEŞİTLİLİĞİ KURALLARI:
Her soru özel şartlarda belirtilen farklı bir konuya odaklanmalıdır. Aynı konu başlığından birden fazla soru oluşturulmamalı, her soru pozisyonun farklı bir teknolojik alanına değinmelidir. {total_questions} adet soru birbirinden tamamen farklı konularda olmalıdır.

Örnek farklı konular: .NET Core, Entity Framework, MSSQL, PostgreSQL, JavaScript frameworks, Git/TFS, IIS, Docker, Redis, Web API, MVC, Agile, DevOps, Testing vb.

Kod yazdırmak kesinlikle yasaktır. Soru içerisinde herhangi bir kod, algoritma, script, fonksiyon isteme ya da kod tamamlama ifadesi olmamalıdır. Adaydan sadece açıklama, analiz, yorum, yaklaşım veya deneyim paylaşımı beklenmelidir.

🎯 SORU KALİTESİ KURALLARI:
Soru doğrudan, açık ve konuya odaklı olmalı; içinde ayrıca 'adayın bilgi vermesi beklenir' gibi tekrar eden ifadeler olmamalıdır. Bu açıklama beklenen cevap kısmında yapılacaktır.

Zorluk Dağılımı ({salary_coefficient}x seviyesi):
- Temel Bilgi (%{difficulty_distribution["K1_Temel_Bilgi"]}): Tanım, kavram açıklama (kod içermez)
- Uygulamalı Bilgi (%{difficulty_distribution["K2_Uygulamali"]}): Konfigürasyon, yöntem, kullanım önerisi (kod içermez)
- Hata Çözümleme (%{difficulty_distribution["K3_Hata_Cozumleme"]}): Log analizi, hata tespiti ve değerlendirme (kod içermez)
- Tasarım (%{difficulty_distribution["K4_Tasarim"]}): Mimari yapı, teknoloji karşılaştırması, ölçeklenebilirlik gibi konular
- Stratejik (%{difficulty_distribution["K5_Stratejik"]}): Süreç iyileştirme, teknoloji seçimi, karar gerekçesi gibi liderlik odaklı sorular

🎯 BEKLENEN CEVAP FORMATI (ÇOK ÖNEMLİ):
Beklenen cevap jüri için bilgilendirici tonda yazılmalı, adayın ağzından değil, gözlemleyen veya değerlendiren kişi diliyle ifade edilmelidir. Şu yapıda olmalıdır:

"Adayın [seçilen konu] hakkında [beklenen bilgi/deneyim] göstermesi beklenir. [Detaylı açıklama ve örnekler]. Ayrıca, [konuyla ilgili spesifik teknik detaylar, kullanım senaryoları, avantaj/dezavantajlar] gibi konularda bilgi vermesi değerlidir."

Beklenen cevap EN AZ 3-4 cümle, tercihen daha uzun olmalıdır. Kısa cevaplar kabul edilmez!

Sonuç şu JSON formatında döndürülmelidir (category_code kullan):

{{
  "professional_experience": [
    {{"question": "Entity Framework ile çalıştığınız projelerde performans optimizasyonu konusunda deneyimlerinizi paylaşır mısınız?", "expected_answer": "Adayın Entity Framework ile performans optimizasyonu konusunda deneyim ve bilgi göstermesi beklenir. Lazy loading, eager loading stratejileri, query optimization teknikleri, N+1 problem çözümleri gibi konularda pratik deneyimlerini açıklaması önemlidir. Ayrıca, profiling araçları kullanımı, cache stratejileri ve database indexing konularında bilgi vermesi değerlidir.\\n\\nAnahtar kelimeler: Entity Framework, performans optimizasyonu, lazy loading, query optimization, N+1 problem"}},
    {{"question": "Büyük ölçekli projelerde veri tabanı tasarımı yaparken hangi faktörleri göz önünde bulundurursunuz?", "expected_answer": "Adayın büyük ölçekli veri tabanı tasarımı konusunda stratejik düşünce yapısını göstermesi beklenir. Normalizasyon vs denormalizasyon kararları, partitioning stratejileri, index planlaması, backup/recovery stratejileri gibi konularda bilgi vermesi önemlidir. Ayrıca, scalability, data integrity, security ve maintenance açısından aldığı önlemleri açıklaması değerlidir.\\n\\nAnahtar kelimeler: veri tabanı tasarımı, normalizasyon, partitioning, scalability, backup stratejileri"}}
  ],
  "theoretical_knowledge": [
    {{"question": "SOLID prensiplerini açıklayın ve yazılım geliştirme sürecindeki önemini belirtin.", "expected_answer": "Adayın SOLID prensiplerinin (Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion) her birini detaylı olarak açıklaması beklenir. Bu prensiplerin yazılım mimarisindeki rolü, kod kalitesine etkisi, maintenance kolaylığı sağlaması gibi avantajları üzerinde durması önemlidir. Ayrıca, gerçek proje örnekleriyle bu prensiplerin nasıl uygulandığını göstermesi değerlidir.\\n\\nAnahtar kelimeler: SOLID prensipleri, yazılım mimarisi, kod kalitesi, maintenance, dependency injection"}},
    {{"question": "Mikroservis mimarisi ile monolitik mimari arasındaki farkları karşılaştırın.", "expected_answer": "Adayın mikroservis ve monolitik mimarilerin avantaj/dezavantajlarını detaylı karşılaştırması beklenir. Scalability, deployment, development süreçleri, data management, network latency, complexity management gibi konularda bilgi vermesi önemlidir. Ayrıca, hangi durumlarda hangi mimarinin tercih edilmesi gerektiği konusunda karar verme kriterlerini açıklaması değerlidir.\\n\\nAnahtar kelimeler: mikroservis mimarisi, monolitik mimari, scalability, deployment, data management"}}
  ],
  "practical_application": [
    {{"question": "Web API geliştirirken güvenlik önlemlerini nasıl sağlarsınız?", "expected_answer": "Adayın Web API güvenliği konusunda pratik bilgi ve deneyim göstermesi beklenir. Authentication/Authorization mekanizmaları, JWT token kullanımı, HTTPS zorunluluğu, input validation, rate limiting, CORS politikaları gibi konularda detaylı bilgi vermesi önemlidir. Ayrıca, API versioning, logging ve monitoring stratejileri konularında da bilgi göstermesi değerlidir.\\n\\nAnahtar kelimeler: Web API güvenliği, authentication, JWT token, input validation, rate limiting"}},
    {{"question": "CI/CD süreçlerini nasıl tasarlayıp uygularsınız?", "expected_answer": "Adayın CI/CD pipeline tasarımı ve implementasyonu konusunda pratik deneyim göstermesi beklenir. Source control integration, automated testing, build processes, deployment strategies (blue-green, rolling, canary), environment management gibi konularda bilgi vermesi önemlidir. Ayrıca, Docker containerization, monitoring ve rollback stratejileri konularında da deneyim paylaşması değerlidir.\\n\\nAnahtar kelimeler: CI/CD, automated testing, deployment strategies, Docker, environment management"}}
  ]
}}"""

            logger.info(f"Tek istek ile {total_questions} soru üretimi başlıyor...")
            
            # OpenAI API'sine istek gönder
            config = get_openai_config()
            response = self.client.chat.completions.create(
                model=config["model"],
                messages=[
                    {"role": "system", "content": SYSTEM_MESSAGE},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=config["max_tokens"],
                temperature=config["temperature"]
            )
            
            generated_text = response.choices[0].message.content.strip()
            logger.info(f"Tek istek yanıtı alındı: {len(generated_text)} karakter")
            
            # JSON parse et (kategoriler halinde)
            all_questions = self._parse_all_questions(generated_text, question_counts)
            
            logger.info(f"Tek istek tamamlandı: {sum(len(qs) for qs in all_questions.values())} soru")
            
            return {
                "success": True,
                "questions": all_questions,
                "total_questions": sum(len(qs) for qs in all_questions.values())
            }
            
        except Exception as e:
            logger.error(f"Tek istek hatası: {e}")
            return {
                "success": False,
                "error": str(e),
                "questions": {}
            }
    
    def generate_questions_category_based(
        self,
        role_name: str,
        job_context: str,
        description: str,
        salary_coefficient: int,
        question_counts: Dict[str, int]
    ) -> Dict[str, Any]:
        """
        Kategori bazlı soru üretimi - En kaliteli sistem (≤15 soru için)
        
        Args:
            role_name: Pozisyon ismi
            job_context: İlan bağlamı  
            description: İş tanımı
            salary_coefficient: Maaş katsayısı
            question_counts: {kategori_kodu: soru_sayısı} formatında
            
        Returns:
            dict: Her kategoriden kaliteli sorular
        """
        try:
            from config.question_categories import get_active_question_categories
            active_categories = get_active_question_categories()
            all_questions = {}
            
            logger.info("KATEGORİ BAZLI sistem başlıyor - her kategori için ayrı API isteği")
            
            for category_code, category_name in active_categories:
                question_count = question_counts.get(category_code, 0)
                
                if question_count <= 0:
                    all_questions[category_code] = []
                    continue
                    
                logger.info(f"{category_name}: {question_count} adet soru üretiliyor...")
                
                # Kategori bazlı batch üretimi
                batch_result = self.generate_questions_batch(
                    role_name=role_name,
                    job_context=job_context,
                    description=description,
                    salary_coefficient=salary_coefficient,
                    question_type=category_code,
                    type_name=category_name,
                    question_count=question_count
                )
                
                if batch_result.get("success", False):
                    all_questions[category_code] = batch_result["questions"]
                    logger.info(f"{category_name} başarılı: {len(batch_result['questions'])} soru")
                else:
                    logger.error(f"{category_name} başarısız!")
                    all_questions[category_code] = []
            
            total_generated = sum(len(qs) for qs in all_questions.values())
            logger.info(f"KATEGORİ BAZLI sistem tamamlandı: {total_generated} soru")
            
            return {
                "success": True,
                "questions": all_questions,
                "total_questions": total_generated
            }
            
        except Exception as e:
            logger.error(f"Kategori bazlı sistem hatası: {e}")
            return {
                "success": False,
                "error": str(e),
                "questions": {}
            }
    
    def generate_questions_chunked(
        self,
        role_name: str,
        job_context: str,
        description: str,
        salary_coefficient: int,
        question_counts: Dict[str, int]
    ) -> Dict[str, Any]:
        """
        Büyük istekler için chunk sistemi (50'şer soru)
        
        Args:
            role_name: Pozisyon ismi
            job_context: İlan bağlamı  
            description: İş tanımı
            salary_coefficient: Maaş katsayısı
            question_counts: {kategori_kodu: soru_sayısı} formatında
            
        Returns:
            dict: Tüm chunk'lardan birleştirilmiş sorular
        """
        try:
            total_questions = sum(question_counts.values())
            chunk_size = 50
            chunks_needed = (total_questions + chunk_size - 1) // chunk_size
            
            logger.info(f"CHUNK SİSTEMİ: {total_questions} soru -> {chunks_needed} chunk ({chunk_size}'şer)")
            
            all_results = {}
            for category_code in question_counts.keys():
                all_results[category_code] = []
            
            # Her chunk için istek at
            for chunk_num in range(chunks_needed):
                start_idx = chunk_num * chunk_size
                remaining = total_questions - start_idx
                current_chunk_size = min(chunk_size, remaining)
                
                logger.info(f"Chunk {chunk_num + 1}/{chunks_needed}: {current_chunk_size} soru")
                
                # Bu chunk için question_counts'u hesapla
                chunk_counts = {}
                remaining_per_category = current_chunk_size
                
                for category_code, total_count in question_counts.items():
                    if remaining_per_category <= 0:
                        chunk_counts[category_code] = 0
                    else:
                        # Orantılı dağılım
                        ratio = total_count / total_questions
                        chunk_count = min(
                            remaining_per_category,
                            max(1, int(current_chunk_size * ratio))
                        )
                        chunk_counts[category_code] = chunk_count
                        remaining_per_category -= chunk_count
                
                # Chunk isteği gönder
                chunk_result = self.generate_all_questions_single_request(
                    role_name=role_name,
                    job_context=job_context,
                    description=description,
                    salary_coefficient=salary_coefficient,
                    question_counts=chunk_counts
                )
                
                # Sonuçları birleştir
                if chunk_result.get("success", False):
                    for category_code, questions_list in chunk_result["questions"].items():
                        all_results[category_code].extend(questions_list)
                    logger.info(f"Chunk {chunk_num + 1} başarılı: {chunk_result.get('total_questions', 0)} soru")
                else:
                    logger.error(f"Chunk {chunk_num + 1} başarısız!")
            
            total_generated = sum(len(qs) for qs in all_results.values())
            logger.info(f"CHUNK SİSTEMİ tamamlandı: {total_generated} soru")
            
            return {
                "success": True,
                "questions": all_results,
                "total_questions": total_generated
            }
            
        except Exception as e:
            logger.error(f"Chunk sistemi hatası: {e}")
            return {
                "success": False,
                "error": str(e),
                "questions": {}
            }
    
    def generate_questions_batch(
        self,
        role_name: str,
        job_context: str,
        description: str,
        salary_coefficient: int,
        question_type: str,
        type_name: str,
        question_count: int
    ) -> Dict[str, Any]:
        """
        Belirli bir kategori için toplu soru üretimi (daha verimli ve çeşitli)
        
        Args:
            role_name: Pozisyon ismi
            job_context: İlan bağlamı  
            description: İş tanımı
            salary_coefficient: Maaş katsayısı
            question_type: Soru kategorisi kodu
            type_name: Soru kategorisi ismi
            question_count: Üretilecek soru sayısı
            
        Returns:
            dict: Üretilen sorular listesi
        """
        try:
            # Zorluk dağılımını hesapla
            difficulty_distribution = get_difficulty_distribution_by_multiplier(salary_coefficient)
            
            # Prompt'u oluştur (Batch template kullan)
            prompt = BATCH_PROMPT_TEMPLATE.format(
                job_context=job_context,
                role_name=role_name,
                salary_coefficient=salary_coefficient,
                description=description,
                type_name=type_name,
                question_count=question_count,
                K1=difficulty_distribution["K1_Temel_Bilgi"],
                K2=difficulty_distribution["K2_Uygulamali"],
                K3=difficulty_distribution["K3_Hata_Cozumleme"],
                K4=difficulty_distribution["K4_Tasarim"],
                K5=difficulty_distribution["K5_Stratejik"]
            )
            
            logger.info(f"{type_name} - {question_count} soru toplu üretimi başlıyor...")
            
            # OpenAI API'sine istek gönder
            config = get_openai_config()
            response = self.client.chat.completions.create(
                model=config["model"],
                messages=[
                    {"role": "system", "content": SYSTEM_MESSAGE},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=config["max_tokens"],
                temperature=config["temperature"]
            )
            
            generated_text = response.choices[0].message.content.strip()
            logger.info(f"OpenAI yanıtı alındı: {len(generated_text)} karakter")
            
            # JSON Array parse et (güçlendirilmiş)
            questions_data = self._parse_questions_array_robust(generated_text)
            
            # Eğer parse başarısız oldu ama content var ise nested parse dene
            if not questions_data and generated_text.strip():
                logger.warning("Normal parse başarısız, nested JSON deneniyor...")
                questions_data = self._try_parse_nested_json(generated_text)
            
            # Son çare: Fallback parse
            if not questions_data:
                logger.error("Tüm parse yöntemleri başarısız, fallback...")
                questions_data = self._fallback_parse(generated_text)
            
            # Her soruya metadata ekle
            for i, question in enumerate(questions_data):
                question.update({
                    "question_type": question_type,
                    "type_name": type_name,
                    "role": role_name,
                    "salary_coefficient": salary_coefficient,
                    "difficulty_distribution": difficulty_distribution,
                    "api_used": "openai",
                    "raw_response": None
                })
            
            logger.info(f"{type_name} kategorisi tamamlandı: {len(questions_data)} soru")
            
            return {
                "success": True,
                "questions": questions_data,
                "category": question_type,
                "total_questions": len(questions_data)
            }
            
        except Exception as e:
            logger.error(f"Batch soru üretim hatası: {e}")
            return {
                "success": False,
                "error": str(e),
                "questions": [],
                "category": question_type
            }

    def generate_questions_for_role(
        self,
        role_name: str,
        job_context: str,
        description: str,
        salary_coefficient: int,
        question_counts: Dict[str, int]
    ) -> Dict[str, Any]:
        """
        Bir rol için tüm kategorilerde sorular üret.
        
        Args:
            role_name: Pozisyon ismi
            job_context: İlan bağlamı
            description: İş tanımı
            salary_coefficient: Maaş katsayısı
            question_counts: {kategori_kodu: soru_sayısı} formatında soru sayıları
            
        Returns:
            dict: Üretilen tüm sorular
        """
        logger.info(f"{role_name} ({salary_coefficient}x) için soru üretimi başlatılıyor")
        
        all_questions = {}
        active_categories = get_active_question_categories()
        
        # TEK API İSTEĞİ ile tüm soruları üret
        total_questions = sum(question_counts.values())
        
        # HER ZAMAN KATEGORİ BAZLI - En kaliteli ve güvenilir sistem
        logger.info(f"KATEGORİ BAZLI sistem: {total_questions} soru -> {len([c for c in question_counts.values() if c > 0])} kategori")
        all_batch_result = self.generate_questions_category_based(
            role_name=role_name,
            job_context=job_context,
            description=description,
            salary_coefficient=salary_coefficient,
            question_counts=question_counts
        )
        
        if all_batch_result.get("success", False):
            all_questions = all_batch_result["questions"]
            
            # Metadata'yı doldur
            difficulty_distribution = get_difficulty_distribution_by_multiplier(salary_coefficient)
            for category_code, questions_list in all_questions.items():
                for question in questions_list:
                    question.update({
                        "role": role_name,
                        "salary_coefficient": salary_coefficient,
                        "difficulty_distribution": difficulty_distribution
                    })
            
            logger.info(f"TEK İSTEK başarılı: {all_batch_result.get('total_questions', 0)} soru")
        else:
            logger.error("TEK İSTEK başarısız, kategori bazlı fallback...")
            # Fallback: Kategori bazlı üretim
            for category_code, category_name in active_categories:
                question_count = question_counts.get(category_code, 0)
                
                if question_count <= 0:
                    continue
                    
                logger.info(f"{category_name} soruları üretiliyor: {question_count} adet (FALLBACK)")
                
                batch_result = self.generate_questions_batch(
                    role_name=role_name,
                    job_context=job_context,
                    description=description,
                    salary_coefficient=salary_coefficient,
                    question_type=category_code,
                    type_name=category_name,
                    question_count=question_count
                )
                
                if batch_result.get("success", False):
                    all_questions[category_code] = batch_result["questions"]
                else:
                    all_questions[category_code] = []
        
        logger.info(f"{role_name} için soru üretimi tamamlandı")
        return {
            "success": True,
            "role": role_name,
            "salary_coefficient": salary_coefficient,
            "questions": all_questions,
            "total_questions": sum(len(questions) for questions in all_questions.values()),
            "api_used": "openai"
        }