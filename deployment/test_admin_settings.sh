#!/bin/bash
RESP=$(curl -s -X POST http://localhost:8000/api/auth/admin/login \
  -H "Content-Type: application/json" \
  -d @/tmp/login.json)
TOKEN=$(echo "$RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('access_token',''))" 2>/dev/null)
if [ -z "$TOKEN" ]; then echo "Login response: $RESP"; exit 1; fi
echo "Settings:"
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/admin/settings
