#!/bin/bash
# Bootstrap production: admin, system_settings, default plan
set -e
cd /var/www/bella
BACKEND=/var/www/bella/backend

# Generate password hash (use bcrypt directly to avoid passlib version issues)
PW_HASH=$($BACKEND/venv/bin/python -c 'import bcrypt; print(bcrypt.hashpw(b"Admin123!", bcrypt.gensalt()).decode())')
PW_ESC=$(echo "$PW_HASH" | sed "s/'/''/g")

TMPF=$(mktemp)
cat > "$TMPF" << EOSQL
-- Admin
INSERT INTO users (id, email, password_hash, role, created_at, updated_at)
VALUES (gen_random_uuid(), 'admin@bellahasias.ru', '$PW_ESC', 'admin', now(), now())
ON CONFLICT (email) DO UPDATE SET password_hash = EXCLUDED.password_hash, role = EXCLUDED.role;

-- System settings (value is JSON type - use empty string as JSON)
INSERT INTO system_settings (id, key, value, description, created_at, updated_at)
SELECT gen_random_uuid(), 'TELEGRAM_BOT_TOKEN', '""'::json, 'Telegram Bot API token', now(), now()
WHERE NOT EXISTS (SELECT 1 FROM system_settings WHERE key = 'TELEGRAM_BOT_TOKEN');
INSERT INTO system_settings (id, key, value, description, created_at, updated_at)
SELECT gen_random_uuid(), 'TELEGRAM_CHANNEL_ID', '""'::json, 'Telegram channel ID', now(), now()
WHERE NOT EXISTS (SELECT 1 FROM system_settings WHERE key = 'TELEGRAM_CHANNEL_ID');
INSERT INTO system_settings (id, key, value, description, created_at, updated_at)
SELECT gen_random_uuid(), 'YOOKASSA_SHOP_ID', '""'::json, 'YooKassa shop ID', now(), now()
WHERE NOT EXISTS (SELECT 1 FROM system_settings WHERE key = 'YOOKASSA_SHOP_ID');
INSERT INTO system_settings (id, key, value, description, created_at, updated_at)
SELECT gen_random_uuid(), 'YOOKASSA_SECRET_KEY', '""'::json, 'YooKassa secret key', now(), now()
WHERE NOT EXISTS (SELECT 1 FROM system_settings WHERE key = 'YOOKASSA_SECRET_KEY');
INSERT INTO system_settings (id, key, value, description, created_at, updated_at)
SELECT gen_random_uuid(), 'MINIAPP_URL', '""'::json, 'Mini App URL', now(), now()
WHERE NOT EXISTS (SELECT 1 FROM system_settings WHERE key = 'MINIAPP_URL');
INSERT INTO system_settings (id, key, value, description, created_at, updated_at)
SELECT gen_random_uuid(), 'OFFER_URL', '""'::json, 'Offer/privacy URL', now(), now()
WHERE NOT EXISTS (SELECT 1 FROM system_settings WHERE key = 'OFFER_URL');
INSERT INTO system_settings (id, key, value, description, created_at, updated_at)
SELECT gen_random_uuid(), 'SUPPORT_USERNAME', '""'::json, 'Support Telegram username', now(), now()
WHERE NOT EXISTS (SELECT 1 FROM system_settings WHERE key = 'SUPPORT_USERNAME');

-- Default plan
INSERT INTO subscription_plans (id, name, description, price, first_month_price, duration_days, currency, features, is_active, created_at, updated_at)
VALUES (
  gen_random_uuid(),
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
);
EOSQL

chmod 644 "$TMPF"
sudo -u postgres psql -d bella -f "$TMPF"
rm -f "$TMPF"
echo "Bootstrap complete"
