# ChattyM — Social Network (Django)

**ChattyM** is a minimal social network built with **Django 5**, **PostgreSQL**, and **Bootstrap 5**. It demonstrates core web app patterns: email-based auth, profiles, posts, comments, likes, subscriptions, private messaging, notifications, and a small REST API. I kept the original compact style and emojis. 🚀

---

## Features

* 👤 **User Authentication**

  * Custom `User` model with email as login (USERNAME_FIELD = `email`)
  * Sign up / sign in / sign out
  * Email confirmation & password reset (console backend in dev)

* 📄 **User Profiles**

  * Avatar, birthday, editable profile fields
  * Profile page with posts, followers, stats

* 📝 **Content**

  * Create / edit / delete posts (image + tags)
  * Comments with reply support, soft-delete and edit tracking
  * Likes with a `likes_count` counter on posts

* 🔔 **Notifications**

  * In-app notification model and small API to mark read

* 🔁 **Subscriptions / Follow**

  * Follow/unfollow users, follower counts and follow toggles
  * Personalized feeds (posts from people you follow)

* 💬 **Messaging**

  * Simple Conversation / Participant / Message models for DMs

* 🔌 **REST API**

  * DRF-based endpoints (posts CRUD, search, ordering)
  * Swagger/OpenAPI docs available at `/api/docs/` when drf-spectacular is installed

* ⚙️ **Admin & Dev tooling**

  * Django admin configured for users, posts, comments, notifications
  * Dockerized app + entrypoint script that runs migrations & collects static

---

## Tech stack

* **Python:** 3.11
* **Django:** 5.x
* **DB:** PostgreSQL (docker-compose uses `postgres:15`)
* **API:** Django REST Framework, drf-spectacular
* **Auth:** django-allauth (email-based)
* **Storage:** local filesystem by default (S3/MinIO optional)
* **Deployment:** Docker + Docker Compose
* **Dependency manager:** Poetry (`pyproject.toml`)

---

## Quick start — Docker (recommended)

Project includes `Dockerfile` and `docker-compose.yml`.

```bash
# build and run
docker compose build --no-cache web
docker compose up -d

# view logs
docker compose logs -f web
```

To run commands inside the `web` container:

```bash
docker compose exec web bash
# inside container
python manage.py migrate
python manage.py loaddata fixtures/users_fixture.json
python manage.py loaddata fixtures/users_emails_fixture.json
python manage.py loaddata fixtures/posts_fixture.json
python manage.py loaddata fixtures/comments_fixture.json
```

**Note:** `docker/entrypoint.sh` waits for the DB, runs `migrate`, optionally creates a superuser if `DJANGO_SUPERUSER_EMAIL` and `DJANGO_SUPERUSER_PASSWORD` are present, runs `collectstatic`, and then starts the dev server. The entrypoint is safe for local development. ⚙️

---

## Quick start — local (no Docker)

1. Install dependencies with Poetry:

```bash
poetry install
```

2. Copy `.env.example` → `.env` and update secrets.
3. Run migrations and start server:

```bash
python manage.py migrate --settings=config.settings.dev
python manage.py createsuperuser --settings=config.settings.dev
python manage.py runserver --settings=config.settings.dev
```

---

## Environment variables (key ones)

Use `.env` based on `.env.example`.

* `SECRET_KEY` — Django secret
* `DJANGO_DEBUG` — toggle debug
* `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `DB_HOST`, `DB_PORT`
* `DATABASE_URL` — optional (used in `prod` settings if present)
* `USE_S3` — `0` or `1` (if `1`, set MinIO/S3 vars)
* `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY`, `MINIO_ENDPOINT`, `MINIO_BUCKET`
* `EMAIL_BACKEND` — default console backend in dev
* `DJANGO_SUPERUSER_EMAIL` & `DJANGO_SUPERUSER_PASSWORD` — auto-create in entrypoint (dev)

---

## Fixtures & test data

Fixtures are in `/fixtures/`:

* `users_fixture.json`
* `users_emails_fixture.json`
* `posts_fixture.json`
* `comments_fixture.json`

Load them with `manage.py loaddata` (examples above). Test images referenced by posts are in `static/images/posts/` (used by fixtures).

---

## API

* Posts API (DRF): `/api/posts/` — list, retrieve, create, update, delete

  * Query params supported: `?search=`, `?ordering=`, `?user=`, `?active=1`, `?q=` (title/text)
* Schema & docs (if drf-spectacular installed):

  * `/api/schema/` (OpenAPI JSON)
  * `/api/docs/` (Swagger UI)

---

## Important project paths

* `apps/` — local Django apps (users, posts, comments, likes, subscriptions, messaging, notifications)
* `config/` — Django settings & urls
* `docker/entrypoint.sh` — container entrypoint (migrations, superuser, collectstatic, runserver)
* `fixtures/` — test fixtures
* `static/` & `templates/` — frontend static files and templates

---

## Development commands

```bash
# run migrations
python manage.py makemigrations
python manage.py migrate

# create superuser
python manage.py createsuperuser

# load fixtures
python manage.py loaddata fixtures/users_fixture.json

# run tests
pytest
```

---

## Production notes

* `config/settings/prod.py` contains production-ready defaults: `DEBUG=False`, HSTS/SECURE flags, optional S3/MinIO storage, and `ManifestStaticFilesStorage` for static files.
* Use a proper WSGI/ASGI server (gunicorn/uvicorn) + reverse proxy (nginx) for static + security headers.
* Ensure:

  * `SECRET_KEY` is secret
  * `DEBUG = False`
  * `ALLOWED_HOSTS` set correctly
  * Email backend points to real SMTP
  * Database credentials and S3 creds secured
* Consider Celery + Redis for background tasks (sending email, heavy processing) and a proper logging/monitoring setup.

---

## Suggestions & TODOs

* Add DRF permission hardening / throttling for public endpoints.
* Move heavy work (email sending, push notifications) to background workers.
* Add full-text search (Postgres `tsvector` or Elastic) for large datasets.
* Add CI pipeline for tests and linters (black, isort, flake8).