-- Bootstrap production: admin, settings, plan
-- Run: PGHASH="<output of gen_hash.py>" and substitute below, or run gen_hash on server first

-- STEP 1: Admin (password_hash placeholder - replace with output of: cd backend && ./venv/bin/python ../../deployment/gen_hash.py)
INSERT INTO users (id, email, password_hash, role, created_at, updated_at)
VALUES (gen_random_uuid(), 'admin@bellahasias.ru', '$2b$12$REPLACE_ME', 'admin', now(), now())
ON CONFLICT (email) DO UPDATE SET password_hash = EXCLUDED.password_hash, role = EXCLUDED.role;
