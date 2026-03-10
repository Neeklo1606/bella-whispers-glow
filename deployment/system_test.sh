#!/bin/bash
# Full system test for Bella platform
set +e
BASE="http://localhost:8000"
echo "=== STEP 1: Health ==="
curl -s $BASE/health
echo ""
echo "=== STEP 1: GET /api/settings (public) ==="
curl -s $BASE/api/settings
echo ""
echo "=== STEP 2: GET /api/subscriptions/plans ==="
curl -s $BASE/api/subscriptions/plans
echo ""
echo "=== Admin login ==="
ADMIN_JSON=$(curl -s -X POST $BASE/api/auth/admin/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@bella.local","password":"admin123"}')
echo "$ADMIN_JSON"
TOKEN=$(echo "$ADMIN_JSON" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
if [ -n "$TOKEN" ]; then
  echo ""
  echo "=== GET /api/admin/settings (with admin token) ==="
  curl -s -H "Authorization: Bearer $TOKEN" $BASE/api/admin/settings
  echo ""
  echo "=== GET /api/admin/plans ==="
  curl -s -H "Authorization: Bearer $TOKEN" $BASE/api/admin/plans
  echo ""
  echo "=== POST /api/admin/plans (create plan) ==="
  PLAN_JSON=$(curl -s -X POST $BASE/api/admin/plans \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"name":"1 месяц","price":990,"duration_days":30,"currency":"RUB"}')
  echo "$PLAN_JSON"
  PLAN_ID=$(echo "$PLAN_JSON" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
  echo "Plan ID: $PLAN_ID"
fi
echo ""
echo "=== GET /api/subscriptions/plans (after create) ==="
curl -s $BASE/api/subscriptions/plans
