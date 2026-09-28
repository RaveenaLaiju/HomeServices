from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY
SECRET_KEY = 'django-insecure-6i#!a)-d*2zi*ei$f(v1&09&c2mq4s$w1nsr8ull=*m(4=81t7'
DEBUG = True

ALLOWED_HOSTS = ["127.0.0.1", "localhost", "ca585bbd9a0c.ngrok-free.app"]
CSRF_TRUSTED_ORIGINS = ["https://ca585bbd9a0c.ngrok-free.app"]

# ---------------------- INSTALLED APPS ----------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app.apps.AppConfig',
]

# ---------------------- MIDDLEWARE ----------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # If you are using your own session middleware (optional)
    # 'app.middleware.SessionCookieSwitcherMiddleware',
]

ROOT_URLCONF = 'HomeServices.urls'

# ---------------------- TEMPLATES ----------------------
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

WSGI_APPLICATION = 'HomeServices.wsgi.application'

# ---------------------- DATABASE ----------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ---------------------- SESSION SETTINGS ----------------------
# You’re using Firefox Containers, so each role (customer, provider, admin)
# already has an isolated cookie automatically.
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_NAME = 'sessionid'
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SECURE = False  # Change to True if using HTTPS in production
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 1209600  # 2 weeks

# ---------------------- PASSWORD VALIDATION ----------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ---------------------- LANGUAGE & TIMEZONE ----------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ---------------------- STATIC & MEDIA ----------------------
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'HomeServices']
STATIC_ROOT = BASE_DIR / 'static'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ---------------------- EMAIL SETTINGS ----------------------
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = 'raveenalaiju@gmail.com'
EMAIL_HOST_PASSWORD = 'gsvo qhev rmds yvdx'  # App password

# ---------------------- OTHER ----------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Razorpay test credentials
RAZORPAY_KEY_ID = 'rzp_test_oH81YjMTp7hBJ6'
RAZORPAY_KEY_SECRET = 's0arLNs5t9N0s2jRdKAAfAOv'
