# Complete Project Tree

```
bella/
├── backend/                          # FastAPI Backend Application
│   ├── .gitignore
│   ├── .env.example                  # Environment variables template
│   ├── Dockerfile                    # Backend Docker image
│   ├── README.md                     # Backend documentation
│   ├── requirements.txt              # Python dependencies
│   ├── alembic.ini                   # Alembic configuration
│   │
│   ├── alembic/                      # Database migrations
│   │   ├── env.py                    # Alembic environment
│   │   ├── script.py.mako            # Migration template
│   │   ├── README
│   │   └── versions/                 # Migration files (empty initially)
│   │
│   └── src/                          # Source code
│       ├── main.py                   # FastAPI application entry point
│       │
│       ├── core/                     # Core application components
│       │   ├── __init__.py
│       │   │
│       │   ├── config/               # Configuration management
│       │   │   ├── __init__.py
│       │   │   └── settings.py       # Pydantic settings
│       │   │
│       │   ├── db/                   # Database configuration
│       │   │   ├── __init__.py
│       │   │   ├── database.py       # SQLAlchemy setup
│       │   │   └── base_model.py    # Base model class
│       │   │
│       │   ├── security/             # Security utilities
│       │   │   ├── __init__.py
│       │   │   ├── jwt.py           # JWT token handling
│       │   │   └── dependencies.py  # FastAPI dependencies
│       │   │
│       │   └── utils/                # Utilities
│       │       ├── __init__.py
│       │       └── redis_client.py  # Redis client
│       │
│       ├── modules/                  # Business logic modules
│       │   │
│       │   ├── auth/                 # Authentication module
│       │   │   ├── __init__.py
│       │   │   ├── models.py        # SQLAlchemy models
│       │   │   ├── schemas.py       # Pydantic schemas
│       │   │   ├── repository.py    # Data access layer
│       │   │   ├── service.py       # Business logic
│       │   │   └── router.py        # FastAPI routes
│       │   │
│       │   ├── users/                # Users module
│       │   │   ├── __init__.py
│       │   │   ├── models.py
│       │   │   ├── schemas.py
│       │   │   ├── repository.py
│       │   │   ├── service.py
│       │   │   └── router.py
│       │   │
│       │   ├── subscriptions/        # Subscriptions module
│       │   │   ├── __init__.py
│       │   │   ├── models.py
│       │   │   ├── schemas.py
│       │   │   ├── repository.py
│       │   │   ├── service.py
│       │   │   └── router.py
│       │   │
│       │   ├── payments/             # Payments module
│       │   │   ├── __init__.py
│       │   │   ├── models.py
│       │   │   ├── schemas.py
│       │   │   ├── repository.py
│       │   │   ├── service.py
│       │   │   └── router.py
│       │   │
│       │   ├── telegram/             # Telegram integration module
│       │   │   ├── __init__.py
│       │   │   ├── models.py
│       │   │   ├── schemas.py
│       │   │   ├── repository.py
│       │   │   ├── service.py
│       │   │   └── router.py
│       │   │
│       │   ├── broadcasts/           # Broadcasts module
│       │   │   ├── __init__.py
│       │   │   ├── models.py
│       │   │   ├── schemas.py
│       │   │   ├── repository.py
│       │   │   ├── service.py
│       │   │   └── router.py
│       │   │
│       │   ├── schedule/             # Schedule module
│       │   │   ├── __init__.py
│       │   │   ├── models.py
│       │   │   ├── schemas.py
│       │   │   ├── repository.py
│       │   │   ├── service.py
│       │   │   └── router.py
│       │   │
│       │   └── settings/              # Settings module
│       │       ├── __init__.py
│       │       ├── models.py
│       │       ├── schemas.py
│       │       ├── repository.py
│       │       ├── service.py
│       │       └── router.py
│       │
│       └── workers/                  # Background tasks
│           ├── __init__.py
│           ├── celery_app.py        # Celery configuration
│           └── tasks/                # Task definitions
│               ├── __init__.py
│               ├── subscription_tasks.py
│               ├── payment_tasks.py
│               └── broadcast_tasks.py
│
├── bot/                              # Telegram Bot (aiogram)
│   ├── .gitignore
│   ├── Dockerfile                    # Bot Docker image
│   ├── requirements.txt              # Bot dependencies
│   │
│   └── src/                          # Bot source code
│       ├── main.py                   # Bot entry point
│       │
│       ├── handlers/                  # Message handlers
│       │   ├── __init__.py          # Handler registration
│       │   ├── start.py             # /start command
│       │   ├── subscription.py      # Subscription handlers
│       │   ├── payment.py           # Payment handlers
│       │   └── menu.py              # Menu handlers
│       │
│       ├── keyboards/                # Inline keyboards
│       │   ├── __init__.py
│       │   └── main_menu.py         # Main menu keyboard
│       │
│       ├── services/                 # Business services
│       │   ├── __init__.py
│       │   └── api_client.py        # Backend API client
│       │
│       ├── middlewares/              # Bot middlewares
│       │   └── __init__.py          # Middleware registration
│       │
│       └── utils/                    # Utilities
│           ├── __init__.py
│           └── config.py            # Bot configuration
│
├── docker/                           # Docker configuration
│   ├── docker-compose.yml            # Multi-container setup
│   │
│   └── nginx/                        # Nginx configuration
│       ├── nginx.conf                # Main Nginx config
│       └── conf.d/
│           └── backend.conf          # Backend proxy config
│
├── miniapp/                          # React Mini App (existing)
│   └── (existing React application)
│
├── admin/                            # Admin Panel (future)
│   └── (to be implemented)
│
├── ARCHITECTURE.md                   # System architecture document
├── PROJECT_STRUCTURE.md              # Detailed structure documentation
└── PROJECT_TREE.md                   # This file
```

## File Count Summary

- **Backend**: ~75 files
- **Bot**: ~15 files
- **Docker**: 4 files
- **Total**: ~94 files

## Module Structure Pattern

Each module follows this structure:

```
module_name/
├── __init__.py       # Module exports
├── models.py         # SQLAlchemy models (database schema)
├── schemas.py        # Pydantic schemas (API validation)
├── repository.py     # Data access layer (database queries)
├── service.py        # Business logic layer
└── router.py         # FastAPI route handlers
```

## Key Files

### Backend Entry Point
- `backend/src/main.py` - FastAPI application initialization

### Configuration
- `backend/src/core/config/settings.py` - Application settings
- `backend/.env.example` - Environment variables template

### Database
- `backend/src/core/db/database.py` - Database connection
- `backend/src/core/db/base_model.py` - Base model class
- `backend/alembic/` - Database migrations

### Security
- `backend/src/core/security/jwt.py` - JWT token handling
- `backend/src/core/security/dependencies.py` - Auth dependencies

### Bot Entry Point
- `bot/src/main.py` - Bot initialization

### Docker
- `docker/docker-compose.yml` - Container orchestration

## Next Steps

1. Implement database models in `models.py` files
2. Implement repository methods in `repository.py` files
3. Implement business logic in `service.py` files
4. Complete route handlers in `router.py` files
5. Implement bot handlers
6. Configure background tasks
7. Add tests
