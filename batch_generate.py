#!/usr/bin/env python3
"""
TOPLU SORU ÜRETİM SCRIPT'İ
==========================

Tüm rolleri tek sayfada göster, kullanıcı soru sayılarını girsin,
tümünü tek seferde üret.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.roles_config import ROLES
from generators.single_generator import SingleGenerator
from core.question_generator import QuestionGenerator
from config.openai_settings import validate_api_key
from exporters.word_exporter import WordExporter
from utils.file_helpers import FileHelper
import logging

# Logging ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def display_header():
    """Başlık göster"""
    print("\n" + "="*60)
    print("🚀 MÜLAKAT SORU HAVUZU - TOPLU ÜRETİM")
    print("="*60)
    print("📋 Tüm roller için istediğin soru sayılarını gir")
    print("💡 0 girersen o rol atlanır")
    print("🎯 Enter'a basınca tümü tek seferde üretilir!")
    print("="*60 + "\n")

def display_roles():
    """Tüm rolleri ve mevcut zorluk seviyelerini göster"""
    print("📝 MEVCUT ROLLER VE ZORLUK SEVİYELERİ:")
    print("-" * 50)
    
    for i, (role_code, role_config) in enumerate(ROLES.items(), 1):
        role_name = role_config["name"]
        multipliers = role_config["salary_multipliers"]
        multipliers_str = ", ".join([f"{m}x" for m in multipliers])
        
        print(f"{i:2d}. {role_name}")
        print(f"    Kod: {role_code}")
        print(f"    Zorluk: {multipliers_str}")
        print(f"    Açıklama: {role_config['description'][:80]}...")
        print()

def get_user_input():
    """Kullanıcıdan soru sayılarını al"""
    print("🎯 HER ROL İÇİN SORU SAYISINI GİR:")
    print("-" * 40)
    
    generation_plan = {}
    
    for role_code, role_config in ROLES.items():
        role_name = role_config["name"]
        multipliers = role_config["salary_multipliers"]
        
        print(f"\n📌 {role_name}")
        
        for multiplier in multipliers:
            while True:
                try:
                    prompt = f"   {multiplier}x zorluk için kaç soru? (0=atla): "
                    count = input(prompt).strip()
                    
                    if count == "":
                        count = "0"
                    
                    count = int(count)
                    
                    if count < 0:
                        print("   ❌ Negatif sayı giremezsin!")
                        continue
                    elif count > 500:
                        print("   ⚠️  500'den fazla soru önerilmez. Devam et? (y/n): ", end="")
                        confirm = input().strip().lower()
                        if confirm not in ['y', 'yes', 'evet', 'e']:
                            continue
                    
                    if count > 0:
                        if role_code not in generation_plan:
                            generation_plan[role_code] = {}
                        generation_plan[role_code][multiplier] = count
                        print(f"   ✅ {count} soru kaydedildi")
                    else:
                        print("   ⏭️  Atlandı")
                    
                    break
                    
                except ValueError:
                    print("   ❌ Lütfen geçerli bir sayı gir!")
                except KeyboardInterrupt:
                    print("\n\n❌ İptal edildi!")
                    sys.exit(0)
    
    return generation_plan

def display_plan(generation_plan):
    """Üretim planını göster"""
    if not generation_plan:
        print("\n❌ Hiç soru seçilmedi!")
        return False
    
    print("\n" + "="*50)
    print("📋 ÜRETİM PLANI")
    print("="*50)
    
    total_questions = 0
    total_api_calls = 0
    
    for role_code, difficulties in generation_plan.items():
        role_name = ROLES[role_code]["name"]
        print(f"\n🎯 {role_name}")
        
        for difficulty, count in difficulties.items():
            print(f"   {difficulty}x: {count} soru")
            total_questions += count
            total_api_calls += 3  # Kategori bazlı sistem - her rol için 3 API isteği
    
    print(f"\n📊 TOPLAM:")
    print(f"   • Soru sayısı: {total_questions}")
    print(f"   • API isteği: {total_api_calls}")
    print(f"   • Tahmini maliyet: ~${total_api_calls * 0.01:.2f}")
    print("="*50)
    
    return True

def calculate_question_distribution(total_count):
    """
    Soru dağılımını hesapla: Mesleki 1x, Teorik 2x, Pratik 2x oranında
    
    Args:
        total_count (int): Toplam soru sayısı
        
    Returns:
        dict: Kategori bazlı soru sayıları
        
    Örnekler:
        15 soru -> 3 mesleki, 6 teorik, 6 pratik
        20 soru -> 4 mesleki, 8 teorik, 8 pratik  
        100 soru -> 20 mesleki, 40 teorik, 40 pratik
    """
    # 1x + 2x + 2x = 5x toplam oran
    base_unit = total_count // 5
    remainder = total_count % 5
    
    professional = base_unit  # 1x
    theoretical = base_unit * 2  # 2x
    practical = base_unit * 2  # 2x
    
    # Kalan soruları dağıt (önce teorik, sonra pratik, son mesleki)
    if remainder >= 1:
        theoretical += 1
        remainder -= 1
    if remainder >= 1:
        practical += 1
        remainder -= 1
    if remainder >= 1:
        professional += 1
        remainder -= 1
    if remainder >= 1:
        theoretical += 1
        remainder -= 1
    if remainder >= 1:
        practical += 1
    
    return {
        "professional_experience": professional,
        "theoretical_knowledge": theoretical,
        "practical_application": practical
    }

def confirm_generation():
    """Üretimi onayla"""
    print("\n🚀 Üretimi başlat? (y/n): ", end="")
    confirm = input().strip().lower()
    return confirm in ['y', 'yes', 'evet', 'e']

def generate_questions(generation_plan):
    """Soruları üret"""
    print("\n" + "="*60)
    print("🚀 SORU ÜRETİMİ BAŞLIYOR...")
    print("="*60 + "\n")
    
    generator = SingleGenerator()
    word_exporter = WordExporter()
    results = []
    
    for role_code, difficulties in generation_plan.items():
        role_name = ROLES[role_code]["name"]
        role_config = ROLES[role_code]
        
        for difficulty, count in difficulties.items():
            print(f"📝 {role_name} ({difficulty}x) - {count} soru üretiliyor...")
            
            try:
                # Soruları üret
                result = generator.generate_questions(
                    role_code=role_code,
                    salary_coefficient=difficulty,
                    question_counts=calculate_question_distribution(count)
                )
                
                if result.get("success", False):
                    print(f"   ✅ JSON: {result.get('total_questions', 0)} soru üretildi")
                    
                    # Word belgesi oluştur
                    try:
                        # İlan metnini yükle
                        job_file_path = f"data/job_descriptions/{role_config['job_description_file']}"
                        job_description = FileHelper.load_job_description(job_file_path)
                        
                        # Word dosyasını oluştur
                        word_filename = word_exporter.generate_filename(
                            role_name, 
                            difficulty,
                            "data/word_exports"
                        )
                        
                        if word_exporter.export_questions(result, job_description, word_filename):
                            print(f"   ✅ Word: {word_filename}")
                            word_file = word_filename
                        else:
                            print(f"   ⚠️  Word oluşturulamadı")
                            word_file = None
                            
                    except Exception as word_error:
                        print(f"   ⚠️  Word hatası: {str(word_error)}")
                        word_file = None
                    
                    results.append({
                        "role": role_name,
                        "difficulty": difficulty,
                        "count": result.get('total_questions', 0),
                        "word_file": word_file,
                        "json_file": result.get('json_file')
                    })
                else:
                    print(f"   ❌ Başarısız: {result.get('error', 'Bilinmeyen hata')}")
                    
            except Exception as e:
                print(f"   ❌ Hata: {str(e)}")
            
            print()
    
    return results

def display_results(results):
    """Sonuçları göster"""
    if not results:
        print("❌ Hiç soru üretilemedi!")
        return
    
    print("="*60)
    print("✅ SORU ÜRETİMİ TAMAMLANDI!")
    print("="*60)
    
    total_questions = sum(r["count"] for r in results)
    
    print(f"\n📊 ÖZET:")
    print(f"   • Toplam {len(results)} farklı rol/zorluk kombinasyonu")
    print(f"   • Toplam {total_questions} soru üretildi")
    
    print(f"\n📄 OLUŞTURULAN DOSYALAR:")
    for result in results:
        print(f"\n🎯 {result['role']} ({result['difficulty']}x) - {result['count']} soru")
        if result.get('word_file'):
            print(f"   📄 Word: {result['word_file']}")
        if result.get('json_file'):
            print(f"   📄 JSON: {result['json_file']}")
    
    print("\n🎉 Tüm dosyalar hazır!")

def main():
    """Ana fonksiyon"""
    try:
        # API key kontrolü
        if not validate_api_key():
            print("❌ OPENAI_API_KEY environment variable tanımlı değil!")
            print("💡 Önce API key'ini ayarla: export OPENAI_API_KEY='your-key'")
            sys.exit(1)
        
        # Header göster
        display_header()
        
        # Rolleri listele
        display_roles()
        
        # Kullanıcı girişi al
        generation_plan = get_user_input()
        
        # Planı göster
        if not display_plan(generation_plan):
            print("👋 Çıkılıyor...")
            sys.exit(0)
        
        # Onay al
        if not confirm_generation():
            print("👋 İptal edildi!")
            sys.exit(0)
        
        # Soruları üret
        results = generate_questions(generation_plan)
        
        # Sonuçları göster
        display_results(results)
        
    except KeyboardInterrupt:
        print("\n\n❌ İptal edildi!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Beklenmeyen hata: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()