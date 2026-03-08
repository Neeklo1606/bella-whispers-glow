# System Settings Implementation Audit Report

**Date:** 2026-03-08  
**Scope:** `system_settings` and `settings` modules, TelegramBotService, admin API, scheduler, database, frontend

---

## STEP 1 — MODULE DUPLICATION

### Finding: Both modules exist with overlapping responsibilities

| Module | Contents | Uses |
|--------|----------|------|
| `modules/system_settings` | SystemSetting model, SystemSettingRepository, SystemSettingService | Own model (value: `Text`) |
| `modules/settings` | SettingsRepository, SettingsService, router, schemas, **duplicate** SystemSetting model | Imports `system_settings.models.SystemSetting` in repository |

### Duplication details

1. **Two SystemSetting model definitions**
   - `settings/models.py`: `value = Column(JSON, nullable=False)` 
   - `system_settings/models.py`: `value = Column(Text, nullable=True)`
   - Alembic migration 005 defines `value` as `sa.Text()` — **matches system_settings only**.

2. **Two services performing the same work**
   - `SystemSettingService`: `get()`, `set()`, `get_all()`, `delete()`
   - `SettingsService`: `get_settings()`, `get_setting()`, `update_setting()` — wraps same `system_settings` table via `SettingsRepository` → `system_settings.models`

3. **Split consumers**
   - **TelegramBotService** → `SystemSettingService` (system_settings)
   - **Admin API** → `SettingsService` (settings)

### Recommendation

**Merge into `modules/system_settings`.** Remove `modules/settings` and:

- Move admin endpoints into admin router (already done) or a sub-router under system_settings
- Deprecate `SettingsService`; use `SystemSettingService` only
- Delete `settings/models.py` (or keep one canonical model in system_settings)
- Ensure `init_db` and `alembic/env.py` import from `system_settings.models`

---

## STEP 2 — TELEGRAM BOT SERVICE (PERFORMANCE)

### Finding: Bot instance is recreated on every request

| Call site | Behavior |
|-----------|----------|
| Admin router (revoke, ban) | `bot_service = await TelegramBotService.create(db)` → new instance, DB read, new `Bot()` |
| Telegram router (revoke-invite-link) | Same |
| SubscriptionService | Lazy `_get_bot_service()` — caches per service instance, but service is per-request |
| subscription_tasks | `bot_service = await TelegramBotService.create(db)` per task run |

### Impact

- Each `TelegramBotService.create()` runs 2 DB queries (token, channel_id) and creates a new aiogram `Bot`.
- No shared/pooled bot instance. High request volume → unnecessary DB load and object creation.

### Recommendation

Introduce a singleton/cached bot factory or app-state bot:

```python
# Option: app.state.telegram_bot or a cached async factory
# Initialize once at startup (or lazily on first use), reuse for all requests
```

---

## STEP 3 — SCHEDULER / DB SESSION LIFECYCLE

### Finding: Session usage is correct

- `subscription_tasks.check_expired_subscriptions()` uses `async with AsyncSessionLocal() as db` for the whole task.
- `TelegramBotService.create(db)` receives that session; `SystemSettingService(db)` runs in the same transaction.
- `bot_service.close()` is called before session ends.
- Session lifecycle is bounded and consistent.

### Status

- Scheduler tasks can access SystemSettingService safely. No changes required.

---

## STEP 4 — ADMIN SETTINGS SECURITY

### Finding: Critical settings can be changed; runtime is unaffected today

| Setting | Used by | Source |
|---------|---------|--------|
| SECRET_KEY | `core/security/jwt.py` | `settings.SECRET_KEY` (ENV at startup) |
| BOT_API_SECRET | `core/security/bot_auth.py` | `settings.BOT_API_SECRET` (ENV at startup) |

- JWT and bot auth read from **environment/startup config**, not from the DB.
- Changes via admin UI update only the database; they have **no effect until restart**.
- Risk: an admin can overwrite DB values with invalid/empty data. If later code starts reading these from the DB, that could break auth.

### Recommendation

1. Add validation/warning when modifying `SECRET_KEY`, `BOT_API_SECRET` (e.g. require confirmation or block edits).
2. Document that runtime changes require restart and are currently not applied.
3. Optionally exclude these keys from admin editing until a proper reload mechanism exists.

---

## STEP 5 — DATABASE STRUCTURE

### Finding: Table structure is correct

- Migration 005: `key` has `unique=True`.
- Index: `idx_system_settings_key` on `key`.
- No extra duplicate-prevention logic needed; unique constraint prevents duplicate rows.

### Status

- Schema is appropriate. No changes required.

---

## STEP 6 — TELEGRAM SETTINGS KEYS

### Finding: Keys are correct

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHANNEL_ID`

Both are used in `TelegramBotService` and in the admin UI. No changes required.

---

## STEP 7 — FALLBACK TO ENV

### Finding: Implemented as required

```python
if not token:
    token = settings.TELEGRAM_BOT_TOKEN
if not channel_id:
    channel_id = settings.TELEGRAM_CHANNEL_ID
```

- Missing or empty DB values fall back to environment variables. No changes required.

---

## STEP 8 — ADMIN API

### Finding: Admin endpoints exist and behave correctly

| Endpoint | Method | Auth | Status |
|----------|--------|------|--------|
| `/api/admin/settings` | GET | `require_admin_user` | OK |
| `/api/admin/settings/{key}` | PUT | `require_admin_user` | OK |

### Security issue: `/api/settings` (non-admin) router

| Endpoint | Method | Auth |
|----------|--------|------|
| `/api/settings` | GET | None |
| `/api/settings/{key}` | GET | None |
| `/api/settings/{key}` | PATCH | `get_current_user_id` |

- **PATCH `/api/settings/{key}`** allows any authenticated user (not just admin) to update settings. This is a serious security gap if settings are sensitive.

### Recommendation

- Remove or protect `PATCH /api/settings/{key}`.
- If it must remain, restrict it to admin users (e.g. `require_admin_user`).

---

## STEP 9 — FRONTEND

### Finding: Admin settings page works correctly

- Route: `/admin/settings`.
- Loads: `GET /api/admin/settings`.
- Updates: `PUT /api/admin/settings/{key}`.
- Sections: Telegram, Payments, Security.
- Uses admin token for requests.
- Per-field save with loading states.

### Status

- Implementation is correct. No changes required.

---

## SUMMARY: ISSUES BY CATEGORY

### Architecture issues

| # | Issue | Severity |
|---|-------|----------|
| 1 | Two modules (`system_settings` and `settings`) with overlapping logic | High |
| 2 | Two `SystemSetting` models; `settings` uses `JSON` for value, migration uses `Text` | High |
| 3 | PATCH `/api/settings/{key}` allows non-admin users to change settings | Critical |
| 4 | GET `/api/settings` returns all settings without auth | Medium |

### Performance risks

| # | Issue | Severity |
|---|-------|----------|
| 1 | `TelegramBotService` recreated on every request | Medium |
| 2 | Two DB reads per bot operation (token + channel_id) | Low |

### Security risks

| # | Issue | Severity |
|---|-------|----------|
| 1 | Non-admin users can PATCH settings via `/api/settings/{key}` | Critical |
| 2 | `SECRET_KEY` and `BOT_API_SECRET` editable in admin with no warning | Medium |
| 3 | GET `/api/settings` exposes all settings without authentication | Medium |

---

## RECOMMENDED ACTION ITEMS (PRIORITY ORDER)

1. **Immediate:** Restrict `/api/settings` PATCH to admin only or remove it; avoid unauthenticated GET if settings are sensitive.
2. **Short-term:** Merge `settings` into `system_settings`; remove duplicate model and service.
3. **Short-term:** Add warnings/restrictions when editing `SECRET_KEY` and `BOT_API_SECRET`.
4. **Medium-term:** Introduce a shared/cached bot instance for `TelegramBotService` to reduce DB and object creation load.
5. **Low:** Revisit whether `/api/settings` should exist or be fully replaced by `/api/admin/settings`.
