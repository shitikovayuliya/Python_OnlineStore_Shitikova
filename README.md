# Интернет-магазин

**Автор:** Юлия Шитикова
**GitHub:** [@shitikovayuliya](https://github.com/shitikovayuliya)
**Email:** shitikovayuliya@mail.ru

> ⚠️ **Учебный проект** — создан для демонстрации навыков работы с Django.

## Описание

Django-приложение интернет-магазина с каталогом товаров, корзиной, оформлением заказов
и системой управления остатками на складе.

### Особенности

- ✅ Каталог товаров и категорий
- ✅ Корзина с проверкой остатков на складе
- ✅ Атомарное оформление заказов (`transaction.atomic`)
- ✅ Разграничение доступа (заказы видны только владельцу)
- ✅ Docker-контейнеризация с healthcheck

## Технологии

- **Django 4.2** — фреймворк
- **PostgreSQL** — база данных
- **Gunicorn** — WSGI-сервер
- **Docker** — контейнеризация

## Структура проекта

```
onlinestore/          # Корневое Django-приложение
├── store/            # Основной модуль: товары, категории, заказы, корзина
├── users/            # Модуль аутентификации (кастомная модель User)
└── onlinestore/      # Настройки проекта
```

## Запуск

### 1. Настройка окружения

```bash
# Скопируйте шаблон переменных окружения
cp .env.example .env

# Отредактируйте .env при необходимости
```

### 2. Запуск через Docker

```bash
# Сборка и запуск контейнеров
docker-compose up --build -d

# Просмотр логов
docker-compose logs -f web

# Остановка
docker-compose down
```

### 3. Создание суперпользователя

```bash
docker-compose exec web python manage.py createsuperuser
```

### 4. Загрузка тестовых данных

```bash
# Добавить 10 товаров с остатками
docker-compose exec web python manage.py seed_products

# Загрузить fixture данные
docker-compose exec web python manage.py loaddata data_full.json
```

## URL-адреса

| Путь | Описание |
|------|----------|
| `/` | Главная страница |
| `/products/` | Каталог товаров |
| `/categories/` | Категории |
| `/cart/` | Корзина (авторизация) |
| `/checkout/` | Оформление заказа (авторизация) |
| `/orders/` | Список заказов (авторизация) |
| `/admin/` | Админ-панель |
| `/register/` | Регистрация |
| `/login/` | Вход |

## Тесты

```bash
# Запуск тестов с SQLite (локально)
DJANGO_SETTINGS_MODULE=test_settings python manage.py test

# Запуск через Docker
docker-compose exec web python manage.py test
```
