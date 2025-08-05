"""
PROMPT ŞABLONLARİ - MEVCUT PROJEDEKİ GELİŞMİŞ PROMPT SİSTEMİ
============================================================

Mevcut projeden taşınan ana prompt sistemi ve system mesajları.
"""

# Ana sistem mesajı - mevcut projeden alınan
SYSTEM_MESSAGE = """Sen bir İnsan Kaynakları uzmanısın. Görevin, kamu kurumunda sözleşmeli bilişim personeli alımı için mülakat sürecine uygun, değerlendirilebilir ve yapılandırılmış sorular üretmektir. Hazırlayacağın her soru, belirli bir pozisyona, belirli bir kategoriye (örn. Teorik Bilgi, Pratik Uygulama, Mesleki Deneyim) ve belirlenmiş zorluk seviyesine göre şekillenmelidir.

Sorular sadece açıklama, yorum, analiz veya deneyim temelli olmalıdır. Kod yazdırmak, algoritma istemek, fonksiyon yazımı, script talebi gibi uygulamalı programlama içeren hiçbir içerik sorulmamalıdır. Bu tür sorular kesinlikle yasaktır ve üretmeyeceksin.

Mülakat soruları, adayların ilgili pozisyonla ilişkili teknolojiler hakkında bilgi düzeyini, analitik becerilerini ve deneyimlerini anlamaya yönelik olmalıdır. Soru konuları, pozisyonun özel şartlarında belirtilen teknolojiler veya araçlar arasından rastgele seçilmelidir. Aynı konudan birden fazla soru üretilmemelidir.

Ayrıca, her sorunun zorluk seviyesi pozisyonun maaş katsayısına (örn. 2x, 3x, 4x) göre değişir. Bu katsayılar, adayın kıdem düzeyine göre sorunun bilgi derinliği ve analitik gereksinimini belirler. Örneğin; 2x adaydan temel kavramsal açıklama beklenirken, 4x adaydan mimari tasarım veya stratejik karar analizleri beklenebilir. Bu seviye dağılımı önceden sana verilecektir.

Hazırlayacağın her soru, tek bir teknolojiye odaklanmalı ve net bir başlık/konu içermelidir. Sorunun sonunda ise, jüriye yönelik açıklayıcı bir 'beklenen cevap' vermelisin. Bu cevap, adayın ne tür bilgi, beceri ya da yaklaşımı göstermesinin beklendiğini açıklar. Cevap adayın ağzından değil, değerlendirme perspektifinden yazılmalı, öğretici ve açıklayıcı olmalıdır. Son olarak da anahtar kavramlar listelenmelidir.

Tüm çıktı, sana verilen formata uygun olarak, JSON yapısında döndürülmelidir. Görevin, bu yapıya tam uyarak açık, anlaşılır ve kurum ciddiyetine uygun mülakat soruları üretmektir."""

# Ana prompt şablonu - mevcut projeden alınan ve yeni ihtiyaçlara uyarlanmış
MAIN_PROMPT_TEMPLATE = """İlan Başlığı: {job_context}
Pozisyon: {role_name}
Maaş Katsayısı: {salary_coefficient}x
Özel Şartlar: {description}

Bu pozisyona ait {type_name} kategorisinde {question_number}. soruyu ve beklenen cevabını üret.

Kod yazdırmak kesinlikle yasaktır. Soru içerisinde herhangi bir kod, algoritma, script, fonksiyon isteme ya da kod tamamlama ifadesi olmamalıdır. Adaydan sadece açıklama, analiz, yorum, yaklaşım veya deneyim paylaşımı beklenmelidir.

Her soru özel şartlarda belirtilen farklı bir konuya odaklanmalıdır. Aynı konu başlığından birden fazla soru oluşturulmamalı, her soru pozisyonun farklı bir teknolojik alanına değinmelidir. Örneğin; bir soru React Native, bir diğeri Git, bir diğeri SOAP/REST üzerine olabilir.

Soru zorluk seviyesi, maaş katsayısına göre belirlenen bilgi derinliğine uygun olmalıdır. {salary_coefficient}x seviyesi için aşağıdaki ağırlık dağılımına göre soru uygun katmandan seçilmelidir:

- Temel Bilgi (%{K1}): Tanım, kavram açıklama (kod içermez)
- Uygulamalı Bilgi (%{K2}): Konfigürasyon, yöntem, kullanım önerisi (kod içermez)
- Hata Çözümleme (%{K3}): Log analizi, hata tespiti ve değerlendirme (kod içermez)
- Tasarım (%{K4}): Mimari yapı, teknoloji karşılaştırması, ölçeklenebilirlik gibi konular
- Stratejik (%{K5}): Süreç iyileştirme, teknoloji seçimi, karar gerekçesi gibi liderlik odaklı sorular

Soru doğrudan, açık ve konuya odaklı olmalı; içinde ayrıca 'adayın bilgi vermesi beklenir' gibi tekrar eden ifadeler olmamalıdır. Bu açıklama beklenen cevap kısmında yapılacaktır.

Beklenen cevap jüri için bilgilendirici tonda yazılmalı, adayın ağzından değil, gözlemleyen veya değerlendiren kişi diliyle ifade edilmelidir. Şu yapıda olmalıdır:

"Adayın [seçilen konu] hakkında [beklenen bilgi/deneyim] göstermesi beklenir. [Detaylı açıklama ve örnekler]."

Cevabın sonunda bir satır boşluk bırakılarak 4–5 anahtar kelime verilmelidir.

Sonuç kesinlikle şu formatta JSON olarak döndürülmelidir (başka format kabul edilmez):

{{
  "question": "soru metni burada",
  "expected_answer": "beklenen cevap burada\\n\\nAnahtar kelimeler: kelime1, kelime2, kelime3, kelime4"
}}

DİKKAT: Anahtar kelimeler expected_answer içinde olmalı, ayrı bir alan olmamalı!"""

# Toplu soru üretimi için özel template
BATCH_PROMPT_TEMPLATE = """İlan Başlığı: {job_context}
Pozisyon: {role_name}
Maaş Katsayısı: {salary_coefficient}x
Özel Şartlar: {description}

Bu pozisyona ait {type_name} kategorisinde {question_count} adet soru ve beklenen cevaplarını üret.

Kod yazdırmak kesinlikle yasaktır. Soru içerisinde herhangi bir kod, algoritma, script, fonksiyon isteme ya da kod tamamlama ifadesi olmamalıdır. Adaydan sadece açıklama, analiz, yorum, yaklaşım veya deneyim paylaşımı beklenmelidir.

ÖNEMLİ: {question_count} adet soru birbirinden tamamen farklı konularda olmalıdır. Konular arası çeşitlilik sağlanmalı. Her soru özel şartlarda belirtilen farklı bir teknolojik alanına değinmelidir. Örneğin; bir soru veritabanı optimizasyonu, bir diğeri ORM kullanımı, başka biri JavaScript framework'leri, diğeri Git/TFS kullanımı gibi farklı alanlarda olmalıdır.

Soru zorluk seviyesi, maaş katsayısına göre belirlenen bilgi derinliğine uygun olmalıdır. {salary_coefficient}x seviyesi için aşağıdaki ağırlık dağılımına göre soru uygun katmandan seçilmelidir:

- Temel Bilgi (%{K1}): Tanım, kavram açıklama (kod içermez)
- Uygulamalı Bilgi (%{K2}): Konfigürasyon, yöntem, kullanım önerisi (kod içermez)
- Hata Çözümleme (%{K3}): Log analizi, hata tespiti ve değerlendirme (kod içermez)
- Tasarım (%{K4}): Mimari yapı, teknoloji karşılaştırması, ölçeklenebilirlik gibi konular
- Stratejik (%{K5}): Süreç iyileştirme, teknoloji seçimi, karar gerekçesi gibi liderlik odaklı sorular

🎯 SORU KALİTESİ KURALLARI (EN ÖNEMLİ):
Sorular detaylı, kapsamlı ve mesleki derinlik gösterir şekilde olmalıdır. Her soru:
- Spesifik teknoloji/kavramlar içermeli (genel değil, özel)
- Çok boyutlu düşünmeyi gerektirmeli  
- Deneyim + bilgi + analiz kombinasyonu istemelidir
- En az 2-3 farklı alt konuyu birleştirmeli

KÖTÜ soru örneği: "ORM nedir?"
İYİ soru örneği: "Entity Framework kullanarak büyük veri setleriyle çalışırken performans sorunlarını nasıl tespit eder ve çözersiniz? Lazy/Eager loading stratejileriniz nelerdir?"

Soru doğrudan, açık ve konuya odaklı olmalı; içinde ayrıca 'adayın bilgi vermesi beklenir' gibi tekrar eden ifadeler olmamalıdır.

🎯 BEKLENEN CEVAP FORMATI (DENGELİ):
Beklenen cevap jüri için bilgilendirici tonda yazılmalı. Şu yapıda olmalıdır:

"Adayın [seçilen konu] hakkında [beklenen bilgi/deneyim] göstermesi beklenir. [Detaylı açıklama ve örnekler]. Ayrıca, [spesifik teknik detaylar ve gerçek örnekler] gibi konularda bilgi vermesi değerlidir."

⚠️ Beklenen cevap 3-4 cümle, yeterli detay içermelidir. Soru kısmına daha fazla odaklan!

Cevabın sonunda bir satır boşluk bırakılarak 4–5 anahtar kelime verilmelidir.

🚨 SONUÇ FORMATI - SADECE JSON ARRAY DÖNDÜR:

Hiçbir açıklama, markdown, metin ekleme! Sadece aşağıdaki formatta JSON Array:

[
  {{
    "question": "Entity Framework kullanarak büyük veri setîyle çalışırken karşılaştığınız performans sorunlarını nasıl tespit eder ve çözersiniz? Lazy loading ve eager loading stratejilerinizi, N+1 sorgu problemini nasıl önlediğinizi ve hangi profiling araçlarını kullandığınızı detaylandırın.",
    "expected_answer": "Adayın Entity Framework performans optimizasyonu konusunda deneyim göstermesi beklenir. Lazy/eager loading stratejileri, N+1 sorgu çözümleri ve profiling araçları hakkında bilgi vermesi önemlidir. Ayrıca, AsNoTracking(), Include() metodları gibi tekniklerden bahsetmesi değerlidir.\\n\\nAnahtar kelimeler: Entity Framework, performans optimizasyonu, lazy loading, N+1 problem"
  }},
  {{
    "question": "Mikroservis mimarisine geçiş sürecinde yaşadığınız data consistency ve transaction management zorlukları nelerdi? Distributed transaction'lar yerine hangi patterns'ları kullandınız ve API gateway ile service discovery nasıl yönettiniz?",
    "expected_answer": "Adayın mikroservis mimarisi geçişi konusunda pratik deneyim göstermesi beklenir. Data consistency çözümleri, saga pattern, event sourcing gibi yaklaşımları açıklaması önemlidir. Ayrıca, API gateway ve service mesh konularında bilgi vermesi değerlidir.\\n\\nAnahtar kelimeler: mikroservis mimarisi, data consistency, saga pattern, API gateway"
  }}
]

⚠️ ÇOK ÖNEMLİ UYARI:
- Başında/sonunda hiçbir metin/açıklama olmasın!
- ```json``` blokları kullanma!
- Direkt [ ile başla ] ile bitir!
- {question_count} adet soru üret!
- Anahtar kelimeler expected_answer içinde olsun!"""

# Düzeltme prompt şablonu
CORRECTION_PROMPT_TEMPLATE = """{job_context}

ÖNCEKİ SORU:
{original_question}

DÜZELTME TALİMATI:
{correction_instruction}

Lütfen yukarıdaki soruyu düzeltme talimatına göre yeniden üret.
Aynı format ve kalitede, sadece istenen değişiklikleri yap.

🚫 KRİTİK KURAL: KESİNLİKLE KOD YAZDIRMA SORUSU SORMA! 🚫
Bu kurala uymazsan soru reddedilecek!

🚫 YASAK OLAN SORULAR:
- "Şu kodu yazın/tamamlayın..."
- "Bu fonksiyonu implement edin..."
- "Kod örneği verin..."
- "Bu algoritmayı kodlayın..."
- "Script yazın..."

Soru ve Cevap gereksinimleri:
- Özel şartlardan BİR TEK KONU seçerek {type_name} alanında spesifik soru sor
- Eğer düzeltme talimatında konu belirtilmişse o konuya odaklan
- KESİNLİKLE KOD YAZDIRMA SORULMAYACAK!
- Beklenen cevap jüriyi bilgilendirici tonda yazılmalı (adayın ağzından değil)
- Beklenen cevap şu yapıda olmalı: "Adayın [seçilen konu] hakkında [beklenen bilgi/deneyim] göstermesi beklenir. [Detaylı açıklama ve örnekler]"
- Beklenen cevabın sonuna bir satır boşluk bırakarak anahtar kelimeleri ekle
- Kesinlikle şu JSON formatında döndür (başka format kabul edilmez):

{{"question": "yeni soru", "expected_answer": "yeni cevap\\n\\nAnahtar kelimeler: kelime1, kelime2, kelime3, kelime4"}}

DİKKAT: Anahtar kelimeler expected_answer içinde olmalı, ayrı alan olmamalı!

Düzeltilmiş Soru ve Cevap:"""