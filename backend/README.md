# Bella Subscription Platform - Backend

FastAPI backend for Telegram subscription platform.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Copy environment file:
```bash
cp .env.example .env
```

3. Configure `.env` with your settings.

4. Run database migrations:
```bash
alembic upgrade head
```

5. Start the server:
```bash
uvicorn src.main:app --reload
```

## Project Structure

```
backend/
├── src/
│   ├── core/           # Core functionality
│   │   ├── config/     # Configuration
│   │   ├── db/         # Database setup
│   │   ├── security/   # Security (JWT, etc.)
│   │   └── utils/      # Utilities
│   ├── modules/        # Business modules
│   │   ├── auth/
│   │   ├── users/
│   │   ├── subscriptions/
│   │   ├── payments/
│   │   ├── telegram/
│   │   ├── broadcasts/
│   │   ├── schedule/
│   │   └── settings/
│   ├── workers/        # Background tasks
│   └── main.py         # Application entry point
├── alembic/            # Database migrations
└── requirements.txt
```

## Development

- API docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
