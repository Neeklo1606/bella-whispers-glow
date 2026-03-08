# Final Project Structure - After Architecture Updates

## ✅ Completed Tasks

1. ✅ **Removed Docker** - All Docker files and directories deleted
2. ✅ **Replaced Celery with APScheduler** - Lightweight scheduler integrated
3. ✅ **Implemented SQLAlchemy Models** - All 6 tables with relationships
4. ✅ **Created Alembic Migration** - Initial migration with all tables

---

## 📁 Updated Project Structure

```
bella/
├── backend/                    # FastAPI Backend
│   ├── src/
│   │   ├── core/
│   │   │   ├── config/         # Settings
│   │   │   ├── db/             # Database
│   │   │   ├── security/       # JWT, auth
│   │   │   └── utils/          # Redis client
│   │   │
│   │   ├── modules/
│   │   │   ├── auth/
│   │   │   ├── users/          # ✅ Models implemented
│   │   │   ├── subscriptions/  # ✅ Models implemented
│   │   │   ├── payments/       # ✅ Models implemented
│   │   │   ├── telegram/
│   │   │   ├── broadcasts/     # ✅ Models implemented
│   │   │   ├── schedule/
│   │   │   └── settings/       # ✅ Models implemented
│   │   │
│   │   ├── workers/            # ✅ APScheduler
│   │   │   ├── scheduler.py
│   │   │   └── tasks/
│   │   │
│   │   └── main.py
│   │
│   ├── alembic/
│   │   ├── versions/
│   │   │   └── 001_initial_migration_create_all_tables.py  # ✅
│   │   └── env.py
│   │
│   └── requirements.txt         # ✅ Updated
│
├── bot/                        # Telegram Bot
├── miniapp/                    # React Mini App
└── admin/                      # Admin Panel (future)
```

---

## 🗄️ Database Models

### 1. User Model (`users` table)

```python
class User(BaseModel):
    telegram_id: BigInteger (unique, indexed)
    username: String(255)
    first_name: String(255)
    last_name: String(255)
    email: String(255, unique, indexed)
    avatar_url: String(512)
    is_admin: Boolean (default: False)
    
    # Relationships
    subscriptions: One-to-Many → Subscription
    payments: One-to-Many → Payment
    
    # Indexes
    idx_users_telegram_id (unique)
    idx_users_email (unique)
```

### 2. SubscriptionPlan Model (`subscription_plans` table)

```python
class SubscriptionPlan(BaseModel):
    name: String(255)
    description: String(1000)
    price: Numeric(10, 2)
    first_month_price: Numeric(10, 2)
    duration_days: Integer (default: 30)
    features: JSON
    is_active: Boolean (default: True)
    
    # Relationships
    subscriptions: One-to-Many → Subscription
    
    # Indexes
    idx_subscription_plans_is_active
```

### 3. Subscription Model (`subscriptions` table)

```python
class Subscription(BaseModel):
    user_id: UUID (FK → users.id)
    plan_id: UUID (FK → subscription_plans.id)
    status: Enum (active, expired, cancelled, pending)
    start_date: DateTime(timezone=True)
    end_date: DateTime(timezone=True, indexed)
    auto_renew: Boolean (default: True)
    cancelled_at: DateTime(timezone=True)
    next_billing_date: DateTime(timezone=True)
    
    # Relationships
    user: Many-to-One → User
    plan: Many-to-One → SubscriptionPlan
    payments: One-to-Many → Payment
    
    # Indexes
    idx_subscriptions_user_id
    idx_subscriptions_status
    idx_subscriptions_end_date
    idx_subscriptions_user_status (composite)
    
    # Foreign Keys
    user_id → users.id (CASCADE DELETE)
    plan_id → subscription_plans.id (CASCADE DELETE)
```

### 4. Payment Model (`payments` table)

```python
class Payment(BaseModel):
    user_id: UUID (FK → users.id)
    subscription_id: UUID (FK → subscriptions.id, nullable)
    amount: Numeric(10, 2)
    currency: String(3, default: 'RUB')
    status: Enum (pending, completed, failed, refunded)
    payment_provider: String(50)
    provider_payment_id: String(255, unique, indexed)
    payment_url: String(512)
    paid_at: DateTime(timezone=True)
    metadata: JSON
    
    # Relationships
    user: Many-to-One → User
    subscription: Many-to-One → Subscription
    
    # Indexes
    idx_payments_user_id
    idx_payments_status
    idx_payments_provider_payment_id (unique)
    idx_payments_user_status (composite)
    
    # Foreign Keys
    user_id → users.id (CASCADE DELETE)
    subscription_id → subscriptions.id (CASCADE DELETE)
```

### 5. Broadcast Model (`broadcasts` table)

```python
class Broadcast(BaseModel):
    created_by: UUID (FK → users.id)
    title: String(255)
    content: Text
    media_url: String(512)
    scheduled_at: DateTime(timezone=True, indexed)
    sent_at: DateTime(timezone=True)
    status: Enum (draft, scheduled, sent, failed)
    telegram_message_id: BigInteger
    
    # Relationships
    creator: Many-to-One → User
    
    # Indexes
    idx_broadcasts_created_by
    idx_broadcasts_status
    idx_broadcasts_scheduled_at
    idx_broadcasts_status_scheduled (composite)
    
    # Foreign Keys
    created_by → users.id (CASCADE DELETE)
```

### 6. SystemSetting Model (`system_settings` table)

```python
class SystemSetting(BaseModel):
    key: String(255, unique, indexed)
    value: JSON
    description: Text
    
    # Indexes
    idx_system_settings_key (unique)
```

---

## ⏰ Background Jobs (APScheduler)

### Scheduler Configuration

**Location**: `backend/src/workers/scheduler.py`

**Jobs Registered**:

1. **check_expired_subscriptions**
   - Trigger: Cron (daily at 00:00 UTC)
   - Function: `subscription_tasks.check_expired_subscriptions()`

2. **process_auto_renewals**
   - Trigger: Cron (daily at 00:05 UTC)
   - Function: `subscription_tasks.process_auto_renewals()`

3. **send_renewal_reminders**
   - Trigger: Cron (daily at 09:00 UTC)
   - Function: `subscription_tasks.send_renewal_reminders()`

4. **verify_pending_payments**
   - Trigger: Interval (every 5 minutes)
   - Function: `payment_tasks.verify_pending_payments()`

5. **send_scheduled_broadcasts**
   - Trigger: Interval (every minute)
   - Function: `broadcast_tasks.send_scheduled_broadcasts()`

**Integration**: Scheduler starts automatically with FastAPI app via lifespan events.

---

## 📝 Migration File

**File**: `backend/alembic/versions/001_initial_migration_create_all_tables.py`

**Revision ID**: `001_initial`

**Creates**:
- ✅ 6 tables (users, subscription_plans, subscriptions, payments, broadcasts, system_settings)
- ✅ All foreign key constraints
- ✅ All indexes (single and composite)
- ✅ All enum types (SubscriptionStatus, PaymentStatus, BroadcastStatus)
- ✅ Unique constraints
- ✅ Default values
- ✅ CASCADE DELETE on foreign keys

**To Apply Migration**:
```bash
cd backend
alembic upgrade head
```

---

## 🔧 Key Changes Summary

### Removed
- ❌ Docker directory
- ❌ All Dockerfiles
- ❌ docker-compose.yml
- ❌ Nginx configurations
- ❌ Celery
- ❌ Flower

### Added/Updated
- ✅ APScheduler
- ✅ Scheduler integration in FastAPI
- ✅ All SQLAlchemy models
- ✅ Complete Alembic migration
- ✅ Updated requirements.txt

---

## 📊 Database Schema Summary

**Total Tables**: 6
**Total Indexes**: 15+
**Total Foreign Keys**: 5
**Total Enums**: 3

**Relationships**:
- User → Subscriptions (1:N)
- User → Payments (1:N)
- SubscriptionPlan → Subscriptions (1:N)
- Subscription → Payments (1:N)
- User → Broadcasts (1:N, as creator)

---

## 🚀 Next Steps

1. ✅ Project structure updated
2. ✅ Docker removed
3. ✅ APScheduler integrated
4. ✅ Models implemented
5. ✅ Migration created
6. ⏳ Run migration on database
7. ⏳ Implement repository methods
8. ⏳ Implement service logic
9. ⏳ Implement bot handlers
10. ⏳ Test all components

---

**Status**: ✅ Architecture updated and ready for implementation

**Date**: 2026-03-08
