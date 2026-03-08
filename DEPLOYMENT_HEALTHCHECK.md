# Deployment Health Check System

## ✅ Implemented Features

### 1. Health Check Endpoint ✅
**Location**: `backend/src/main.py`

**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "ok"
}
```

**Features**:
- No authentication required
- Simple and fast
- Returns 200 status code

### 2. Enhanced deploy.sh ✅
**Location**: `/var/www/bella/deploy.sh`

**New Steps**:
1. ✅ Wait 5 seconds after service restart
2. ✅ Check backend service status (`systemctl is-active`)
3. ✅ Check bot service status (optional)
4. ✅ Check scheduler service status (optional)
5. ✅ Wait 2 more seconds for API readiness
6. ✅ Check API health endpoint (`curl http://localhost:8000/health`)
7. ✅ Validate response body contains `"status": "ok"`
8. ✅ Auto-rollback on failure
9. ✅ Print "DEPLOY SUCCESS" on success

### 3. Auto-Rollback ✅
**Trigger**: If health check fails

**Actions**:
1. Rollback code: `git reset --hard HEAD~1`
2. Restart all services
3. Exit with error code

### 4. Success Message ✅
**Display**: "DEPLOY SUCCESS" in green

---

## 📋 Updated deploy.sh Script

### Health Check Flow

```bash
# Step 7: Wait for services
sleep 5

# Step 8: Check service status
systemctl is-active bella-backend.service

# Step 9: Check API health
curl http://localhost:8000/health

# If health check fails:
# - Rollback code
# - Restart services
# - Exit with error

# If success:
# - Print "DEPLOY SUCCESS"
```

### Rollback Logic

```bash
if [ "$HEALTH_RESPONSE" != "200" ]; then
    print_error "Rolling back deployment..."
    cd "$PROJECT_DIR"
    git reset --hard HEAD~1
    systemctl restart bella-backend.service
    systemctl restart bella-bot.service || true
    systemctl restart bella-scheduler.service || true
    exit 1
fi
```

---

## 🔍 Health Check Details

### API Endpoint
- **URL**: `http://localhost:8000/health`
- **Method**: GET
- **Auth**: None required
- **Expected Response**: `{"status": "ok"}`
- **Expected Status**: 200

### Validation
1. HTTP status code must be 200
2. Response body must contain `"status": "ok"`

### Failure Handling
- If HTTP status ≠ 200 → Rollback
- If response body invalid → Rollback
- If service inactive → Rollback

---

## 📊 Deployment Flow

```
1. Pull code from git
2. Install dependencies
3. Run migrations
4. Restart services
5. Wait 5 seconds
6. Check service status
7. Wait 2 seconds
8. Check API health
9. Validate response
10. If OK → SUCCESS
11. If FAIL → Rollback + Exit
```

---

## ✅ Success Criteria

Deployment succeeds if:
- ✅ Backend service is active
- ✅ API health endpoint returns 200
- ✅ Response body contains `"status": "ok"`

Deployment fails if:
- ❌ Backend service is inactive
- ❌ API health endpoint returns non-200
- ❌ Response body is invalid

---

## 🚨 Rollback Behavior

When health check fails:
1. **Rollback code**: `git reset --hard HEAD~1`
2. **Restart services**: All services restarted
3. **Exit**: Script exits with code 1
4. **Log**: Error message printed

---

## 📝 Example Output

### Successful Deployment
```
[INFO] Step 9: Checking API health endpoint...
[INFO] API health check passed

========================================
   DEPLOY SUCCESS
========================================

[INFO] All services are running and healthy
[INFO] Services status:
✓ Backend: Active
✓ Bot: Active
✓ Scheduler: Active
[INFO] Application is available at: https://app.bellahasias.ru
```

### Failed Deployment (with rollback)
```
[INFO] Step 9: Checking API health endpoint...
[ERROR] API health check failed - HTTP status: 500
[ERROR] Rolling back deployment...
[INFO] Backend service restarted
```

---

## 🔧 Testing Health Endpoint

### Manual Test
```bash
# On server
curl http://localhost:8000/health

# Expected output:
{"status":"ok"}
```

### From Local Machine
```bash
curl https://app.bellahasias.ru/api/health
```

---

## ✅ Status

- ✅ Health check endpoint added
- ✅ deploy.sh updated with checks
- ✅ API health validation implemented
- ✅ Auto-rollback on failure
- ✅ Success message displayed
- ✅ Script uploaded to server

**Ready for reliable deployments!**
