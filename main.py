"""
MÜLAKAT SORU HAVUZU - ANA CLI INTERFACE
=======================================

Komut satırı arayüzü ile soru üretimi ve Word export sistemi.
"""

import click
import logging
import sys
from pathlib import Path
from typing import Dict, Any

# Logging konfigürasyonu
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('mulakat_soru_havuzu.log')
    ]
)

logger = logging.getLogger(__name__)

# Import'lar
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from generators.single_generator import SingleGenerator
    from generators.batch_generator import BatchGenerator
    from exporters.word_exporter import WordExporter
    from config.roles_config import get_available_roles, get_role_config
    from config.question_categories import get_active_question_categories
    from core.difficulty_manager import DifficultyManager
    from utils.file_helpers import FileHelper
except ImportError as e:
    logger.error(f"Module import hatası: {e}")
    logger.error("Lütfen tüm bağımlılıkların yüklü olduğundan emin olun.")
    sys.exit(1)

@click.group()
@click.version_option(version='1.0.0', prog_name='Mülakat Soru Havuzu')
def cli():
    """
    Mülakat Soru Havuzu - AI destekli soru üretim sistemi
    
    Her rol için özelleştirilmiş, zorluk seviyesine göre mülakat soruları üretir
    ve profesyonel Word belgeleri oluşturur.
    """
    pass

@cli.command()
@click.option('--role', '-r', required=True, help='Rol kodu (örn: yazilim_gelistirici)')
@click.option('--difficulty', '-d', type=int, required=True, help='Zorluk seviyesi (2x, 3x, 4x)')
@click.option('--count', '-c', type=int, default=20, help='Toplam soru sayısı (varsayılan: 20)')
@click.option('--categories', help='Belirli kategoriler (virgülle ayrılmış)')
@click.option('--job-file', help='İlan metin dosyası yolu')
@click.option('--output-dir', default='data/word_exports', help='Çıktı dizini')
@click.option('--no-word', is_flag=True, help='Word belgesi oluşturma')
@click.option('--preview', is_flag=True, help='Sadece önizleme göster')
def generate(role, difficulty, count, categories, job_file, output_dir, no_word, preview):
    """
    Tek rol için belirli zorluk seviyesinde sorular üret.
    
    Örnek kullanım:
    python main.py generate --role yazilim_gelistirici --difficulty 4 --count 25
    """
    try:
        logger.info(f"Soru üretimi başlatılıyor: {role} - {difficulty}x - {count} soru")
        
        # Single generator başlat
        generator = SingleGenerator()
        
        # Kategori dağılımını belirle
        if categories:
            # Belirli kategoriler
            category_list = [cat.strip() for cat in categories.split(',')]
            questions_per_category = count // len(category_list)
            question_counts = {cat: questions_per_category for cat in category_list}
            
            # Kalan soruları ilk kategoriye ekle
            remaining = count % len(category_list)
            if remaining > 0 and category_list:
                question_counts[category_list[0]] += remaining
        else:
            # Dengeli dağılım
            result = generator.generate_balanced_questions(
                role_code=role,
                salary_coefficient=difficulty,
                total_question_count=count
            )
            
            if preview:
                preview_result = generator.preview_generation_plan(role, difficulty, 
                    {cat: count//3 for cat in ['professional_experience', 'theoretical_knowledge', 'practical_application']})
                _print_preview(preview_result)
                return
            
            if not result.get("success", False):
                click.echo(f"❌ Hata: {result.get('error', 'Bilinmeyen hata')}", err=True)
                return
            
            # Word belgesini oluştur
            if not no_word:
                _export_to_word(result, job_file, output_dir)
            
            _print_generation_summary(result)
            return
        
        # Önizleme modunda
        if preview:
            preview_result = generator.preview_generation_plan(role, difficulty, question_counts)
            _print_preview(preview_result)
            return
        
        # İlan metni
        job_description = None
        if job_file:
            job_description = FileHelper.load_job_description(job_file)
        
        # Soruları üret
        result = generator.generate_questions(
            role_code=role,
            salary_coefficient=difficulty,
            question_counts=question_counts,
            job_description=job_description
        )
        
        if not result.get("success", False):
            click.echo(f"❌ Hata: {result.get('error', 'Bilinmeyen hata')}", err=True)
            return
        
        # Word belgesini oluştur
        if not no_word:
            _export_to_word(result, job_file, output_dir)
        
        _print_generation_summary(result)
        
    except Exception as e:
        logger.error(f"Generate komutu hatası: {e}")
        click.echo(f"❌ Beklenmeyen hata: {e}", err=True)

@cli.command()
@click.option('--role', '-r', required=True, help='Rol kodu')
@click.option('--all-difficulties', is_flag=True, help='Tüm zorluk seviyeleri için üret')
@click.option('--count-per-level', type=int, default=15, help='Her seviye için soru sayısı')
@click.option('--output-dir', default='data/word_exports', help='Çıktı dizini')
@click.option('--job-file', help='İlan metin dosyası yolu')
def batch_generate(role, all_difficulties, count_per_level, output_dir, job_file):
    """
    Tek rol için tüm zorluk seviyelerinde toplu üretim.
    
    Örnek kullanım:
    python main.py batch-generate --role yazilim_gelistirici --all-difficulties --count-per-level 20
    """
    try:
        logger.info(f"Toplu üretim başlatılıyor: {role}")
        
        # Batch generator başlat
        batch_generator = BatchGenerator()
        
        # Soru sayısını kategorilere dağıt
        active_categories = get_active_question_categories()
        questions_per_category = count_per_level // len(active_categories)
        question_counts = {cat[0]: questions_per_category for cat in active_categories}
        
        # İlan metni
        job_description = None
        if job_file:
            job_description = FileHelper.load_job_description(job_file)
        
        # Toplu üretim
        result = batch_generator.generate_for_single_role_all_difficulties(
            role_code=role,
            question_counts=question_counts,
            job_description=job_description
        )
        
        if not result.get("success", False):
            click.echo(f"❌ Hata: {result.get('error', 'Bilinmeyen hata')}", err=True)
            return
        
        # Word belgelerini oluştur
        word_exporter = WordExporter()
        
        role_config = get_role_config(role)
        if not job_description:
            try:
                job_file_path = f"data/job_descriptions/{role_config['job_description_file']}"
                job_description = FileHelper.load_job_description(job_file_path)
            except:
                job_description = f"{role_config['name']} pozisyonu için mülakat soruları"
        
        # Her zorluk seviyesi için Word belgesi oluştur
        exported_files = []
        for single_result in result["results"]:
            if single_result.get("success", False):
                output_path = word_exporter.generate_filename(
                    single_result["role"],
                    single_result["salary_coefficient"],
                    output_dir
                )
                
                if word_exporter.export_questions(single_result, job_description, output_path):
                    exported_files.append(output_path)
        
        _print_batch_summary(result, exported_files)
        
    except Exception as e:
        logger.error(f"Batch generate komutu hatası: {e}")
        click.echo(f"❌ Beklenmeyen hata: {e}", err=True)

@cli.command()
@click.option('--config-file', '-c', required=True, help='Konfigürasyon dosyası yolu')
@click.option('--output-dir', default='data/word_exports', help='Çıktı dizini')
def mass_generate(config_file, output_dir):
    """
    Konfigürasyon dosyasından çoklu rol üretimi.
    
    Örnek kullanım:
    python main.py mass-generate --config-file batch_config.json
    """
    try:
        logger.info(f"Kitlesel üretim başlatılıyor: {config_file}")
        
        batch_generator = BatchGenerator()
        
        # Konfigürasyon dosyasından üret
        result = batch_generator.generate_from_config_file(config_file)
        
        if not result.get("success", False):
            click.echo(f"❌ Hata: {result.get('error', 'Bilinmeyen hata')}", err=True)
            return
        
        # Word belgelerini oluştur
        _export_mass_results_to_word(result["results"], output_dir)
        
        click.echo("✅ Kitlesel üretim tamamlandı!")
        _print_mass_summary(result)
        
    except Exception as e:
        logger.error(f"Mass generate komutu hatası: {e}")
        click.echo(f"❌ Beklenmeyen hata: {e}", err=True)

@cli.command()
def list_roles():
    """Mevcut rolleri listele."""
    try:
        # API key kontrol etmeden direkt config'ten rolleri al
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from config.roles_config import get_available_roles
        
        roles = get_available_roles()
        
        click.echo("\n📋 MEVCUT ROLLER:")
        click.echo("=" * 50)
        
        for role_code, role_name in roles:
            role_config = get_role_config(role_code)
            multipliers = role_config["salary_multipliers"]
            
            click.echo(f"🔹 {role_name}")
            click.echo(f"   Kod: {role_code}")
            click.echo(f"   Zorluk Seviyeleri: {multipliers}")
            click.echo(f"   Özel Şartlar: {role_config['description'][:60]}...")
            click.echo()
            
    except Exception as e:
        logger.error(f"List roles komutu hatası: {e}")
        click.echo(f"❌ Hata: {e}", err=True)

@cli.command()
def list_categories():
    """Soru kategorilerini listele."""
    try:
        categories = get_active_question_categories()
        
        click.echo("\n📂 SORU KATEGORİLERİ:")
        click.echo("=" * 50)
        
        for category_code, category_name in categories:
            click.echo(f"🔸 {category_name} ({category_code})")
        
        click.echo()
        
    except Exception as e:
        logger.error(f"List categories komutu hatası: {e}")
        click.echo(f"❌ Hata: {e}", err=True)

@cli.command()
def check_status():
    """Sistem durumunu kontrol et."""
    try:
        from core.question_generator import QuestionGenerator
        
        click.echo("🔍 SİSTEM DURUM KONTROLÜ")
        click.echo("=" * 50)
        
        # OpenAI API durumu
        generator = QuestionGenerator()
        api_status = generator.check_api_status()
        
        if api_status["api_available"]:
            click.echo("✅ OpenAI API: Bağlantı başarılı")
            click.echo(f"   Model: {api_status['model']}")
        else:
            click.echo("❌ OpenAI API: Bağlantı başarısız")
            click.echo(f"   Hata: {api_status.get('error', 'Bilinmeyen hata')}")
        
        # Dizin kontrolleri
        required_dirs = [
            "data/job_descriptions",
            "data/generated_questions", 
            "data/word_exports"
        ]
        
        click.echo("\n📁 DİZİN KONTROLLERI:")
        for dir_path in required_dirs:
            if Path(dir_path).exists():
                click.echo(f"✅ {dir_path}")
            else:
                click.echo(f"❌ {dir_path} (eksik)")
                Path(dir_path).mkdir(parents=True, exist_ok=True)
                click.echo(f"   📁 Dizin oluşturuldu: {dir_path}")
        
        # İlan dosyaları
        job_files = FileHelper.list_job_description_files("data/job_descriptions")
        click.echo(f"\n📄 İlan Dosyaları: {len(job_files)} adet")
        for job_file in job_files[:3]:  # İlk 3'ünü göster
            click.echo(f"   • {job_file['filename']}")
        
        if len(job_files) > 3:
            click.echo(f"   ... ve {len(job_files) - 3} adet daha")
        
        click.echo("\n✅ Sistem durumu kontrolü tamamlandı!")
        
    except Exception as e:
        logger.error(f"Check status komutu hatası: {e}")
        click.echo(f"❌ Hata: {e}", err=True)

# Yardımcı fonksiyonlar
def _export_to_word(result: Dict[str, Any], job_file: str, output_dir: str):
    """Tek sonucu Word belgesine export et"""
    try:
        word_exporter = WordExporter()
        
        # İlan metnini al
        job_description = ""
        if job_file:
            job_description = FileHelper.load_job_description(job_file)
        else:
            role_code = result.get("role_code")
            if role_code:
                role_config = get_role_config(role_code)
                try:
                    job_file_path = f"data/job_descriptions/{role_config['job_description_file']}"
                    job_description = FileHelper.load_job_description(job_file_path)
                except:
                    job_description = f"{result['role']} pozisyonu için mülakat soruları"
        
        # Dosya yolu oluştur
        output_path = word_exporter.generate_filename(
            result["role"],
            result["salary_coefficient"],
            output_dir
        )
        
        # Export et
        if word_exporter.export_questions(result, job_description, output_path):
            click.echo(f"📄 Word belgesi oluşturuldu: {output_path}")
        else:
            click.echo("❌ Word belgesi oluşturulamadı", err=True)
            
    except Exception as e:
        logger.error(f"Word export hatası: {e}")
        click.echo(f"❌ Word export hatası: {e}", err=True)

def _print_generation_summary(result: Dict[str, Any]):
    """Üretim özetini yazdır"""
    click.echo("\n✅ SORU ÜRETİMİ TAMAMLANDI!")
    click.echo("=" * 50)
    click.echo(f"Rol: {result['role']}")
    click.echo(f"Zorluk: {result['salary_coefficient']}x")
    click.echo(f"Toplam Soru: {result.get('total_questions', 0)}")
    
    questions = result.get("questions", {})
    for category, category_questions in questions.items():
        successful_count = len([q for q in category_questions if q.get("success", False)])
        click.echo(f"  • {category}: {successful_count} soru")
    
    if result.get("json_file"):
        click.echo(f"\n💾 JSON kaydedildi: {result['json_file']}")

def _print_preview(preview_result: Dict[str, Any]):
    """Önizleme sonucunu yazdır"""
    if not preview_result.get("valid", False):
        click.echo(f"❌ Geçersiz konfigürasyon: {preview_result.get('error')}", err=True)
        return
    
    click.echo("\n👁️  ÜRETİM ÖNİZLEMESİ")
    click.echo("=" * 50)
    
    role = preview_result["role"]
    difficulty = preview_result["difficulty"]
    
    click.echo(f"Rol: {role['name']} ({role['code']})")
    click.echo(f"Zorluk: {difficulty['difficulty_label']['label']} - {difficulty['difficulty_label']['name']}")
    click.echo(f"Toplam Soru: {preview_result['total_questions']}")
    click.echo(f"Tahmini API Çağrısı: {preview_result['estimated_api_calls']}")
    
    click.echo("\nKategoriler:")
    for category in preview_result["categories"]:
        click.echo(f"  • {category['name']}: {category['question_count']} soru")
    
    click.echo(f"\nRübrik Dağılımı:")
    for level, percentage in difficulty["distribution"].items():
        click.echo(f"  • {level}: %{percentage}")

def _print_batch_summary(result: Dict[str, Any], exported_files: list):
    """Batch üretim özetini yazdır"""
    click.echo("\n✅ TOPLU ÜRETİM TAMAMLANDI!")
    click.echo("=" * 50)
    click.echo(f"Rol: {result['role']}")
    click.echo(f"Başarılı Seviyeler: {result['successful_difficulties']}/{result['total_difficulties']}")
    
    summary = result.get("summary", {})
    click.echo(f"Toplam Soru: {summary.get('total_questions_generated', 0)}")
    
    click.echo("\n📄 Oluşturulan Word Belgeleri:")
    for file_path in exported_files:
        click.echo(f"  • {file_path}")

def _print_mass_summary(result: Dict[str, Any]):
    """Kitlesel üretim özetini yazdır"""
    click.echo("\n📊 KİTLESEL ÜRETİM ÖZETİ:")
    click.echo("=" * 50)
    
    summary = result.get("summary", {})
    click.echo(f"Başarılı Görevler: {result['successful_tasks']}/{result['total_tasks']}")
    click.echo(f"Toplam Soru: {summary.get('total_questions_generated', 0)}")
    click.echo(f"İşlenen Roller: {summary.get('unique_roles_processed', 0)}")

def _export_mass_results_to_word(results: list, output_dir: str):
    """Kitlesel sonuçları Word'e export et"""
    word_exporter = WordExporter()
    
    for result in results:
        if not result.get("success", False):
            continue
            
        try:
            role_code = result.get("role_code")
            role_config = get_role_config(role_code)
            
            # İlan metnini yükle
            try:
                job_file_path = f"data/job_descriptions/{role_config['job_description_file']}"
                job_description = FileHelper.load_job_description(job_file_path)
            except:
                job_description = f"{result['role']} pozisyonu için mülakat soruları"
            
            # Export et
            output_path = word_exporter.generate_filename(
                result["role"],
                result["salary_coefficient"],
                output_dir
            )
            
            word_exporter.export_questions(result, job_description, output_path)
            
        except Exception as e:
            logger.error(f"Mass export hatası ({result.get('role', 'unknown')}): {e}")

if __name__ == '__main__':
    cli()