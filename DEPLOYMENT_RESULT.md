# Deployment System - Final Result

## ✅ Completed Tasks

### 1. Server Project Structure
- ✅ Project located at `/var/www/bella`
- ✅ Structure: `backend/`, `bot/`, `miniapp/`

### 2. Systemd Services Created
- ✅ `bella-backend.service`
- ✅ `bella-bot.service`
- ✅ `bella-scheduler.service`

### 3. Deployment Script Created
- ✅ `/var/www/bella/deploy.sh`
- ✅ Handles: git pull, dependencies, migrations, service restart

### 4. SSH Deploy Command
- ✅ `ssh root@155.212.210.214 "bash /var/www/bella/deploy.sh"`

### 5. Git Automation
- ✅ PowerShell script `deploy.ps1` for Windows/Cursor
- ✅ Commits changes automatically
- ✅ Pushes to repository
- ✅ Deploys to server

---

## 📁 Files Created

### Systemd Services

1. **bella-backend.service**
   - Location: `deployment/bella-backend.service`
   - Command: `uvicorn src.main:app --host 0.0.0.0 --port 8000`
   - Dependencies: PostgreSQL, Redis

2. **bella-bot.service**
   - Location: `deployment/bella-bot.service`
   - Command: `python src/main.py`
   - Dependencies: Backend service

3. **bella-scheduler.service**
   - Location: `deployment/bella-scheduler.service`
   - Command: Runs APScheduler
   - Dependencies: Backend service

### Deployment Scripts

1. **deploy.sh** (Server-side)
   - Location: `/var/www/bella/deploy.sh`
   - Handles full deployment process

2. **deploy.ps1** (Local/Cursor)
   - Location: `deploy.ps1` (project root)
   - Handles: Git commit, push, and server deployment

3. **setup-services.sh**
   - Location: `deployment/setup-services.sh`
   - One-time setup script for systemd services

---

## 🚀 Usage

### From Cursor (Recommended)

```powershell
# Full deployment (commit + push + deploy)
.\deploy.ps1

# Deploy without committing
.\deploy.ps1 -SkipCommit

# Custom commit message
.\deploy.ps1 -CommitMessage "Feature: add user roles"
```

### Direct SSH Command

```bash
ssh root@155.212.210.214 "bash /var/www/bella/deploy.sh"
```

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
ExecStart=/usr/bin/python3 -c "from src.workers.scheduler import create_scheduler, start_scheduler; import asyncio; scheduler = create_scheduler(); start_scheduler(scheduler); asyncio.get_event_loop().run_forever()"
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

---

## 📜 Deploy Script (deploy.sh)

**Location**: `/var/www/bella/deploy.sh`

**Steps**:
1. ✅ Pull latest code from git
2. ✅ Install backend dependencies (`pip install -r requirements.txt`)
3. ✅ Install bot dependencies
4. ✅ Install and build miniapp (`npm install && npm run build`)
5. ✅ Run database migrations (`alembic upgrade head`)
6. ✅ Restart all services (backend, bot, scheduler)
7. ✅ Check service status

**Features**:
- Error handling (set -e)
- Colored output
- Status checks
- Service health verification

---

## 🔧 Initial Setup on Server

### 1. Install Systemd Services

```bash
# Copy service files
cp /tmp/bella-backend.service /etc/systemd/system/
cp /tmp/bella-bot.service /etc/systemd/system/
cp /tmp/bella-scheduler.service /etc/systemd/system/

# Or use setup script
bash /var/www/bella/deployment/setup-services.sh

# Reload systemd
systemctl daemon-reload

# Enable services
systemctl enable bella-backend bella-bot bella-scheduler
```

### 2. Start Services

```bash
systemctl start bella-backend
systemctl start bella-bot
systemctl start bella-scheduler
```

### 3. Verify

```bash
systemctl status bella-backend
systemctl status bella-bot
systemctl status bella-scheduler
```

---

## 📝 Deployment Workflow

### Automated (from Cursor)

1. **Developer makes changes**
2. **Runs**: `.\deploy.ps1`
3. **Script**:
   - Commits changes to git
   - Pushes to repository
   - Connects to server via SSH
   - Executes `deploy.sh` on server
4. **Server**:
   - Pulls latest code
   - Installs dependencies
   - Runs migrations
   - Restarts services
5. **Done!** ✅

### Manual (SSH)

```bash
ssh root@155.212.210.214 "bash /var/www/bella/deploy.sh"
```

---

## 🔍 Monitoring

### View Logs

```bash
# Backend logs
journalctl -u bella-backend -f

# Bot logs
journalctl -u bella-bot -f

# Scheduler logs
journalctl -u bella-scheduler -f

# All services
journalctl -u bella-* -f
```

### Check Status

```bash
systemctl status bella-backend
systemctl status bella-bot
systemctl status bella-scheduler
```

### Service Management

```bash
# Restart single service
systemctl restart bella-backend

# Restart all services
systemctl restart bella-backend bella-bot bella-scheduler

# Stop services
systemctl stop bella-backend bella-bot bella-scheduler

# Start services
systemctl start bella-backend bella-bot bella-scheduler
```

---

## ✅ Deployment Checklist

- [x] Systemd services created
- [x] Deploy script created and uploaded
- [x] PowerShell deployment script created
- [x] Git automation implemented
- [x] Service dependencies configured
- [x] Error handling in scripts
- [x] Logging configured
- [x] Documentation created

---

## 🎯 Quick Deploy Command

**From Cursor**:
```powershell
.\deploy.ps1
```

**From SSH**:
```bash
ssh root@155.212.210.214 "bash /var/www/bella/deploy.sh"
```

---

**Status**: ✅ Deployment system ready

**Domain**: https://app.bellahasias.ru
