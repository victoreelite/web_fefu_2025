#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${1:-}"
if [[ -z "${REPO_URL}" ]]; then
  echo "Usage: sudo bash deploy/scripts/deploy.sh <repo_url>"
  exit 1
fi

APP_DIR="/var/www/fefu_lab"
ENV_DIR="/etc/fefu_lab"
ENV_FILE="${ENV_DIR}/fefu_lab.env"
GUNICORN_LOG_DIR="/var/log/gunicorn"

DB_NAME="fefu_lab_db"
DB_USER="fefu_user"

echo "[1/9] apt update + install packages"
apt update -y
apt install -y \
  git curl nginx \
  python3 python3-venv python3-pip \
  postgresql postgresql-contrib \
  libpq-dev

echo "[2/9] Ensure PostgreSQL listens only on localhost"
PG_VER="$(ls /etc/postgresql | head -n 1)"
PG_CONF="/etc/postgresql/${PG_VER}/main/postgresql.conf"
PG_HBA="/etc/postgresql/${PG_VER}/main/pg_hba.conf"

sed -i "s/^#\?listen_addresses\s*=.*/listen_addresses = 'localhost'/" "$PG_CONF"

grep -q "127.0.0.1/32" "$PG_HBA" || echo "host all all 127.0.0.1/32 scram-sha-256" >> "$PG_HBA"
grep -q "::1/128" "$PG_HBA" || echo "host all all ::1/128 scram-sha-256" >> "$PG_HBA"

systemctl restart postgresql

echo "[3/9] Create PostgreSQL user + database (if not exists)"
DB_PASSWORD="$(python3 -c "import secrets; print(secrets.token_urlsafe(18))")"

sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname='${DB_USER}'" | grep -q 1 \
  || sudo -u postgres psql -c "CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASSWORD}';"

sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='${DB_NAME}'" | grep -q 1 \
  || sudo -u postgres psql -c "CREATE DATABASE ${DB_NAME} OWNER ${DB_USER};"

echo "[4/9] Clone repo to ${APP_DIR}"
rm -rf "${APP_DIR}"
git clone "${REPO_URL}" "${APP_DIR}"

echo "[5/9] Create venv + install requirements"
python3 -m venv "${APP_DIR}/venv"
"${APP_DIR}/venv/bin/pip" install --upgrade pip
"${APP_DIR}/venv/bin/pip" install -r "${APP_DIR}/requirements.txt"

echo "[6/9] Create env file for Django (production settings)"
mkdir -p "${ENV_DIR}"
DJANGO_SECRET_KEY="$("${APP_DIR}/venv/bin/python" -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")"

VM_IP="192.168.50.100"

cat > "${ENV_FILE}" <<EOF
DJANGO_ENV=production
DJANGO_SECRET_KEY='${DJANGO_SECRET_KEY}'
DJANGO_ALLOWED_HOSTS='${VM_IP},localhost,127.0.0.1'
DJANGO_CSRF_TRUSTED_ORIGINS='http://${VM_IP}'

DB_NAME='${DB_NAME}'
DB_USER='${DB_USER}'
DB_PASSWORD='${DB_PASSWORD}'
DB_HOST='localhost'
DB_PORT='5432'
EOF

chmod 600 "${ENV_FILE}"

echo "[7/9] Prepare dirs (static/media/logs) + permissions"
mkdir -p "${APP_DIR}/static" "${APP_DIR}/media" "${GUNICORN_LOG_DIR}"
chown -R www-data:www-data "${APP_DIR}" "${GUNICORN_LOG_DIR}"
chmod -R 755 "${APP_DIR}"

echo "[8/9] Django migrate + collectstatic"
set -a
source "${ENV_FILE}"
set +a

sudo -u www-data -E "${APP_DIR}/venv/bin/python" "${APP_DIR}/manage.py" migrate --noinput
sudo -u www-data -E "${APP_DIR}/venv/bin/python" "${APP_DIR}/manage.py" collectstatic --noinput

# Если положить data.json в deploy/data.json — загрузка автоматическая
if [[ -f "${APP_DIR}/deploy/data.json" ]]; then
  echo "Found deploy/data.json -> loaddata"
  sudo -u www-data -E "${APP_DIR}/venv/bin/python" "${APP_DIR}/manage.py" loaddata "${APP_DIR}/deploy/data.json"
fi

echo "[9/9] Install configs: gunicorn systemd + nginx, then start"
cp "${APP_DIR}/deploy/systemd/gunicorn.service" /etc/systemd/system/gunicorn.service
systemctl daemon-reload
systemctl enable gunicorn
systemctl restart gunicorn

cp "${APP_DIR}/deploy/nginx/fefu_lab.conf" /etc/nginx/sites-available/fefu_lab.conf
ln -sf /etc/nginx/sites-available/fefu_lab.conf /etc/nginx/sites-enabled/fefu_lab.conf
rm -f /etc/nginx/sites-enabled/default

nginx -t
systemctl enable nginx
systemctl restart nginx

echo "Checking: curl http://localhost:80"
HTTP_CODE="$(curl -s -o /dev/null -w "%{http_code}" http://localhost:80 || true)"
echo "HTTP status: ${HTTP_CODE}"

echo "DONE. Open from host: http://${VM_IP}/"