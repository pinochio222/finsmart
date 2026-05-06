# FinSmart Local Development Setup Guide

## 🚀 Quick Start

### 1. Chuẩn bị môi trường

```bash
# Vào thư mục chính
cd finsmart_django

# Tạo virtual environment
python -m venv .venv

# Activate venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
```

### 2. Cài đặt packages

```bash
pip install -r requirements.txt
```

### 3. Cấu hình environment

Copy `.env.example` thành `.env` và điền cấu hình:

```env
DB_BACKEND=mssql

# SQL Server
MSSQL_HOST=localhost
MSSQL_PORT=1433
MSSQL_DB=FinSmartDB
MSSQL_USER=sa
MSSQL_PASSWORD=YourStrongPassword

# Django
SESSION_SECRET=your-secret-key-32-char-minimum

# Groq AI (optional)
GROQ_API_KEY=gsk_your_key_here
```

### 4. Setup Database

**Option A: SQL Server**
- Chạy file `../database.sql` trong SSMS hoặc Azure Data Studio
- Hoặc qua command line:
  ```bash
  sqlcmd -S localhost -U sa -P YourPassword -i ../database.sql
  ```

**Option B: PostgreSQL**
```env
DB_BACKEND=postgresql
DATABASE_URL=postgresql://user:password@localhost:5432/finsmart
```

### 5. Migrate & Seed Data

```bash
# Chạy migrations
python manage.py migrate --run-syncdb

# Tạo 16 danh mục mặc định
python manage.py seed_categories

# Tạo admin account
python manage.py create_superuser_auto

# (Optional) Tạo test user
python manage.py create_test_user
```

### 6. Chạy server

```bash
python manage.py runserver 0.0.0.0:8000
```

Mở trình duyệt:
- **App:** http://localhost:8000/
- **Admin Jazzmin:** http://localhost:8000/admin/

## 📊 Admin Panel (Jazzmin)

Cấu hình trong `finsmart/settings.py`:

- **Theme:** Lux (clean, modern)
- **Dark Mode:** Slate
- **Features:** Search, task log, custom icons
- **Icons:** Tùy chỉnh cho mỗi model (Category, Transaction, Budget, Goal...)

### Tài khoản Admin mặc định:
- **Email:** admin@finsmart.vn
- **Password:** Admin@FinSmart2026

(Được tạo tự động bởi `create_superuser_auto`)

## 🛠️ Management Commands

```bash
# Tạo 16 danh mục mặc định
python manage.py seed_categories

# Tạo tài khoản admin tự động
python manage.py create_superuser_auto

# Tạo tài khoản test user
python manage.py create_test_user

# Tạo migrations từ models
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput
```

## 📁 File Structure

```
finsmart_django/
├── finsmart/                 # Django config
│   ├── settings.py          # Settings + Jazzmin config
│   ├── urls.py              # URL routing
│   └── wsgi.py
├── finance/                 # Main app
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   └── management/commands/
└── templates/finance/       # HTML templates
```

## 🐛 Troubleshooting

**Error: "msodbcsql can't connect"**
- Cài ODBC Driver 17 for SQL Server
- Tải: https://aka.ms/sqlodbc

**Error: "ModuleNotFoundError: No module named 'X'"**
- Chạy: `pip install -r requirements.txt`

**Database connection error**
- Kiểm tra `.env` có đúng connection string không
- Kiểm tra SQL Server có chạy không

## 📝 Notes

- Tất cả dữ liệu riêng biệt per user
- Theme Jazzmin có thể thay đổi trong settings
- Static files được serve bởi WhiteNoise
- Các icon Font Awesome v6 được cấu hình sẵn

---

**Ready to dev!** 🚀
