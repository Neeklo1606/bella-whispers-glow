# Bella — Полный аудит проекта

**Документ для AI и разработчиков.** Содержит структуру, возможности, deployment и информацию для дальнейшей работы.

---

## 1. О проекте

**Название:** Bella Subscription Platform / Bella Whispers Glow  

**Назначение:** SaaS-платформа Telegram Paywall — пользователь открывает MiniApp, выбирает тариф, оплачивает (YooKassa), бот выдаёт invite-link в закрытый Telegram-канал. При окончании подписки бот удаляет пользователя из чата.

**Публичный URL:** https://app.bellahasias.ru  
**API URL:** https://app.bellahasias.ru/api  
**Admin Panel:** https://app.bellahasias.ru/admin  

**Репозиторий:** https://github.com/Neeklo1606/bella-whispers-glow (ветка `main`)

---

## 2. Архитектура

```
┌─────────────────┐     MiniApp      ┌──────────────────┐
│ Telegram User   │ ───────────────► │ Frontend (React) │
└─────────────────┘                  │ Vite, port 8080  │
                                     └────────┬─────────┘
                                              │ REST API
                                     ┌────────▼─────────┐
                                     │ Backend (FastAPI)│
                                     │ port 8000        │
                                     └────────┬─────────┘
                        ┌─────────────────────┼─────────────────────┐
                        │                     │                     │
                        ▼                     ▼                     ▼
                 ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
                 │ PostgreSQL  │      │   Redis     │      │ Scheduler   │
                 └─────────────┘      └─────────────┘      └─────────────┘
                        ▲
                        │
                 ┌──────┴──────┐
                 │ Telegram Bot│  (aiogram, polling)
                 │ bot/        │
                 └─────────────┘
```

---

## 3. Структура проекта

```
bella/
├── backend/                    # FastAPI backend
│   ├── alembic/                # Миграции БД
│   │   └── versions/
│   │       001_initial_migration_create_all_tables.py
│   │       002_add_user_password_and_role.py
│   │       003_add_subscription_telegram_fields.py
│   │       004_extend_platform_security_payments.py
│   │       005_create_system_settings.py
│   ├── src/
│   │   ├── core/               # Конфиг, БД, security, redis
│   │   │   ├── config/
│   │   │   ├── db/
│   │   │   ├── security/
│   │   │   └── utils/
│   │   ├── modules/
│   │   │   ├── admin/          # Админ API
│   │   │   ├── auth/           # Auth (telegram, login, admin)
│   │   │   ├── broadcasts/
│   │   │   ├── channel_logs/
│   │   │   ├── payments/
│   │   │   ├── schedule/
│   │   │   ├── subscriptions/
│   │   │   ├── system_settings/
│   │   │   ├── telegram/       # Invite link, channel access
│   │   │   └── users/
│   │   └── workers/            # Scheduler, tasks
│   ├── requirements.txt
│   ├── alembic.ini
│   └── .env                    # Локально / на сервере
│
├── bot/                        # Telegram Bot (aiogram)
│   ├── src/
│   │   ├── handlers/           # start, menu, payment, subscription, channel
│   │   ├── keyboards/
│   │   ├── middlewares/
│   │   ├── services/           # api_client
│   │   └── utils/
│   └── requirements.txt
│
├── src/                        # Frontend (React + Vite)
│   ├── components/
│   │   ├── layout/             # AdminLayout, BottomNav
│   │   └── ui/                 # shadcn/ui
│   ├── pages/
│   │   ├── Index.tsx
│   │   ├── Pricing.tsx
│   │   ├── Login.tsx
│   │   ├── Profile.tsx
│   │   ├── SubscriptionManagement.tsx
│   │   ├── AdminLogin.tsx
│   │   ├── AdminDashboard.tsx
│   │   ├── AdminUsers.tsx
│   │   ├── AdminSubscriptions.tsx
│   │   ├── AdminSettings.tsx
│   │   └── ...
│   ├── hooks/
│   ├── lib/
│   │   ├── api.ts              # Все API вызовы
│   │   └── utils.ts
│   └── App.tsx
│
├── deployment/                 # Скрипты и конфиги деплоя
│   ├── nginx-bella.conf
│   ├── bella-backend.service
│   ├── bella-bot.service
│   ├── bella-scheduler.service
│   ├── init_system_settings.sql
│   ├── create_admin.py
│   ├── login.json
│   └── ...
│
├── package.json
├── vite.config.ts
├── .env.production             # VITE_API_URL=https://app.bellahasias.ru
└── tailwind.config.js
```

---

## 4. Сервер и SSH

### 4.1 Подключение

```
ssh root@155.212.210.214
```

### 4.2 Пути на сервере

| Что | Путь |
|-----|------|
| Проект | `/var/www/bella` |
| Backend | `/var/www/bella/backend` |
| Bot | `/var/www/bella/bot` |
| Frontend build | `/var/www/bella/dist` |
| Backend venv | `/var/www/bella/backend/venv` |
| Bot venv | `/var/www/bella/bot/venv` |
| Backend .env | `/var/www/bella/backend/.env` |
| Nginx config | `/etc/nginx/sites-available/bella` |

### 4.3 systemd-сервисы

| Сервис | Описание |
|--------|----------|
| `bella-backend` | FastAPI на порту 8000 |
| `bella-bot` | Telegram Bot (aiogram) |
| `bella-scheduler` | APScheduler (подписки, платежи, рассылки) |

```bash
systemctl status bella-backend bella-bot bella-scheduler
systemctl restart bella-backend bella-bot bella-scheduler
```

### 4.4 Полезные команды

```bash
# Логи
journalctl -u bella-backend -f
journalctl -u bella-bot -f

# Health
curl http://localhost:8000/health

# Миграции
cd /var/www/bella/backend && source venv/bin/activate && alembic upgrade head
```

---

## 5. Frontend

### 5.1 Стек

- **React 18** + TypeScript
- **Vite 5**
- **React Router 6**
- **Tailwind CSS** + **shadcn/ui**
- **TanStack Query**
- **Framer Motion**

### 5.2 Роуты

| Путь | Описание |
|------|----------|
| `/` | Главная |
| `/pricing` | Тарифы |
| `/login` | Вход (Telegram) |
| `/consent` | Согласие |
| `/dashboard/profile` | Профиль пользователя |
| `/dashboard/subscription` | Управление подпиской |
| `/admin/login` | Вход админа |
| `/admin` | Админ-панель (защищено) |
| `/admin/users` | Пользователи |
| `/admin/subscriptions` | Подписки |
| `/admin/settings` | Настройки |

### 5.3 API Base URL

```ts
// src/lib/api.ts
const API_BASE_URL =
  import.meta.env.VITE_API_URL ||
  (typeof window !== "undefined" ? window.location.origin : "http://localhost:8000");
```

**Production:** `.env.production` → `VITE_API_URL=https://app.bellahasias.ru`

### 5.4 Admin API (src/lib/api.ts)

- `adminLogin()` — POST /api/auth/admin/login
- `validateAdminToken()` — GET /api/admin/dashboard
- `getAdminDashboard()` — users_count, active_subscriptions, revenue_today, revenue_total, churn_rate
- `getAdminUsers()`, `getAdminSubscriptions()`
- `banUser()`, `extendSubscription()`, `revokeSubscription()`
- `getUserSubscriptions()`
- `getAdminSettings()`, `updateAdminSetting()`
- `testTelegram()`, `testPayment()`

### 5.5 Auth

- **Admin:** JWT в localStorage (`admin_token`)
- **User:** JWT в localStorage (`user_token`), Telegram initData
- `AdminGuard` — проверяет токен, редирект на /admin/login

---

## 6. Backend

### 6.1 Стек

- **FastAPI**
- **SQLAlchemy 2** (async)
- **PostgreSQL** (asyncpg)
- **Redis** (кеш, jobs)
- **Alembic** (миграции)
- **JWT** (python-jose)
- **YooKassa** (платежи)

### 6.2 Переменные окружения (backend/.env)

```
DATABASE_URL=postgresql+asyncpg://...
SECRET_KEY=...
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHANNEL_ID=
YOOKASSA_SHOP_ID=
YOOKASSA_SECRET_KEY=
REDIS_URL=redis://localhost:6379/0
```

Токены и ключи могут храниться в `system_settings` (БД), .env используется для bootstrap.

### 6.3 Таблицы БД

| Таблица | Назначение |
|---------|------------|
| users | Пользователи (telegram_id, email, role, password_hash) |
| subscription_plans | Тарифы |
| subscriptions | Подписки пользователей |
| payments | Платежи |
| broadcasts | Рассылки |
| channel_access_logs | Логи доступа к каналу |
| system_settings | Key-value настройки |
| alembic_version | Версия миграций |

### 6.4 API Endpoints

**Auth**
- `POST /api/auth/telegram` — авторизация через Telegram
- `POST /api/auth/login` — логин email/password
- `POST /api/auth/refresh` — refresh token
- `POST /api/auth/admin/login` — логин админа

**Admin** (требуют JWT admin)
- `GET /api/admin/dashboard` — метрики
- `GET /api/admin/users`
- `GET /api/admin/users/{id}/subscriptions`
- `POST /api/admin/users/{id}/ban`
- `GET /api/admin/subscriptions`
- `POST /api/admin/subscriptions/{id}/extend`
- `POST /api/admin/subscriptions/{id}/revoke`
- `GET /api/admin/payments`
- `GET /api/admin/settings`
- `PUT /api/admin/settings/{key}`
- `POST /api/admin/test/telegram`
- `POST /api/admin/test/payment`

**Остальное**
- `GET /api/users/me`, `PATCH /api/users/me`
- `GET /api/subscriptions/plans`, `GET /api/subscriptions/me`, `POST /api/subscriptions/create`
- `POST /api/payments/create`, `POST /api/payments/webhook`
- `GET /api/telegram/invite-link`, `POST /api/telegram/revoke-invite-link`, `POST /api/telegram/channel-access`
- `GET /api/settings`, `GET /api/settings/{key}`, `PATCH /api/settings/{key}`
- `GET /api/broadcasts`, `POST /api/broadcasts`
- `GET /api/schedule/upcoming`, `GET /api/schedule/past`

### 6.5 Scheduler

Отдельный systemd-сервис `bella-scheduler` запускает `backend/scripts/run_scheduler.py` (APScheduler). Задачи:
- Истечение подписок (каждые 10 мин)
- Auto-renewal
- Напоминания о продлении
- Проверка pending-платежей
- Отправка отложенных рассылок

*Примечание: в `main.py` lifespan тоже стартует scheduler — в production обычно используется отдельный `bella-scheduler`, а не встроенный в backend.*

---

## 7. Telegram Bot

### 7.1 Стек

- **aiogram 3**
- Конфиг из `.env` (BOT_TOKEN, API_BASE_URL, CHANNEL_ID)

### 7.2 Handlers

- `start` — /start
- `menu` — главное меню
- `payment` — оплата
- `subscription` — статус подписки
- `channel` — доступ к каналу

### 7.3 Поведение

- Без BOT_TOKEN — бот не падает, ждёт настройки
- Получает тарифы с backend
- При успешной оплате — invite link
- Scheduler вызывает `kickChatMember` для просроченных подписок

---

## 8. Nginx

**Файл:** `/etc/nginx/sites-available/bella`  
**Домен:** app.bellahasias.ru

- `/api/` → `http://127.0.0.1:8000` (backend)
- `/` → `http://127.0.0.1:8080` (frontend)
- SSL через Let's Encrypt

---

## 9. Deployment Pipeline

**Локально (Windows):**
```powershell
.\deploy.ps1                    # Коммит + push + SSH deploy
.\deploy.ps1 -SkipCommit        # Только deploy без коммита
```

**На сервере:**
```bash
# deploy.ps1 вызывает: ssh root@155.212.210.214 "bash /var/www/bella/deploy.sh"
bash /var/www/bella/deploy.sh   # или bash /var/www/bella/deployment/deploy.sh
# Или вручную:
cd /var/www/bella && git pull origin main
cd backend && source venv/bin/activate && pip install -r requirements.txt && alembic upgrade head
cd .. && npm install && npm run build
systemctl restart bella-backend bella-bot bella-scheduler
# Запуск serve для frontend (если не настроен отдельный сервис):
# npx serve dist -l 8080 &
```

*Примечание: `deploy.sh` ожидает `miniapp/` — в проекте её нет, фронт в корне. Сборка frontend выполняется из корня: `npm run build`.*

---

## 10. Админ-учётная запись

- **Email:** admin@bella.local
- **Пароль:** Admin123!
- Создаётся скриптом `deployment/create_admin.py` + SQL

---

## 11. system_settings (ключи)

| Ключ | Описание |
|------|----------|
| TELEGRAM_BOT_TOKEN | Токен бота |
| TELEGRAM_CHANNEL_ID | ID канала |
| BOT_API_SECRET | Секрет для webhook/API бота |
| YOOKASSA_SHOP_ID | Shop ID YooKassa |
| YOOKASSA_SECRET_KEY | Секрет YooKassa |

Редактируются через Admin Settings.

---

## 12. Тестирование

- Frontend: `npm run test` (Vitest)
- Backend: `pytest` (в backend/)

---

## 13. Известные особенности

- SQLAlchemy Enum: в БД значения lowercase (`active`, `pending`), в коде используются `values_callable`.
- `metadata` в Payment переименовано в `provider_metadata` (резервированное слово SQLAlchemy).
- bcrypt 4.3.0 (для совместимости с passlib).
- Бот использует polling, не webhook.
- Frontend: `npm run build` (корень проекта) → `dist/`. Nginx проксирует `/` на `127.0.0.1:8080` — на сервере должен работать процесс (например `npx serve dist -p 8080` или `vite preview`), иначе статика не отдаётся.

---

## 14. Что можно развить

- [ ] CRUD тарифов в админке
- [ ] Модуль content_blocks (тексты MiniApp)
- [ ] support_messages
- [ ] Расширенные рассылки (target: all/paid/free/vip)
- [ ] Telegram Stars
- [ ] CI/CD (GitHub Actions)
- [ ] Полный набор тестов по TDD

---

## 15. Контакты и ресурсы

- **Репозиторий:** https://github.com/Neeklo1606/bella-whispers-glow
- **Сервер:** root@155.212.210.214
- **Production URL:** https://app.bellahasias.ru
