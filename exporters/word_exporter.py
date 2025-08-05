"""
WORD BELGESİ EXPORT SİSTEMİ
===========================

Üretilen soruları profesyonel Word belgesine çeviren sistem.
"""

import logging
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

try:
    from docx import Document
    from docx.shared import Inches, Pt
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.style import WD_STYLE_TYPE
    from docx.oxml.shared import OxmlElement, qn
except ImportError:
    raise ImportError("python-docx kütüphanesi yüklü değil. 'pip install python-docx' komutu ile yükleyin.")

from config.rubric_system import DIFFICULTY_LABELS
from utils.file_helpers import FileHelper

logger = logging.getLogger(__name__)

class WordExporter:
    """Word belgesi export sınıfı"""
    
    def __init__(self):
        """Word exporter başlatıcı"""
        self.document = None
    
    def create_document(self) -> Document:
        """Yeni Word belgesi oluştur"""
        self.document = Document()
        self._setup_document_styles()
        return self.document
    
    def _setup_document_styles(self):
        """Belge stillerini ayarla"""
        # Başlık stilleri
        title_style = self.document.styles.add_style('Custom Title', WD_STYLE_TYPE.PARAGRAPH)
        title_style.font.name = 'Arial'
        title_style.font.size = Pt(16)
        title_style.font.bold = True
        title_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        title_style.paragraph_format.space_after = Pt(12)
        
        # Alt başlık stilleri
        subtitle_style = self.document.styles.add_style('Custom Subtitle', WD_STYLE_TYPE.PARAGRAPH)
        subtitle_style.font.name = 'Arial'
        subtitle_style.font.size = Pt(14)
        subtitle_style.font.bold = True
        subtitle_style.paragraph_format.space_before = Pt(12)
        subtitle_style.paragraph_format.space_after = Pt(6)
        
        # Soru stilleri
        question_style = self.document.styles.add_style('Custom Question', WD_STYLE_TYPE.PARAGRAPH)
        question_style.font.name = 'Arial'
        question_style.font.size = Pt(11)
        question_style.font.bold = True
        question_style.paragraph_format.space_before = Pt(8)
        question_style.paragraph_format.space_after = Pt(4)
        
        # Cevap stilleri
        answer_style = self.document.styles.add_style('Custom Answer', WD_STYLE_TYPE.PARAGRAPH)
        answer_style.font.name = 'Arial'
        answer_style.font.size = Pt(10)
        answer_style.paragraph_format.space_after = Pt(8)
        answer_style.paragraph_format.left_indent = Inches(0.25)
    
    def export_questions(
        self,
        questions_data: Dict[str, Any],
        job_description: str,
        output_path: str
    ) -> bool:
        """
        Soruları Word belgesine export et.
        
        Args:
            questions_data (dict): Soru verileri
            job_description (str): İlan metni
            output_path (str): Çıktı dosyası yolu
            
        Returns:
            bool: Başarı durumu
        """
        try:
            # Yeni belge oluştur
            self.create_document()
            
            # Belge başlığını ekle
            self._add_document_header(questions_data)
            
            # Soruları ekle
            self._add_questions_sections(questions_data)
            
            # Dosyayı kaydet
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            self.document.save(str(output_file))
            logger.info(f"Word belgesi başarıyla kaydedildi: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Word export hatası: {e}")
            return False
    
    def _add_document_header(self, questions_data: Dict[str, Any]):
        """Belge başlığını ekle"""
        role = questions_data.get("role", "Bilinmeyen Pozisyon")
        salary_coefficient = questions_data.get("salary_coefficient", 2)
        
        # Ana başlık - katsayı bilgisiyle
        title = f"{role.upper()} {salary_coefficient}x MÜLAKAT SORULARI"
        title_para = self.document.add_paragraph(title, style='Custom Title')
        
        # Tarih
        date_para = self.document.add_paragraph(f"Oluşturulma Tarihi: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
        date_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        self.document.add_paragraph()  # Boş satır
    
    def _add_job_description_section(self, job_description: str):
        """İlan bilgileri bölümünü ekle"""
        self.document.add_paragraph("İlan Bilgileri", style='Custom Subtitle')
        self.document.add_paragraph("-" * 50)
        
        # İlan metnini paragraf paragraf ekle
        for paragraph in job_description.split('\n'):
            if paragraph.strip():
                self.document.add_paragraph(paragraph.strip())
        
        self.document.add_paragraph()  # Boş satır
    
    def _add_rubric_distribution_section(self, questions_data: Dict[str, Any]):
        """Rübrik dağılımı bölümünü ekle"""
        salary_coefficient = questions_data.get("salary_coefficient", 2)
        
        # İlk sorudan difficulty_distribution'ı al
        difficulty_distribution = None
        for category_questions in questions_data.get("questions", {}).values():
            if category_questions and len(category_questions) > 0:
                difficulty_distribution = category_questions[0].get("difficulty_distribution")
                break
        
        if not difficulty_distribution:
            return
        
        difficulty_label = DIFFICULTY_LABELS.get(salary_coefficient, {"label": f"{salary_coefficient}x"})
        
        self.document.add_paragraph(f"Rübrik Dağılımı ({difficulty_label['label']} Seviye)", style='Custom Subtitle')
        self.document.add_paragraph("-" * 50)
        
        # Rübrik seviyelerini listele
        rubric_mapping = {
            "K1_Temel_Bilgi": "K1 - Temel Bilgi",
            "K2_Uygulamali": "K2 - Uygulamalı",
            "K3_Hata_Cozumleme": "K3 - Hata Çözümleme",
            "K4_Tasarim": "K4 - Tasarım",
            "K5_Stratejik": "K5 - Stratejik"
        }
        
        for level, percentage in difficulty_distribution.items():
            level_name = rubric_mapping.get(level, level)
            self.document.add_paragraph(f"• {level_name}: %{percentage}")
        
        self.document.add_paragraph()  # Boş satır
    
    def _add_questions_sections(self, questions_data: Dict[str, Any]):
        """Soru bölümlerini ekle"""
        questions = questions_data.get("questions", {})
        
        category_names = {
            "professional_experience": "Mesleki Deneyim Soruları",
            "theoretical_knowledge": "Teorik Bilgi Soruları",
            "practical_application": "Pratik Uygulama Soruları"
        }
        
        for category_code, category_questions in questions.items():
            if not category_questions:
                continue
            
            category_name = category_names.get(category_code, category_code.replace("_", " ").title())
            question_count = len([q for q in category_questions if q.get("success", False)])
            
            # Kategori başlığı
            section_title = f"{category_name} ({question_count} Soru)"
            self.document.add_paragraph(section_title, style='Custom Subtitle')
            self.document.add_paragraph("-" * len(section_title))
            
            # Her soruyu ekle
            for i, question_data in enumerate(category_questions, 1):
                if not question_data.get("success", False):
                    continue
                
                self._add_single_question(i, question_data)
            
            self.document.add_paragraph()  # Kategori arası boşluk
    
    def _add_single_question(self, question_number: int, question_data: Dict[str, Any]):
        """Tek bir soruyu ekle"""
        question_text = question_data.get("question", "Soru metni eksik")
        expected_answer = question_data.get("expected_answer", "Beklenen cevap eksik")
        
        # Soru başlığı ve metni
        question_para = self.document.add_paragraph(f"{question_number}. {question_text}", style='Custom Question')
        
        # Beklenen cevap
        if expected_answer:
            answer_para = self.document.add_paragraph(f"Beklenen Cevap: {expected_answer}", style='Custom Answer')
        
        self.document.add_paragraph()  # Soru arası boşluk
    
    def _add_document_footer(self):
        """Belge alt bilgisini ekle"""
        self.document.add_paragraph()
        self.document.add_paragraph("-" * 80)
        
        footer_para = self.document.add_paragraph("Bu belge Mülakat Soru Havuzu sistemi tarafından otomatik olarak üretilmiştir.")
        footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        footer_para.italic = True
    
    def generate_filename(
        self,
        role_name: str,
        salary_coefficient: int,
        base_dir: str = "data/word_exports"
    ) -> str:
        """
        Dosya ismi oluştur.
        
        Args:
            role_name (str): Pozisyon ismi
            salary_coefficient (int): Maaş katsayısı
            base_dir (str): Ana dizin
            
        Returns:
            str: Tam dosya yolu
        """
        # Güvenli dosya ismi oluştur - katsayı bilgisiyle
        safe_role_name = FileHelper.get_safe_filename(role_name)
        
        filename = f"{safe_role_name}_{salary_coefficient}x.docx"
        
        return str(Path(base_dir) / filename)
    
    def export_multiple_roles(
        self,
        multiple_questions_data: List[Dict[str, Any]],
        job_descriptions: Dict[str, str],
        output_dir: str = "data/word_exports"
    ) -> Dict[str, Any]:
        """
        Birden fazla rol için Word belgeleri oluştur.
        
        Args:
            multiple_questions_data (list): Çoklu soru verileri
            job_descriptions (dict): İlan metinleri
            output_dir (str): Çıktı dizini
            
        Returns:
            dict: Export sonuçları
        """
        results = {
            "success": True,
            "exported_files": [],
            "failed_exports": []
        }
        
        for questions_data in multiple_questions_data:
            try:
                role = questions_data.get("role", "unknown")
                salary_coefficient = questions_data.get("salary_coefficient", 2)
                
                # Dosya yolu oluştur
                output_path = self.generate_filename(role, salary_coefficient, output_dir)
                
                # İlan metnini al
                job_description = job_descriptions.get(role, f"{role} pozisyonu için iş tanımı")
                
                # Export et
                export_success = self.export_questions(questions_data, job_description, output_path)
                
                if export_success:
                    results["exported_files"].append({
                        "role": role,
                        "salary_coefficient": salary_coefficient,
                        "file_path": output_path
                    })
                else:
                    results["failed_exports"].append({
                        "role": role,
                        "salary_coefficient": salary_coefficient,
                        "error": "Export işlemi başarısız"
                    })
                    
            except Exception as e:
                logger.error(f"Çoklu export hatası: {e}")
                results["failed_exports"].append({
                    "role": questions_data.get("role", "unknown"),
                    "error": str(e)
                })
        
        # Genel başarı durumu
        if results["failed_exports"]:
            results["success"] = False
        
        logger.info(f"Çoklu export tamamlandı: {len(results['exported_files'])} başarılı, {len(results['failed_exports'])} başarısız")
        return results