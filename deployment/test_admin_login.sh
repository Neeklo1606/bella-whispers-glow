#!/bin/bash
# Test admin login and output response (LF line endings)
curl -s -X POST http://localhost:8000/api/auth/admin/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@bellahasias.ru","password":"Admin123!"}'
echo
