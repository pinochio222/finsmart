# FinSmart - Hệ Thống Quản Lý Tài Chính Cá Nhân

FinSmart là một ứng dụng quản lý tài chính cá nhân toàn diện được xây dựng bằng Django. Nó giúp người dùng theo dõi giao dịch, quản lý ngân sách, đặt mục tiêu tài chính và nhận được các gợi ý thông minh được cung cấp bởi AI.

## Các Tính Năng

- Quản Lý Giao Dịch: Ghi chép và phân loại các giao dịch tài chính
- Theo Dõi Ngân Sách: Tạo và giám sát ngân sách trên các danh mục khác nhau
- Mục Tiêu Tài Chính: Đặt và theo dõi tiến trình hướng tới các mục tiêu tài chính
- Gợi Ý AI: Nhận được những hiểu biết sâu sắc được cung cấp bởi AI để đưa ra quyết định tài chính tốt hơn
- Xác Thực Người Dùng: Hệ thống đăng ký và đăng nhập an toàn
- Bảng Điều Khiển Quản Trị: Bảng điều khiển quản trị toàn diện cho quản lý hệ thống
- Phân Tích: Biểu đồ và báo cáo phân tích các dữ liệu tài chính
- Giao Diện Đáp Ứng: Giao diện thân thiện với thiết bị di động được xây dựng bằng Bootstrap

## Yêu Cầu

- Python 3.8+
- Django 3.2+
- PostgreSQL (hoặc SQLite cho phát triển)
- Node.js (cho tài sản tĩnh)

## Cài Đặt

### 1. Clone Repository

```bash
git clone https://github.com/pinochio222/finsmart.git
cd Document-Report-Writer
```

### 2. Tạo Virtual Environment

```bash
# Cho Windows
python -m venv finsmart_django/.venv
finsmart_django\.venv\Scripts\Activate.ps1

# Cho macOS/Linux
python3 -m venv finsmart_django/.venv
source finsmart_django/.venv/bin/activate
```

### 3. Cài Đặt Các Phụ Thuộc

```bash
cd finsmart_django
pip install -r requirements.txt
```

### 4. Cấu Hình Biến Môi Trường

Tạo file `.env` trong thư mục `finsmart_django/` dựa trên `.env.example`:

```bash
cp .env.example .env
```

Chỉnh sửa `.env` và thêm cấu hình của bạn:
```env
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=your-database-url
```

### 5. Thiết Lập Cơ Sở Dữ Liệu

```bash
python manage.py migrate
python manage.py create_superuser_auto
python manage.py seed_categories
python manage.py create_test_user
```

### 6. Tạo Dữ Liệu Test (Tuỳ Chọn)

```bash
python create_test_data.py
```

## Chạy Ứng Dụng

### Máy Chủ Phát Triển

```bash
python manage.py runserver
```

Truy cập ứng dụng tại: `http://localhost:8000`

Bảng điều khiển quản trị: `http://localhost:8000/admin`

### Máy Chủ Sản Xuất

```bash
bash start_production.sh
```

## Cấu Trúc Dự Án

```
finsmart_django/
├── finance/                 # Ứng dụng tài chính chính
│   ├── models.py           # Các mô hình cơ sở dữ liệu
│   ├── views.py            # Các hàm xem
│   ├── urls.py             # Định tuyến URL
│   ├── forms.py            # Định nghĩa biểu mẫu
│   ├── admin.py            # Cấu hình quản trị
│   ├── ai_suggestions.py   # Mô-đun AI
│   ├── signals.py          # Tín hiệu Django
│   ├── management/         # Các lệnh quản lý tùy chỉnh
│   ├── migrations/         # Di chuyển cơ sở dữ liệu
│   ├── templatetags/       # Bộ lọc mẫu tùy chỉnh
│   └── templates/          # Các mẫu HTML
├── finsmart/               # Cài đặt dự án
│   ├── settings.py         # Cài đặt Django
│   ├── urls.py             # Bộ định tuyến URL chính
│   └── wsgi.py             # Cấu hình WSGI
├── static/                 # Tệp tĩnh (CSS, JS)
├── templates/              # Mẫu toàn cục
├── media/                  # Các tệp được tải lên của người dùng
├── manage.py               # Quản lý Django
└── requirements.txt        # Các phụ thuộc Python
```

## Mô Hình Cơ Sở Dữ Liệu

### Các Mô Hình Cốt Lõi
- User (Người Dùng Django Auth)
- UserProfile: Thông tin người dùng mở rộng
- Transaction: Các giao dịch tài chính
- Budget: Lập kế hoạch và theo dõi ngân sách
- Category: Danh mục giao dịch
- Goal: Các mục tiêu tài chính
- ChatMessage: Tin nhắn trò chuyện AI
- AISuggestion: Các gợi ý được tạo bởi AI

## Xác Thực

- Đăng ký và đăng nhập người dùng
- Xác thực dựa trên phiên
- Quản lý người dùng quản trị
- Kiểm soát truy cập dựa trên vai trò

## Các Tính Năng AI

- Gợi ý tài chính được cung cấp bởi AI
- Giám sát cuộc trò chuyện
- Cấu hình lời nhắc
- Quản lý dữ liệu huấn luyện

## Các Tính Năng Quản Trị

- Quản lý người dùng hoàn chỉnh
- Bảng điều khiển phân tích
- Báo cáo hệ thống
- Quản lý hoạt động AI
- Công cụ phân tích dữ liệu

## Lệnh Quản Lý

```bash
# Tạo siêu người dùng tự động
python manage.py create_superuser_auto

# Tạo người dùng test
python manage.py create_test_user

# Khởi tạo danh mục
python manage.py seed_categories

# Sửa biểu tượng mục tiêu
python manage.py fix_goal_icons
```

## Di Chuyển

Để tạo di chuyển mới sau khi thay đổi mô hình:

```bash
python manage.py makemigrations
python manage.py migrate
```

Xem lịch sử di chuyển:

```bash
python manage.py showmigrations
```

## Thử Nghiệm

```bash
python manage.py test
```

## Các Điểm Cuối API

### Xác Thực
- `POST /login` - Đăng nhập người dùng
- `POST /register` - Đăng ký người dùng
- `GET /logout` - Đăng xuất người dùng

### Giao Dịch
- `GET /transactions/` - Danh sách giao dịch
- `POST /transaction/create/` - Tạo giao dịch
- `PUT /transaction/<id>/edit/` - Chỉnh sửa giao dịch
- `DELETE /transaction/<id>/delete/` - Xoá giao dịch
- `POST /transactions/bulk-import/` - Nhập hàng loạt giao dịch

### Ngân Sách
- `GET /budgets/` - Danh sách ngân sách
- `POST /budget/create/` - Tạo ngân sách
- `PUT /budget/<id>/edit/` - Chỉnh sửa ngân sách
- `DELETE /budget/<id>/delete/` - Xoá ngân sách

### Mục Tiêu
- `GET /goals/` - Danh sách mục tiêu
- `POST /goal/create/` - Tạo mục tiêu
- `PUT /goal/<id>/edit/` - Chỉnh sửa mục tiêu
- `DELETE /goal/<id>/delete/` - Xoá mục tiêu
- `POST /goal/<id>/deposit/` - Thêm tiền vào mục tiêu

### Danh Mục
- `GET /categories/` - Danh sách danh mục
- `POST /category/create/` - Tạo danh mục

### Phân Tích
- `GET /dashboard/` - Bảng điều khiển chính
- `GET /analytics/` - Trang phân tích

### Các Tính Năng AI
- `GET /ai/` - Giao diện trò chuyện AI
- `POST /ai/suggest/` - Nhận gợi ý AI

## Công Nghệ Frontend

- Bootstrap 5
- JQuery
- Select2
- FontAwesome Icons
- Bảng điều khiển AdminLTE
- Giao diện Quản trị Jazzmin

## Các Tính Năng Bảo Mật

- Bảo vệ CSRF
- Ngăn chặn SQL injection
- Bảo vệ XSS
- Mã hoá mật khẩu
- Quản lý phiên

## Tài Liệu

Để biết thêm thông tin chi tiết, xem:
- [Hướng dẫn Cài đặt](SETUP.md)
- [Tài Liệu Cơ Sở Dữ Liệu](DONG_BO_DATABASE_HOAN_TAT.md)
- [Hướng dẫn Người Dùng](HUONG_DAN_SU_DUNG_FINSMART.md)
- [Sơ Đồ Tuần Tự](SO_DO_TUAN_TU_CHINH_SUA_NGUOI_DUNG.puml)

## Tác Giả

- pinochio222 - Công việc ban đầu

## Giấy Phép

Dự án này được cấp phép theo Giấy phép MIT - xem tệp LICENSE để biết chi tiết.

## Đóng Góp

1. Fork repository
2. Tạo nhánh tính năng của bạn (`git checkout -b feature/TinhNangLaKy`)
3. Commit các thay đổi của bạn (`git commit -m 'Thêm tính năng nào đó'`)
4. Push đến nhánh (`git push origin feature/TinhNangLaKy`)
5. Mở một Pull Request

## Hỗ Trợ

Để được hỗ trợ, vui lòng gửi email đến pinochio222@example.com hoặc mở một vấn đề trên GitHub.

## Triển Khai

### Sử Dụng Script Sản Xuất

```bash
bash finsmart_django/start_production.sh
```

### Triển Khai Thủ Công

```bash
# Sưu tầm các tệp tĩnh
python manage.py collectstatic --noinput

# Chạy với Gunicorn
gunicorn finsmart.wsgi:application --bind 0.0.0.0:8000
```

## Lịch Sử Phiên Bản

- v1.0.0 - Phát hành ban đầu
  - Quản lý giao dịch
  - Theo dõi ngân sách
  - Các mục tiêu tài chính
  - Gợi ý AI
  - Xác thực người dùng
  - Bảng điều khiển quản trị

## Lộ Trình

- [ ] Ứng dụng di động (React Native)
- [ ] Phân tích nâng cao
- [ ] Hỗ trợ đa tiền tệ
- [ ] Tích hợp ngân hàng
- [ ] Theo dõi đầu tư
- [ ] Báo cáo thuế

## Lời Cảm Ơn

- Cộng đồng Django
- Nhóm Bootstrap
- Bảng điều khiển AdminLTE
- Tất cả những người đóng góp