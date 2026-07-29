# API-Key-Manager
# api-manager
# api-manager

## Seed test data

Create 100 repeatable test users and fake encrypted API keys:

```bash
.venv/bin/python seed_test_data.py
```

All test users use the password `TestPass!2026`. Users `test_user_005`,
`test_user_010`, and every fifth user after that have multiple API keys.
