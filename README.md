# API Key Manager

A FastAPI service for storing, listing, and deleting API keys for authenticated users. API-key values are encrypted before they are saved to the database, and protected endpoints use JWT bearer tokens.

## Features

- User signup and password hashing
- OAuth2-compatible login with JWT access tokens
- Encrypted API-key storage
- Per-user key listing and deletion
- SQLAlchemy database models for users and API keys

## Requirements

- Python 3.10+
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

## Run the API

Start the development server from the project directory:

```bash
.venv/bin/python -m uvicorn main:app --reload
```

The interactive API documentation is available at <http://127.0.0.1:8000/docs>.

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
.venv/bin/python seed_test_data.py
```

All test users use the password `TestPass!2026`. Users `test_user_005`, `test_user_010`, and every fifth user after that have multiple API keys.

## Security notes

- Keep `.env`, database credentials, JWT secrets, and real API keys out of version control.
- Use a strong, unique `SECRET` in every deployed environment.
- Run behind HTTPS in production.
