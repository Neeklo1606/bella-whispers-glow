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
SELECT gen_random_uuid(), 'MINIAPP_URL', '"https://app.bellahasias.ru"'::json, 'Mini App URL', now(), now()
WHERE NOT EXISTS (SELECT 1 FROM system_settings WHERE key = 'MINIAPP_URL');

INSERT INTO system_settings (id, key, value, description, created_at, updated_at)
SELECT gen_random_uuid(), 'OFFER_URL', '"https://app.bellahasias.ru/privacy"'::json, 'Offer/privacy URL', now(), now()
WHERE NOT EXISTS (SELECT 1 FROM system_settings WHERE key = 'OFFER_URL');

INSERT INTO system_settings (id, key, value, description, created_at, updated_at)
SELECT gen_random_uuid(), 'SUPPORT_USERNAME', '"Bella_hasias"'::json, 'Support Telegram username', now(), now()
WHERE NOT EXISTS (SELECT 1 FROM system_settings WHERE key = 'SUPPORT_USERNAME');
