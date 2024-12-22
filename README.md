# İHA Üretim Yönetim Sistemi

## Proje Hakkında
Bu proje, İnsansız Hava Araçları (İHA) üretim sürecini yönetmek için geliştirilmiş bir web uygulamasıdır. Sistem, farklı ekiplerin (kanat, gövde, kuyruk, aviyonik ve montaj) parça üretimini ve İHA montajını koordine etmelerini sağlar.

## Özellikler

### Parça Yönetimi
- **Parça Tipleri**:
  - Kanat
  - Gövde
  - Kuyruk
  - Aviyonik
- **Parça İşlemleri**:
  - Üretim
  - Listeleme
  - Geri dönüşüm (silme)
  - Kullanım durumu takibi
  - İHA tipi bazında uyumluluk kontrolü

### Takım Yönetimi
- **Takımlar**:
  - Kanat Takımı
  - Gövde Takımı
  - Kuyruk Takımı
  - Aviyonik Takımı
  - Montaj Takımı
- **Yetkilendirme**:
  - Her takım sadece kendi parça tipini üretebilir
  - Montaj takımı tüm parçaları görüntüleyebilir
  - Takım bazlı parça üretim ve stok takibi

### İHA Yönetimi
- **İHA Tipleri**:
  - TB2
  - TB3
  - AKINCI
  - KIZILELMA
- **Montaj İşlemleri**:
  - Parça uyumluluk kontrolü
  - Stok kontrolü
  - Montaj kaydı
  - Parça-İHA eşleştirmesi

### Envanter Sistemi
- **Stok Takibi**:
  - Parça bazında stok durumu
  - Kullanılan/kullanılabilir parça sayısı
  - İHA tipi bazında parça ihtiyacı
- **Uyarı Sistemi**:
  - Eksik parça uyarıları
  - Stok dengesizlik uyarıları
  - İHA tipi bazında üretim durumu

## Teknik Özellikler

### Backend
- Python 3.9+
- Django 4.2
- Django REST Framework
- PostgreSQL
- Django Crispy Forms
- Swagger/OpenAPI (API dokümantasyonu)

### Frontend
- Bootstrap 5
- jQuery
- DataTables (Server-side processing)
- AJAX/Fetch API
- Responsive tasarım

### Deployment
- Docker
- Docker Compose
- Nginx
- Gunicorn

### Güvenlik
- Django Authentication
- Permission-based yetkilendirme
- CSRF koruması
- API Token authentication

## API Dokümantasyonu
API dokümantasyonuna aşağıdaki URL'lerden erişilebilir:
- Swagger UI: `/swagger/` - İnteraktif API test arayüzü
- ReDoc: `/redoc/` - Daha detaylı API dokümantasyonu
- OpenAPI Şeması: `/swagger.json` - Raw API şeması

### API Kullanımı
1. Swagger UI'a giriş yapın (`/swagger/`)
2. Sağ üstteki "Authorize" butonuna tıklayın
3. API token'ınızı girin (Bearer [token])
4. Artık tüm API endpoint'lerini test edebilirsiniz

## Test Sistemi

### Unit Testler
Aşağıdaki alanlar için kapsamlı unit testler mevcuttur:

#### Parça Yönetimi Testleri
- Parça oluşturma ve yetkilendirme kontrolü
- Parça silme (geri dönüşüm) işlemleri
- Parça kullanım durumu takibi

#### İHA Montaj Testleri
- Montaj işlemi ve parça durumu güncellemesi
- Parça-İHA tipi uyumluluk kontrolü
- Montaj ekibi yetkilendirmesi

#### Envanter Testleri
- Stok durumu kontrolü
- Parça sayısı ve kullanım durumu takibi
- Envanter uyarı sistemi

#### Takım Yetkilendirme Testleri
- Takım üyesi olmayan kullanıcı erişim kontrolü
- Takımlar arası işlem kısıtlamaları
  - Her takımın kendi parça tipini üretebilmesi
  - Diğer takımların parçalarına erişim kısıtlaması
  - Montaj yetkisi kontrolü

### Test Çalıştırma
```bash
# Tüm testleri çalıştırma
docker-compose exec web python manage.py test

# Belirli bir test sınıfını çalıştırma
docker-compose exec web python manage.py test production.tests.ProductionTests

# Detaylı test çıktısı
docker-compose exec web python manage.py test production.tests.ProductionTests --verbosity=2
```

### Test Kapsamı
- Models: Veri modelleri ve ilişkileri
- Views: HTTP istekleri ve yetkilendirme
- Forms: Form validasyonu ve veri doğrulama
- Permissions: Takım bazlı yetkilendirme sistemi

## Ekran Görüntüleri

### Admin Paneli
Admin panelinden takımları ve kullanıcıları yönetebilirsiniz.

![Admin - Takımlar](/screenshots/admin/takimlar.png)

### Parça Takımları
Her takım kendi parça tipini üretebilir ve yönetebilir.

#### Ana Sayfa
![Parça Takımı - Ana Sayfa](/screenshots/parca_takımları/home.png)

#### Parça Listesi
![Parça Takımı - Parça Listesi](/screenshots/parca_takımları/parça_listesi.png)

#### Yeni Parça Ekleme
![Parça Takımı - Yeni Kanat Ekle](/screenshots/parca_takımları/yeni_kanat_ekle.png)

### Montaj Takımı
Montaj takımı tüm parçaları görüntüleyebilir ve İHA montajı yapabilir.

#### Ana Sayfa
Stok durumu ve envanter uyarıları görüntülenir.
![Montaj Takımı - Ana Sayfa](/screenshots/montaj_takımı/anasayfa.png)

#### İHA Yönetim Sayfası
Montajlanmış İHA'ların listesi ve detayları.
![Montaj Takımı - İHA Yönetimi](/screenshots/montaj_takımı/iha_yönetim_sayfasi.png)

#### İHA'da Kullanılan Parçalar
Her İHA'nın hangi parçalardan oluştuğunu görüntüleyebilirsiniz.
![Montaj Takımı - İHA Parçaları](/screenshots/montaj_takımı/ihada_kullanilan_parcalar.png)

#### Yeni İHA Montaj Kartı
Select2 ile gelişmiş parça seçimi yapabilirsiniz.
![Montaj Takımı - Yeni Montaj](/screenshots/montaj_takımı/yeni_montaj_kartı_select2.png)

## Kurulum

### Gereksinimler
- Docker
- Docker Compose

### Kurulum Adımları
1. Projeyi klonlayın:
```bash
git clone [repo-url]
cd [repo-directory]
```

2. Docker ile projeyi başlatın:
```bash
sudo docker-compose up --build
```

3. Sistemi durdurmak için:
```bash
sudo docker-compose down -v
```

### İlk Kullanım
- Sistem ilk çalıştığında otomatik olarak örnek veriler oluşturulur
- Varsayılan kullanıcı bilgileri:
  - Kullanıcı adı: [ekip_adı]_user (örn: wing_user, body_user, tail_user, avionics_user, assembly_user)
  - Şifre: user123

- Admin kullanıcı bilgileri:
  - Kullanıcı adı: admin
  - Şifre: admin123

## Kullanım Kılavuzu

### Ekip Üyeleri İçin
1. Sisteme giriş yapın
2. Ana sayfada ekibinize ait uyarıları görüntüleyin
3. "Yeni Parça Üret" butonu ile parça üretimi yapın
4. "Parça Listesi" sayfasından:
   - Ürettiğiniz tüm parçaları görüntüleyin
   - Parçaların kullanım durumunu kontrol edin
   - Hangi parçanın hangi İHA'da kullanıldığını görün
   - Kullanılmayan parçaları geri dönüşüme gönderebilirsiniz

### Montaj Ekibi İçin
1. Sisteme giriş yapın
2. Ana sayfada İHA üretimi için gerekli parça durumlarını kontrol edin
3. "Yeni İHA Oluştur" butonu ile montaj işlemi başlatın
4. İHA tipini seçin ve uygun parçaları atayın
5. Montaj tamamlandığında:
   - Seçilen parçalar otomatik olarak 'kullanımda' durumuna geçer
   - İHA'nın seri numarası, montaj tarihi ve montajı yapan ekip üyesi kaydedilir
   - Parça-İHA eşleştirmesi sistem tarafından kaydedilir

## Proje Yapısı
```
uav_production/
├── accounts/           # Kullanıcı ve takım yönetimi
├── api/               # REST API endpoints
├── production/        # Ana uygulama modülü
├── templates/         # HTML şablonları
├── static/           # Statik dosyalar
├── requirements.txt  # Python bağımlılıkları
├── docker-compose.yml
└── Dockerfile
```

## Lisans
Bu proje MIT lisansı ile lisanslanmıştır.
