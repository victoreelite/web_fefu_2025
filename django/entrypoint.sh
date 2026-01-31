#!/usr/bin/env sh
set -e

echo "[entrypoint] wait for db..."
python - <<'PY'
import os, time
import psycopg2

host=os.getenv("DB_HOST","db")
port=int(os.getenv("DB_PORT","5432"))
name=os.getenv("DB_NAME")
user=os.getenv("DB_USER")
pwd=os.getenv("DB_PASSWORD")

for i in range(60):
    try:
        conn = psycopg2.connect(host=host, port=port, dbname=name, user=user, password=pwd)
        conn.close()
        print("DB is ready")
        break
    except Exception as e:
        time.sleep(1)
else:
    raise SystemExit("DB not ready after 60s")
PY

echo "[entrypoint] migrate..."
python manage.py migrate --noinput

if [ "${RUN_SEED:-0}" = "1" ]; then
  echo "[entrypoint] seed_data..."
  python manage.py seed_data || true
fi

if [ -d "/app/staticfiles" ] && [ -z "$(ls -A /app/static 2>/dev/null)" ]; then
  echo "[entrypoint] copy staticfiles to /app/static volume..."
  cp -r /app/staticfiles/* /app/static/ || true
fi

echo "[entrypoint] start: $@"
exec "$@"