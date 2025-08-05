"""
TOPLU SORU ÜRETİMİ
=================

Birden fazla rol ve zorluk seviyesi için toplu soru üretim sistemi.
"""

import logging
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

from core.question_generator import QuestionGenerator
from core.difficulty_manager import DifficultyManager
from config.roles_config import get_role_config, get_available_roles
from utils.file_helpers import FileHelper

logger = logging.getLogger(__name__)

class BatchGenerator:
    """Toplu soru üretim sınıfı"""
    
    def __init__(self):
        """Batch generator başlatıcı"""
        self.question_generator = QuestionGenerator()
        self.file_helper = FileHelper()
    
    def generate_for_single_role_all_difficulties(
        self,
        role_code: str,
        question_counts: Dict[str, int],
        job_description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Tek rol için tüm zorluk seviyelerinde sorular üret.
        
        Args:
            role_code (str): Rol kodu
            question_counts (dict): Her kategori için soru sayıları
            job_description (str, optional): İlan metni (None ise dosyadan yükle)
            
        Returns:
            dict: Üretim sonuçları
        """
        try:
            # Rol konfigürasyonunu al
            role_config = get_role_config(role_code)
            role_name = role_config["name"]
            salary_multipliers = role_config["salary_multipliers"]
            description = role_config["description"]
            
            # İlan metnini yükle
            if job_description is None:
                job_file = f"data/job_descriptions/{role_config['job_description_file']}"
                job_description = self.file_helper.load_job_description(job_file)
            
            logger.info(f"{role_name} için tüm zorluk seviyelerinde soru üretimi başlatılıyor")
            
            all_results = []
            
            # Her zorluk seviyesi için soru üret
            for salary_coefficient in salary_multipliers:
                logger.info(f"{role_name} - {salary_coefficient}x seviyesi işleniyor")
                
                result = self.question_generator.generate_questions_for_role(
                    role_name=role_name,
                    job_context=job_description,
                    description=description,
                    salary_coefficient=salary_coefficient,
                    question_counts=question_counts
                )
                
                if result.get("success", False):
                    # JSON olarak kaydet
                    json_filename = f"data/generated_questions/{FileHelper.get_safe_filename(role_name)}_{salary_coefficient}x_questions.json"
                    self.file_helper.save_questions_json(result, json_filename)
                    result["json_file"] = json_filename
                
                all_results.append(result)
            
            # Toplu sonuç
            successful_results = [r for r in all_results if r.get("success", False)]
            
            return {
                "success": len(successful_results) > 0,
                "role": role_name,
                "role_code": role_code,
                "total_difficulties": len(salary_multipliers),
                "successful_difficulties": len(successful_results),
                "results": all_results,
                "summary": self._generate_batch_summary(all_results)
            }
            
        except Exception as e:
            logger.error(f"Toplu üretim hatası ({role_code}): {e}")
            return {
                "success": False,
                "role_code": role_code,
                "error": str(e)
            }
    
    def generate_for_multiple_roles(
        self,
        role_configs: List[Dict[str, Any]],
        max_workers: int = 3
    ) -> Dict[str, Any]:
        """
        Birden fazla rol için paralel soru üretimi.
        
        Args:
            role_configs (list): Rol konfigürasyonları
                Format: [{"role_code": str, "question_counts": dict, "salary_coefficients": list}]
            max_workers (int): Maksimum paralel işçi sayısı
            
        Returns:
            dict: Toplu üretim sonuçları
        """
        logger.info(f"{len(role_configs)} rol için paralel soru üretimi başlatılıyor")
        
        all_results = []
        
        # Paralel işleme için ThreadPoolExecutor kullan
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Her rol için future oluştur
            future_to_role = {}
            
            for role_config in role_configs:
                role_code = role_config["role_code"]
                question_counts = role_config["question_counts"]
                salary_coefficients = role_config.get("salary_coefficients", [2, 3, 4])
                
                # Her zorluk seviyesi için ayrı future
                for salary_coefficient in salary_coefficients:
                    future = executor.submit(
                        self._generate_single_role_difficulty,
                        role_code,
                        salary_coefficient,
                        question_counts
                    )
                    future_to_role[future] = (role_code, salary_coefficient)
            
            # Sonuçları topla
            for future in as_completed(future_to_role):
                role_code, salary_coefficient = future_to_role[future]
                
                try:
                    result = future.result()
                    all_results.append(result)
                    
                    if result.get("success", False):
                        logger.info(f"✅ {role_code} - {salary_coefficient}x tamamlandı")
                    else:
                        logger.warning(f"❌ {role_code} - {salary_coefficient}x başarısız")
                        
                except Exception as e:
                    logger.error(f"Paralel işlem hatası ({role_code} - {salary_coefficient}x): {e}")
                    all_results.append({
                        "success": False,
                        "role_code": role_code,
                        "salary_coefficient": salary_coefficient,
                        "error": str(e)
                    })
        
        # Genel sonuç özeti
        successful_results = [r for r in all_results if r.get("success", False)]
        
        return {
            "success": len(successful_results) > 0,
            "total_tasks": len(all_results),
            "successful_tasks": len(successful_results),
            "failed_tasks": len(all_results) - len(successful_results),
            "results": all_results,
            "summary": self._generate_multi_role_summary(all_results)
        }
    
    def _generate_single_role_difficulty(
        self,
        role_code: str,
        salary_coefficient: int,
        question_counts: Dict[str, int]
    ) -> Dict[str, Any]:
        """Tek rol ve tek zorluk seviyesi için soru üret (paralel işlem için)"""
        try:
            # Rol konfigürasyonunu al
            role_config = get_role_config(role_code)
            role_name = role_config["name"]
            description = role_config["description"]
            
            # İlan metnini yükle
            job_file = f"data/job_descriptions/{role_config['job_description_file']}"
            job_description = self.file_helper.load_job_description(job_file)
            
            # Soru üret
            result = self.question_generator.generate_questions_for_role(
                role_name=role_name,
                job_context=job_description,
                description=description,
                salary_coefficient=salary_coefficient,
                question_counts=question_counts
            )
            
            # JSON olarak kaydet
            if result.get("success", False):
                json_filename = f"data/generated_questions/{FileHelper.get_safe_filename(role_name)}_{salary_coefficient}x_questions.json"
                self.file_helper.save_questions_json(result, json_filename)
                result["json_file"] = json_filename
            
            return result
            
        except Exception as e:
            logger.error(f"Tekil üretim hatası ({role_code} - {salary_coefficient}x): {e}")
            return {
                "success": False,
                "role_code": role_code,
                "salary_coefficient": salary_coefficient,
                "error": str(e)
            }
    
    def generate_from_config_file(self, config_file_path: str) -> Dict[str, Any]:
        """
        Konfigürasyon dosyasından toplu üretim yap.
        
        Args:
            config_file_path (str): Konfigürasyon dosyası yolu
            
        Returns:
            dict: Üretim sonuçları
        """
        try:
            # Konfigürasyon dosyasını yükle
            config_data = self.file_helper.load_questions_json(config_file_path)
            
            if not config_data:
                raise ValueError(f"Konfigürasyon dosyası yüklenemedi: {config_file_path}")
            
            # Konfigürasyonu validate et
            required_fields = ["roles", "default_question_counts"]
            for field in required_fields:
                if field not in config_data:
                    raise ValueError(f"Konfigürasyon dosyasında eksik alan: {field}")
            
            # Rol konfigürasyonlarını hazırla
            role_configs = []
            default_counts = config_data["default_question_counts"]
            
            for role_info in config_data["roles"]:
                role_code = role_info["role_code"]
                question_counts = role_info.get("question_counts", default_counts)
                salary_coefficients = role_info.get("salary_coefficients", [2, 3, 4])
                
                role_configs.append({
                    "role_code": role_code,
                    "question_counts": question_counts,
                    "salary_coefficients": salary_coefficients
                })
            
            # Paralel işlem ayarları
            max_workers = config_data.get("max_workers", 3)
            
            # Toplu üretimi başlat
            return self.generate_for_multiple_roles(role_configs, max_workers)
            
        except Exception as e:
            logger.error(f"Konfigürasyon dosyasından üretim hatası: {e}")
            return {
                "success": False,
                "error": str(e),
                "config_file": config_file_path
            }
    
    def _generate_batch_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Tek rol için batch özeti oluştur"""
        total_questions = 0
        successful_levels = 0
        
        for result in results:
            if result.get("success", False):
                successful_levels += 1
                total_questions += result.get("total_questions", 0)
        
        return {
            "total_difficulty_levels": len(results),
            "successful_levels": successful_levels,
            "total_questions_generated": total_questions,
            "average_questions_per_level": total_questions / max(successful_levels, 1)
        }
    
    def _generate_multi_role_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Çoklu rol için batch özeti oluştur"""
        role_stats = {}
        total_questions = 0
        
        for result in results:
            role_code = result.get("role_code", "unknown")
            salary_coefficient = result.get("salary_coefficient", 0)
            
            if role_code not in role_stats:
                role_stats[role_code] = {"successful": 0, "failed": 0, "questions": 0}
            
            if result.get("success", False):
                role_stats[role_code]["successful"] += 1
                role_stats[role_code]["questions"] += result.get("total_questions", 0)
                total_questions += result.get("total_questions", 0)
            else:
                role_stats[role_code]["failed"] += 1
        
        return {
            "role_statistics": role_stats,
            "total_questions_generated": total_questions,
            "unique_roles_processed": len(role_stats),
            "overall_success_rate": len([r for r in results if r.get("success", False)]) / max(len(results), 1)
        }