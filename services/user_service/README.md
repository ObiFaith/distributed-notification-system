# User Service (Flask)

### Run locally (without Docker)
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=wsgi.py
export DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/postgres
flask db init
flask db migrate -m "init users"
flask db upgrade
gunicorn -w 2 -b 0.0.0.0:8000 wsgi:app

### Endpoints (snake_case)
POST   /auth/register                  body: { email, password, role? }
POST   /auth/login                     body: { email, password }
GET    /users?page=1&limit=20          (admin; self for non-admin)
POST   /users                          (admin)
GET    /users/{id}                     (self or admin)
PATCH  /users/{id}                     (admin)
PATCH  /users/{id}/preferences         (self or admin)
DELETE /users/{id}                     (admin)
GET    /health
