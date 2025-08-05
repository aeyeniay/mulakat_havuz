"""
ROL TANIMLARI VE KONFİGÜRASYONLARI
==================================

Gerçek ilan metinlerinden çıkarılmış detaylı rol tanımları.
Her rol için özel şartlar, maaş katsayıları ve iş tanımı dosya referansları.
"""

ROLES = {
    "kidemli_yazilim_gelistirme_uzmani": {
        "name": "Kıdemli Yazılım Geliştirme Uzmanı",
        "salary_multipliers": [3],
        "job_description_file": "kidemli_yazilim_gelistirme_uzmani_3x.txt",
        "categories": ["professional_experience", "theoretical_knowledge", "practical_application"],
        "description": """B Grubu kadrolar için kıdemli yazılım geliştirme uzmanı pozisyonu. 
        
ZORUNLU NİTELİKLER: .NET teknolojilerinde (C#, .NET Core, .NET Framework, ASP.NET Core, ASP.NET MVC) uzmanlaşmış, ORM araçlarında (Entity Framework, Entity Framework Core, Dapper) deneyimli, MSSQL ve/veya PostgreSQL ile T-SQL/PL-SQL bilgisine sahip, JavaScript frameworkleri (jQuery, Vue, Angular, React) konusunda bilgili, veri tabanı tasarımı ve performans optimizasyonu yapabilen, IIS kurulumu ve deployment süreçlerini bilen, TFS/GIT/SVN gibi kaynak kod kontrol araçlarını kullanan profesyoneller.

TERCİH EDİLEN NİTELİKLER: Kurumsal Yazılım Mimarisi ve Tasarım Kalıpları konusunda bilgi sahibi, DevOps ve CI/CD süreçleri deneyimi, Konteyner mimarisi (Kubernetes, Docker) bilgisi, Linux/Unix işletim sistemleri deneyimi, NoSQL veritabanları bilgisi, ELK Stack ve full-text search deneyimi, dağıtık önbellek mimarileri (Redis, Memcached) deneyimi, mesaj kuyruğu sistemleri (RabbitMQ, Apache Kafka) bilgisi."""
    },
    
    "yazilim_gelistirme_uzmani": {
        "name": "Yazılım Geliştirme Uzmanı",
        "salary_multipliers": [2],
        "job_description_file": "yazilim_gelistirme_uzmani_2x.txt",
        "categories": ["professional_experience", "theoretical_knowledge", "practical_application"],
        "description": """C Grubu kadrolar için yazılım geliştirme uzmanı pozisyonu.
        
ZORUNLU NİTELİKLER: .NET teknolojilerinde (C#, .NET Core, .NET Framework, ASP.NET Core, ASP.NET MVC) temel seviyede bilgi sahibi, ORM araçlarında (Entity Framework, Entity Framework Core, Dapper) bilgili, MSSQL veya PostgreSQL ile T-SQL veya PL-SQL konularında deneyimli, veri tabanı tasarımı ve performans optimizasyonu yapabilen, TFS/GIT/SVN gibi kaynak kod kontrol araçlarını kullanan profesyoneller.

TERCİH EDİLEN NİTELİKLER: IIS kurulumu ve web uygulaması deployment süreçleri konusunda bilgi sahibi olmak."""
    },

    "kidemli_mobil_yazilim_gelistirme_uzmani": {
        "name": "Kıdemli Mobil Yazılım Geliştirme Uzmanı", 
        "salary_multipliers": [3],
        "job_description_file": "kidemli_mobil_yazilim_gelistirme_uzmani_3x.txt",
        "categories": ["professional_experience", "theoretical_knowledge", "practical_application"],
        "description": """B Grubu kadrolar için kıdemli mobil yazılım geliştirme uzmanı pozisyonu.
        
ZORUNLU NİTELİKLER: Yazılım yaşam döngüsü ve güvenli yazılım geliştirme konularında bilgili, React Native ile mobil uygulama geliştirme deneyimi, SOAP/REST mimarisinde web servisleri ve JSON/XML veri protokolleri konusunda uzman, SoapUI ve Postman gibi web servis test araçlarını kullanan, TFS/GIT/SVN kaynak kod kontrol sistemlerinde deneyimli profesyoneller.

TERCİH EDİLEN NİTELİKLER: Mikroservisler ve Web Servisleri teknolojileri bilgisi, JavaScript/CSS3/HTML5 web teknolojileri deneyimi, Google Play Store veya App Store'da yayınlanmış referans uygulaması bulunan, ön bellekleme (caching) sistemleri konusunda bilgi sahibi olmak."""
    },

    "mobil_yazilim_gelistirme_uzmani": {
        "name": "Mobil Yazılım Geliştirme Uzmanı",
        "salary_multipliers": [2], 
        "job_description_file": "mobil_yazilim_gelistirme_uzmani_2x.txt",
        "categories": ["professional_experience", "theoretical_knowledge", "practical_application"],
        "description": """C Grubu kadrolar için mobil yazılım geliştirme uzmanı pozisyonu.
        
ZORUNLU NİTELİKLER: Yazılım yaşam döngüsü ve güvenli yazılım geliştirme temel bilgisine sahip, React Native ile mobil uygulama geliştirme deneyimi, SOAP/REST web servisleri ve JSON/XML protokolleri konusunda bilgili, SoapUI/Postman test araçlarını kullanan, TFS/GIT/SVN kaynak kod kontrol sistemlerinde temel deneyimli profesyoneller.

TERCİH EDİLEN NİTELİKLER: Mikroservisler ve Web Servisleri teknolojileri bilgisi, JavaScript/CSS3/HTML5 temel bilgisi, uygulama mağazalarında yayın deneyimi, caching sistemleri hakkında temel bilgi sahibi olmak."""
    },

    "kidemli_veritabani_uzmani": {
        "name": "Kıdemli Veritabanı Uzmanı (PostgreSQL)",
        "salary_multipliers": [3],
        "job_description_file": "kidemli_veritabani_uzmani_postgresql_3x.txt", 
        "categories": ["professional_experience", "theoretical_knowledge", "practical_application"],
        "description": """B Grubu kadrolar için PostgreSQL uzmanı pozisyonu.
        
ZORUNLU NİTELİKLER: PostgreSQL veri tabanı mimarisi, veri hizmetleri planlaması, veri tabanı modelleme-tasarımı ve optimizasyon/normalizasyon konularında uzman, PostgreSQL Cluster ve High Availability çözümleri (Patroni, auto failover, replication, disaster recovery, BarMan, PgPool, PgBouncer) deneyimi, performans tuning ve kapasite planlama bilgisi, PostgreSQL stored procedure veri modelleri geliştirme, veri tabanı performans izleme ve log analizi, Linux işletim sistemi bilgisi, Linux'ta bash scriptleri ve Crontab entegrasyonu, LVM disk yapılandırması, ileri seviye PL/pgSQL ve TSQL bilgisi, ETL/OLAP/OLTP modelleri geliştirme, ETL job oluşturma ve performans optimizasyonu, CDC (Change Data Capture) çözümleri konusunda deneyimli profesyoneller.

TERCİH EDİLEN NİTELİKLER: NoSQL veritabanları (Elasticsearch, MongoDB, Redis) yönetimi deneyimi."""
    },

    "devops_uzmani": {
        "name": "DevOps Uzmanı",
        "salary_multipliers": [3],
        "job_description_file": "devops_uzmani_3x.txt",
        "categories": ["professional_experience", "theoretical_knowledge", "practical_application"],
        "description": """B Grubu kadrolar için konteyner teknolojileri ve CI/CD uzmanı pozisyonu.
        
ZORUNLU NİTELİKLER: Kubernetes, Docker Swarm, Rancher, OpenShift gibi konteyner teknolojilerinde uzman, Unix/Linux işletim sistemleri, veri tabanı, uygulama katmanı, yazılım ve güvenlik konularında bilgili, scripting dillerinde (Shell, bash, PowerShell, Python) deneyimli, Git versiyonlama sisteminde uzman, GitLab CI, Jenkins, TeamCity, Azure DevOps gibi CI/CD araçlarından en az birinde deneyimli, Jira/Bitbucket/Bamboo araçlarını kullanan profesyoneller.

TERCİH EDİLEN NİTELİKLER: CI/CD araçlarının bakımı ve yönetimi, pipeline oluşturma deneyimi, Prometheus/Grafana/Zabbix gibi monitoring araçları bilgisi, Keycloak kimlik yönetimi deneyimi."""
    },

    "kidemli_ag_uzmani": {
        "name": "Kıdemli Ağ Uzmanı",
        "salary_multipliers": [3],
        "job_description_file": "kidemli_ag_uzmani_3x.txt",
        "categories": ["professional_experience", "theoretical_knowledge", "practical_application"],
        "description": """B Grubu kadrolar için kıdemli network altyapı uzmanı pozisyonu.
        
ZORUNLU NİTELİKLER: LAN/WAN/WLAN/VPN/Dinamik Yönlendirme Protokolleri ve ağ teknolojileri uzmanı, TCP/IP/DNS/DHCP/802.1x protokolleri konusunda ileri seviyede bilgili, Wireless/Load Balancer/Firewall teknolojileri ve yönetimi deneyimi, Antivirus/IDS/IPS teknolojileri bilgisi, DDoS Protection teknolojisi ve yönetimi, Cisco/Huawei/H3C/Juniper/Dell/HP marka switch/router/WLC konfigürasyonu ve VoIP kurulum/yönetimi, network mimarileri tasarımı/planlaması/entegrasyonu, ağ güvenliği uzmanı, büyük kapasiteli omurga cihazları yönetimi, PAM (Privileged Access Management) kurulum/yönetimi, NAC (Network Access Control) teknolojisi ve yönetimi, network monitoring araçlarının kurulum/yönetimi/raporlama konularında deneyimli profesyoneller."""
    },

    "ag_uzmani": {
        "name": "Ağ Uzmanı", 
        "salary_multipliers": [2],
        "job_description_file": "ag_uzmani_2x.txt",
        "categories": ["professional_experience", "theoretical_knowledge", "practical_application"],
        "description": """C Grubu kadrolar için network altyapı uzmanı pozisyonu.
        
ZORUNLU NİTELİKLER: LAN/WAN/WLAN/VPN/Dinamik Yönlendirme Protokolleri ve ağ teknolojileri konusunda bilgili, TCP/IP/DNS/DHCP/802.1x protokolleri temel/orta seviyede bilgisi, Wireless/Load Balancer/Firewall teknolojileri ve yönetimi deneyimi, Antivirus/IDS/IPS teknolojileri temel bilgisi, DDoS Protection teknolojisi bilgisi, network mimarileri tasarımı/planlaması/entegrasyonu, ağ güvenliği konusunda bilgili, büyük kapasiteli omurga cihazları temel yönetimi, PAM kurulum/yönetimi, NAC teknolojisi ve yönetimi, network monitoring araçları kurulum/yönetimi/raporlama konularında deneyimli profesyoneller."""
    },

    "kidemli_sistem_uzmani": {
        "name": "Kıdemli Sistem Uzmanı",
        "salary_multipliers": [3],
        "job_description_file": "kidemli_sistem_uzmani_3x.txt",
        "categories": ["professional_experience", "theoretical_knowledge", "practical_application"],
        "description": """B Grubu kadrolar için kıdemli sistem altyapı uzmanı pozisyonu.
        
ZORUNLU NİTELİKLER: VMware sanallaştırma kurulum/yapılandırma/yönetimi konusunda ileri seviyede uzman, Storage ve SAN anahtar yönetimi alanında kurulum/yapılandırma/bakım/yönetimi ileri seviye deneyimi, yedekleme yönetimi kurulum/yapılandırma/bakım/yönetimi ileri seviye, arşiv & backup (teyp) kurulum/yapılandırma/yönetimi, Microsoft Exchange/Active Directory/DNS/DHCP/File Server/Windows RDP mimarisi kurulum/yapılandırma/cluster/güncelleme/sorun çözümleme uzmanı, Windows sunucu log inceleme/sınıflandırma/performans/sorun çözümü, Windows Server 2016/2019/2022 bakım/izleme/yapılandırma, Failover cluster/Always-on yapılandırmalar, SAN/NAS cihazları yönetimi ve sistem entegrasyonu, Linux sunucu kurulum/yapılandırma/yönetim/sorun çözümlemeleri ve temel Linux servisleri konularında deneyimli profesyoneller."""
    },

    "sistem_uzmani_microsoft": {
        "name": "Sistem Uzmanı (Microsoft)",
        "salary_multipliers": [2],
        "job_description_file": "sistem_uzmani_microsoft_2x.txt", 
        "categories": ["professional_experience", "theoretical_knowledge", "practical_application"],
        "description": """C Grubu kadrolar için Microsoft teknolojileri sistem uzmanı pozisyonu.
        
ZORUNLU NİTELİKLER: Microsoft Exchange/Active Directory/DNS/DHCP kurulum/yapılandırma/yönetimi konusunda ileri seviyede bilgili, Microsoft SCCM (System Center Configuration Manager) ve işletim sistemi imajları oluşturma/kurulum/dağıtım deneyimi, File Server/Windows RDP mimarisi kurulum/yapılandırma/cluster/güncelleme/sorun çözümleme, Windows sunucu log inceleme/sınıflandırma/performans/sorun çözümü, Windows Server 2016/2019/2022 bakım/izleme/yapılandırma, PowerShell scripting konusunda iyi derecede bilgili, Failover cluster/Always-on yapılandırmalar, sunucu donanımları ve konfigürasyonları (disk/Ethernet/HBA/RAID) bilgisi, veri depolama/SAN/NAS cihazları yönetimi, veri merkezi yönetimi, bilgi sistemleri güvenliği/temel ağ/bilişim sistemi politikalar konularında deneyimli profesyoneller."""
    },

    "sistem_uzmani_linux": {
        "name": "Sistem Uzmanı (Linux)",
        "salary_multipliers": [2],
        "job_description_file": "sistem_uzmani_linux_2x.txt",
        "categories": ["professional_experience", "theoretical_knowledge", "practical_application"], 
        "description": """C Grubu kadrolar için Linux sistem uzmanı pozisyonu.
        
ZORUNLU NİTELİKLER: Linux işletim sistemi ve hizmetlerinin kurulum/konfigürasyon/sorun çözümleme konusunda bilgili, Linux disk yapılandırmaları (LVM/Multipath) deneyimi, Linux sunucularında (Ubuntu 16+, CentOS 6+, Debian 8+) güvenlik açıkları ve pro-aktif güvenlik tedbirleri uygulayabilen, sunucu donanımları ve konfigürasyonları (disk/Ethernet/HBA/RAID) bilgisi, veri depolama/SAN/NAS cihazları yönetimi ve sistem entegrasyonu, sunucu/istemci işletim sistemi imajları oluşturma/kurulum/dağıtım, VMware sanallaştırma kurulum/yapılandırma/yönetimi, Linux sunucu sistemlerinde (Debian/RPM&RedHat) kurulum/yapılandırma/sıkılaştırma/izleme/performans artırma/sorun çözümleme, sistem yazılımları ve Linux Script Language bilgisi, UNIX/Linux kurulum/optimizasyon/yönetim/yedekleme/kullanıcı yönetimi/performans yönetimi/kapasite planlama/log inceleme/güvenlik/bakım, DHCP/DNS/Proxy sistem servisleri, kurumsal yedekleme yazılımları/donanımları/teknolojileri yönetimi konularında deneyimli profesyoneller.

TERCİH EDİLEN NİTELİKLER: DevOps, Konteyner mimarisi, Kubernetes, Docker konusunda bilgi sahibi olmak."""
    },

    "kidemli_siber_guvenlik_uzmani": {
        "name": "Kıdemli Siber Güvenlik Uzmanı",
        "salary_multipliers": [3],
        "job_description_file": "kidemli_siber_guvenlik_uzmani_3x.txt",
        "categories": ["professional_experience", "theoretical_knowledge", "practical_application"],
        "description": """B Grubu kadrolar için kıdemli siber güvenlik uzmanı pozisyonu.
        
ZORUNLU NİTELİKLER: SIEM/SOAR/IDS/IPS/İçerik Filtreleme/EDR/NDR/WAF/Mail Gateway/Sandbox/Zafiyet Tarama güvenlik teknolojileri uzmanı, PAM/DLP/XDR/UEBA/SSL Inspection/Kaynak Kod Analiz Araçları/Database Firewall/Honeypot teknolojileri deneyimi, SOC (Siber Güvenlik Operasyon Merkezi) işletim süreçleri uzmanı, TCP/IP/ağ yapıları/ağ trafik-paket analizi/ağ sıkılaştırma konusunda ileri seviyede bilgili, ISO 27001/KVKK/5651 sayılı Kanun/regülasyon/standartlar uzmanı, DHCP/DNS/Active Directory/Exchange/Veritabanı Sistemleri/web teknolojileri (IIS/SharePoint)/network protokollerinin çalışma ve sıkılaştırma mimarileri uzmanı, kurumsal sistem yapılandırmaları değerlendirme/olay müdahaleleri/iyileştirme/kurtarma planı yönetimi konusunda ileri seviyede deneyimli, güvenli yazılım geliştirme süreçleri bilgisi, SOME (Siber Olaylara Müdahale Ekibi) kurulum/yönetim/işleyişi uzmanı, Bash/Perl/Python/VBScript/PowerShell/PHP ortamlarında script geliştirme konusunda ileri seviyede programlama bilgisi, Dark Web/MITRE ATT&CK/CVE platformları konusunda uzman profesyoneller."""
    },

    "is_analisti": {
        "name": "İş Analisti",
        "salary_multipliers": [2],
        "job_description_file": "is_analisti_2x.txt",
        "categories": ["professional_experience", "theoretical_knowledge", "practical_application"],
        "description": """C Grubu kadrolar için iş analisti pozisyonu.
        
ZORUNLU NİTELİKLER: Nesne tabanlı analiz ve tasarım yöntemleri bilgisi, süreç yönetimi/süreç analizi/süreç modelleme/süreç iyileştirme konusunda deneyimli, test süreçleri ve test senaryoları üretme/uygulama konusunda bilgili, iş süreçlerinin modellenmesi ve analizi için şablonlar/formlar/prosedürler bilgisi, iş akışı grafikleri hazırlama ve ilgili yazılımları (Balsamiq/MS Visio/Smartdraw/MS Project) kullanan, kamu kurumları web servisleri ve servis entegrasyonları konusunda bilgili, SoapUI/Postman/ThunderClient gibi web servis ve API test araçlarını kullanan, TFS ve/veya JIRA araçları deneyimi, web teknolojileri alanında iş analizi çıkarma/UX & Usability çalışmaları bilgisi, Agile süreçleri bilgisi, yazılım proje yönetimi konusunda deneyimli profesyoneller.

TERCİH EDİLEN NİTELİKLER: SQL konusunda bilgi sahibi olmak."""
    }
}

def get_role_config(role_code: str) -> dict:
    """
    Rol koduna göre konfigürasyon bilgilerini döndür.
    
    Args:
        role_code (str): Rol kodu (örn: 'yazilim_gelistirici')
        
    Returns:
        dict: Rol konfigürasyon bilgileri
        
    Raises:
        KeyError: Tanımlanmamış rol kodu için
    """
    if role_code not in ROLES:
        available_roles = list(ROLES.keys())
        raise KeyError(f"Tanımlanmamış rol: {role_code}. Mevcut roller: {available_roles}")
    
    return ROLES[role_code]

def get_available_roles() -> list:
    """
    Mevcut tüm rollerin listesini döndür.          
    
    Returns:
        list: [(kod, isim)] formatında rol listesi
    """
    return [(code, config["name"]) for code, config in ROLES.items()]

def validate_role_config(role_code: str, salary_multiplier: int) -> bool:
    """
    Rol ve maaş katsayısı kombinasyonunu doğrular.
    
    Args:
        role_code (str): Rol kodu
        salary_multiplier (int): Maaş katsayısı
        
    Returns:
        bool: Geçerli kombinasyon ise True
    """
    try:
        role_config = get_role_config(role_code)
        return salary_multiplier in role_config["salary_multipliers"]
    except KeyError:
        return False