# FinSmart - Django Finance Management System

A comprehensive personal finance management application built with Django. FinSmart helps users track transactions, manage budgets, set financial goals, and get AI-powered financial suggestions.

## 🚀 Features

- **Transaction Management**: Record and categorize financial transactions
- **Budget Tracking**: Create and monitor budgets across different categories
- **Financial Goals**: Set and track progress toward financial goals
- **AI Suggestions**: Get AI-powered insights and recommendations for better financial decisions
- **User Authentication**: Secure user registration and login system
- **Admin Dashboard**: Comprehensive admin panel for system management
- **Analytics**: Visual analytics and reports for financial data
- **Responsive UI**: Mobile-friendly interface built with Bootstrap

## 📋 Requirements

- Python 3.8+
- Django 3.2+
- PostgreSQL (or SQLite for development)
- Node.js (for static assets)

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/pinochio222/finsmart.git
cd Document-Report-Writer
```

### 2. Create Virtual Environment

```bash
# For Windows
python -m venv finsmart_django/.venv
finsmart_django\.venv\Scripts\Activate.ps1

# For macOS/Linux
python3 -m venv finsmart_django/.venv
source finsmart_django/.venv/bin/activate
```

### 3. Install Dependencies

```bash
cd finsmart_django
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in `finsmart_django/` directory based on `.env.example`:

```bash
cp .env.example .env
```

Edit `.env` and add your configuration:
```env
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=your-database-url
```

### 5. Database Setup

```bash
python manage.py migrate
python manage.py create_superuser_auto
python manage.py seed_categories
python manage.py create_test_user
```

### 6. Create Test Data (Optional)

```bash
python create_test_data.py
```

## 🚀 Running the Application

### Development Server

```bash
python manage.py runserver
```

Access the application at: `http://localhost:8000`

Admin panel: `http://localhost:8000/admin`

### Production Server

```bash
bash start_production.sh
```

## 📁 Project Structure

```
finsmart_django/
├── finance/                 # Main finance app
│   ├── models.py           # Database models
│   ├── views.py            # View functions
│   ├── urls.py             # URL routing
│   ├── forms.py            # Form definitions
│   ├── admin.py            # Admin configuration
│   ├── ai_suggestions.py   # AI module
│   ├── signals.py          # Django signals
│   ├── management/         # Custom management commands
│   ├── migrations/         # Database migrations
│   ├── templatetags/       # Custom template filters
│   └── templates/          # HTML templates
├── finsmart/               # Project settings
│   ├── settings.py         # Django settings
│   ├── urls.py             # Main URL router
│   └── wsgi.py             # WSGI configuration
├── static/                 # Static files (CSS, JS)
├── templates/              # Global templates
├── media/                  # User uploaded files
├── manage.py               # Django management
└── requirements.txt        # Python dependencies
```

## 💾 Database Models

### Core Models
- **User** (Django Auth User)
- **UserProfile**: Extended user information
- **Transaction**: Financial transactions
- **Budget**: Budget planning and tracking
- **Category**: Transaction categories
- **Goal**: Financial goals
- **ChatMessage**: AI chat messages
- **AISuggestion**: AI-generated suggestions

## 🔐 Authentication

- User registration and login
- Session-based authentication
- Admin user management
- Role-based access control

## 🤖 AI Features

- AI-powered financial suggestions
- Conversation monitoring
- Prompt configuration
- Training data management

## 📊 Admin Features

- Complete user management
- Analytics dashboard
- System reports
- AI operations management
- Data analysis tools

## 🔧 Management Commands

```bash
# Create superuser automatically
python manage.py create_superuser_auto

# Create test user
python manage.py create_test_user

# Seed categories
python manage.py seed_categories

# Fix goal icons
python manage.py fix_goal_icons
```

## 📝 Migrations

To create new migrations after model changes:

```bash
python manage.py makemigrations
python manage.py migrate
```

View migration history:

```bash
python manage.py showmigrations
```

## 🧪 Testing

```bash
python manage.py test
```

## 📚 API Endpoints

### Authentication
- `POST /login` - User login
- `POST /register` - User registration
- `GET /logout` - User logout

### Transactions
- `GET /transactions/` - List transactions
- `POST /transaction/create/` - Create transaction
- `PUT /transaction/<id>/edit/` - Edit transaction
- `DELETE /transaction/<id>/delete/` - Delete transaction
- `POST /transactions/bulk-import/` - Bulk import transactions

### Budgets
- `GET /budgets/` - List budgets
- `POST /budget/create/` - Create budget
- `PUT /budget/<id>/edit/` - Edit budget
- `DELETE /budget/<id>/delete/` - Delete budget

### Goals
- `GET /goals/` - List goals
- `POST /goal/create/` - Create goal
- `PUT /goal/<id>/edit/` - Edit goal
- `DELETE /goal/<id>/delete/` - Delete goal
- `POST /goal/<id>/deposit/` - Add deposit to goal

### Categories
- `GET /categories/` - List categories
- `POST /category/create/` - Create category

### Analytics
- `GET /dashboard/` - Main dashboard
- `GET /analytics/` - Analytics page

### AI Features
- `GET /ai/` - AI chat interface
- `POST /ai/suggest/` - Get AI suggestions

## 🎨 Frontend Technologies

- Bootstrap 5
- JQuery
- Select2
- FontAwesome Icons
- AdminLTE Dashboard
- Jazzmin Admin Interface

## 🔒 Security Features

- CSRF protection
- SQL injection prevention
- XSS protection
- Password hashing
- Session management

## 📖 Documentation

For more detailed information, see:
- [Setup Guide](SETUP.md)
- [Database Documentation](DONG_BO_DATABASE_HOAN_TAT.md)
- [User Guide](HUONG_DAN_SU_DUNG_FINSMART.md)
- [Sequence Diagrams](SO_DO_TUAN_TU_CHINH_SUA_NGUOI_DUNG.puml)

## 👤 Author

- **pinochio222** - Initial work

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📧 Support

For support, email pinochio222@example.com or open an issue on GitHub.

## 🚀 Deployment

### Using Production Script

```bash
bash finsmart_django/start_production.sh
```

### Manual Deployment

```bash
# Collect static files
python manage.py collectstatic --noinput

# Run with Gunicorn
gunicorn finsmart.wsgi:application --bind 0.0.0.0:8000
```

## 📝 Version History

- **v1.0.0** - Initial release
  - Transaction management
  - Budget tracking
  - Financial goals
  - AI suggestions
  - User authentication
  - Admin dashboard

## 🎯 Roadmap

- [ ] Mobile app (React Native)
- [ ] Advanced analytics
- [ ] Multi-currency support
- [ ] Bank integration
- [ ] Investment tracking
- [ ] Tax reporting

## 🙏 Acknowledgments

- Django community
- Bootstrap team
- AdminLTE dashboard
- All contributors