# ⚡ 5-Minute Quickstart: FastAPI + CUBRID

## 1) Prerequisites
Install Docker Desktop (or Docker Engine + Docker Compose).

## 2) Start everything
```bash
docker compose up -d
```

## 3) Verify API is running
```bash
curl localhost:8000/items
```

You should get a JSON array response (for example, `[]` on first run).

## What's Next?
- Production-ready starter: `../../templates/api-service-fastapi/`
- Core database patterns: `../../fundamentals/`
