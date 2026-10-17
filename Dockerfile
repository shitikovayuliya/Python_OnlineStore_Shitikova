# =============================================================================
# Dockerfile для интернет-магазина
# =============================================================================
# Многоступенчатая сборка на базе Python 3.9-slim
# Использует gunicorn для продакшн-раздачи

FROM python:3.9-slim

# Отключаем буферизацию Python для корректного логирования в Docker
ENV PYTHONUNBUFFERED=1

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем requirements для кэширования слоёв (best practice)
COPY requirements.txt /app/

# Обновляем pip и устанавливаем зависимости
RUN pip install --upgrade pip && pip install -r /app/requirements.txt

# Копируем весь исходный код проекта
COPY . /app/

# Переходим в директорию Django-проекта
WORKDIR /app/onlinestore

# Открываем порт для Gunicorn
EXPOSE 8000

# Запускаем Gunicorn с 3 воркерами
# onlinestore.wsgi:application — WSGI-приложение Django
CMD ["gunicorn", "onlinestore.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
