# Admin Panel Redeploy Report

**Date:** 2026-03-08  
**Server:** root@155.212.210.214  
**Project Path:** /var/www/bella  

---

## DEPLOYMENT SUCCESSFUL

---

## Summary

| Stage | Status |
|-------|--------|
| 1. Verify local changes | OK |
| 2. Commit changes | OK |
| 3. Push to repository | OK |
| 4. Connect to server | OK |
| 5. Update code on server | OK |
| 6. Rebuild frontend | OK |
| 7. Restart services | OK |
| 8. Verify services | OK – all ACTIVE |
| 9. Health check | OK – `{"status":"ok"}` |
| 10. Admin API (dashboard) | OK – returns real metrics |
| 11. Admin auth | OK – 403 without token |
| 12. Settings keys | OK – TELEGRAM_*, YOOKASSA_* present |
| 13. Frontend | Manual: https://app.bellahasias.ru/admin |
| 14. Final report | OK |

---

## Git Commit Deployed

**Commit:** `9cbd720` – Fix Enum values_callable for Subscription, Payment, Broadcast (PostgreSQL lowercase)  

**Previous:** `0a6570d` – Admin panel connected to real APIs, added tests, removed mock data

---

## Services Status

- **bella-backend:** active (running)
- **bella-bot:** active (running)
- **bella-scheduler:** active (running)

---

## Health Check

```json
{"status":"ok"}
```

---

## Admin API Test (with token)

**Dashboard response:**
```json
{"users_count":1,"active_subscriptions":0,"revenue_today":0.0,"revenue_total":0.0,"churn_rate":0.0,"user":{"id":"38abb309-f806-4125-809f-21a72f9c0877","email":"admin@bella.local","role":"super_admin"}}
```

---

## Admin Auth Verification

- **GET /api/admin/users** without token: **403** (Not authenticated)
- Admin routes require Bearer JWT

---

## Settings Keys (GET /api/admin/settings)

- TELEGRAM_BOT_TOKEN
- TELEGRAM_CHANNEL_ID
- YOOKASSA_SHOP_ID
- YOOKASSA_SECRET_KEY

(BOT_API_SECRET can be added via the settings UI if needed)

---

## Frontend Verification

URL: **https://app.bellahasias.ru/admin**

To verify manually:
- Login required
- Dashboard loads real data
- Settings page updates keys
- Test Telegram button
- Test YooKassa button

---

## Fix Applied During Redeploy

Enum mismatch: PostgreSQL stores lowercase values (`active`, `pending`) while SQLAlchemy defaulted to names (`ACTIVE`, `PENDING`). Added `values_callable=lambda obj: [e.value for e in obj]` to Subscription, Payment, and Broadcast status columns.
