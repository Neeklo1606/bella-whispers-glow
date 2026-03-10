#!/usr/bin/env python3
"""Bootstrap production: admin user, system_settings, default plan."""
import asyncio
import uuid
from passlib.context import CryptContext

# Use sync approach - run raw SQL via psql or use asyncpg/sqlalchemy
# For simplicity: output SQL that can be run via psql

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
pw_hash = pwd_ctx.hash("Admin123!")
# Escape single quotes for SQL
pw_esc = pw_hash.replace("'", "''")

admin_id = str(uuid.uuid4())
plan_id = str(uuid.uuid4())

sql = f"""
-- STEP 1: Admin user
INSERT INTO users (id, email, password_hash, role, created_at, updated_at)
VALUES ('{admin_id}', 'admin@bellahasias.ru', '{pw_esc}', 'admin', now(), now())
ON CONFLICT (email) DO UPDATE SET password_hash = EXCLUDED.password_hash, role = EXCLUDED.role;

-- STEP 2: System settings (value stored as text; init uses json cast)
INSERT INTO system_settings (id, key, value, description, created_at, updated_at)
SELECT gen_random_uuid(), k, COALESCE((SELECT value FROM system_settings WHERE key = k), '""'), d, now(), now()
FROM (VALUES 
  ('TELEGRAM_BOT_TOKEN', 'Telegram Bot API token'),
  ('TELEGRAM_CHANNEL_ID', 'Telegram channel ID'),
  ('YOOKASSA_SHOP_ID', 'YooKassa shop ID'),
  ('YOOKASSA_SECRET_KEY', 'YooKassa secret key'),
  ('MINIAPP_URL', 'Mini App URL'),
  ('OFFER_URL', 'Offer/privacy URL'),
  ('SUPPORT_USERNAME', 'Support Telegram username')
) AS v(k, d)
WHERE NOT EXISTS (SELECT 1 FROM system_settings WHERE key = v.k);

-- Handle value column: if it uses JSON type, use empty json. If TEXT, use empty string.
-- Check system_settings schema - value is Text. Use empty string.
UPDATE system_settings SET value = '""' WHERE value IS NULL OR value = '';
-- Insert missing keys (PostgreSQL)
INSERT INTO system_settings (id, key, value, description, created_at, updated_at)
SELECT gen_random_uuid(), 'TELEGRAM_BOT_TOKEN', '""', 'Telegram Bot API token', now(), now()
WHERE NOT EXISTS (SELECT 1 FROM system_settings WHERE key = 'TELEGRAM_BOT_TOKEN');
INSERT INTO system_settings (id, key, value, description, created_at, updated_at)
SELECT gen_random_uuid(), 'TELEGRAM_CHANNEL_ID', '""', 'Telegram channel ID', now(), now()
WHERE NOT EXISTS (SELECT 1 FROM system_settings WHERE key = 'TELEGRAM_CHANNEL_ID');
INSERT INTO system_settings (id, key, value, description, created_at, updated_at)
SELECT gen_random_uuid(), 'YOOKASSA_SHOP_ID', '""', 'YooKassa shop ID', now(), now()
WHERE NOT EXISTS (SELECT 1 FROM system_settings WHERE key = 'YOOKASSA_SHOP_ID');
INSERT INTO system_settings (id, key, value, description, created_at, updated_at)
SELECT gen_random_uuid(), 'YOOKASSA_SECRET_KEY', '""', 'YooKassa secret key', now(), now()
WHERE NOT EXISTS (SELECT 1 FROM system_settings WHERE key = 'YOOKASSA_SECRET_KEY');
INSERT INTO system_settings (id, key, value, description, created_at, updated_at)
SELECT gen_random_uuid(), 'MINIAPP_URL', '""', 'Mini App URL', now(), now()
WHERE NOT EXISTS (SELECT 1 FROM system_settings WHERE key = 'MINIAPP_URL');
INSERT INTO system_settings (id, key, value, description, created_at, updated_at)
SELECT gen_random_uuid(), 'OFFER_URL', '""', 'Offer/privacy URL', now(), now()
WHERE NOT EXISTS (SELECT 1 FROM system_settings WHERE key = 'OFFER_URL');
INSERT INTO system_settings (id, key, value, description, created_at, updated_at)
SELECT gen_random_uuid(), 'SUPPORT_USERNAME', '""', 'Support Telegram username', now(), now()
WHERE NOT EXISTS (SELECT 1 FROM system_settings WHERE key = 'SUPPORT_USERNAME');

-- STEP 3: Default plan
INSERT INTO subscription_plans (id, name, description, price, first_month_price, duration_days, currency, features, is_active, created_at, updated_at)
VALUES (
  '{plan_id}',
  '1 месяц',
  'Доступ в закрытый канал на 30 дней',
  990,
  990,
  30,
  'RUB',
  '["Доступ к закрытому Telegram каналу"]'::json,
  true,
  now(),
  now()
)
ON CONFLICT DO NOTHING;
"""

# Simplify - the INSERT for settings with complex logic may fail. Use simpler approach.
sql_simple = f"""
-- Admin user
INSERT INTO users (id, email, password_hash, role, created_at, updated_at)
VALUES ('{admin_id}', 'admin@bellahasias.ru', '{pw_esc}', 'admin', now(), now())
ON CONFLICT (email) DO UPDATE SET password_hash = EXCLUDED.password_hash, role = EXCLUDED.role;

-- System settings (insert if not exists)
INSERT INTO system_settings (id, key, value, description, created_at, updated_at)
SELECT gen_random_uuid(), 'TELEGRAM_BOT_TOKEN', '', 'Telegram Bot API token', now(), now()
WHERE NOT EXISTS (SELECT 1 FROM system_settings WHERE key = 'TELEGRAM_BOT_TOKEN');
INSERT INTO system_settings (id, key, value, description, created_at, updated_at)
SELECT gen_random_uuid(), 'TELEGRAM_CHANNEL_ID', '', 'Telegram channel ID', now(), now()
WHERE NOT EXISTS (SELECT 1 FROM system_settings WHERE key = 'TELEGRAM_CHANNEL_ID');
INSERT INTO system_settings (id, key, value, description, created_at, updated_at)
SELECT gen_random_uuid(), 'YOOKASSA_SHOP_ID', '', 'YooKassa shop ID', now(), now()
WHERE NOT EXISTS (SELECT 1 FROM system_settings WHERE key = 'YOOKASSA_SHOP_ID');
INSERT INTO system_settings (id, key, value, description, created_at, updated_at)
SELECT gen_random_uuid(), 'YOOKASSA_SECRET_KEY', '', 'YooKassa secret key', now(), now()
WHERE NOT EXISTS (SELECT 1 FROM system_settings WHERE key = 'YOOKASSA_SECRET_KEY');
INSERT INTO system_settings (id, key, value, description, created_at, updated_at)
SELECT gen_random_uuid(), 'MINIAPP_URL', '', 'Mini App URL', now(), now()
WHERE NOT EXISTS (SELECT 1 FROM system_settings WHERE key = 'MINIAPP_URL');
INSERT INTO system_settings (id, key, value, description, created_at, updated_at)
SELECT gen_random_uuid(), 'OFFER_URL', '', 'Offer/privacy URL', now(), now()
WHERE NOT EXISTS (SELECT 1 FROM system_settings WHERE key = 'OFFER_URL');
INSERT INTO system_settings (id, key, value, description, created_at, updated_at)
SELECT gen_random_uuid(), 'SUPPORT_USERNAME', '', 'Support Telegram username', now(), now()
WHERE NOT EXISTS (SELECT 1 FROM system_settings WHERE key = 'SUPPORT_USERNAME');

-- Default plan
INSERT INTO subscription_plans (id, name, description, price, first_month_price, duration_days, currency, features, is_active, created_at, updated_at)
VALUES (
  '{plan_id}',
  '1 месяц',
  'Доступ в закрытый канал на 30 дней',
  990,
  990,
  30,
  'RUB',
  '["Доступ к закрытому Telegram каналу"]'::jsonb,
  true,
  now(),
  now()
);
"""

print(sql_simple)
