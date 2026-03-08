# Deployment Report — 155.212.210.214

**Date:** 2026-03-08  
**Server:** root@155.212.210.214  
**Project path:** /var/www/bella

---

## Summary

**Deployment could not be completed** because the backend and bot directories are not present in the repository on the server.

---

## STEP 1 — Connect

- **Status:** OK
- **Project directory:** /var/www/bella
- **Branch:** main (commit 40c4b2e)
- **Remote:** https://github.com/Neeklo1606/bella-whispers-glow.git

---

## STEP 2 — Update code

- **Status:** OK
- **Result:** `git pull` — "Already up to date"
- Repository is on the latest main

---

## STEP 3–5 — Backend steps (skipped)

- **Status:** Blocked
- **Reason:** `/var/www/bella/backend` does not exist
- The git repo does not contain a `backend/` directory
- Systemd service `bella-backend.service` expects: `WorkingDirectory=/var/www/bella/backend`

---

## STEP 6 — Restart services

- **Status:** Failed
- **Result:** Services fail to start because:
  1. `Unit redis.service not found`
  2. Backend directory is missing
- **Services:**
  - `bella-backend.service` — inactive (dead)
  - `bella-bot.service` — inactive (dead)
  - `bella-scheduler.service` — inactive (dead)

---

## STEP 7–12 — Verification (skipped)

- Health check — not run (backend not running)
- Telegram bot — not run
- Payment webhook — not run

---

## Required actions before deployment

### 1. Add backend and bot to the repository

Ensure the repo includes:

- `backend/` (FastAPI app, alembic, requirements.txt)
- `bot/` (Telegram bot)

Then push and pull on the server:

```bash
git pull
```

### 2. Install and enable Redis

Services depend on Redis but it is not installed or enabled:

```bash
# Ubuntu/Debian
apt install redis-server
systemctl enable redis-server
systemctl start redis-server
```

### 3. Re-run deployment

```bash
cd /var/www/bella
bash deploy.sh
```

---

## Current server setup

| Item            | Status                    |
|-----------------|---------------------------|
| Project path    | /var/www/bella            |
| Backend dir     | Missing                   |
| Bot dir         | Missing                   |
| bella-backend   | Inactive (backend missing)|
| bella-bot       | Inactive                  |
| bella-scheduler | Inactive                  |
| PostgreSQL      | Not verified              |
| Redis           | Not found                 |

---

## Configuration files (unchanged)

- No system or application configuration files were changed during this deployment attempt.
