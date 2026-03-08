# API URL Fix – Deployment Verification Report

## Summary

Admin login was calling `http://localhost:8000/api/auth/admin/login` in production. The frontend now uses the current domain.

---

## Changes Applied

### 1. API Base URL Configuration

**File:** `src/lib/api.ts`

**Before:**
```ts
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
```

**After:**
```ts
const API_BASE_URL =
  import.meta.env.VITE_API_URL ||
  (typeof window !== "undefined" ? window.location.origin : "http://localhost:8000");
```

- Production: `VITE_API_URL` from `.env.production` or `window.location.origin` (e.g. `https://app.bellahasias.ru`)
- Development: `VITE_API_URL` or `window.location.origin` (or `http://localhost:8000` when `window` is undefined, e.g. build/SSR)

### 2. Production Environment

**File:** `.env.production`
```
VITE_API_URL=https://app.bellahasias.ru
```

### 3. API Usage

All API calls use `${API_BASE_URL}/api/...`:

- `adminLogin` → `${API_BASE_URL}/api/auth/admin/login`
- `validateAdminToken` → `${API_BASE_URL}/api/admin/dashboard`
- `adminApiRequest` → `${API_BASE_URL}${endpoint}`
- `authenticateTelegram` → `${API_BASE_URL}/api/auth/telegram`
- `userApiRequest` → `${API_BASE_URL}${endpoint}`

---

## Git Status

**Commit:** `ec397ac` – Fix API URL: use VITE_API_URL / window.location.origin instead of localhost

**Note:** Push failed (permission denied for current user). Push manually with credentials that have write access.

---

## Deployment Steps (Manual)

1. **Push to repository**
   ```bash
   git push origin main
   ```

2. **On server**
   ```bash
   cd /var/www/bella
   git pull origin main
   npm install
   npm run build
   ```

3. **Restart backend** (only if backend code changed)
   ```bash
   systemctl restart bella-backend
   ```

4. **Verify**
   - Open https://app.bellahasias.ru/admin
   - Open DevTools → Network
   - Log in as admin
   - Confirm login request goes to `https://app.bellahasias.ru/api/auth/admin/login` (not localhost)

---

## Expected Result

- Login request: `https://app.bellahasias.ru/api/auth/admin/login`
- No requests to `localhost:8000` when using the production site.

---

## Verification Checklist

- [x] API base URL config updated in `src/lib/api.ts`
- [x] `.env.production` created with `VITE_API_URL=https://app.bellahasias.ru`
- [x] All API calls use `${API_BASE_URL}/api/...`
- [ ] Push to main (manual)
- [ ] Rebuild on server
- [ ] Confirm login request URL in browser Network tab
