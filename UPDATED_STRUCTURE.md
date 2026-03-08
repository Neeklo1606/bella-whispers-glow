# Updated Project Structure

## Changes Made

### 1. Removed Docker
- ✅ Deleted `docker/` directory
- ✅ Deleted all `Dockerfile` files
- ✅ Removed docker-compose.yml
- ✅ Removed nginx configurations

**Reason**: Project will run directly on server using Python.

### 2. Replaced Celery with APScheduler
- ✅ Removed Celery dependencies
- ✅ Added APScheduler
- ✅ Created `scheduler.py` for job registration
- ✅ Updated tasks to use async functions
- ✅ Integrated scheduler into FastAPI lifespan

**Reason**: APScheduler is lighter and sufficient for MVP.

### 3. Implemented SQLAlchemy Models
- ✅ Created all 6 table models
- ✅ Defined fields, indexes, foreign keys
- ✅ Set up relationships

### 4. Created Alembic Migration
- ✅ Initial migration file created
- ✅ All tables, indexes, constraints defined

---

## Updated Root Structure

```
bella/
├── backend/          # FastAPI backend
├── bot/              # Telegram bot (aiogram)
├── miniapp/          # React Mini App (existing)
└── admin/            # Admin panel (future)
```

---

## Backend Structure

```
backend/
├── src/
│   ├── core/                    # Core components
│   │   ├── config/              # Configuration
│   │   ├── db/                  # Database setup
│   │   ├── security/            # Security (JWT)
│   │   └── utils/               # Utilities (Redis)
│   │
│   ├── modules/                 # Business modules
│   │   ├── auth/
│   │   ├── users/               # ✅ Models implemented
│   │   ├── subscriptions/       # ✅ Models implemented
│   │   ├── payments/            # ✅ Models implemented
│   │   ├── telegram/
│   │   ├── broadcasts/          # ✅ Models implemented
│   │   ├── schedule/
│   │   └── settings/            # ✅ Models implemented
│   │
│   ├── workers/                 # Background jobs (APScheduler)
│   │   ├── scheduler.py         # ✅ Scheduler configuration
│   │   └── tasks/
│   │       ├── subscription_tasks.py
│   │       ├── payment_tasks.py
│   │       └── broadcast_tasks.py
│   │
│   └── main.py                  # FastAPI app
│
├── alembic/                     # Database migrations
│   ├── versions/
│   │   └── 001_initial_migration_create_all_tables.py  # ✅ Initial migration
│   ├── env.py
│   └── script.py.mako
│
├── requirements.txt             # ✅ Updated (APScheduler instead of Celery)
└── README.md
```

---

## Database Models

### 1. User Model
**Table**: `users`
- Fields: id, telegram_id, username, first_name, last_name, email, avatar_url, is_admin, created_at, updated_at
- Indexes: telegram_id (unique), email (unique)
- Relationships: subscriptions, payments

### 2. SubscriptionPlan Model
**Table**: `subscription_plans`
- Fields: id, name, description, price, first_month_price, duration_days, features (JSON), is_active, created_at, updated_at
- Indexes: is_active
- Relationships: subscriptions

### 3. Subscription Model
**Table**: `subscriptions`
- Fields: id, user_id (FK), plan_id (FK), status (enum), start_date, end_date, auto_renew, cancelled_at, next_billing_date, created_at, updated_at
- Indexes: user_id, status, end_date, (user_id, status)
- Foreign Keys: user_id → users.id, plan_id → subscription_plans.id
- Relationships: user, plan, payments

### 4. Payment Model
**Table**: `payments`
- Fields: id, user_id (FK), subscription_id (FK), amount, currency, status (enum), payment_provider, provider_payment_id, payment_url, paid_at, metadata (JSON), created_at, updated_at
- Indexes: user_id, status, provider_payment_id (unique), (user_id, status)
- Foreign Keys: user_id → users.id, subscription_id → subscriptions.id
- Relationships: user, subscription

### 5. Broadcast Model
**Table**: `broadcasts`
- Fields: id, created_by (FK), title, content, media_url, scheduled_at, sent_at, status (enum), telegram_message_id, created_at, updated_at
- Indexes: created_by, status, scheduled_at, (status, scheduled_at)
- Foreign Keys: created_by → users.id
- Relationships: creator

### 6. SystemSetting Model
**Table**: `system_settings`
- Fields: id, key (unique), value (JSON), description, created_at, updated_at
- Indexes: key (unique)

---

## Background Jobs (APScheduler)

### Registered Jobs

1. **check_expired_subscriptions**
   - Schedule: Daily at 00:00 UTC
   - Task: Check and expire subscriptions

2. **process_auto_renewals**
   - Schedule: Daily at 00:05 UTC
   - Task: Process automatic renewals

3. **send_renewal_reminders**
   - Schedule: Daily at 09:00 UTC
   - Task: Send renewal reminders

4. **verify_pending_payments**
   - Schedule: Every 5 minutes
   - Task: Verify payment status

5. **send_scheduled_broadcasts**
   - Schedule: Every minute
   - Task: Send scheduled broadcasts

---

## Migration File

**Location**: `backend/alembic/versions/001_initial_migration_create_all_tables.py`

**Contains**:
- All 6 tables creation
- All indexes
- All foreign keys
- All constraints
- Enum types creation
- Downgrade function

---

## Next Steps

1. ✅ Project structure cleaned
2. ✅ Docker removed
3. ✅ Celery replaced with APScheduler
4. ✅ Models implemented
5. ✅ Migration created
6. ⏳ Implement repository methods
7. ⏳ Implement service logic
8. ⏳ Implement bot handlers
9. ⏳ Test migration

---

## Running the Project

### Setup Database

```bash
cd backend
alembic upgrade head
```

### Start Backend

```bash
cd backend
uvicorn src.main:app --reload
```

### Start Bot

```bash
cd bot
python src/main.py
```

---

**Updated**: 2026-03-08
