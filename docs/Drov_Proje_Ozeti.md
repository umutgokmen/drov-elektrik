# Drov Proje Özeti ve Gereksinim Analizi

Bu döküman, sistemdeki mevcut dosyalardan (Excel, Word, PDF) analiz edilen gereksinimleri ve proje kapsamını özetler.

## 1. Proje Amacı
Elektrik panoları / kutuları (ex-proof vb.) için tasarım ve teknik çizim sürecini otomatiğe bağlayacak, prompt ve inputlar ile çalışan bir konfigüratör sistemi geliştirmek.

## 2. Pilot Proje Kapsamı (Şubat 2026)
Odak noktası: **EJB Tipi Kutular**

### A. Kutu Modelleri ve Kapasiteleri
| Kutu Modeli | Ray Sayısı | Maks. Klemens (2.5mm²) | Uzun Kenar M20 Delik | Kısa Kenar M20 Delik |
| :--- | :---: | :---: | :---: | :---: |
| EJB21 | 1 | 30 | 10 | 8 |
| EJB31 | 2 | 52 | 28 | 20 |
| EJB51 | 2 | 80 | 44 | 24 |
| EJB61 | 3 | 92 | 72 | 48 |
| EJB63 | 3 | 92 | 36 | 24 |
| EJB71 | 3 | 110 | 90 | 59 |
| EJB73 | 3 | 110 | 40 | 16 |
| EJB91 | 3 | 140 | 112 | 70 |
| EJB93 | 3 | 140 | 48 | 30 |

### B. Teknik Kurallar
- **Delikler:** Sadece Metrik 20 (M20) boyutu desteklenecek.
- **Klemensler:** Sadece 2.5mm² kesitli klemensler kullanılacak.
- **Montaj:** Delikler arası mesafe ve kenar boşlukları otomatik hesaplanacak.
- **Çıktı:** Otomatik PDF çizimi ve Parça Listesi (BOM).

## 3. Kilometre Taşları (Milestones)
- **07 Şubat 2026:** Boş kutu çizim yeteneği.
- **14 Şubat 2026:** Delik delme/yerleştirme yeteneği.
- **21 Şubat 2026:** Klemens/Ray yerleşimi ve tam çizim.
- **28 Şubat 2026:** Pilot projenin sunumu ve onayı.

## 4. Gelecek Fazlar (Pilot Sonrası)
- Diğer kutu tipleri (ESA, ESP, EJBX, ESX).
- Farklı delik tipleri (NPT, farklı metrik ölçüler).
- Kutu kapağına buton, kumanda kolu, sinyal lambası ekleme.
- Kablo rakoru, kör tapa, havalandırma tapası montaj görselleri.
- DWG formatında çıktı desteği.
