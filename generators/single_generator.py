"""
TEKİL SORU ÜRETİMİ
==================

Tek bir rol ve zorluk seviyesi için özelleştirilmiş soru üretim sistemi.
"""

import logging
from typing import Dict, Any, List, Optional

from core.question_generator import QuestionGenerator
from core.difficulty_manager import DifficultyManager
from config.roles_config import get_role_config
from config.question_categories import get_active_question_categories, get_category_config
from utils.file_helpers import FileHelper

logger = logging.getLogger(__name__)

class SingleGenerator:
    """Tekil soru üretim sınıfı"""
    
    def __init__(self):
        """Single generator başlatıcı"""
        self.question_generator = QuestionGenerator()
        self.difficulty_manager = DifficultyManager()
        self.file_helper = FileHelper()
    
    def generate_questions(
        self,
        role_code: str,
        salary_coefficient: int,
        question_counts: Dict[str, int],
        job_description: Optional[str] = None,
        save_json: bool = True
    ) -> Dict[str, Any]:
        """
        Belirtilen rol ve zorluk seviyesi için sorular üret.
        
        Args:
            role_code (str): Rol kodu
            salary_coefficient (int): Maaş katsayısı (zorluk seviyesi)
            question_counts (dict): Her kategori için soru sayıları
            job_description (str, optional): İlan metni (None ise dosyadan yükle)
            save_json (bool): JSON olarak kaydet
            
        Returns:
            dict: Üretim sonuçları
        """
        try:
            # Rol konfigürasyonunu doğrula
            validation_result = self.difficulty_manager.validate_difficulty_requirements(
                role_code, salary_coefficient
            )
            
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": validation_result["error"],
                    "message": validation_result["message"]
                }
            
            # Rol bilgilerini al
            role_config = get_role_config(role_code)
            role_name = role_config["name"]
            description = role_config["description"]
            
            # İlan metnini yükle
            if job_description is None:
                job_file = f"data/job_descriptions/{role_config['job_description_file']}"
                try:
                    job_description = self.file_helper.load_job_description(job_file)
                except FileNotFoundError:
                    logger.warning(f"İlan dosyası bulunamadı: {job_file}. Varsayılan metin kullanılıyor.")
                    job_description = f"{role_name} pozisyonu için mülakat soruları"
            
            logger.info(f"{role_name} ({salary_coefficient}x) için soru üretimi başlatılıyor")
            
            # Soruları üret
            result = self.question_generator.generate_questions_for_role(
                role_name=role_name,
                job_context=job_description,
                description=description,
                salary_coefficient=salary_coefficient,
                question_counts=question_counts
            )
            
            # Ek bilgileri ekle
            if result.get("success", False):
                result["role_code"] = role_code
                result["difficulty_info"] = validation_result["difficulty_info"]
                result["generation_metadata"] = {
                    "question_counts_requested": question_counts,
                    "categories_processed": list(question_counts.keys()),
                    "job_description_length": len(job_description) if job_description else 0
                }
                
                # JSON olarak kaydet
                if save_json:
                    json_filename = f"data/generated_questions/{FileHelper.get_safe_filename(role_name)}_{salary_coefficient}x_questions.json"
                    if self.file_helper.save_questions_json(result, json_filename):
                        result["json_file"] = json_filename
                
                logger.info(f"{role_name} ({salary_coefficient}x) soru üretimi başarıyla tamamlandı")
            else:
                logger.error(f"{role_name} ({salary_coefficient}x) soru üretimi başarısız")
            
            return result
            
        except Exception as e:
            logger.error(f"Tekil soru üretim hatası ({role_code} - {salary_coefficient}x): {e}")
            return {
                "success": False,
                "role_code": role_code,
                "salary_coefficient": salary_coefficient,
                "error": str(e)
            }
    
    def generate_by_category(
        self,
        role_code: str,
        salary_coefficient: int,
        category_code: str,
        question_count: int,
        job_description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Belirli bir kategori için sorular üret.
        
        Args:
            role_code (str): Rol kodu
            salary_coefficient (int): Maaş katsayısı
            category_code (str): Kategori kodu
            question_count (int): Soru sayısı
            job_description (str, optional): İlan metni
            
        Returns:
            dict: Üretim sonuçları
        """
        try:
            # Kategori doğrulaması
            category_config = get_category_config(category_code)
            
            # Sadece bu kategori için soru sayısı belirle
            question_counts = {category_code: question_count}
            
            # Ana üretim fonksiyonunu çağır
            result = self.generate_questions(
                role_code=role_code,
                salary_coefficient=salary_coefficient,
                question_counts=question_counts,
                job_description=job_description,
                save_json=False  # Kategori bazlı üretimde JSON kaydetme
            )
            
            # Sadece ilgili kategoriyi döndür
            if result.get("success", False):
                category_questions = result.get("questions", {}).get(category_code, [])
                
                return {
                    "success": True,
                    "role": result["role"],
                    "role_code": role_code,
                    "salary_coefficient": salary_coefficient,
                    "category": category_config["name"],
                    "category_code": category_code,
                    "questions": category_questions,
                    "question_count": len(category_questions),
                    "difficulty_info": result.get("difficulty_info"),
                    "api_used": result.get("api_used")
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"Kategori bazlı üretim hatası ({role_code} - {category_code}): {e}")
            return {
                "success": False,
                "role_code": role_code,
                "category_code": category_code,
                "error": str(e)
            }
    
    def generate_balanced_questions(
        self,
        role_code: str,
        salary_coefficient: int,
        total_question_count: int,
        job_description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Toplam soru sayısını kategorilere dengeli şekilde dağıtarak üret.
        
        Args:
            role_code (str): Rol kodu
            salary_coefficient (int): Maaş katsayısı
            total_question_count (int): Toplam soru sayısı
            job_description (str, optional): İlan metni
            
        Returns:
            dict: Üretim sonuçları
        """
        try:
            # Aktif kategorileri al
            active_categories = get_active_question_categories()
            category_count = len(active_categories)
            
            if category_count == 0:
                return {
                    "success": False,
                    "error": "Aktif kategori bulunamadı"
                }
            
            # Her kategoriye eşit soru sayısı dağıt
            base_questions_per_category = total_question_count // category_count
            remaining_questions = total_question_count % category_count
            
            question_counts = {}
            
            for i, (category_code, category_name) in enumerate(active_categories):
                # Kalan soruları ilk kategorilere dağıt
                extra_question = 1 if i < remaining_questions else 0
                question_counts[category_code] = base_questions_per_category + extra_question
            
            logger.info(f"Dengeli dağılım: {question_counts}")
            
            # Sorular üret
            return self.generate_questions(
                role_code=role_code,
                salary_coefficient=salary_coefficient,
                question_counts=question_counts,
                job_description=job_description
            )
            
        except Exception as e:
            logger.error(f"Dengeli üretim hatası ({role_code}): {e}")
            return {
                "success": False,
                "role_code": role_code,
                "error": str(e)
            }
    
    def preview_generation_plan(
        self,
        role_code: str,
        salary_coefficient: int,
        question_counts: Dict[str, int]
    ) -> Dict[str, Any]:
        """
        Üretim planını önizle (gerçek üretim yapmadan).
        
        Args:
            role_code (str): Rol kodu
            salary_coefficient (int): Maaş katsayısı
            question_counts (dict): Soru sayıları
            
        Returns:
            dict: Üretim planı bilgileri
        """
        try:
            # Doğrulama
            validation_result = self.difficulty_manager.validate_difficulty_requirements(
                role_code, salary_coefficient
            )
            
            if not validation_result["valid"]:
                return {
                    "valid": False,
                    "error": validation_result["error"]
                }
            
            # Rol bilgileri
            role_config = get_role_config(role_code)
            difficulty_info = validation_result["difficulty_info"]
            
            # Kategori detayları
            category_details = []
            total_questions = 0
            
            for category_code, question_count in question_counts.items():
                if question_count > 0:
                    try:
                        category_config = get_category_config(category_code)
                        category_details.append({
                            "code": category_code,
                            "name": category_config["name"],
                            "description": category_config["description"],
                            "question_count": question_count
                        })
                        total_questions += question_count
                    except KeyError:
                        logger.warning(f"Bilinmeyen kategori: {category_code}")
            
            return {
                "valid": True,
                "role": {
                    "code": role_code,
                    "name": role_config["name"],
                    "description": role_config["description"]
                },
                "difficulty": difficulty_info,
                "categories": category_details,
                "total_questions": total_questions,
                "estimated_api_calls": total_questions,
                "description": role_config["description"]
            }
            
        except Exception as e:
            logger.error(f"Önizleme hatası ({role_code}): {e}")
            return {
                "valid": False,
                "error": str(e)
            }