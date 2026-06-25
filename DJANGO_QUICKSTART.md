# 🚀 Django Quickstart - ProManage

Aplikasi ProManage sekarang fully integrated dengan Django! Semua halaman (Home, Projects, About, dll) di-render oleh Django templates.

## ✅ Setup & Run

### 1. Install Dependencies
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Setup Database
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. (Optional) Create Test Data
```bash
python manage.py shell < create_test_data.py
```

Test credentials:
- Email: `test@promanage.com`
- Password: `password123`

### 4. Run Server
```bash
python manage.py runserver
```

Aplikasi berjalan di: **http://localhost:8000**

## 📄 Halaman Yang Tersedia

| URL | Deskripsi | Template |
|-----|-----------|----------|
| `/` | Home page | `api/templates/home.html` |
| `/about` | About page | `api/templates/about.html` |
| `/projects` | Project management (perlu login) | `api/templates/projects.html` |
| `/projects/<id>/` | Project detail | `api/templates/project_detail.html` |
| `/works/<id>/` | Work detail | `api/templates/work_detail.html` |
| `/admin` | Django admin panel | Built-in |

## 🔌 API Endpoints (untuk template)

Templates menggunakan JavaScript untuk call API:

| Endpoint | Method | Deskripsi |
|----------|--------|-----------|
| `/api/auth/register/` | POST | Register user |
| `/api/auth/login/` | POST | Login user |
| `/api/projects/` | GET | List projects |
| `/api/projects/` | POST | Create project |
| `/api/projects/<id>/` | GET | Project detail |
| `/api/works/by_project/?project_id=<id>` | GET | Works by project |
| `/api/activities/by_work/?work_id=<id>` | GET | Activities by work |

## 🎨 Templates Structure

```
backend/
└── api/
    └── templates/
        ├── base.html                  # Base template
        ├── home.html                  # Home page
        ├── about.html                 # About page
        ├── projects.html              # Projects list
        ├── project_detail.html        # Project detail
        ├── work_detail.html           # Work detail
        └── components/
            ├── header.html            # Header component
            └── login_modal.html       # Login/Register modal
```

## 🔑 Authentication Flow

1. User buka `/` (home)
2. Klik "Mulai Sekarang" atau "Login" → Modal login muncul
3. Login/Register → Token disimpan di `localStorage`
4. Redirect ke `/projects`
5. Templates pakai JavaScript + API untuk CRUD data

## 💻 Technology Stack

### Frontend (Templates)
- Django Templates
- Tailwind CSS (CDN)
- Vanilla JavaScript
- Lucide Icons (CDN)

### Backend
- Django 5.0
- Django REST Framework
- JWT Authentication
- SQLite (dev) / PostgreSQL (prod)

## 🔧 Development

### Create Superuser
```bash
python manage.py createsuperuser
```

### Access Admin Panel
http://localhost:8000/admin

### Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Reset Database
```bash
rm db.sqlite3
python manage.py migrate
```

## 📝 Fitur Yang Sudah Terintegrasi

- ✅ Home page dengan hero section
- ✅ About page dengan team info
- ✅ Projects page (list & create)
- ✅ Project detail page
- ✅ Work detail page
- ✅ Login/Register modal
- ✅ Header dengan authentication status
- ✅ Toast notifications
- ✅ Responsive design (mobile & desktop)
- ✅ JWT token authentication
- ✅ API integration via JavaScript

## 🚧 Fitur Yang Perlu Ditambahkan

- [ ] Form wizard untuk create project
- [ ] Inline edit untuk rename
- [ ] Upload foto dokumentasi
- [ ] Delete & update functionality
- [ ] Modal untuk tambah work & activity
- [ ] Evaluasi form
- [ ] Project close/archive

## 🐛 Troubleshooting

### Template Not Found
Pastikan `TEMPLATES['DIRS']` sudah include `BASE_DIR / 'api' / 'templates'` di `backend/settings.py`

### Static Files Not Loading
Jalankan `python manage.py collectstatic` untuk production

### CORS Error
Check `CORS_ALLOWED_ORIGINS` di `settings.py`

### 404 on API Calls
Pastikan URL di JavaScript pakai `/api/` prefix

## 📚 Documentation

- [Django Docs](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Tailwind CSS](https://tailwindcss.com/)

---

**🎉 Aplikasi sekarang fully integrated dengan Django!**

Tidak perlu lagi `npm` atau `pnpm` untuk development. Cukup jalankan `python manage.py runserver` dan semua sudah jalan!
