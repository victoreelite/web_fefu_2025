# Lab 6: Контейнеризация Django-приложения с Docker

## 1. Описание
Проект развёрнут как мультиконтейнерное приложение:

Пользователь -> Nginx (контейнер) -> Django+Gunicorn (контейнер) -> PostgreSQL (контейнер)

Сервисы:
- db (PostgreSQL 15)
- web (Django + Gunicorn)
- nginx (reverse proxy + отдача static/media)

Требования лабы реализованы:
- Dockerfile для Django (multi-stage)
- Dockerfile для Nginx (nginx:alpine, удаление дефолтных конфигов)
- docker-compose.yml с volumes, healthchecks, env
- сборка статических файлов на этапе build (collectstatic)
- dev/prod окружения через env_file и override
- healthchecks для db/web/nginx

---

## 2. Структура проекта
Корень репозитория:
- docker-compose.yml
- docker-compose.override.yml
- .env.development
- .env.production
- .dockerignore
- README.md
- django/
  - Dockerfile
  - entrypoint.sh
  - requirements/
    - base.txt
    - dev.txt
    - prod.txt
  - manage.py
  - web_2025/...
  - fefu_lab/...
  - templates/...
- nginx/
  - Dockerfile
  - default.conf

---

## 3. Требования (ПО)
Docker + Docker Compose v2.

Проверка:
- docker version
- docker compose version

---

## 4. Быстрый старт (DEVELOPMENT)
Development использует:
- docker-compose.yml + docker-compose.override.yml (подхватывается автоматически)
- bind mount кода (./django -> /app)
- проброс порта web: 8000:8000 (для удобства)
- Nginx доступен на 80

1) Запуск:
docker compose up -d --build

2) Проверка контейнеров:
docker compose ps

3) Логи:
docker compose logs -f web
docker compose logs -f nginx
docker compose logs -f db

4) Открыть в браузере:
http://localhost/
http://localhost/admin/

5) Применить миграции вручную (если нужно):
docker compose exec web python manage.py migrate --noinput

6) Загрузить тестовые данные (если нужно):
docker compose exec web python manage.py seed_data

---

## 5. Запуск (PRODUCTION)
Production запуск без override (без проброса порта 8000 и без bind mount кода).

Вариант A (просто использовать docker-compose.yml с .env.production по умолчанию):
docker compose -f docker-compose.yml up -d --build

Вариант B (если нужно явно указать env):
(1) Отредактировать docker-compose.yml -> env_file: .env.production
(2) Запуск как в варианте A

Проверка:
- docker compose ps
- curl -I http://localhost/

---

## 6. Health checks
Проверка health:
docker compose ps

Ожидаемо:
- db: healthy (pg_isready)
- web: healthy (HTTP запрос к /admin/login/)
- nginx: healthy (curl http://localhost/ внутри контейнера)

---

## 7. Volumes и данные
Используются volumes:
- postgres_data: данные БД сохраняются между перезапусками
- static_volume: статика (collectstatic) доступна nginx
- media_volume: медиа-файлы

Проверка, что данные БД сохраняются:
- docker compose down
- docker compose up -d
(данные остаются, пока не удалили volumes)

Полное удаление вместе с volumes (ОСТОРОЖНО: удалит БД):
docker compose down -v

---

## 8. Полезные команды
Список контейнеров:
docker compose ps

Список образов и размер:
docker images

Пересобрать образы:
docker compose build --no-cache

Зайти внутрь контейнера web:
docker compose exec web sh

Проверить доступность сайта:
curl http://localhost/