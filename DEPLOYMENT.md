# Deployment Documentation

## Server Structure

```
/var/www/bella/
├── backend/          # FastAPI backend
├── bot/              # Telegram bot
├── miniapp/          # React Mini App
└── deploy.sh         # Deployment script
```

## Systemd Services

### 1. bella-backend.service
**Location**: `/etc/systemd/system/bella-backend.service`

**Command**: `uvicorn src.main:app --host 0.0.0.0 --port 8000`

**Dependencies**: PostgreSQL, Redis

### 2. bella-bot.service
**Location**: `/etc/systemd/system/bella-bot.service`

**Command**: `python src/main.py`

**Dependencies**: Backend service

### 3. bella-scheduler.service
**Location**: `/etc/systemd/system/bella-scheduler.service`

**Command**: Runs APScheduler for background jobs

**Dependencies**: Backend service

## Deployment Script

**Location**: `/var/www/bella/deploy.sh`

**Steps**:
1. Pull latest code from git
2. Install backend dependencies
3. Install bot dependencies
4. Install and build miniapp
5. Run database migrations
6. Restart all services

## Deployment Commands

### From Cursor (Windows)

```powershell
# Full deployment (commit + push + deploy)
.\deploy.ps1

# Deploy without committing
.\deploy.ps1 -SkipCommit

# Deploy with custom commit message
.\deploy.ps1 -CommitMessage "Fix: update user model"
```

### Direct SSH Deployment

```bash
ssh root@155.212.210.214 "bash /var/www/bella/deploy.sh"
```

## Service Management

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

## Initial Setup

### 1. Install Services

```bash
# Copy service files
cp deployment/bella-backend.service /etc/systemd/system/
cp deployment/bella-bot.service /etc/systemd/system/
cp deployment/bella-scheduler.service /etc/systemd/system/

# Reload systemd
systemctl daemon-reload

# Enable services
systemctl enable bella-backend
systemctl enable bella-bot
systemctl enable bella-scheduler
```

### 2. Create Project Structure

```bash
mkdir -p /var/www/bella/{backend,bot,miniapp}
```

### 3. Clone Repository

```bash
cd /var/www/bella
git clone https://github.com/Neeklo1606/bella-whispers-glow.git .
```

## Environment Variables

Backend requires `.env` file in `/var/www/bella/backend/`:

```bash
# Copy from example
cp backend/.env.example backend/.env

# Edit with actual values
nano backend/.env
```

Bot requires `.env` file in `/var/www/bella/bot/`:

```bash
# Copy from example
cp bot/.env.example bot/.env

# Edit with actual values
nano bot/.env
```

## Troubleshooting

### Service won't start
```bash
# Check logs
journalctl -u bella-backend -n 50

# Check service file
systemctl cat bella-backend

# Test command manually
cd /var/www/bella/backend
python3 -m uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### Deployment fails
```bash
# Run deploy script manually with verbose output
bash -x /var/www/bella/deploy.sh
```

### Database migration errors
```bash
cd /var/www/bella/backend
alembic current
alembic history
alembic upgrade head --sql  # Preview SQL
```
