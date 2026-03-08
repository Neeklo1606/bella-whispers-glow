#!/bin/bash
RESP=$(curl -s -X POST http://localhost:8000/api/auth/admin/login -H "Content-Type: application/json" -d @/tmp/login.json)
TOKEN=$(echo "$RESP" | python3 -c 'import sys,json; print(json.load(sys.stdin).get("access_token",""))')
# Need a valid plan_id - get first plan or use placeholder
curl -s -X POST http://localhost:8000/api/payments/create \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"plan_id":"00000000-0000-0000-0000-000000000001","amount":100}'
