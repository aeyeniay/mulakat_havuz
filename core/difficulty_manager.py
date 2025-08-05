"""
ZORLUK SEVİYESİ YÖNETİCİSİ
========================

Maaş katsayıları ve rübrik sistemine dayalı zorluk seviyesi yönetimi.
"""

from typing import Dict, List, Any
from config.rubric_system import (
    get_difficulty_distribution_by_multiplier,
    RUBRIC_LEVELS,
    DIFFICULTY_LABELS
)

class DifficultyManager:
    """Zorluk seviyesi yönetim sınıfı"""
    
    @staticmethod
    def get_difficulty_info(salary_coefficient: int) -> Dict[str, Any]:
        """
        Maaş katsayısına göre zorluk bilgilerini döndür.
        
        Args:
            salary_coefficient (int): Maaş katsayısı (2, 3, 4, 5+)
            
        Returns:
            dict: Zorluk seviyesi bilgileri
        """
        # Zorluk dağılımını al
        distribution = get_difficulty_distribution_by_multiplier(salary_coefficient)
        
        # Seviye etiketini al
        difficulty_label = DIFFICULTY_LABELS.get(
            salary_coefficient, 
            {"name": "Expert", "label": f"{salary_coefficient}x", "description": "Uzman seviye"}
        )
        
        return {
            "salary_coefficient": salary_coefficient,
            "difficulty_label": difficulty_label,
            "distribution": distribution,
            "primary_focus": DifficultyManager._get_primary_focus(distribution),
            "total_percentage": sum(distribution.values())
        }
    
    @staticmethod
    def _get_primary_focus(distribution: Dict[str, int]) -> str:
        """
        Dağılımda en yüksek ağırlığa sahip rübrik seviyesini bul.
        
        Args:
            distribution (dict): Rübrik dağılımı
            
        Returns:
            str: En yüksek ağırlığa sahip seviye
        """
        max_level = max(distribution, key=distribution.get)
        return RUBRIC_LEVELS[max_level]["name"]
    
    @staticmethod
    def calculate_question_distribution(
        total_questions: int, 
        salary_coefficient: int
    ) -> Dict[str, int]:
        """
        Toplam soru sayısını rübrik seviyelerine göre dağıt.
        
        Args:
            total_questions (int): Toplam soru sayısı
            salary_coefficient (int): Maaş katsayısı
            
        Returns:
            dict: Her rübrik seviyesi için soru sayısı
        """
        distribution = get_difficulty_distribution_by_multiplier(salary_coefficient)
        question_counts = {}
        
        # Yüzdelik dağılımı soru sayısına çevir
        for level, percentage in distribution.items():
            question_count = round((percentage / 100) * total_questions)
            question_counts[level] = question_count
        
        # Yuvarlama hatalarını düzelt
        total_assigned = sum(question_counts.values())
        difference = total_questions - total_assigned
        
        if difference != 0:
            # En yüksek yüzdeye sahip seviyeye farkı ekle/çıkar
            max_level = max(distribution, key=distribution.get)
            question_counts[max_level] += difference
        
        return question_counts
    
    @staticmethod
    def validate_difficulty_requirements(
        role_code: str, 
        salary_coefficient: int
    ) -> Dict[str, Any]:
        """
        Rol ve zorluk seviyesi kombinasyonunu doğrula.
        
        Args:
            role_code (str): Rol kodu
            salary_coefficient (int): Maaş katsayısı
            
        Returns:
            dict: Doğrulama sonucu
        """
        try:
            from config.roles_config import validate_role_config
            
            is_valid = validate_role_config(role_code, salary_coefficient)
            
            if is_valid:
                difficulty_info = DifficultyManager.get_difficulty_info(salary_coefficient)
                return {
                    "valid": True,
                    "difficulty_info": difficulty_info,
                    "message": f"Geçerli kombinasyon: {role_code} - {salary_coefficient}x"
                }
            else:
                return {
                    "valid": False,
                    "error": f"Geçersiz kombinasyon: {role_code} - {salary_coefficient}x",
                    "message": "Bu rol için belirtilen maaş katsayısı desteklenmiyor"
                }
                
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "message": "Doğrulama sırasında hata oluştu"
            }
    
    @staticmethod
    def get_rubric_explanation() -> Dict[str, Any]:
        """
        Rübrik sisteminin açıklamasını döndür.
        
        Returns:
            dict: Rübrik açıklamaları
        """
        return {
            "system_name": "K1-K5 Rübrik Modeli",
            "description": "Bilişsel seviye tabanlı soru değerlendirme sistemi",
            "levels": RUBRIC_LEVELS,
            "difficulty_labels": DIFFICULTY_LABELS,
            "usage": "Maaş katsayısına göre otomatik zorluk dağılımı"
        }
    
    @staticmethod
    def get_all_difficulty_levels() -> List[Dict[str, Any]]:
        """
        Tüm zorluk seviyelerinin listesini döndür.
        
        Returns:
            list: Zorluk seviyesi bilgileri
        """
        levels = []
        
        for coefficient in sorted(DIFFICULTY_LABELS.keys()):
            difficulty_info = DifficultyManager.get_difficulty_info(coefficient)
            levels.append(difficulty_info)
        
        return levels