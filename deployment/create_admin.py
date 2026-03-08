"""Create admin user - outputs SQL. Uses bcrypt directly (passlib compat)."""
import bcrypt
import uuid
from datetime import datetime

# bcrypt hash compatible with passlib verify
pw_hash = bcrypt.hashpw(b'Admin123!', bcrypt.gensalt()).decode()
user_id = str(uuid.uuid4())
now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
# Escape single quotes in hash
pw_esc = pw_hash.replace("'", "''")
print(f"INSERT INTO users (id, email, password_hash, role, created_at, updated_at) VALUES ('{user_id}', 'admin@bella.local', '{pw_esc}', 'super_admin', '{now}', '{now}');")
