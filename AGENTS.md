# AGENTS.md

## Repo shape
- Django 6.1.2 project (Python >= 3.14.7). Entry: `manage.py` sets `DJANGO_SETTINGS_MODULE=config.settings`.
- Config package: `config/` (`settings.py`, `urls.py`, `wsgi.py`, `asgi.py`). Root URLconf only registers `admin/`. 
- No custom Django apps in repo root/visible INSTALLED_APPS (only contrib). No `README`, tests, or app source beyond config.
- SQLite default DB at `db.sqlite3` (repo may create it). Dev email backend is console.

## Environment
- Managed with `uv` (venv in `.venv/`, Python 3.14.7 from pyvenv.cfg). Prefer running with the project's venv.
- Dependencies in `pyproject.toml` + `uv.lock` (asgiref pinned transitively). No `requirements.txt`.

## Commands
- Run dev server: `python manage.py runserver` (uses config.settings)
- Migrations: `python manage.py migrate` (initial migrate needed for auth/admin)
- Create superuser: `python manage.py createsuperuser`
- Shell: `python manage.py shell`
- Check: `python manage.py check`

## Gotchas
- `settings.py` has hardcoded `SECRET_KEY` and `DEBUG=True` (demo only). 
- `config/settings.py` uses `MAILERS` (not default `EMAIL_BACKEND`) configured to console.
- No app dirs added yet - if adding apps, register in `INSTALLED_APPS` and add URLs in `config/urls.py`.
