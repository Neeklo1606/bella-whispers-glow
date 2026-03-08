# Deployment System - Summary

## ✅ All Tasks Completed

### 1. Server Project Structure ✅
- Project location: `/var/www/bella`
- Structure: `backend/`, `bot/`, `miniapp/`

### 2. Systemd Services ✅
Created 3 services:
- `bella-backend.service` - FastAPI backend
- `bella-bot.service` - Telegram bot
- `bella-scheduler.service` - Background scheduler

### 3. Deployment Script ✅
- Created `/var/www/bella/deploy.sh`
- Handles: git pull, dependencies, migrations, service restart

### 4. SSH Deploy Command ✅
```bash
ssh root@155.212.210.214 "bash /var/www/bella/deploy.sh"
```

### 5. Git Automation ✅
- Created `deploy.ps1` for Windows/Cursor
- Auto-commits and pushes changes
- Then deploys to server

---

## 📋 Systemd Service Files

### bella-backend.service
```ini
[Unit]
Description=Bella Subscription Platform Backend API
After=network.target postgresql.service redis.service
Requires=postgresql.service redis.service

[Service]
Type=simple
User=root
WorkingDirectory=/var/www/bella/backend
ExecStart=/usr/bin/python3 -m uvicorn src.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### bella-bot.service
```ini
[Unit]
Description=Bella Subscription Platform Telegram Bot
After=network.target bella-backend.service
Requires=bella-backend.service

[Service]
Type=simple
User=root
WorkingDirectory=/var/www/bella/bot
ExecStart=/usr/bin/python3 src/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### bella-scheduler.service
```ini
[Unit]
Description=Bella Subscription Platform Background Scheduler
After=network.target bella-backend.service
Requires=bella-backend.service

[Service]
Type=simple
User=root
WorkingDirectory=/var/www/bella/backend
ExecStart=/usr/bin/python3 -c "import sys; sys.path.insert(0, '/var/www/bella/backend'); from src.workers.scheduler import create_scheduler, start_scheduler; import asyncio; scheduler = create_scheduler(); start_scheduler(scheduler); asyncio.get_event_loop().run_forever()"
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

---

## 📜 Deploy Script (deploy.sh)

**Location**: `/var/www/bella/deploy.sh`

**Script Steps**:
1. Pull latest code from git
2. Install backend dependencies (`pip install -r requirements.txt`)
3. Install bot dependencies
4. Install and build miniapp (`npm install && npm run build`)
5. Run database migrations (`alembic upgrade head`)
6. Restart backend service
7. Restart bot service
8. Restart scheduler service
9. Check service status

**Features**:
- Error handling (`set -e`)
- Colored output
- Status verification
- Service health checks

---

## 🚀 Deployment Commands

### From Cursor (Recommended)

```powershell
# Full deployment (commit + push + deploy)
.\deploy.ps1

# Deploy without committing
.\deploy.ps1 -SkipCommit

# Custom commit message
.\deploy.ps1 -CommitMessage "Fix: update user authentication"
```

### Direct SSH

```bash
ssh root@155.212.210.214 "bash /var/www/bella/deploy.sh"
```

---

## 📁 File Locations

### Local (Windows)
- `deploy.ps1` - PowerShell deployment script
- `deployment/bella-backend.service` - Backend service file
- `deployment/bella-bot.service` - Bot service file
- `deployment/bella-scheduler.service` - Scheduler service file
- `deployment/deploy.sh` - Server deployment script

### Server (Linux)
- `/var/www/bella/deploy.sh` - Deployment script
- `/etc/systemd/system/bella-backend.service` - Backend service
- `/etc/systemd/system/bella-bot.service` - Bot service
- `/etc/systemd/system/bella-scheduler.service` - Scheduler service

---

## 🔧 Service Management

### Start Services
```bash
systemctl start bella-backend
systemctl start bella-bot
systemctl start bella-scheduler
```

### Stop Services
```bash
systemctl stop bella-backend
systemctl stop bella-bot
systemctl stop bella-scheduler
```

### Restart Services
```bash
systemctl restart bella-backend
systemctl restart bella-bot
systemctl restart bella-scheduler
```

### Check Status
```bash
systemctl status bella-backend
systemctl status bella-bot
systemctl status bella-scheduler
```

### View Logs
```bash
journalctl -u bella-backend -f
journalctl -u bella-bot -f
journalctl -u bella-scheduler -f
```

---

## ✅ Status

- ✅ Systemd services created and configured
- ✅ Deployment script created and uploaded
- ✅ PowerShell script for automated deployment
- ✅ Git automation implemented
- ✅ Services enabled on server
- ✅ Ready for deployment

---

**Domain**: https://app.bellahasias.ru

**Server**: root@155.212.210.214
