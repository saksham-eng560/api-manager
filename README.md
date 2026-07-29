# Keyline — API Key Manager

Keyline is a full-stack API key manager. The FastAPI backend stores encrypted API keys and hashed passwords; the included responsive frontend provides the landing page, authentication flow, and personal key vault.

## Project structure

```text
.
├── backend/       # FastAPI API, database models, encryption, and seed script
└── frontend/      # Responsive landing page and authenticated vault UI
```

## Features

- User signup and password hashing
- OAuth2-compatible login with JWT access tokens
- Encrypted API-key storage
- Per-user key listing and deletion
- SQLAlchemy database models for users and API keys

## Requirements

- Python 3.9+
- A PostgreSQL database (or another database supported by SQLAlchemy)

## Setup

Create and activate a virtual environment, then install the dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Create a `.env` file in the project root. Never commit this file.

```env
DATABASE_URL=postgresql://USERNAME:PASSWORD@HOST:5432/DATABASE
SECRET=replace-with-a-long-random-secret
ALGORITHM=HS256
TIME_TO_EXPIRE=30
```

`TIME_TO_EXPIRE` is expressed in minutes. `SECRET_KEY` is also supported for backwards compatibility, but `SECRET` is preferred.

## Run the application

Start the development server from the project directory:

```bash
.venv/bin/python -m uvicorn backend.main:app --reload
```

Open <http://127.0.0.1:8000> for the Keyline frontend. The interactive API documentation is at <http://127.0.0.1:8000/docs>.

The backend serves the `frontend/` directory itself, so the sign-up, log-in, add-key, list-key, and delete-key flows work on the same origin. To work on the frontend separately, serve `frontend/` with a local static server; the backend allows common localhost development origins and the UI will use `http://127.0.0.1:8000` automatically.

The application creates its SQLAlchemy tables when it starts. For production, use a dedicated migration workflow instead of relying on automatic table creation.

## API endpoints

| Method | Path | Authentication | Purpose |
| --- | --- | --- | --- |
| `POST` | `/signup` | No | Create a user account |
| `POST` | `/login` | No | Receive a JWT access token |
| `GET` | `/home` | Bearer token | List the current user's stored API keys |
| `POST` | `/new` | Bearer token | Store a new API key |
| `DELETE` | `/delete/{api_id}` | Bearer token | Delete one of the current user's API keys |

### Example workflow

Create an account:

```bash
curl -X POST http://127.0.0.1:8000/signup \
  -H 'Content-Type: application/json' \
  -d '{"username":"ada","password":"a-strong-password","email":"ada@example.com"}'
```

Log in. This endpoint expects form data, as required by OAuth2:

```bash
curl -X POST http://127.0.0.1:8000/login \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=ada&password=a-strong-password'
```

Store a key, replacing `TOKEN` with the `access_token` returned by login:

```bash
curl -X POST http://127.0.0.1:8000/new \
  -H 'Authorization: Bearer TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"api_key":"example-secret-key","model":"gpt-4.1","expiry":"2027-01-01","usability":"development"}'
```

## Seed test data

Create 100 repeatable test users and fake encrypted API keys:

```bash
.venv/bin/python -m backend.seed_test_data
```

All test users use the password `TestPass!2026`. Users `test_user_005`, `test_user_010`, and every fifth user after that have multiple API keys.

## Security notes

- Keep `.env`, database credentials, JWT secrets, and real API keys out of version control.
- Use a strong, unique `SECRET` in every deployed environment.
- Run behind HTTPS in production.
