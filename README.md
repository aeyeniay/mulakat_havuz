# Mülakat Soru Havuzu

Rol bazlı (uygulama arayüzü olmadan) mülakat soru üretimi için Python tabanlı araç. 
- K1–K5 rübrik modeli ve zorluk dağılımları mevcut projeye (mulakat_soru) paralel
- İlan metni tam metin olarak dosyadan verilir
- Soru üretimi OpenAI API ile yapılır, Word çıktısı alınır
- Docker konteynerı ile çalıştırılır

## Hızlı Başlangıç (Docker)
```bash
cp .env.example .env
# .env dosyasına OPENAI_API_KEY değerini yazın

# Build
docker compose build

# Örnek ilan dosyası oluşturun
mkdir -p data/job_descriptions
printf "YAZILIM GELİŞTİRİCİ İLAN METNİ\n\n[Buraya tam ilan metni]" > data/job_descriptions/yazilim_gelistirici.txt

# Örnek komut (ileride CLI komutları tamamlanınca)
docker compose run --rm app --help
```
