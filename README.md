# Universal Dispatcher Backend

## Setup

```
cd universal-dispatcher-backend/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

## Test

```
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Cold room at the flower warehouse near the airport is not cooling"}'
```
