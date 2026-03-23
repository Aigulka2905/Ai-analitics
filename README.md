# Analytics PRO Backend (FastAPI)

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload
```

## API
- Base URL: `http://localhost:8000`
- OpenAPI docs: `http://localhost:8000/docs`
- Prefix: `/api/pro/*`

## JWT
Use `Authorization: Bearer <jwt>` where token payload contains `sub` (userId).

## Seed
```bash
python scripts/seed.py
```
