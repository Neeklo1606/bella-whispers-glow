# Project Structure Documentation

## Overview

This document describes the complete structure of the Telegram Subscription Platform backend project.

## Root Structure

```
bella/
├── backend/          # FastAPI backend application
├── bot/              # Telegram bot (aiogram)
├── miniapp/          # React Mini App (existing)
├── admin/            # Admin panel (future)
└── docker/           # Docker configuration
```

---

## Backend Structure

### `backend/`

FastAPI application with modular architecture.

```
backend/
├── src/
│   ├── core/                    # Core application components
│   │   ├── config/              # Configuration management
│   │   │   ├── __init__.py
│   │   │   └── settings.py     # Application settings (Pydantic)
│   │   ├── db/                  # Database configuration
│   │   │   ├── __init__.py
│   │   │   ├── database.py     # SQLAlchemy setup, session management
│   │   │   └── base_model.py   # Base model with common fields
│   │   ├── security/            # Security utilities
│   │   │   ├── __init__.py
│   │   │   ├── jwt.py          # JWT token generation/validation
│   │   │   └── dependencies.py # FastAPI security dependencies
│   │   └── utils/              # Utility functions
│   │       ├── __init__.py
│   │       └── redis_client.py # Redis client singleton
│   │
│   ├── modules/                 # Business logic modules
│   │   ├── auth/               # Authentication module
│   │   │   ├── __init__.py
│   │   │   ├── models.py       # SQLAlchemy models
│   │   │   ├── schemas.py      # Pydantic schemas
│   │   │   ├── repository.py  # Data access layer
│   │   │   ├── service.py      # Business logic
│   │   │   └── router.py       # FastAPI routes
│   │   ├── users/              # Users module
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── repository.py
│   │   │   ├── service.py
│   │   │   └── router.py
│   │   ├── subscriptions/      # Subscriptions module
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── repository.py
│   │   │   ├── service.py
│   │   │   └── router.py
│   │   ├── payments/           # Payments module
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── repository.py
│   │   │   ├── service.py
│   │   │   └── router.py
│   │   ├── telegram/           # Telegram integration module
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── repository.py
│   │   │   ├── service.py
│   │   │   └── router.py
│   │   ├── broadcasts/         # Broadcasts module
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── repository.py
│   │   │   ├── service.py
│   │   │   └── router.py
│   │   ├── schedule/          # Schedule module
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── repository.py
│   │   │   ├── service.py
│   │   │   └── router.py
│   │   └── settings/          # Settings module
│   │       ├── __init__.py
│   │       ├── models.py
│   │       ├── schemas.py
│   │       ├── repository.py
│   │       ├── service.py
│   │       └── router.py
│   │
│   ├── workers/               # Background tasks
│   │   ├── __init__.py
│   │   ├── celery_app.py      # Celery application
│   │   └── tasks/              # Task definitions
│   │       ├── __init__.py
│   │       ├── subscription_tasks.py
│   │       ├── payment_tasks.py
│   │       └── broadcast_tasks.py
│   │
│   └── main.py                # FastAPI application entry point
│
├── alembic/                   # Database migrations
│   ├── versions/              # Migration files
│   ├── env.py                # Alembic environment
│   ├── script.py.mako        # Migration template
│   └── README
│
├── .env.example              # Environment variables template
├── .gitignore
├── requirements.txt          # Python dependencies
├── Dockerfile               # Docker image definition
└── README.md               # Backend documentation
```

### Module Structure Pattern

Each module follows the same structure:

- **models.py**: SQLAlchemy database models
- **schemas.py**: Pydantic schemas for request/response validation
- **repository.py**: Data access layer (database queries)
- **service.py**: Business logic layer
- **router.py**: FastAPI route handlers
- **__init__.py**: Module exports

---

## Bot Structure

### `bot/`

Telegram bot built with aiogram 3.x.

```
bot/
├── src/
│   ├── handlers/              # Message and callback handlers
│   │   ├── __init__.py       # Handler registration
│   │   ├── start.py          # /start command handler
│   │   ├── subscription.py  # Subscription handlers
│   │   ├── payment.py        # Payment handlers
│   │   └── menu.py           # Menu handlers
│   │
│   ├── keyboards/            # Inline keyboards
│   │   ├── __init__.py
│   │   └── main_menu.py      # Main menu keyboard
│   │
│   ├── services/              # Business services
│   │   ├── __init__.py
│   │   └── api_client.py     # Backend API client
│   │
│   ├── middlewares/           # Bot middlewares
│   │   ├── __init__.py       # Middleware registration
│   │   └── (future middlewares)
│   │
│   ├── utils/                 # Utilities
│   │   ├── __init__.py
│   │   └── config.py         # Bot configuration
│   │
│   └── main.py               # Bot entry point
│
├── .env.example
├── .gitignore
├── requirements.txt
└── Dockerfile
```

---

## Docker Structure

### `docker/`

Docker Compose configuration and Nginx setup.

```
docker/
├── docker-compose.yml        # Main compose file
└── nginx/
    ├── nginx.conf           # Nginx main config
    └── conf.d/
        └── backend.conf    # Backend proxy config
```

---

## Responsibility of Each Folder

### Backend Core (`backend/src/core/`)

- **config/**: Application configuration management using Pydantic Settings
- **db/**: Database connection, session management, base models
- **security/**: JWT authentication, password hashing, security dependencies
- **utils/**: Shared utilities (Redis client, helpers)

### Backend Modules (`backend/src/modules/`)

Each module is self-contained with:
- **models.py**: Database schema definitions
- **schemas.py**: API request/response validation
- **repository.py**: Database queries (data access)
- **service.py**: Business logic
- **router.py**: HTTP endpoints

**Modules:**
- **auth**: User authentication (Telegram, email/password)
- **users**: User management
- **subscriptions**: Subscription plans and user subscriptions
- **payments**: Payment processing and webhooks
- **telegram**: Telegram channel access management
- **broadcasts**: Message broadcasting to channel
- **schedule**: Event scheduling
- **settings**: System settings management

### Workers (`backend/src/workers/`)

- **celery_app.py**: Celery application configuration
- **tasks/**: Background task definitions
  - **subscription_tasks.py**: Subscription expiration, renewals
  - **payment_tasks.py**: Payment verification
  - **broadcast_tasks.py**: Scheduled broadcasts

### Bot (`bot/src/`)

- **handlers/**: Message and callback handlers
- **keyboards/**: Inline keyboard builders
- **services/**: Business logic (API communication)
- **middlewares/**: Request processing middlewares
- **utils/**: Helper functions

### Docker (`docker/`)

- **docker-compose.yml**: Multi-container orchestration
- **nginx/**: Reverse proxy configuration

---

## Technology Stack

### Backend
- **Framework**: FastAPI
- **Database**: PostgreSQL (async with SQLAlchemy)
- **ORM**: SQLAlchemy 2.0 (async)
- **Migrations**: Alembic
- **Cache/Jobs**: Redis
- **Background Tasks**: Celery
- **Authentication**: JWT (python-jose)

### Bot
- **Framework**: aiogram 3.x
- **HTTP Client**: httpx

### Infrastructure
- **Containerization**: Docker, Docker Compose
- **Reverse Proxy**: Nginx

---

## Development Workflow

1. **Database Changes**: Create Alembic migration
2. **New Features**: Add to appropriate module
3. **API Endpoints**: Add routes in module router
4. **Background Tasks**: Add to workers/tasks
5. **Bot Commands**: Add handlers in bot/src/handlers

---

## Next Steps

1. Implement database models
2. Implement business logic in services
3. Implement repository methods
4. Add bot handlers
5. Configure background tasks
6. Set up CI/CD
7. Add tests
