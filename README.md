<p align="center">
  <img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white" />
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" />
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" />
  <img src="https://img.shields.io/badge/REST_API-FF6F00?style=for-the-badge&logo=fastapi&logoColor=white" />
</p>

# Project Management - Web

> **Subsistem Manajemen Proyek, Tugas, dan Timeline**
>
> Bagian dari ekosistem **Intelligence System** - Platform Terintegrasi untuk Siklus Hidup Pengembangan Kecerdasan Buatan.

## Tentang Proyek

**Intelligence Engineerings** adalah platform terintegrasi yang dirancang untuk mendukung seluruh siklus hidup (*lifecycle*) pengembangan proyek berbasis kecerdasan buatan (AI). Platform ini dikembangkan sebagai bagian dari mata kuliah **Sistem Cerdas Blok** di **Universitas Trisakti**, dengan tujuan memberikan pengalaman langsung kepada mahasiswa dalam membangun sistem perangkat lunak berskala besar yang saling terintegrasi.

Platform ini terdiri dari **5 subsistem** yang masing-masing menangani fase berbeda dalam *lifecycle* pengembangan AI:

| No | Subsistem | Deskripsi |
|----|-----------|-----------|
| 1 | **Intelligence Engineering** | Perencanaan & perancangan blueprint proyek AI |
| 2 | **Project Management** | Manajemen proyek, tugas, dan timeline |
| 3 | **Intelligence Creation** | Pembuatan & pelatihan model machine learning |
| 4 | **Dataset Management** | Pengelolaan dataset dan distribusi data |
| 5 | **Implementation** | Deployment, monitoring, dan pemeliharaan model AI |

Aplikasi web ini merupakan sistem utama untuk subsistem **Project Management**, yang bertindak sebagai pusat koordinasi proyek AI dengan fitur manajemen pekerjaan, aktivitas, dan pelaporan tugas antar subsistem.

## Fitur Utama

- **Dashboard Proyek** - Tampilan ringkasan seluruh proyek beserta status dan progres pekerjaan
- **Manajemen Proyek (CRUD)** - Buat, lihat, edit, dan hapus proyek dengan informasi pelaksana, pengawas, lokasi, dan timeline
- **Manajemen Pekerjaan** - Kelola pekerjaan per proyek dengan kategorisasi Engineering, Creation, dan Implementation
- **Manajemen Aktivitas** - Catat aktivitas detail untuk setiap pekerjaan, lengkap dengan evaluasi dan rencana tambahan
- **Bukti Aktivitas** - Upload bukti berupa file dan gambar untuk setiap aktivitas yang dilaporkan
- **Task Submission** - Sistem pengumpulan tugas antar subsistem dengan status tracking (Draft, Submitted, Reviewed, Approved, Rejected)
- **Task Report** - Halaman laporan tugas dengan filter dan ringkasan per kategori subsistem
- **Export PDF & Excel** - Export laporan proyek dan semua data ke format PDF dan Excel
- **Profile Management** - Pengaturan profil pengguna dengan NIM dan foto profil
- **Cross-System Integration** - Sinkronisasi proyek dengan Intelligence Engineering, Intelligence Creation, dan Implementation

## Tech Stack

| Teknologi | Versi | Keterangan |
|-----------|-------|------------|
| Python | 3.12 | Bahasa pemrograman utama |
| Django | 5.0 | Web framework |
| Django REST Framework | 3.14 | API layer |
| PyJWT | 2.8 | Token-based authentication |
| ReportLab | 4.1 | PDF generation |
| openpyxl | 3.1 | Excel generation |
| JavaScript | ES6+ | Frontend interactivity |
| TailwindCSS | CDN | Styling framework |
| SQLite | 3 | Database |
| Docker | Latest | Containerization |
| Nginx | Alpine | Reverse proxy |
| Gunicorn | 21.2 | WSGI HTTP server |

## Getting Started

### Prerequisites

- [Python](https://www.python.org/downloads/) (>= 3.10)
- [Docker](https://docs.docker.com/get-docker/) (untuk deployment via container)
- Git

### Installation (Local Development)

```bash
# Clone repository
git clone <repository-url>

# Masuk ke direktori proyek
cd "Project Management/backend"

# Buat virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Jalankan migrasi database
python manage.py migrate

# Jalankan development server
python manage.py runserver
```

### Deployment (Docker)

```bash
# Dari root project (folder yang berisi docker-compose.yml)
docker compose up -d --build pm_web

# Akses di browser
# http://localhost/tif2/pm/
```

### Konfigurasi

Pengaturan utama terdapat di `backend/settings.py`. Untuk deployment, pastikan variabel environment berikut sudah dikonfigurasi:

```
DEBUG=0
DJANGO_SETTINGS_MODULE=backend.settings
FORCE_SCRIPT_NAME=/tif2/pm
```

## Struktur Proyek

```
backend/
|-- manage.py
|-- requirements.txt
|-- Dockerfile
|-- entrypoint.sh
|-- backend/                 # Konfigurasi Django
|   |-- settings.py
|   |-- urls.py
|   +-- wsgi.py
|-- api/                     # Aplikasi utama
|   |-- models.py            # User, Proyek, Pekerjaan, Aktivitas, BuktiAktivitas, TaskSubmission
|   |-- views.py             # View functions & API endpoints
|   |-- views_export.py      # Export PDF & Excel
|   |-- urls.py              # URL routing
|   |-- serializers.py       # DRF serializers
|   |-- authentication.py    # JWT authentication
|   |-- permissions.py       # Custom permissions
|   |-- templates/           # HTML templates
|   |   |-- home.html        # Landing page
|   |   |-- projects.html    # Daftar proyek & manajemen
|   |   |-- project_detail.html  # Detail proyek + pekerjaan + aktivitas
|   |   |-- work_detail.html # Detail pekerjaan
|   |   |-- task_report.html # Laporan tugas
|   |   |-- submissions.html # Pengumpulan tugas
|   |   |-- profile.html     # Profil pengguna
|   |   +-- about.html       # Tentang kami
|   +-- static/              # Static assets (CSS, JS)
+-- users/                   # User management module
```

## API Endpoints

### Autentikasi

| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| POST | `/api/auth/register/` | Registrasi akun baru |
| POST | `/api/auth/login/` | Login dan dapatkan JWT token |
| POST | `/api/auth/logout/` | Logout |

### Proyek & Pekerjaan

| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| GET/POST | `/api/proyek/` | List & create proyek |
| GET/PUT/DELETE | `/api/proyek/<id>/` | Detail, update, hapus proyek |
| GET/POST | `/api/pekerjaan/` | List & create pekerjaan |
| GET/PUT/DELETE | `/api/pekerjaan/<id>/` | Detail, update, hapus pekerjaan |
| GET/POST | `/api/aktivitas/` | List & create aktivitas |
| GET/POST | `/api/bukti-aktivitas/` | Upload bukti aktivitas |
| GET/POST | `/api/task-submissions/` | Pengumpulan tugas |

### Export & Report

| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| GET | `/api/reports/all/pdf/` | Export semua proyek ke PDF |
| GET | `/api/reports/all/excel/` | Export semua proyek ke Excel |
| GET | `/api/reports/project/<id>/pdf/` | Export proyek spesifik ke PDF |
| GET | `/api/reports/project/<id>/excel/` | Export proyek spesifik ke Excel |

### Integrasi

| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| POST | `/api/integration/sync/` | Sinkronisasi status integrasi |

## Integrasi Antar-Subsistem

Project Management bertindak sebagai pusat koordinasi dan terintegrasi dengan subsistem lain:

| Arah | Subsistem | Mekanisme |
|------|-----------|-----------|
| PM -> IE | Intelligence Engineering | Kirim project assignment untuk dibuatkan blueprint |
| PM -> IC | Intelligence Creation | Kirim project assignment untuk pembuatan model |
| PM -> IMPL | Implementation | Kirim project assignment untuk deployment |
| IE -> PM | Intelligence Engineering | Terima update status blueprint proyek |

## Dokumentasi

| Dokumen | Link |
|---------|------|
| User Guide | [Download PDF](https://drive.google.com/file/d/1WTeHLY9JuE3rY4PTO3hp7VTAXNJax0UE/view?usp=sharing) |
| UML Diagrams (APPL) | [Download PDF](https://drive.google.com/file/d/1feMkxV2QAGJ4yXbWxB_K1bZZDuGjGf61/view?usp=sharing) |
| Live Demo | [Open Web App](http://38.47.94.194/tif2/pm/) |

## Subsistem Terkait

| Subsistem | Web | Mobile |
|-----------|-----|--------|
| Intelligence Engineering | [Repository](../../../Intelligence%20Engineering/ie_project) | [GitHub](https://github.com/faturrachmanhuda/intelligence-engineering-mobile) |
| Project Management | *You are here* | [GitHub](https://github.com/faturrachmanhuda/project-management-mobile) |
| Intelligence Creation | [Repository](../../../Intelligence%20Creation) | [GitHub](https://github.com/faturrachmanhuda/intelligence-creation-mobile) |
| Dataset Management | [Repository](../../../Dataset%20Management) | [GitHub](https://github.com/faturrachmanhuda/dataset-management-mobile) |
| Implementation | [Repository](../../../Implementation/main_web) | [GitHub](https://github.com/faturrachmanhuda/implementation-mobile) |

## Tim Pengembang

Dikembangkan oleh mahasiswa **Universitas Trisakti**, Fakultas Teknologi Industri, Program Studi Teknik Informatika.

## Lisensi

Proyek ini dikembangkan untuk keperluan akademis dalam rangka mata kuliah **Sistem Cerdas Blok**.

<p align="center">
  <b>Intelligence Engineerings</b> - Integrated AI Development Lifecycle Platform<br/>
  <sub>Universitas Trisakti | 2024/2025</sub>
</p>
