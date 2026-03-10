#!/bin/bash

# Bella Subscription Platform Deployment Script
# This script deploys the application to the server

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="/var/www/bella"
BACKEND_DIR="$PROJECT_DIR/backend"
BOT_DIR="$PROJECT_DIR/bot"
MINIAPP_DIR="$PROJECT_DIR/miniapp"
LOCK_FILE="/tmp/bella_deploy.lock"

echo -e "${GREEN}=== Bella Deployment Script ===${NC}"
echo ""

# Function to print status
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Function to cleanup on exit
cleanup() {
    if [ -f "$LOCK_FILE" ]; then
        rm -f "$LOCK_FILE"
        print_info "Lock file removed"
    fi
}

# Set trap to cleanup on exit
trap cleanup EXIT

# Check for lock file
if [ -f "$LOCK_FILE" ]; then
    print_error "Deployment is already in progress (lock file exists: $LOCK_FILE)"
    print_error "If previous deployment failed, remove the lock file manually: rm $LOCK_FILE"
    exit 1
fi

# Create lock file
touch "$LOCK_FILE"
print_info "Deployment lock acquired"

# Store current commit for safe rollback
cd "$PROJECT_DIR"
if [ -d ".git" ]; then
    PREVIOUS_COMMIT=$(git rev-parse HEAD)
    print_info "Current commit stored: $PREVIOUS_COMMIT"
else
    PREVIOUS_COMMIT=""
    print_warning "Not a git repository, rollback will not be available"
fi

# Step 1: Pull latest code from git
print_info "Step 1: Pulling latest code from git..."
cd "$PROJECT_DIR"

if [ -d ".git" ]; then
    git fetch origin
    git reset --hard origin/main || git reset --hard origin/master
    print_success "Code updated from git"
else
    print_warning "Not a git repository, skipping git pull"
fi

# Step 2: Install backend dependencies
if [ -d "$BACKEND_DIR" ]; then
    print_info "Step 2: Installing backend dependencies..."
    cd "$BACKEND_DIR"
    
    if [ ! -d "venv" ]; then
        print_info "Creating backend venv..."
        /usr/bin/python3 -m venv venv
    fi
    PIP_CMD="./venv/bin/pip"
    
    if [ -f "requirements.txt" ]; then
        $PIP_CMD install --upgrade pip --quiet
        $PIP_CMD install -r requirements.txt --quiet
        print_success "Backend dependencies installed"
    else
        print_warning "requirements.txt not found in backend directory"
    fi
else
    print_warning "Backend directory not found: $BACKEND_DIR"
fi

# Step 3: Install bot dependencies
if [ -d "$BOT_DIR" ]; then
    print_info "Step 3: Installing bot dependencies..."
    cd "$BOT_DIR"
    
    BOT_PIP="/usr/bin/python3 -m pip"
    [ -f "venv/bin/pip" ] && BOT_PIP="./venv/bin/pip"
    
    if [ -f "requirements.txt" ]; then
        $BOT_PIP install -r requirements.txt --quiet
        print_success "Bot dependencies installed"
    else
        print_warning "requirements.txt not found in bot directory"
    fi
else
    print_warning "Bot directory not found: $BOT_DIR"
fi

# Step 4: Install frontend dependencies and build (root project)
print_info "Step 4: Installing frontend dependencies and building..."
cd "$PROJECT_DIR"
if [ -f "package.json" ] && [ -d "src" ]; then
    npm install --silent
    npm run build
    if [ -d "dist" ]; then
        print_success "Frontend built successfully (dist directory exists)"
    else
        print_error "Frontend build failed - dist directory not found"
        exit 1
    fi
else
    # Fallback: miniapp if exists
    if [ -d "$MINIAPP_DIR" ] && [ -f "$MINIAPP_DIR/package.json" ]; then
        cd "$MINIAPP_DIR"
        npm install --silent
        npm run build --silent
        [ -d "dist" ] && print_success "MiniApp built" || (print_error "MiniApp build failed"; exit 1)
    else
        print_warning "No frontend package.json found"
    fi
fi

# Step 5: Run database migrations
if [ -d "$BACKEND_DIR" ]; then
    print_info "Step 5: Running database migrations..."
    cd "$BACKEND_DIR"
    
    PYTHON_CMD="/usr/bin/python3"
    [ -f "venv/bin/python" ] && PYTHON_CMD="./venv/bin/python"
    
    if [ -f "alembic.ini" ]; then
        $PYTHON_CMD -m alembic upgrade head
        
        # Print current migration revision
        CURRENT_REVISION=$($PYTHON_CMD -m alembic current 2>/dev/null | awk '{print $1}' || echo "unknown")
        print_success "Database migrations completed"
        print_info "Current migration revision: $CURRENT_REVISION"
    else
        print_warning "alembic.ini not found, skipping migrations"
    fi
    
    # Step 5.5: Ensure admin user exists (standalone script, no app imports)
    print_info "Step 5.5: Ensuring admin user exists..."
    if [ -f "scripts/ensure_admin_standalone.py" ]; then
        $PYTHON_CMD scripts/ensure_admin_standalone.py && print_success "Admin user verified/created" || print_warning "ensure_admin failed (admin may already exist)"
    elif [ -f "scripts/ensure_admin.py" ]; then
        $PYTHON_CMD scripts/ensure_admin.py && print_success "Admin user verified/created" || print_warning "ensure_admin failed"
    else
        print_warning "ensure_admin script not found"
    fi
else
    print_warning "Backend directory not found, skipping migrations"
fi

# Step 6: Restart services
print_info "Step 6: Restarting services..."

# Restart backend
if systemctl is-active --quiet bella-backend.service; then
    systemctl restart bella-backend.service
    print_success "Backend service restarted"
else
    print_warning "Backend service not active, starting..."
    systemctl start bella-backend.service || print_error "Failed to start backend service"
fi

# Ensure bot service is installed, then restart
if [ ! -f /etc/systemd/system/bella-bot.service ] && [ -f "$PROJECT_DIR/deployment/bella-bot.service" ]; then
    cp "$PROJECT_DIR/deployment/bella-bot.service" /etc/systemd/system/
    systemctl daemon-reload
    print_info "bella-bot.service installed"
fi
if [ -d "$PROJECT_DIR/bot" ] && [ ! -d "$PROJECT_DIR/bot/venv" ]; then
    print_info "Creating bot venv..."
    /usr/bin/python3 -m venv "$PROJECT_DIR/bot/venv"
    "$PROJECT_DIR/bot/venv/bin/pip" install -r "$PROJECT_DIR/bot/requirements.txt" -q 2>/dev/null || true
fi
if systemctl is-active --quiet bella-bot.service 2>/dev/null; then
    systemctl restart bella-bot.service
    print_success "Bot service restarted"
else
    systemctl start bella-bot.service 2>/dev/null && print_success "Bot service started" || print_warning "Bot service not active (ensure bella-bot.service is installed)"
fi

# Restart scheduler
if systemctl is-active --quiet bella-scheduler.service; then
    systemctl restart bella-scheduler.service
    print_success "Scheduler service restarted"
else
    print_warning "Scheduler service not active, starting..."
    systemctl start bella-scheduler.service || print_warning "Failed to start scheduler service (may not be configured)"
fi

# Step 7: Wait for services to start
print_info "Step 7: Waiting for services to start..."
sleep 5

# Step 8: Check service status
print_info "Step 8: Checking service status..."

# Check backend service
if systemctl is-active --quiet bella-backend.service; then
    print_success "Backend service is active"
else
    print_error "Backend service is not active - deployment failed"
    exit 1
fi

# Check bot service (optional, but log if inactive)
if systemctl is-active --quiet bella-bot.service; then
    print_success "Bot service is active"
else
    print_warning "Bot service is not active (optional service)"
fi

# Check scheduler service (optional, but log if inactive)
if systemctl is-active --quiet bella-scheduler.service; then
    print_success "Scheduler service is active"
else
    print_warning "Scheduler service is not active (optional service)"
fi

# Step 8.5: Verify backend port is listening (retry, backend may need time to bind)
print_info "Step 8.5: Verifying backend port 8000 is listening..."
PORT_OK=0
for _ in 1 2 3 4 5; do
  sleep 2
  if ss -lnt 2>/dev/null | grep -q ":8000"; then
    print_success "Backend is listening on port 8000"
    PORT_OK=1
    break
  fi
done
if [ "$PORT_OK" -ne 1 ]; then
    print_error "Backend is not listening on port 8000 - deployment failed"
    print_error "Rolling back deployment..."
    cd "$PROJECT_DIR"
    if [ -n "$PREVIOUS_COMMIT" ] && [ -d ".git" ]; then
        git reset --hard "$PREVIOUS_COMMIT"
        print_info "Rolled back to commit: $PREVIOUS_COMMIT"
    else
        print_warning "Cannot rollback - no previous commit stored or not a git repository"
    fi
    systemctl restart bella-backend.service
    systemctl restart bella-bot.service || true
    systemctl restart bella-scheduler.service || true
    exit 1
fi

# Step 9: Check API health endpoint
print_info "Step 9: Checking API health endpoint..."

# Wait a bit more for API to be ready
sleep 2

# Check health endpoint with timeout
HEALTH_RESPONSE=$(curl --max-time 5 -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null || echo "000")
HEALTH_BODY=$(curl --max-time 5 -s http://localhost:8000/health 2>/dev/null || echo "")

if [ "$HEALTH_RESPONSE" = "200" ]; then
    # Check if response body contains "ok"
    if echo "$HEALTH_BODY" | grep -q '"status".*"ok"'; then
        print_success "API health check passed"
    else
        print_error "API health check failed - invalid response body: $HEALTH_BODY"
        print_error "Rolling back deployment..."
        cd "$PROJECT_DIR"
        if [ -n "$PREVIOUS_COMMIT" ] && [ -d ".git" ]; then
            git reset --hard "$PREVIOUS_COMMIT"
            print_info "Rolled back to commit: $PREVIOUS_COMMIT"
        else
            print_warning "Cannot rollback - no previous commit stored or not a git repository"
        fi
        systemctl restart bella-backend.service
        systemctl restart bella-bot.service || true
        systemctl restart bella-scheduler.service || true
        exit 1
    fi
else
    if [ "$HEALTH_RESPONSE" = "000" ]; then
        print_error "API health check failed - request timed out or connection failed"
    else
        print_error "API health check failed - HTTP status: $HEALTH_RESPONSE"
    fi
    print_error "Rolling back deployment..."
    cd "$PROJECT_DIR"
    if [ -n "$PREVIOUS_COMMIT" ] && [ -d ".git" ]; then
        git reset --hard "$PREVIOUS_COMMIT"
        print_info "Rolled back to commit: $PREVIOUS_COMMIT"
    else
        print_warning "Cannot rollback - no previous commit stored or not a git repository"
    fi
    systemctl restart bella-backend.service
    systemctl restart bella-bot.service || true
    systemctl restart bella-scheduler.service || true
    exit 1
fi

# Step 9.5: Check frontend availability
print_info "Step 9.5: Checking frontend availability..."
FRONTEND_RESPONSE=$(curl --max-time 5 -s -o /dev/null -w "%{http_code}" https://app.bellahasias.ru 2>/dev/null || echo "000")

if [ "$FRONTEND_RESPONSE" = "200" ] || [ "$FRONTEND_RESPONSE" = "301" ] || [ "$FRONTEND_RESPONSE" = "302" ]; then
    print_success "Frontend is reachable (HTTP status: $FRONTEND_RESPONSE)"
else
    if [ "$FRONTEND_RESPONSE" = "000" ]; then
        print_error "Frontend availability check failed - request timed out or connection failed"
    else
        print_error "Frontend availability check failed - HTTP status: $FRONTEND_RESPONSE"
    fi
    print_error "Rolling back deployment..."
    cd "$PROJECT_DIR"
    if [ -n "$PREVIOUS_COMMIT" ] && [ -d ".git" ]; then
        git reset --hard "$PREVIOUS_COMMIT"
        print_info "Rolled back to commit: $PREVIOUS_COMMIT"
    else
        print_warning "Cannot rollback - no previous commit stored or not a git repository"
    fi
    systemctl restart bella-backend.service
    systemctl restart bella-bot.service || true
    systemctl restart bella-scheduler.service || true
    exit 1
fi

# Step 10: Deployment success
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   DEPLOY SUCCESS${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
print_success "All services are running and healthy"
echo ""
print_info "Services status:"
systemctl is-active bella-backend.service && echo -e "${GREEN}✓${NC} Backend: Active" || echo -e "${RED}✗${NC} Backend: Inactive"
systemctl is-active bella-bot.service && echo -e "${GREEN}✓${NC} Bot: Active" || echo -e "${YELLOW}○${NC} Bot: Inactive (optional)"
systemctl is-active bella-scheduler.service && echo -e "${GREEN}✓${NC} Scheduler: Active" || echo -e "${YELLOW}○${NC} Scheduler: Inactive (optional)"
echo ""
print_success "Application is available at: https://app.bellahasias.ru"

# Remove lock file (cleanup function will also handle this, but explicit is better)
if [ -f "$LOCK_FILE" ]; then
    rm -f "$LOCK_FILE"
    print_info "Deployment lock released"
fi
