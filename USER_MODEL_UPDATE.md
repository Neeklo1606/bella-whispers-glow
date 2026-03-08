# User Model Update - Telegram & Admin Users Support

## ✅ Changes Summary

### 1. Created UserRole Enum
**File**: `backend/src/modules/users/enums.py`

```python
class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"
```

### 2. Updated User Model
**File**: `backend/src/modules/users/models.py`

**Changes**:
- ✅ Removed `is_admin` boolean field
- ✅ Added `role` field (UserRole enum)
- ✅ Added `password_hash` field (nullable)
- ✅ `telegram_id` remains nullable (for admin users)
- ✅ `email` remains nullable (for Telegram users)

**New Fields**:
- `password_hash`: String(255), nullable - For admin users
- `role`: Enum(UserRole), default=USER, indexed

**Properties**:
- `is_admin` - Returns True if role is ADMIN or SUPER_ADMIN
- `is_telegram_user` - Returns True if telegram_id is not None
- `is_admin_user` - Returns True if email and password_hash are set

### 3. Updated User Schemas
**File**: `backend/src/modules/users/schemas.py`

**Changes**:
- Added `role` field to all schemas
- Added `password` field to UserCreate and UserUpdate (plain text, will be hashed)
- Updated UserResponse to include role and helper properties

### 4. Created Migration
**File**: `backend/alembic/versions/002_add_user_password_and_role.py`

**Migration Actions**:
1. Creates `userrole` enum type
2. Adds `password_hash` column (nullable)
3. Adds `role` column with default 'user'
4. Creates index on `role`
5. Migrates existing `is_admin` data to `role`
6. Drops `is_admin` column

### 5. Authentication Strategies
**File**: `backend/src/modules/auth/strategies.py`

**Two Strategies**:

1. **TelegramAuthStrategy**
   - Authenticates by `telegram_id`
   - Creates user if doesn't exist
   - Returns JWT tokens

2. **AdminAuthStrategy**
   - Authenticates by `email` + `password`
   - Verifies password hash
   - Checks admin role
   - Returns JWT tokens

### 6. Updated Auth Service
**File**: `backend/src/modules/auth/service.py`

- Uses strategy pattern for authentication
- Supports both Telegram and Admin authentication
- Implements token refresh

### 7. Updated User Repository
**File**: `backend/src/modules/users/repository.py`

**New Methods**:
- `get_by_email()` - Get user by email
- `create()` - Automatically hashes password if provided
- `update()` - Automatically hashes password if provided

---

## 📋 Final User Model Structure

```python
class User(BaseModel):
    # Identity
    id: UUID (PK)
    
    # Telegram fields (nullable for admin users)
    telegram_id: BigInteger (unique, nullable, indexed)
    username: String(255, nullable)
    first_name: String(255, nullable)
    last_name: String(255, nullable)
    avatar_url: String(512, nullable)
    
    # Admin fields (nullable for Telegram users)
    email: String(255, unique, nullable, indexed)
    password_hash: String(255, nullable)
    
    # Role
    role: Enum(UserRole) (default: USER, indexed)
    
    # Timestamps
    created_at: DateTime
    updated_at: DateTime
    
    # Relationships
    subscriptions: One-to-Many → Subscription
    payments: One-to-Many → Payment
```

---

## 🔐 Authentication Flow

### Telegram Users
1. User opens Mini App
2. Mini App sends Telegram auth data
3. Backend verifies Telegram hash (TODO)
4. Backend gets or creates user by `telegram_id`
5. Backend generates JWT tokens
6. User authenticated

### Admin Users
1. Admin enters email + password
2. Backend finds user by `email`
3. Backend verifies `password_hash`
4. Backend checks `role` (must be ADMIN or SUPER_ADMIN)
5. Backend generates JWT tokens
6. Admin authenticated

---

## 📊 Database Schema

### Users Table (Updated)

| Column | Type | Nullable | Unique | Index | Default |
|--------|------|----------|--------|-------|---------|
| id | UUID | No | Yes | Yes | uuid4() |
| telegram_id | BigInteger | Yes | Yes | Yes | NULL |
| username | String(255) | Yes | No | No | NULL |
| first_name | String(255) | Yes | No | No | NULL |
| last_name | String(255) | Yes | No | No | NULL |
| avatar_url | String(512) | Yes | No | No | NULL |
| email | String(255) | Yes | Yes | Yes | NULL |
| password_hash | String(255) | Yes | No | No | NULL |
| role | Enum(UserRole) | No | No | Yes | 'user' |
| created_at | DateTime | No | No | No | NOW() |
| updated_at | DateTime | No | No | No | NOW() |

### Indexes
- `idx_users_telegram_id` (unique)
- `idx_users_email` (unique)
- `idx_users_role`

---

## 🚀 Migration Instructions

### Apply Migration

```bash
cd backend
alembic upgrade head
```

This will:
1. Create `userrole` enum
2. Add `password_hash` column
3. Add `role` column
4. Migrate existing data
5. Drop `is_admin` column

### Rollback (if needed)

```bash
alembic downgrade -1
```

---

## 📝 Usage Examples

### Create Telegram User
```python
user = await repository.create({
    "telegram_id": 123456789,
    "username": "john_doe",
    "first_name": "John",
    "role": UserRole.USER,
})
```

### Create Admin User
```python
user = await repository.create({
    "email": "admin@example.com",
    "password": "secure_password",  # Will be hashed automatically
    "first_name": "Admin",
    "role": UserRole.ADMIN,
})
```

### Check User Type
```python
if user.is_telegram_user:
    # Telegram user logic
    pass

if user.is_admin_user:
    # Admin user logic
    pass

if user.is_admin:
    # Admin or super_admin
    pass
```

---

## ✅ Status

- ✅ UserRole enum created
- ✅ User model updated
- ✅ Migration created
- ✅ Authentication strategies implemented
- ✅ Repository methods updated
- ✅ Schemas updated

**Ready for**: Database migration and testing
