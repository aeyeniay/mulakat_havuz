"""
RÜBRİK SİSTEMİ - K1-K5 MODELİ VE ZORLUK KATSAYILARI
==================================================

Mevcut projeden taşınan rübrik sistemi.
K1-K5 bilişsel seviye modeli ve maaş katsayısına göre zorluk dağılımları.
"""

def get_difficulty_distribution_by_multiplier(salary_multiplier):
    """
    Maaş katsayısına göre güncellenmiş zorluk dağılımı hesapla
    
    Args:
        salary_multiplier (int): Maaş katsayısı (2x, 3x, 4x, 5x+)
        
    Returns:
        dict: K1-K5 rübrik dağılım yüzdeleri
    """
    if salary_multiplier <= 2:  # 2x – Uzman (Junior)
        return {
            "K1_Temel_Bilgi": 45,      # Tanım, kavram (yüksek)
            "K2_Uygulamali": 40,       # Uygulama örneği (yüksek)
            "K3_Hata_Cozumleme": 10,   # Az hata tespiti
            "K4_Tasarim": 5,           # Sınırlı mimari
            "K5_Stratejik": 0          # YOK
        }
    elif salary_multiplier <= 3:  # 3x – Kıdemli Uzman (Mid)
        return {
            "K1_Temel_Bilgi": 20,      # Kavramlar
            "K2_Uygulamali": 25,       # Uygulama mantığı
            "K3_Hata_Cozumleme": 35,   # Log analizi, hata çözümü
            "K4_Tasarim": 20,          # Mimarî karşılaştırma
            "K5_Stratejik": 0          # Henüz yok
        }
    elif salary_multiplier <= 4:  # 4x – Takım Lideri (Senior)
        return {
            "K1_Temel_Bilgi": 5,       # Temel bilgi çok az
            "K2_Uygulamali": 15,       # Stratejik uygulama
            "K3_Hata_Cozumleme": 25,   # Derinlemesine analiz
            "K4_Tasarim": 35,          # Mimarî kararlar
            "K5_Stratejik": 20         # Liderlik, süreç kararı
        }
    else:  # 5x+ – Stratejik Liderlik
        return {
            "K1_Temel_Bilgi": 5,       # Minimal
            "K2_Uygulamali": 10,       # Üst seviye uygulama
            "K3_Hata_Cozumleme": 20,   # Enterprise düzey hata çözüm
            "K4_Tasarim": 30,          # Büyük ölçekli mimari
            "K5_Stratejik": 35         # Roadmap, stratejik kararlar
        }

# Rübrik seviyeleri tanımları
RUBRIC_LEVELS = {
    "K1_Temel_Bilgi": {
        "name": "Temel Bilgi",
        "description": "Tanım, kavram açıklama (kod içermez)",
        "focus": ["temel_kavramlar", "definisyonlar", "terminoloji"]
    },
    "K2_Uygulamali": {
        "name": "Uygulamalı Bilgi", 
        "description": "Konfigürasyon, yöntem, kullanım önerisi (kod içermez)",
        "focus": ["konfigurasyon", "metodoloji", "uygulama_ornekleri"]
    },
    "K3_Hata_Cozumleme": {
        "name": "Hata Çözümleme",
        "description": "Log analizi, hata tespiti ve değerlendirme (kod içermez)",
        "focus": ["log_analizi", "hata_tespiti", "troubleshooting"]
    },
    "K4_Tasarim": {
        "name": "Tasarım",
        "description": "Mimari yapı, teknoloji karşılaştırması, ölçeklenebilirlik",
        "focus": ["mimari_tasarim", "teknoloji_secimi", "olceklendirme"]
    },
    "K5_Stratejik": {
        "name": "Stratejik",
        "description": "Süreç iyileştirme, teknoloji seçimi, karar gerekçesi",
        "focus": ["liderlik", "strateji", "surec_iyilestirme", "karar_verme"]
    }
}

# Zorluk seviyesi etiketleri
DIFFICULTY_LABELS = {
    2: {"name": "Junior", "label": "2x", "description": "Temel seviye"},
    3: {"name": "Mid", "label": "3x", "description": "Orta seviye"},
    4: {"name": "Senior", "label": "4x", "description": "İleri seviye"},
    5: {"name": "Lead", "label": "5x", "description": "Liderlik seviye"}
}