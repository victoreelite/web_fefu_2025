# syntax=docker/dockerfile:1
ARG PYTHON_VERSION=3.11

FROM python:${PYTHON_VERSION} AS builder
WORKDIR /app

ARG BUILD_ENV=production

COPY requirements/ requirements/
RUN pip install --upgrade pip \
 && if [ "$BUILD_ENV" = "development" ]; then \
      pip install -r requirements/dev.txt; \
    else \
      pip install -r requirements/prod.txt; \
    fi

COPY . .

ENV DJANGO_SECRET_KEY=build-secret
ENV DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
ENV DJANGO_ENV=production
RUN python manage.py collectstatic --noinput --clear \
 && mkdir -p /app/staticfiles \
 && cp -r /app/static/* /app/staticfiles/ || true

FROM python:${PYTHON_VERSION}-slim AS production
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN useradd -m -u 1000 appuser

COPY --from=builder /usr/local /usr/local
COPY --from=builder /app /app

RUN mkdir -p /app/static /app/media \
 && chown -R appuser:appuser /app

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "web_2025.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120"]