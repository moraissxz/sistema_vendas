import os
from pathlib import Path
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')

# Garante que a chave padrão de exemplo nunca vá para produção
if SECRET_KEY in ('sua-chave-secreta-muito-segura-aqui-troque-isso', 'django-insecure-troque-isso'):
    import warnings
    warnings.warn(
        "\n\n⚠️  ATENÇÃO: Você está usando a SECRET_KEY padrão de exemplo!\n"
        "   Gere uma chave segura e atualize o .env antes de ir para produção.\n"
        "   Comando: python -c \"from django.core.management.utils import "
        "get_random_secret_key; print(get_random_secret_key())\"\n",
        stacklevel=2
    )

DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost', cast=Csv())

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'loja',
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

ROOT_URLCONF = 'sorveteria.urls'

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
                'loja.context_processors.carrinho_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'sorveteria.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='sorveteria_db'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

WHATSAPP_NUMERO = config('WHATSAPP_NUMERO', default='5511999999999')
NOME_SORVETERIA = config('NOME_SORVETERIA', default='Sorveteria Frutidelis')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ──────────────────────────────────────────
# SESSÃO
# Usa o banco de dados (padrão do Django).
# Garante que o carrinho persista entre recarregamentos e abas.
# Requer que `python manage.py migrate` tenha sido executado
# para criar a tabela django_session.
# ──────────────────────────────────────────
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_EXPIRE_AT_BROWSER_CLOSE = False      # Persiste ao fechar o navegador
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7       # 7 dias
SESSION_SAVE_EVERY_REQUEST = True            # Renova o prazo a cada visita
SESSION_COOKIE_HTTPONLY = True               # Impede acesso via JavaScript
SESSION_COOKIE_SAMESITE = 'Lax'             # Proteção CSRF básica

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

# Limite de produtos distintos no carrinho (segurança de memória)
CARRINHO_MAX_ITENS = 30