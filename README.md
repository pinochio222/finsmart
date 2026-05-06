# FinSmart — Quản Lý Tài Chính Thông Minh

> Ứng dụng quản lý tài chính cá nhân dành cho sinh viên Việt Nam  
> **Django 5.2 (Python 3.11) · Bootstrap 5 · Chart.js · Groq AI · SQL Server / PostgreSQL**

---

## Mục lục

1. [Giới thiệu](#1-giới-thiệu)
2. [Tính năng](#2-tính-năng)
3. [Tech Stack](#3-tech-stack)
4. [Cấu trúc dự án](#4-cấu-trúc-dự-án)
5. [Cài đặt & Chạy Local](#5-cài-đặt--chạy-local)
6. [Cấu hình Database](#6-cấu-hình-database)
7. [Tài khoản demo](#7-tài-khoản-demo)
8. [Hướng dẫn sử dụng](#8-hướng-dẫn-sử-dụng)
9. [AI Chatbot](#9-ai-chatbot)

---

## 1. Giới thiệu

**FinSmart** là ứng dụng web quản lý tài chính cá nhân được thiết kế đặc biệt cho sinh viên Việt Nam. Ứng dụng giúp theo dõi thu nhập, chi tiêu, lập ngân sách và đặt mục tiêu tiết kiệm — tất cả trong một giao diện tiếng Việt thân thiện, responsive, không cần cài đặt bất kỳ phần mềm nào phía client.

Điểm nổi bật là tính năng **AI Tư vấn** sử dụng mô hình ngôn ngữ lớn **Llama 3.3-70B** (qua Groq API) để phân tích tài chính và đưa ra lời khuyên cá nhân hóa bằng tiếng Việt.

Kiến trúc: **MVT** (Model — View — Template) của Django.

---

## 2. Tính năng

### Xác thực người dùng
- Đăng ký tài khoản với họ tên, email, mật khẩu
- Validation tiếng Việt: tối thiểu 8 ký tự, phải có chữ cái, không quá đơn giản
- Đăng nhập / Đăng xuất bảo mật qua Django session
- Mỗi người dùng có dữ liệu hoàn toàn riêng biệt

### Dashboard Tổng quan
- Số dư hiện tại (xanh khi dương, đỏ khi âm)
- Tổng thu nhập và tổng chi tiêu trong tháng
- Biểu đồ tròn (Chart.js) — phân bổ chi tiêu theo danh mục
- Biểu đồ cột — thu nhập vs chi tiêu 6 tháng gần nhất
- 5 giao dịch gần nhất
- Cảnh báo ngân sách vượt hạn mức
- Tiến độ mục tiêu tiết kiệm
- Gợi ý nhanh từ AI

### Quản lý Giao dịch
- Thêm giao dịch thu nhập hoặc chi tiêu (mô tả, số tiền VNĐ, ngày, danh mục, ghi chú)
- Danh sách dạng bảng với bộ lọc theo tháng/năm, loại, danh mục
- Sửa và xóa giao dịch

### Quản lý Danh mục
- 16 danh mục mặc định đa màu sắc (ăn uống, di chuyển, học tập, lương...)
- Thêm danh mục tùy chỉnh (tên, màu sắc, loại thu/chi)
- Sửa và **xóa** cả danh mục tự tạo lẫn danh mục mặc định
- Modal xác nhận trước khi xóa (cảnh báo nếu xóa danh mục mặc định)

### Quản lý Ngân sách
- Tạo ngân sách cho từng danh mục theo tháng/năm
- Thanh tiến độ: xanh (< 80%), vàng (80–100%), đỏ (> 100%)
- Cảnh báo vượt ngân sách tức thì
- Sửa / xóa ngân sách

### Mục tiêu Tiết kiệm
- Tạo mục tiêu với tên, số tiền, ngày deadline
- Nạp tiền vào mục tiêu (cộng dồn từng lần)
- Thanh tiến độ %, số ngày còn lại, số tiền cần tiết kiệm mỗi ngày
- Badge trạng thái: Đang thực hiện / Hoàn thành / Quá hạn

### AI Tư vấn Tài chính
- Chatbot Llama 3.3-70B (Groq API) — miễn phí, không cần key riêng
- Tự động đính kèm dữ liệu tài chính thực của người dùng vào prompt
- 4 câu gợi ý nhanh (click để hỏi ngay)
- Lưu và xóa lịch sử chat

### Hồ sơ Cá nhân
- Cập nhật họ tên, đổi mật khẩu
- Thống kê tài khoản: ngày tham gia, tổng giao dịch, số danh mục

### Trang Quản trị (Django Admin)
- Quản lý toàn bộ dữ liệu: Users, Categories, Transactions, Budgets, Goals
- Truy cập tại `/admin/`

---

## 3. Tech Stack

| Thành phần | Công nghệ | Phiên bản |
|-----------|----------|----------|
| Ngôn ngữ backend | Python | 3.11 |
| Web framework | Django (MVT pattern) | 5.2 |
| Production server | Gunicorn | 25.3 |
| Static files | WhiteNoise | — |
| Database chính | Microsoft SQL Server | 2019+ |
| Database dự phòng | PostgreSQL | 14+ |
| Django–SQL Server | mssql-django | 1.7 |
| ORM | Django ORM (thuần — không dùng thư viện thứ ba) | — |
| CSS Framework | Bootstrap | 5.3 |
| Biểu đồ | Chart.js | 4.4 |
| Icons | Bootstrap Icons | 1.11 |
| Template | Django HTML Templates (server-side render) | — |
| AI Chatbot | Groq API — llama-3.3-70b-versatile | — |
| Auth | Django built-in (session-based) | — |
| Timezone | Asia/Ho_Chi_Minh | — |

> Không sử dụng bất kỳ JavaScript framework nào (React, Vue, Angular). Toàn bộ giao diện render phía server.

---

## 4. Cấu trúc dự án

```
finsmart_django/
├── finsmart/                        # Django project config
│   ├── settings.py                  # Cài đặt: DB, apps, static, Groq...
│   ├── urls.py                      # URL routing gốc
│   └── wsgi.py                      # WSGI entry point (Gunicorn)
│
├── finance/                         # App quản lý tài chính
│   ├── models.py                    # Category, Transaction, Budget, Goal,
│   │                                #   ChatMessage, AISuggestion
│   ├── views.py                     # Tất cả views: auth, CRUD, AI chat
│   ├── forms.py                     # Django Forms + validation tiếng Việt
│   ├── urls.py                      # URL patterns của app
│   └── management/commands/
│       ├── seed_categories.py       # Tạo 16 danh mục mặc định
│       ├── create_test_user.py      # Tạo tài khoản demo
│       └── create_superuser_auto.py # Tạo admin tự động
│
├── templates/finance/               # HTML templates (Bootstrap 5)
│   ├── base.html                    # Layout: sidebar + navbar + messages
│   ├── login.html / register.html
│   ├── dashboard.html               # Chart.js biểu đồ tròn + cột
│   ├── transactions.html            # Danh sách + bộ lọc
│   ├── transaction_form.html        # Thêm / sửa giao dịch
│   ├── categories.html              # Card danh mục + modal xóa
│   ├── budgets.html                 # Thanh tiến độ ngân sách
│   ├── goals.html                   # Mục tiêu + nạp tiền
│   ├── ai_chat.html                 # Giao diện chat AI
│   └── profile.html
│
├── static/
│   └── css/custom.css               # CSS tùy chỉnh
│
├── migrations/                      # Django migrations
│   ├── 0001_initial.py
│   ├── 0002_userprofile.py
│   └── 0003_chatmessage_session_key.py
│
└── manage.py
```

### Models

```python
Category     # id, name, type(income/expense), icon, color, is_default, user, created_at
Transaction  # id, user, type, amount, description, note, date, category, created_at
Budget       # id, user, month, year, amount, category, created_at
Goal         # id, user, name, target_amount, current_amount, deadline, icon, created_at
ChatMessage  # id, user, role(user/assistant), content, created_at
AISuggestion # id, user, type, title, message, priority, created_at
```

---

## 5. Cài đặt & Chạy Local

### Yêu cầu hệ thống
- Python 3.11+
- SQL Server 2019+ (hoặc PostgreSQL 14+)
- ODBC Driver 17 for SQL Server *(nếu dùng SQL Server)*

### Bước 1 — Clone và cài packages

```bash
cd finsmart_django

# Cài đặt tất cả packages từ requirements.txt
pip install -r requirements.txt
```

### Bước 2 — Tạo file `.env`

```env
# Chọn loại database: 'mssql' hoặc 'postgresql'
DB_BACKEND=mssql

# SQL Server
MSSQL_HOST=localhost
MSSQL_PORT=1433
MSSQL_DB=FinSmartDB
MSSQL_USER=sa
MSSQL_PASSWORD=YourStrongPassword

# PostgreSQL (nếu DB_BACKEND=postgresql)
DATABASE_URL=postgresql://user:password@localhost:5432/finsmart

# Django
SESSION_SECRET=thay-bang-chuoi-ngau-nhien-dai-32-ky-tu

# Groq AI
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Bước 3 — Tạo database SQL Server

Chạy file `database.sql` trong SQL Server Management Studio (SSMS) hoặc Azure Data Studio:

```sql
-- Mở file và chạy:
-- database.sql
```

Hoặc qua command line:

```bash
sqlcmd -S localhost -U sa -P YourPassword -i database.sql
```

### Bước 4 — Migrate và seed dữ liệu

```bash
cd finsmart_django

# Chạy migrations Django
python manage.py migrate --run-syncdb

# Tạo 16 danh mục mặc định
python manage.py seed_categories

# Tạo tài khoản demo
python manage.py create_test_user

# Tạo tài khoản quản trị viên
python manage.py create_superuser_auto
```

### Bước 5 — Chạy server local

```bash
# Development
python manage.py runserver 0.0.0.0:8000
```

Mở trình duyệt: `http://localhost:8000`

---

## 6. Cấu hình Database

### SQL Server (Khuyến nghị)

Cài ODBC Driver 17 for SQL Server:

**Windows:** Tải tại [https://aka.ms/sqlodbc](https://aka.ms/sqlodbc)

**Ubuntu/Debian:**
```bash
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list \
    | sudo tee /etc/apt/sources.list.d/mssql-release.list
sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql17
```

Cấu hình trong `.env`:
```env
DB_BACKEND=mssql
MSSQL_HOST=localhost       # Tên server hoặc IP
MSSQL_PORT=1433            # Cổng mặc định SQL Server
MSSQL_DB=FinSmartDB        # Tên database (tạo trước bằng SSMS)
MSSQL_USER=sa              # Tài khoản SQL Server Authentication
MSSQL_PASSWORD=Abc@12345   # Mật khẩu (tối thiểu 8 ký tự, có chữ hoa/số/ký tự đặc biệt)
```

**Windows Authentication** (không cần user/password):
```python
# Trong settings.py → OPTIONS:
'Trusted_Connection': 'yes',
```

### PostgreSQL

```env
DB_BACKEND=postgresql
DATABASE_URL=postgresql://username:password@localhost:5432/finsmart
```

### SQLite (chỉ dev, không cần cài gì)

```env
# Bỏ trống DB_BACKEND và DATABASE_URL → tự động dùng SQLite
```

---

## 7. Tài khoản demo

| Vai trò | Email | Mật khẩu |
|---------|-------|---------|
| Người dùng thường | test@finsmart.vn | Test123456 |
| Quản trị viên | admin@finsmart.vn | Admin@FinSmart2026 |

---

## 8. Hướng dẫn sử dụng

**Bắt đầu nhanh:**
1. Đăng ký tài khoản → tự động tạo 16 danh mục mặc định
2. Vào **Giao dịch** → thêm thu nhập (lương tháng này)
3. Vào **Ngân sách** → đặt hạn mức chi tiêu từng danh mục
4. Vào **Mục tiêu** → đặt mục tiêu tiết kiệm (mua laptop, du lịch...)
5. Vào **AI Tư vấn** → hỏi chatbot để nhận lời khuyên cá nhân hóa

**Tips:**
- Nhập giao dịch hàng ngày để có báo cáo chính xác
- Dashboard cập nhật theo thời gian thực mỗi lần reload
- Hỏi AI: *"Tôi có thể cắt giảm chi tiêu ở đâu?"*

---

## 9. AI Chatbot

| Thông số | Giá trị |
|---------|---------|
| Provider | Groq (miễn phí) |
| Model | llama-3.3-70b-versatile |
| Ngôn ngữ | Tiếng Việt |
| Endpoint | POST `/ai/chat/` (AJAX JSON) |
| Context | Số dư, thu chi tháng, ngân sách, mục tiêu |

Chatbot nhận dữ liệu tài chính thực của người dùng tự động — không cần nhập thủ công.

---

*Dự án FinSmart — Đồ án môn học Lập trình Web | Năm học 2025–2026*
