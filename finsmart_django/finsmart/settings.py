import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SESSION_SECRET', 'django-finsmart-dev-secret-2025-abc')

# Auto-detect production: DEBUG=False when REPLIT_DEPLOYMENT is set
IS_PRODUCTION = os.environ.get('REPLIT_DEPLOYMENT', '') == '1'
DEBUG = not IS_PRODUCTION

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'crispy_forms',
    'crispy_bootstrap5',
    'finance',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'finsmart.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'finsmart.wsgi.application'

# ── Cấu hình Database: Microsoft SQL Server ───────────────────
# Package: mssql-django 1.7 + pyodbc
# Driver:  ODBC Driver 17 for SQL Server
# Tham khảo: https://github.com/microsoft/mssql-django
#
# Khi chạy LOCAL: điền MSSQL_* vào file .env → dùng SQL Server

_mssql_password = os.environ.get('MSSQL_PASSWORD', '')
_database_url = os.environ.get('DATABASE_URL', '')
_mssql_trusted = os.environ.get('MSSQL_TRUSTED_CONNECTION', '').lower() in {'1', 'true', 'yes'}
_mssql_driver = os.environ.get('MSSQL_DRIVER', 'ODBC Driver 18 for SQL Server')
_mssql_encrypt = os.environ.get('MSSQL_ENCRYPT', 'yes')
_mssql_trust_cert = os.environ.get('MSSQL_TRUST_SERVER_CERTIFICATE', 'yes')

if _mssql_password or _mssql_trusted:
    # ── SQL Server (chạy local với file .env) ─────────────────
    _mssql_options = {
        'driver': _mssql_driver,
        'unicode_results': True,
        'extra_params': f'Encrypt={_mssql_encrypt};TrustServerCertificate={_mssql_trust_cert}',
    }
    if _mssql_trusted:
        _mssql_options['extra_params'] += ';Trusted_Connection=yes'

    DATABASES = {
        'default': {
            'ENGINE':   'mssql',
            'NAME':     os.environ.get('MSSQL_DB',   'FinSmartDB'),
            'USER':     '' if _mssql_trusted else os.environ.get('MSSQL_USER', 'sa'),
            'PASSWORD': '' if _mssql_trusted else _mssql_password,
            'HOST':     os.environ.get('MSSQL_HOST', 'localhost'),
            'PORT':     os.environ.get('MSSQL_PORT', '1433'),
            'OPTIONS': _mssql_options,
            'TEST': {'NAME': 'FinSmartDB_Test'},
        }
    }
elif _database_url:
    # ── PostgreSQL (Replit managed — chỉ dùng khi deploy Replit) ──
    import urllib.parse
    _u = urllib.parse.urlparse(_database_url)
    DATABASES = {
        'default': {
            'ENGINE':   'django.db.backends.postgresql',
            'NAME':     _u.path[1:],
            'USER':     _u.username,
            'PASSWORD': _u.password,
            'HOST':     _u.hostname,
            'PORT':     _u.port or 5432,
        }
    }
else:
    raise Exception(
        "Chưa cấu hình database!\n"
        "  Local: thêm MSSQL_PASSWORD hoặc bật MSSQL_TRUSTED_CONNECTION trong file finsmart_django/.env\n"
        "  Replit: đảm bảo DATABASE_URL được cài tự động"
    )

# Password validators are handled in RegisterForm (finance/forms.py)
# with Vietnamese error messages. Built-in validators are disabled
# to avoid duplicate/English error messages.
AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'vi'
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Media files (User uploaded files)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'

CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

JAZZMIN_SETTINGS = {
    "site_title": "FinSmart Admin",
    "site_header": "FinSmart Control",
    "site_brand": "FinSmart",
    "site_logo_classes": "img-circle elevation-2",
    "welcome_sign": "Quan tri he thong FinSmart",
    "copyright": "FinSmart",
    "search_model": ["auth.User", "finance.Category"],  # Fixed: Use registered models only
    "custom_css": "css/admin-premium.css",
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    
    # Custom menu links - Removed invalid URL references
    "custom_links": {
        "finance": [{
            "name": "Báo Cáo Hệ Thống",
            "url": "/admin/system-report/",
            "icon": "fas fa-chart-bar",
            "permissions": ["auth.view_user"]
        }]
    },
    
    "icons": {
        "auth.adminaccount": "fas fa-user-shield",
        "auth.regularuser": "fas fa-user",
        "auth.group": "fas fa-users-cog",
        "finance.category": "fas fa-tags",
        "finance.transaction": "fas fa-arrow-right-arrow-left",
        "finance.budget": "fas fa-wallet",
        "finance.goal": "fas fa-bullseye",
        "finance.chatmessage": "fas fa-comments",
        "finance.aisuggestion": "fas fa-lightbulb",
        "finance.userprofile": "fas fa-id-badge",
    },
    "order_with_respect_to": [
        "auth",
        "finance",
    ],
}

JAZZMIN_UI_TWEAKS = {
    "theme": "flatly",
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": False,
    "accent": "accent-info",
    "navbar": "navbar-white navbar-light",
    "no_navbar_border": True,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": True,
    "button_classes": {
        "primary": "btn btn-info",
        "secondary": "btn btn-outline-secondary",
        "info": "btn btn-info",
        "warning": "btn btn-warning",
        "danger": "btn btn-danger",
        "success": "btn btn-success",
    },
}

# Jazzmin theme mode (replaces deprecated dark_mode_theme)
JAZZMIN_SETTINGS = {
    **JAZZMIN_SETTINGS,
    "default_theme_mode": "auto",  # auto, light, or dark
}

CSRF_TRUSTED_ORIGINS = [
    'https://*.replit.dev',
    'https://*.repl.co',
    'https://*.replit.app',
    'http://localhost',
    'http://localhost:18748',
    'http://127.0.0.1',
    'http://127.0.0.1:18748',
]

# Security settings for production
# Note: Replit proxy handles HTTPS termination; Django should NOT enforce
# Secure flag on cookies as it breaks sessions through Replit's proxy
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'
