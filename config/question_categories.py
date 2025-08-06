"""
SORU KATEGORİLERİ VE TİPLERİ
===========================

Mevcut projeden alınan soru kategorileri ve soru tiplerinin tanımları.
"""

# Soru kategorileri - mevcut projeden alınan
QUESTION_CATEGORIES = {
    "professional_experience": {
        "name": "Mesleki Deneyim Soruları",
        "description": "Adayın geçmişte yaşadığı projeler, ekip içindeki rolü, karşılaştığı zorluklar ve bunlara yaklaşımı hakkında bilgi edinmeyi amaçlar. Somut örnekler, kişisel katkılar ve sonuç odaklı anlatımlar aranır. Gerçek deneyim paylaşımı, başarı/başarısızlık durumları sorgulanabilir.",
        "order_index": 1,
        "is_active": True
    },
    "theoretical_knowledge": {
        "name": "Teorik Bilgi Soruları", 
        "description": "Pozisyonla ilgili kavram, yöntem, standart, protokol ya da teknolojilere dair temel bilgi düzeyini ölçen sorulardır. Adaydan tanım yapması, teknik bir yapıyı açıklaması veya iki kavramı karşılaştırması beklenir. Kod içermez; soyut bilgi temellidir.",
        "order_index": 2,
        "is_active": True
    },
    "practical_application": {
        "name": "Pratik Uygulama Soruları",
        "description": "Gerçek dünyadaki bir durumu çözümlemeyi veya yapılandırmayı gerektiren uygulamalı senaryo sorularıdır. Adaydan bir problem durumu karşısında ne yapacağını anlatması, alternatif çözüm yollarını değerlendirmesi beklenir. Kurgusal ama gerçekçi vaka, yapılandırma, süreç tasarımı gibi konular içerebilir.",
        "order_index": 3,
        "is_active": True
    }
}

def get_active_question_categories() -> list:
    """
    Aktif soru kategorilerini döndür.
    
    Returns:
        list: [(kod, isim, açıklama)] formatında kategori listesi
    """
    active_categories = [
        (code, config["name"], config["description"]) 
        for code, config in QUESTION_CATEGORIES.items() 
        if config["is_active"]
    ]
    
    # Sıralama indeksine göre sırala
    return sorted(active_categories, key=lambda x: QUESTION_CATEGORIES[x[0]]["order_index"])

def get_category_config(category_code: str) -> dict:
    """
    Kategori koduna göre konfigürasyon bilgilerini döndür.
    
    Args:
        category_code (str): Kategori kodu
        
    Returns:
        dict: Kategori konfigürasyon bilgileri
        
    Raises:
        KeyError: Tanımlanmamış kategori kodu için
    """
    if category_code not in QUESTION_CATEGORIES:
        available_categories = list(QUESTION_CATEGORIES.keys())
        raise KeyError(f"Tanımlanmamış kategori: {category_code}. Mevcut kategoriler: {available_categories}")
    
    return QUESTION_CATEGORIES[category_code]

def validate_category_for_role(role_code: str, category_code: str) -> bool:
    """
    Rol ve kategori kombinasyonunu doğrular.
    
    Args:
        role_code (str): Rol kodu
        category_code (str): Kategori kodu
        
    Returns:
        bool: Geçerli kombinasyon ise True
    """
    try:
        from config.roles_config import get_role_config
        
        role_config = get_role_config(role_code)
        return category_code in role_config.get("categories", [])
    except (KeyError, ImportError):
        return False