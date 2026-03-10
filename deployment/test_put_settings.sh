#!/bin/bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/admin/login -H 'Content-Type: application/json' -d @/tmp/admin_login.json | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
curl -s -w "\nHTTP_CODE:%{http_code}" -X PUT "http://localhost:8000/api/admin/settings/TELEGRAM_BOT_TOKEN" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"value":"123456:test-token"}'
