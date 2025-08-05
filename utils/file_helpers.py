"""
DOSYA YARDIMCI FONKSİYONLARI
===========================

İlan metinleri, JSON veriler ve diğer dosya işlemleri için yardımcı fonksiyonlar.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class FileHelper:
    """Dosya işlemleri yardımcı sınıfı"""
    
    @staticmethod
    def load_job_description(job_file_path: str) -> str:
        """
        İlan metni dosyasını yükle.
        
        Args:
            job_file_path (str): İlan dosyası yolu
            
        Returns:
            str: İlan metni
            
        Raises:
            FileNotFoundError: Dosya bulunamadığında
            UnicodeDecodeError: Dosya okunamadığında
        """
        try:
            file_path = Path(job_file_path)
            
            if not file_path.exists():
                raise FileNotFoundError(f"İlan dosyası bulunamadı: {job_file_path}")
            
            # UTF-8 ile okumayı dene
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
            except UnicodeDecodeError:
                # UTF-8 başarısızsa latin-1 ile dene
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read().strip()
            
            if not content:
                raise ValueError(f"İlan dosyası boş: {job_file_path}")
            
            logger.info(f"İlan dosyası başarıyla yüklendi: {job_file_path}")
            return content
            
        except Exception as e:
            logger.error(f"İlan dosyası yükleme hatası: {e}")
            raise
    
    @staticmethod
    def save_questions_json(
        questions_data: Dict[str, Any], 
        output_path: str
    ) -> bool:
        """
        Üretilen soruları JSON formatında kaydet.
        
        Args:
            questions_data (dict): Soru verileri
            output_path (str): Çıktı dosyası yolu
            
        Returns:
            bool: Başarı durumu
        """
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(questions_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Sorular JSON olarak kaydedildi: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"JSON kaydetme hatası: {e}")
            return False
    
    @staticmethod
    def load_questions_json(json_path: str) -> Optional[Dict[str, Any]]:
        """
        JSON dosyasından soruları yükle.
        
        Args:
            json_path (str): JSON dosyası yolu
            
        Returns:
            dict: Yüklenen soru verileri (başarısızsa None)
        """
        try:
            json_file = Path(json_path)
            
            if not json_file.exists():
                logger.warning(f"JSON dosyası bulunamadı: {json_path}")
                return None
            
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"JSON dosyası başarıyla yüklendi: {json_path}")
            return data
            
        except Exception as e:
            logger.error(f"JSON yükleme hatası: {e}")
            return None
    
    @staticmethod
    def ensure_directory(dir_path: str) -> bool:
        """
        Dizinin var olduğundan emin ol, yoksa oluştur.
        
        Args:
            dir_path (str): Dizin yolu
            
        Returns:
            bool: Başarı durumu
        """
        try:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"Dizin oluşturma hatası ({dir_path}): {e}")
            return False
    
    @staticmethod
    def get_safe_filename(filename: str) -> str:
        """
        Dosya ismi için güvenli karakter dönüşümü yap.
        
        Args:
            filename (str): Orijinal dosya ismi
            
        Returns:
            str: Güvenli dosya ismi
        """
        # Türkçe karakterleri çevir
        tr_chars = {
            'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u',
            'Ç': 'C', 'Ğ': 'G', 'İ': 'I', 'Ö': 'O', 'Ş': 'S', 'Ü': 'U'
        }
        
        safe_name = filename
        for tr_char, safe_char in tr_chars.items():
            safe_name = safe_name.replace(tr_char, safe_char)
        
        # Diğer özel karakterleri temizle
        safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
        safe_name = ''.join(c if c in safe_chars else '_' for c in safe_name)
        
        # Çoklu alt çizgileri tek yap
        while '__' in safe_name:
            safe_name = safe_name.replace('__', '_')
        
        return safe_name.strip('_')
    
    @staticmethod
    def list_job_description_files(job_descriptions_dir: str) -> list:
        """
        İlan dosyalarını listele.
        
        Args:
            job_descriptions_dir (str): İlan dosyaları dizini
            
        Returns:
            list: İlan dosyalarının listesi
        """
        try:
            job_dir = Path(job_descriptions_dir)
            
            if not job_dir.exists():
                logger.warning(f"İlan dizini bulunamadı: {job_descriptions_dir}")
                return []
            
            job_files = []
            for file_path in job_dir.glob("*.txt"):
                job_files.append({
                    "filename": file_path.name,
                    "path": str(file_path),
                    "size": file_path.stat().st_size,
                    "role_code": file_path.stem.replace("_ilan", "")
                })
            
            logger.info(f"İlan dosyaları listelendi: {len(job_files)} dosya")
            return sorted(job_files, key=lambda x: x["filename"])
            
        except Exception as e:
            logger.error(f"İlan dosyaları listeleme hatası: {e}")
            return []