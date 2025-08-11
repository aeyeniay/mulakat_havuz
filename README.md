# 🎯 Mülakat Soru Havuzu Sistemi

Kamu kurumu sözleşmeli bilişim personeli alımı için otomatik mülakat sorusu üretim sistemi.

## 📋 Özellikler

- **Otomatik Soru Üretimi**: OpenAI API ile akıllı soru üretimi
- **Kategori Bazlı Sistem**: Mesleki deneyim, teorik bilgi, pratik uygulama kategorileri
- **Zorluk Seviyeleri**: Maaş katsayısına göre (2x, 3x, 4x) zorluk derecelendirmesi
- **Word Export**: Oluşturulan soruları Word belgesi olarak export etme
- **Toplu Üretim**: Birden fazla rol için aynı anda soru üretimi

## 🚀 Kurulum

### Gereksinimler
- Python 3.8+
- OpenAI API Key

### Kurulum Adımları

1. **Repository'yi klonlayın:**
   ```bash
   git clone https://github.com/aeyeniay/mulakat_havuz.git
   cd mulakat_havuz
   ```

2. **Virtual environment oluşturun:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # venv\Scripts\activate     # Windows
   ```

3. **Bağımlılıkları yükleyin:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment dosyasını ayarlayın:**
   ```bash
   cp env.example .env
   # .env dosyasını düzenleyip OpenAI API anahtarınızı ekleyin
   ```

## 🎮 Kullanım

### Toplu Soru Üretimi
```bash
python3 batch_generate.py
```

Bu komut ile:
- Tüm roller listelenecek
- Her rol için soru sayıları gireceksiniz
- Sistem otomatik olarak soruları üretecek
- Word belgeleri oluşturulacak

### Soru Kategorileri

1. **Mesleki Deneyim Soruları**: Geçmiş projeler, ekip rolleri, karşılaştığı zorluklar
2. **Teorik Bilgi Soruları**: Kavramlar, yöntemler, teknolojiler hakkında temel bilgi
3. **Pratik Uygulama Soruları**: Gerçek senaryolar, problem çözme, yapılandırma

### Zorluk Seviyeleri

- **2x**: Junior seviye - Temel kavramlar, basit deneyimler
- **3x**: Mid-level - Derinlemesine bilgi, proje deneyimi
- **4x**: Senior seviye - Mimari kararlar, liderlik, stratejik düşünme

## 📁 Proje Yapısı

```
mulakat_havuz/
├── batch_generate.py          # Ana uygulama
├── config/                    # Konfigürasyon dosyaları
│   ├── openai_settings.py     # OpenAI API ayarları
│   ├── question_categories.py # Soru kategorileri
│   ├── roles_config.py        # Rol tanımları
│   └── rubric_system.py       # Zorluk dağılım sistemi
├── core/                      # Ana sistem bileşenleri
│   ├── question_generator.py  # Soru üretim motoru
│   ├── json_parser.py         # JSON parse sistemi
│   └── prompt_templates.py    # AI prompt şablonları
├── data/                      # Veri dosyaları
│   ├── job_descriptions/      # İş tanımları
│   ├── generated_questions/   # Üretilen sorular (JSON)
│   └── word_exports/         # Word belgeleri
├── exporters/                 # Export işlemleri
│   └── word_exporter.py      # Word belge oluşturucu
├── generators/                # Üretim sistemleri
│   └── single_generator.py   # Tekil soru üretici
└── utils/                     # Yardımcı araçlar
    └── file_helpers.py       # Dosya işlemleri
```

## ⚙️ Konfigürasyon

### OpenAI API Ayarları
`config/openai_settings.py` dosyasından model, token limitleri ve diğer API ayarlarını düzenleyebilirsiniz.

### Soru Kategorileri
`config/question_categories.py` dosyasından kategori tanımlarını güncelleyebilirsiniz.

### Rol Tanımları
`config/roles_config.py` dosyasından yeni roller ekleyebilir, mevcut rolleri düzenleyebilirsiniz.

## 📊 Örnekler

### Üretilen Soru Örneği
**Kategori**: Pratik Uygulama  
**Zorluk**: 3x  
**Soru**: "Web API geliştirirken güvenlik önlemlerini nasıl sağlarsınız? Authentication/Authorization mekanizmaları, JWT token kullanımı, input validation ve rate limiting konularında yaklaşımınızı açıklayın."

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add amazing feature'`)
4. Branch'i push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## 📄 Lisans

Bu proje MIT lisansı ile lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın.

## 🆘 Destek

Sorularınız için issue açabilir veya iletişime geçebilirsiniz.

---

**Not**: Bu sistem kamu kurumu mülakatları için geliştirilmiştir ve etik kurallara uygun olarak tasarlanmıştır.