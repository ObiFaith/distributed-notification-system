# Template Service (Flask)

Manages notification templates with version history, multi-language, and variable substitution.

## Run locally (without Docker)
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

export FLASK_APP=wsgi.py
export DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/postgres

flask db init
flask db migrate -m "init templates"
flask db upgrade

gunicorn -w 2 -b 0.0.0.0:8000 wsgi:app

## Endpoints (snake_case)
GET    /templates?code=&language=&page=&limit=
GET    /templates/{code}?lang=en&version=latest
GET    /templates/{code}/versions?lang=en
POST   /templates                         # body: { code, language?, subject?, body_html?, body_text?, meta? }
POST   /templates/render                  # body: { template_code, language?, version?=latest, data? }
GET    /health

## Notes
- Version auto-increments per (code, language).
- Rendering uses Jinja2 with the provided `data` dictionary.
- Responses follow the shared { success, data, error, message, meta } format.
