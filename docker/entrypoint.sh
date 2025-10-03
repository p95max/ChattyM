#!/usr/bin/env bash
set -euo pipefail

echo "[web] Waiting for database at ${DB_HOST:-db}:${DB_PORT:-5432}..."
ATTEMPTS=0
until pg_isready -h "${DB_HOST:-db}" -p "${DB_PORT:-5432}" -U "${POSTGRES_USER:-postgres}" >/dev/null 2>&1; do
  ATTEMPTS=$((ATTEMPTS+1))
  if [ "$ATTEMPTS" -ge 60 ]; then
    echo "[web] ERROR: DB is not available after 60s. Exiting."
    exit 1
  fi
  sleep 1
done
echo "[web] DB is up."

echo "[web] Django system check..."
python -m django check

echo "[web] Apply migrations..."
python manage.py migrate --noinput

# Auto-create superuser if not exists (dev only)
if [ -n "${DJANGO_SUPERUSER_EMAIL:-}" ] && [ -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]; then
  echo "[web] Ensuring superuser ${DJANGO_SUPERUSER_EMAIL} exists..."
  python - <<'PYCODE'
import os
import django
from django.contrib.auth import get_user_model

# если переменная уже выставлена в окружении, эта строка не помешает
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
django.setup()

U = get_user_model()
email = os.environ["DJANGO_SUPERUSER_EMAIL"]
pwd = os.environ["DJANGO_SUPERUSER_PASSWORD"]
username = os.environ.get("DJANGO_SUPERUSER_USERNAME") or (email.split("@")[0] if "@" in email else email)

user = U.objects.filter(email=email).first()
if user:
    print(f"[web] Superuser {email} already exists")
else:
    # если в модели остался username — подставим его
    needs_username = hasattr(U, "USERNAME_FIELD") and U.USERNAME_FIELD != "username"
    kwargs = {"email": email, "password": pwd}
    # На AbstractUser create_superuser часто ожидает username как обязательный аргумент
    if hasattr(U, "username"):
        kwargs["username"] = username
    U.objects.create_superuser(**kwargs)
    print(f"[web] Created superuser {email} (username={username if 'username' in kwargs else 'n/a'})")
PYCODE
fi


echo "[web] Collect static..."
python manage.py collectstatic --noinput

echo "[web] Starting dev server..."
exec python manage.py runserver 0.0.0.0:8000
