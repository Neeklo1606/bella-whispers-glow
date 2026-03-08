# 📋 Pre-deployment checklist

## 1️⃣ Migrations

```bash
cd backend
alembic upgrade head
```

Убедитесь, что миграции применены без ошибок.

---

## 2️⃣ system_settings

```sql
SELECT * FROM system_settings;
```

Проверьте, что таблица существует и содержит нужные ключи (например `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHANNEL_ID`).

---

## 3️⃣ Health

```bash
curl http://localhost:8000/health
```

Ожидается:

```json
{ "status": "ok" }
```

---

## 4️⃣ Admin settings

1. Откройте `/admin/login` и войдите
2. Перейдите на `/admin/settings`
3. Убедитесь, что разделы Telegram, Платежи, Безопасность загружаются
4. Проверьте сохранение настроек (например, тестовый режим YooKassa)

---

## 5️⃣ Telegram bot

Проверка через API (нужен токен бота и ID канала):

```bash
# getMe — информация о боте
curl "https://api.telegram.org/bot<TOKEN>/getMe"

# getChat — информация о канале
curl "https://api.telegram.org/bot<TOKEN>/getChat?chat_id=<CHANNEL_ID>"
```

Или через Python (при запущенном backend):

```python
# В Python с доступом к БД:
from src.core.db.database import AsyncSessionLocal
from src.modules.telegram.bot_service import TelegramBotService

async with AsyncSessionLocal() as db:
    svc = await TelegramBotService.create(db)
    me = await svc.bot.get_me()
    print(me.username)
    chat = await svc.bot.get_chat(svc.channel_id)
    print(chat.title)
```

---

## 6️⃣ Payment webhook

```bash
curl -X POST http://localhost:8000/api/payments/webhook \
  -H "Content-Type: application/json" \
  -d '{"event":"payment.succeeded","object":{"id":"test","status":"succeeded"}}'
```

Endpoint должен отвечать (200, 400 или 500 — в зависимости от валидации). Важно, что маршрут существует и обрабатывает запросы.

---

## Автоматический скрипт

```bash
cd backend
python scripts/pre_deploy_checklist.py
```

Скрипт проверяет пункты 1–6. Для пунктов 3 и 6 backend должен быть запущен (`uvicorn src.main:app`).
