
import os
from pathlib import Path

# Корневая директория проекта
BASE_DIR = Path(__file__).resolve().parent.parent


def get_env_variable(var_name, default=None):
    """
    Получает переменную окружения.
    Если переменная не установлена — выбрасывает ValueError.
    """
    value = os.environ.get(var_name, default)
    if value is None:
        raise ValueError(f'Please set the {var_name} environment variable')
    return value


# =============================================================================
# Безопасность и режим работы
# =============================================================================

# Секретный ключ для криптографических примитивов Django
# !!! Никогда не коммитьте реальный ключ в репозиторий !!!
SECRET_KEY = get_env_variable('SECRET_KEY')

# Режим отладки: True для разработки, False для продакшена
# При DEBUG=False включаются дополнительные проверки безопасности
DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 'yes')

# Список разрешённых хостов для подключения
# В продакшене укажите доменное имя вашего сайта
ALLOWED_HOSTS = [
    host.strip()
    for host in get_env_variable('ALLOWED_HOSTS', '').split(',')
    if host.strip()
]


# =============================================================================
# Приложения Django
# =============================================================================

INSTALLED_APPS = [
    # Собственные приложения
    'users',           # Кастомная модель пользователя и аутентификация
    'store',           # Каталог, корзина, заказы, остатки

    # Улучшенная админ-панель
    'admin_interface',
    'colorfield',

    # Стандартные приложения Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]



# =============================================================================
# Middleware — обработка запросов/ответов
# =============================================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',     # Безопасность
    'django.contrib.sessions.middleware.SessionMiddleware',  # Сессии
    'django.middleware.common.CommonMiddleware',         # URL-фильтрация
    'django.middleware.csrf.CsrfViewMiddleware',         # CSRF-защита
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # Аутентификация
    'django.contrib.messages.middleware.MessageMiddleware',     # Сообщения
    'django.middleware.clickjacking.XFrameOptionsMiddleware',   # Защита от clickjacking
]

ROOT_URLCONF = 'onlinestore.urls'  # Корневой URL-конфиг

# =============================================================================
# Шаблоны Django
# =============================================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # Директории с шаблонами (поиск по APP_DIRS)
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

WSGI_APPLICATION = 'onlinestore.wsgi.application'  # WSGI-entrypoint


# =============================================================================
# База данных
# =============================================================================
# PostgreSQL: параметры берутся из переменных окружения (.env)
# В Docker-окружении HOST='db' (имя сервиса в docker-compose)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': get_env_variable('DB_NAME', 'mydatabase'),
        'USER': get_env_variable('DB_USER', 'myuser'),
        'PASSWORD': get_env_variable('DB_PASSWORD', 'mypassword'),
        'HOST': get_env_variable('DB_HOST', 'db'),
        'PORT': get_env_variable('DB_PORT', '5432'),
    }
}





# =============================================================================
# Валидация паролей
# =============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},  # Не слишком похож на пользователя
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},              # Минимальная длина
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},             # Не распространённый пароль
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},            # Не только цифры
]


# =============================================================================
# Интернационализация
# =============================================================================

LANGUAGE_CODE = 'en-us'   # Язык интерфейса
TIME_ZONE = 'UTC'         # Часовой пояс
USE_I18N = True           # Включить локализацию
USE_TZ = True             # Временные метки в UTC


# =============================================================================
# Статические файлы (CSS, JS, изображения)
# =============================================================================

STATIC_URL = 'static/'    # URL-путь к статике
STATIC_ROOT = 'static/'   # Директория для collectstatic


# =============================================================================
# Дополнительные настройки
# =============================================================================

# Поле автоинкремента по умолчанию
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Кастомная модель пользователя (наследует AbstractUser)
AUTH_USER_MODEL = 'users.User'

# Куда перенаправлять после входа/выхода
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
