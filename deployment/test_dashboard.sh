#!/bin/bash
RESP=$(curl -s -X POST http://localhost:8000/api/auth/admin/login -H "Content-Type: application/json" -d @/tmp/login.json)
TOKEN=$(echo "$RESP" | python3 -c 'import sys,json; print(json.load(sys.stdin).get("access_token",""))')
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/admin/dashboard
