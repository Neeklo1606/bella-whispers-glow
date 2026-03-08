# Системная архитектура Telegram Subscription Platform
## MVP Technical Analysis

---

## STEP 1 — АНАЛИЗ MINI APP

### Используемый фреймворк
- **React 18.3.1** с TypeScript
- **Vite 5.4.19** как сборщик
- **React Router DOM 6.30.1** для маршрутизации
- **TanStack React Query 5.83.0** для управления состоянием и кэширования API запросов
- **shadcn/ui** компоненты на базе Radix UI
- **Tailwind CSS** для стилизации
- **Framer Motion** для анимаций

### Структура папок
```
src/
├── pages/              # Страницы приложения
├── components/         # Переиспользуемые компоненты
│   ├── layout/        # Компоненты макета
│   └── ui/            # UI компоненты (shadcn)
├── hooks/             # Кастомные хуки
├── lib/               # Утилиты
└── assets/            # Статические ресурсы
```

### Основные страницы

#### Публичные страницы:
1. **Index** (`/`) — Лендинг с информацией о сервисе
   - Hero секция
   - Информация о подписке
   - Скриншоты чата
   - FAQ
   - CTA кнопки

2. **Pricing** (`/pricing`) — Страница тарифов
   - Информация о подписке (990₽ первый месяц, далее 1500₽/мес)
   - Список возможностей
   - Кнопка вступления

3. **Login** (`/login`) — Страница входа
   - Вход через Telegram
   - Альтернативный вход по email/password

4. **Consent** (`/consent`) — Согласие на обработку данных

#### Пользовательские страницы:
5. **Profile** (`/dashboard/profile`) — Профиль пользователя
   - Информация о пользователе
   - Статус подписки
   - История платежей
   - Управление подпиской

6. **SubscriptionManagement** (`/dashboard/subscription`) — Управление подпиской
   - Текущий план
   - История платежей
   - Изменение/отмена подписки

#### Админ панель:
7. **AdminDashboard** (`/admin`) — Дашборд администратора
   - KPI метрики (пользователи, подписки, MRR, Churn Rate)
   - График выручки
   - Последняя активность

8. **AdminUsers** (`/admin/users`) — Управление пользователями

### Управление состоянием
- **TanStack React Query** — для серверного состояния и кэширования
- **React Hooks** (useState, useEffect) — для локального состояния компонентов
- **React Router** — для навигации и URL состояния

### Интеграция с API
**Текущее состояние:** API интеграция отсутствует. Все данные статичны.

**Требуется реализовать:**
- HTTP клиент (axios/fetch)
- API endpoints для всех страниц
- Обработка ошибок
- Загрузочные состояния

### Использование Telegram WebApp
**Текущее состояние:** Telegram WebApp SDK не интегрирован.

**Требуется:**
- Инициализация `window.Telegram.WebApp`
- Получение данных пользователя из Telegram
- Авторизация через Telegram
- Открытие Mini App из бота

### Компоненты

#### Layout компоненты:
- `BottomNav` — нижняя навигация
- `AdminLayout` — макет админ панели
- `DashboardLayout` — макет дашборда
- `MobileNav` — мобильная навигация

#### UI компоненты:
- Полный набор shadcn/ui компонентов (49 файлов)
- Кастомные компоненты: `StatusIndicator`, `NavLink`

---

## STEP 2 — ТРЕБУЕМЫЕ BACKEND API ENDPOINTS

### Auth (Аутентификация)
```
POST   /api/auth/telegram          # Авторизация через Telegram
POST   /api/auth/login              # Вход по email/password
POST   /api/auth/logout             # Выход
GET    /api/auth/me                 # Получение текущего пользователя
POST   /api/auth/refresh            # Обновление токена
```

**Ответы:**
- `POST /api/auth/telegram`: `{ user, token, subscription }`
- `GET /api/auth/me`: `{ id, telegramId, username, email, subscription }`

### Users (Пользователи)
```
GET    /api/users/me                # Профиль текущего пользователя
PATCH  /api/users/me                # Обновление профиля
GET    /api/users/:id                # Профиль пользователя (admin)
```

**Ответы:**
- `GET /api/users/me`: `{ id, telegramId, username, firstName, lastName, email, avatar, createdAt }`

### Subscriptions (Подписки)
```
GET    /api/subscriptions/plans      # Список тарифных планов
GET    /api/subscriptions/me         # Текущая подписка пользователя
POST   /api/subscriptions/create     # Создание подписки
PATCH  /api/subscriptions/me         # Изменение подписки
DELETE /api/subscriptions/me         # Отмена подписки
GET    /api/subscriptions/history    # История подписок
```

**Ответы:**
- `GET /api/subscriptions/plans`: `[{ id, name, price, duration, features }]`
- `GET /api/subscriptions/me`: `{ id, planId, status, startDate, endDate, autoRenew, nextBillingDate }`

### Payments (Платежи)
```
POST   /api/payments/create         # Создание платежа
GET    /api/payments/:id            # Статус платежа
GET    /api/payments/history        # История платежей
POST   /api/payments/webhook        # Webhook от платежного провайдера
```

**Ответы:**
- `POST /api/payments/create`: `{ id, amount, currency, paymentUrl, status }`
- `GET /api/payments/history`: `[{ id, amount, status, createdAt, planName }]`

### Schedule (Расписание)
```
GET    /api/schedule/upcoming       # Предстоящие события
GET    /api/schedule/past           # Прошедшие события
```

**Ответы:**
- `GET /api/schedule/upcoming`: `[{ id, title, date, description, type }]`

### Content (Контент)
```
GET    /api/content/feed            # Лента контента
GET    /api/content/:id              # Конкретный контент
POST   /api/content/:id/favorite    # Добавить в избранное
DELETE /api/content/:id/favorite    # Удалить из избранного
GET    /api/content/favorites        # Избранное пользователя
```

**Ответы:**
- `GET /api/content/feed`: `[{ id, title, type, image, createdAt, isFavorite }]`

### Broadcasts (Рассылки)
```
GET    /api/broadcasts               # Список рассылок (admin)
POST   /api/broadcasts               # Создать рассылку (admin)
GET    /api/broadcasts/:id           # Детали рассылки (admin)
```

### Settings (Настройки)
```
GET    /api/settings                 # Системные настройки
PATCH  /api/settings                 # Обновить настройки (admin)
```

---

## STEP 3 — BACKEND МОДУЛИ ДЛЯ MVP

### 1. Auth Module (Аутентификация)
**Ответственность:**
- Верификация Telegram данных
- Генерация и валидация JWT токенов
- Управление сессиями
- Регистрация новых пользователей

**Функции:**
- `verifyTelegramAuth(initData)` — проверка данных Telegram
- `generateToken(userId)` — генерация JWT
- `validateToken(token)` — валидация токена
- `createUser(telegramData)` — создание пользователя

### 2. Users Module (Пользователи)
**Ответственность:**
- CRUD операции с пользователями
- Управление профилями
- Валидация данных пользователя

**Функции:**
- `getUserById(id)`
- `updateUser(id, data)`
- `getUserByTelegramId(telegramId)`

### 3. Subscriptions Module (Подписки)
**Ответственность:**
- Управление тарифными планами
- Создание и управление подписками
- Проверка статуса подписки
- Автоматическое продление

**Функции:**
- `getPlans()`
- `createSubscription(userId, planId)`
- `getUserSubscription(userId)`
- `cancelSubscription(subscriptionId)`
- `renewSubscription(subscriptionId)`
- `checkExpiredSubscriptions()`

### 4. Payments Module (Платежи)
**Ответственность:**
- Интеграция с платежными провайдерами (ЮKassa/Stripe)
- Создание платежей
- Обработка webhook'ов
- Активация подписки после оплаты

**Функции:**
- `createPayment(subscriptionId, amount)`
- `processWebhook(webhookData)`
- `getPaymentStatus(paymentId)`
- `activateSubscription(paymentId)`

### 5. Telegram Module (Telegram интеграция)
**Ответственность:**
- Взаимодействие с Telegram Bot API
- Отправка сообщений
- Управление доступом к каналу
- Генерация invite ссылок

**Функции:**
- `sendMessage(chatId, text)`
- `addUserToChannel(userId, channelId)`
- `removeUserFromChannel(userId, channelId)`
- `generateInviteLink(channelId)`
- `revokeInviteLink(linkId)`

### 6. Broadcasts Module (Рассылки)
**Ответственность:**
- Создание и отправка рассылок
- Планирование рассылок
- Статистика рассылок

**Функции:**
- `createBroadcast(data)`
- `sendBroadcast(broadcastId)`
- `scheduleBroadcast(broadcastId, date)`
- `getBroadcastStats(broadcastId)`

### 7. Schedule Module (Расписание)
**Ответственность:**
- Управление расписанием контента
- Планирование публикаций
- Уведомления о событиях

**Функции:**
- `createEvent(data)`
- `getUpcomingEvents()`
- `getPastEvents()`

### 8. Settings Module (Настройки)
**Ответственность:**
- Системные настройки
- Конфигурация тарифов
- Настройки платежей

**Функции:**
- `getSettings()`
- `updateSettings(key, value)`

---

## STEP 4 — DATABASE MODEL

### Таблица: users
**Назначение:** Хранение данных пользователей

**Поля:**
- `id` (UUID, PK) — уникальный идентификатор
- `telegram_id` (BIGINT, UNIQUE) — ID пользователя в Telegram
- `username` (VARCHAR) — username в Telegram
- `first_name` (VARCHAR) — имя
- `last_name` (VARCHAR) — фамилия
- `email` (VARCHAR, NULL) — email (опционально)
- `avatar_url` (VARCHAR, NULL) — ссылка на аватар
- `is_admin` (BOOLEAN, DEFAULT false) — флаг администратора
- `created_at` (TIMESTAMP) — дата регистрации
- `updated_at` (TIMESTAMP) — дата обновления

**Связи:**
- `has_many` subscriptions
- `has_many` payments

### Таблица: subscription_plans
**Назначение:** Тарифные планы подписки

**Поля:**
- `id` (UUID, PK)
- `name` (VARCHAR) — название плана (например, "Premium")
- `description` (TEXT) — описание
- `price` (DECIMAL) — цена в рублях
- `first_month_price` (DECIMAL, NULL) — цена первого месяца
- `duration_days` (INTEGER) — длительность в днях (30)
- `features` (JSONB) — список возможностей
- `is_active` (BOOLEAN, DEFAULT true) — активен ли план
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

**Связи:**
- `has_many` subscriptions

### Таблица: subscriptions
**Назначение:** Подписки пользователей

**Поля:**
- `id` (UUID, PK)
- `user_id` (UUID, FK -> users.id)
- `plan_id` (UUID, FK -> subscription_plans.id)
- `status` (ENUM: 'active', 'expired', 'cancelled', 'pending') — статус
- `start_date` (TIMESTAMP) — дата начала
- `end_date` (TIMESTAMP) — дата окончания
- `auto_renew` (BOOLEAN, DEFAULT true) — автоматическое продление
- `cancelled_at` (TIMESTAMP, NULL) — дата отмены
- `next_billing_date` (TIMESTAMP, NULL) — дата следующего списания
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

**Связи:**
- `belongs_to` user
- `belongs_to` plan
- `has_many` payments

**Индексы:**
- `idx_subscriptions_user_id`
- `idx_subscriptions_status`
- `idx_subscriptions_end_date`

### Таблица: payments
**Назначение:** История платежей

**Поля:**
- `id` (UUID, PK)
- `user_id` (UUID, FK -> users.id)
- `subscription_id` (UUID, FK -> subscriptions.id, NULL)
- `amount` (DECIMAL) — сумма платежа
- `currency` (VARCHAR, DEFAULT 'RUB') — валюта
- `status` (ENUM: 'pending', 'completed', 'failed', 'refunded') — статус
- `payment_provider` (VARCHAR) — провайдер (yookassa, stripe)
- `provider_payment_id` (VARCHAR) — ID платежа у провайдера
- `payment_url` (VARCHAR, NULL) — URL для оплаты
- `paid_at` (TIMESTAMP, NULL) — дата оплаты
- `metadata` (JSONB, NULL) — дополнительные данные
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

**Связи:**
- `belongs_to` user
- `belongs_to` subscription (опционально)

**Индексы:**
- `idx_payments_user_id`
- `idx_payments_status`
- `idx_payments_provider_payment_id`

### Таблица: broadcasts
**Назначение:** Рассылки в Telegram канал

**Поля:**
- `id` (UUID, PK)
- `created_by` (UUID, FK -> users.id) — создатель (admin)
- `title` (VARCHAR) — заголовок
- `content` (TEXT) — содержимое
- `media_url` (VARCHAR, NULL) — ссылка на медиа
- `scheduled_at` (TIMESTAMP, NULL) — запланированная отправка
- `sent_at` (TIMESTAMP, NULL) — дата отправки
- `status` (ENUM: 'draft', 'scheduled', 'sent', 'failed') — статус
- `telegram_message_id` (BIGINT, NULL) — ID сообщения в Telegram
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

**Связи:**
- `belongs_to` user (creator)

### Таблица: system_settings
**Назначение:** Системные настройки

**Поля:**
- `id` (UUID, PK)
- `key` (VARCHAR, UNIQUE) — ключ настройки
- `value` (JSONB) — значение настройки
- `description` (TEXT, NULL) — описание
- `updated_at` (TIMESTAMP)

**Примеры ключей:**
- `telegram_bot_token`
- `telegram_channel_id`
- `payment_provider_config`
- `subscription_default_plan_id`

---

## STEP 5 — TELEGRAM BOT LOGIC

### Обработчики команд

#### `/start`
**Логика:**
1. Проверка существования пользователя в БД
2. Если новый — создание записи в `users`
3. Проверка активной подписки
4. Отправка приветственного сообщения
5. Показ главного меню

**Сообщение:**
```
Добро пожаловать в Стильный чат Беллы Хасиас! 👋

Выберите действие:
```

#### Главное меню
**Кнопки:**
- 📋 Моя подписка
- 💳 Тарифы
- 🔗 Открыть Mini App
- 📱 Открыть канал
- ⚙️ Настройки

#### Тарифы
**Логика:**
1. Получение списка планов из БД
2. Форматирование сообщения с ценами
3. Кнопка "Оформить подписку"

**Сообщение:**
```
💎 Тарифы подписки:

Премиум — 990₽ (первый месяц)
Далее 1500₽/мес

[Оформить подписку]
```

#### Статус подписки
**Логика:**
1. Получение текущей подписки пользователя
2. Отображение статуса, даты окончания
3. Кнопки: "Продлить", "Отменить", "Открыть Mini App"

**Сообщение:**
```
📋 Ваша подписка:

Статус: ✅ Активна
План: Премиум
Окончание: 15 марта 2026
Автопродление: Включено

[Продлить] [Отменить] [Mini App]
```

#### Поток оплаты
**Логика:**
1. Создание подписки со статусом `pending`
2. Создание платежа через Payments Module
3. Получение `payment_url` от провайдера
4. Отправка inline кнопки с URL оплаты
5. Ожидание webhook от провайдера
6. После успешной оплаты:
   - Активация подписки
   - Добавление пользователя в канал
   - Отправка приветственного сообщения в канал

**Сообщение:**
```
💳 Оформление подписки

План: Премиум
Сумма: 990₽

[Оплатить]
```

#### Открыть Mini App
**Логика:**
1. Генерация deep link с данными пользователя
2. Отправка кнопки с `web_app` параметром

**Кнопка:**
```json
{
  "text": "Открыть приложение",
  "web_app": {
    "url": "https://app.bellahasias.ru?startapp=telegram_user_id"
  }
}
```

#### Открыть Telegram канал
**Логика:**
1. Проверка активной подписки
2. Если подписка активна:
   - Генерация временной invite ссылки
   - Отправка ссылки пользователю
3. Если подписка неактивна:
   - Сообщение о необходимости подписки
   - Кнопка "Оформить подписку"

**Сообщение:**
```
🔗 Доступ к каналу

[Открыть канал]
```

#### Продление подписки
**Логика:**
1. Проверка возможности продления (подписка активна)
2. Создание нового платежа
3. Повторение потока оплаты

### Взаимодействие с Backend

**Схема:**
```
Telegram Bot <--HTTP API--> Backend <--Database-->
                      |
                      v
              Telegram Bot API
```

**API вызовы от бота:**
- `POST /api/auth/telegram` — авторизация пользователя
- `GET /api/subscriptions/me` — получение подписки
- `POST /api/payments/create` — создание платежа
- `GET /api/telegram/invite-link` — генерация invite ссылки
- `POST /api/telegram/add-to-channel` — добавление в канал

**Webhook от Backend к боту:**
- После успешной оплаты → отправка уведомления пользователю
- После истечения подписки → уведомление об окончании

---

## STEP 6 — PAYMENT FLOW

### Жизненный цикл платежа

#### 1. Выбор плана
**Триггер:** Пользователь нажимает "Оформить подписку" в боте или Mini App

**Действия:**
- Пользователь выбирает план (в MVP только один план)
- Frontend отправляет `POST /api/subscriptions/create` с `planId`

#### 2. Создание платежа
**Backend логика:**
1. Проверка авторизации пользователя
2. Создание записи в `subscriptions` со статусом `pending`
3. Создание записи в `payments` со статусом `pending`
4. Вызов API платежного провайдера (ЮKassa/Stripe)
5. Получение `payment_url` от провайдера
6. Сохранение `provider_payment_id` в БД
7. Возврат `payment_url` клиенту

**Ответ API:**
```json
{
  "paymentId": "uuid",
  "paymentUrl": "https://yookassa.ru/checkout/...",
  "amount": 990,
  "currency": "RUB"
}
```

#### 3. Редирект на платежный провайдер
**Frontend логика:**
- Открытие `payment_url` в новом окне/iframe
- Пользователь вводит данные карты
- Провайдер обрабатывает платеж

#### 4. Webhook от провайдера
**Триггер:** Провайдер отправляет webhook после обработки платежа

**Backend обработка:**
1. Валидация подписи webhook (безопасность)
2. Поиск платежа по `provider_payment_id`
3. Обновление статуса платежа:
   - `completed` — успешная оплата
   - `failed` — ошибка оплаты
4. Если `completed`:
   - Активация подписки (`status = 'active'`)
   - Установка `start_date` и `end_date`
   - Добавление пользователя в Telegram канал
   - Отправка уведомления пользователю в боте
5. Сохранение `paid_at` в платеже

**Webhook endpoint:**
```
POST /api/payments/webhook
```

#### 5. Активация подписки
**Автоматические действия:**
- Обновление `subscriptions.status = 'active'`
- Установка `start_date = NOW()`
- Установка `end_date = NOW() + 30 days`
- Установка `next_billing_date = end_date` (если auto_renew)
- Вызов Telegram Module для добавления в канал

#### 6. Уведомление пользователя
**Отправка в бот:**
```
✅ Подписка активирована!

Ваш доступ к каналу открыт до 15 марта 2026.

[Открыть канал] [Mini App]
```

### Схема потока
```
User → Create Payment → Payment Provider
                              ↓
                         Webhook → Backend
                              ↓
                    Activate Subscription
                              ↓
                    Add to Telegram Channel
                              ↓
                    Notify User in Bot
```

---

## STEP 7 — TELEGRAM CHANNEL ACCESS

### Как пользователь получает invite ссылку

#### Метод 1: Через бота (после оплаты)
**Логика:**
1. После успешной оплаты и активации подписки
2. Backend вызывает Telegram Bot API: `exportChatInviteLink`
3. Генерация временной ссылки (действует 24 часа)
4. Сохранение ссылки в БД (опционально)
5. Отправка ссылки пользователю в боте

**Сообщение:**
```
🔗 Ваша ссылка для доступа к каналу:

https://t.me/+AbCdEfGhIjKlMnOpQrStUvWxYz

Ссылка действительна 24 часа.
```

#### Метод 2: Через команду бота
**Логика:**
1. Пользователь нажимает "Открыть канал" в меню
2. Проверка активной подписки
3. Если активна — генерация новой ссылки
4. Если неактивна — предложение оформить подписку

### Как доступ хранится

**В базе данных:**
- Прямое хранение не требуется (Telegram управляет участниками)
- Достаточно проверять статус подписки в `subscriptions`

**В Telegram:**
- Пользователь добавляется в приватный канал как участник
- Telegram хранит список участников

**Альтернативный подход (для аудита):**
Создать таблицу `channel_access_log`:
- `user_id`
- `channel_id`
- `action` ('added', 'removed')
- `timestamp`

### Как пользователь удаляется после истечения подписки

#### Автоматическое удаление
**Scheduler Job (ежедневно):**
1. Поиск подписок с `end_date < NOW()` и `status = 'active'`
2. Для каждой подписки:
   - Обновление `status = 'expired'`
   - Вызов Telegram Bot API: `banChatMember` или `unbanChatMember` + удаление
   - Отправка уведомления пользователю

**Telegram Bot API:**
```python
# Удаление пользователя из канала
bot.ban_chat_member(
    chat_id=CHANNEL_ID,
    user_id=user.telegram_id
)
```

#### Уведомление пользователю
**Сообщение в боте:**
```
⚠️ Ваша подписка истекла

Доступ к каналу закрыт. Продлите подписку, чтобы продолжить пользоваться сервисом.

[Продлить подписку]
```

#### Восстановление доступа
**При продлении:**
1. Активация новой подписки
2. Вызов `unbanChatMember` для разблокировки
3. Отправка новой invite ссылки
4. Добавление обратно в канал

---

## STEP 8 — ADMIN PANEL STRUCTURE

### Разделы админ панели

#### 1. Dashboard (Главная)
**Содержимое:**
- KPI метрики:
  - Общее количество пользователей
  - Активные подписки
  - MRR (Monthly Recurring Revenue)
  - Churn Rate
  - Новые пользователи за период
- График выручки (6 месяцев)
- Последняя активность (лента событий)
- Быстрые действия

**API endpoints:**
- `GET /api/admin/dashboard/stats`
- `GET /api/admin/dashboard/revenue`
- `GET /api/admin/dashboard/activity`

#### 2. Users (Пользователи)
**Содержимое:**
- Таблица пользователей с фильтрами:
  - Поиск по username/email
  - Фильтр по статусу подписки
  - Фильтр по дате регистрации
- Детальная страница пользователя:
  - Профиль
  - История подписок
  - История платежей
  - Действия (заблокировать, удалить)

**API endpoints:**
- `GET /api/admin/users` — список с пагинацией
- `GET /api/admin/users/:id` — детали
- `PATCH /api/admin/users/:id` — обновление
- `DELETE /api/admin/users/:id` — удаление

#### 3. Subscriptions (Подписки)
**Содержимое:**
- Список всех подписок
- Фильтры:
  - По статусу
  - По плану
  - По дате
- Действия:
  - Продлить подписку вручную
  - Отменить подписку
  - Изменить план

**API endpoints:**
- `GET /api/admin/subscriptions`
- `PATCH /api/admin/subscriptions/:id`
- `POST /api/admin/subscriptions/:id/extend`

#### 4. Payments (Платежи)
**Содержимое:**
- История всех платежей
- Фильтры:
  - По статусу
  - По провайдеру
  - По дате
- Детали платежа
- Действия:
  - Возврат платежа
  - Повторная попытка

**API endpoints:**
- `GET /api/admin/payments`
- `GET /api/admin/payments/:id`
- `POST /api/admin/payments/:id/refund`

#### 5. Broadcasts (Рассылки)
**Содержимое:**
- Список рассылок
- Создание новой рассылки:
  - Текст сообщения
  - Медиа (фото/видео)
  - Планирование отправки
- Статистика рассылок:
  - Количество отправленных
  - Количество прочитанных

**API endpoints:**
- `GET /api/admin/broadcasts`
- `POST /api/admin/broadcasts`
- `GET /api/admin/broadcasts/:id/stats`

#### 6. Settings (Настройки)
**Содержимое:**
- Системные настройки:
  - Telegram Bot Token
  - Telegram Channel ID
  - Настройки платежного провайдера
  - Тарифные планы (CRUD)
- Логи системы
- Резервные копии

**API endpoints:**
- `GET /api/admin/settings`
- `PATCH /api/admin/settings`
- `GET /api/admin/settings/plans`
- `POST /api/admin/settings/plans`
- `PATCH /api/admin/settings/plans/:id`

### Права доступа
- Все endpoints требуют `is_admin = true`
- JWT токен с ролью администратора
- Middleware проверки прав доступа

---

## STEP 9 — BACKGROUND JOBS

### Требуемые фоновые задачи

#### 1. Проверка истечения подписок
**Расписание:** Ежедневно в 00:00 UTC

**Логика:**
1. Поиск подписок с `end_date < NOW()` и `status = 'active'`
2. Для каждой подписки:
   - Обновление `status = 'expired'`
   - Удаление пользователя из Telegram канала
   - Отправка уведомления в бот
   - Логирование события

**Реализация:**
- Cron job или task scheduler (Celery/Bull)
- Функция: `checkExpiredSubscriptions()`

#### 2. Автоматическое продление подписок
**Расписание:** Ежедневно в 00:00 UTC

**Логика:**
1. Поиск подписок с:
   - `auto_renew = true`
   - `status = 'active'`
   - `next_billing_date = TODAY`
2. Для каждой подписки:
   - Создание нового платежа
   - Вызов платежного провайдера для списания
   - При успехе:
     - Продление `end_date` на 30 дней
     - Обновление `next_billing_date`
   - При ошибке:
     - Отправка уведомления пользователю
     - Установка `auto_renew = false` (опционально)

**Реализация:**
- Функция: `processAutoRenewals()`

#### 3. Проверка статуса платежей
**Расписание:** Каждые 5 минут

**Логика:**
1. Поиск платежей со статусом `pending` старше 15 минут
2. Запрос статуса у платежного провайдера
3. Обновление статуса в БД
4. При успешной оплате — активация подписки

**Реализация:**
- Функция: `verifyPendingPayments()`

#### 4. Напоминания о продлении
**Расписание:** Ежедневно в 09:00 UTC

**Логика:**
1. Поиск подписок с `end_date = TODAY + 3 days` и `auto_renew = false`
2. Отправка напоминания в бот:
   ```
   ⏰ Ваша подписка истекает через 3 дня
   
   Продлите подписку, чтобы не потерять доступ.
   
   [Продлить]
   ```

**Реализация:**
- Функция: `sendRenewalReminders()`

#### 5. Отправка запланированных рассылок
**Расписание:** Каждую минуту

**Логика:**
1. Поиск рассылок с `status = 'scheduled'` и `scheduled_at <= NOW()`
2. Для каждой рассылки:
   - Отправка в Telegram канал
   - Обновление `status = 'sent'`
   - Сохранение `telegram_message_id`
   - Обновление `sent_at`

**Реализация:**
- Функция: `sendScheduledBroadcasts()`

#### 6. Очистка старых данных
**Расписание:** Еженедельно (воскресенье 02:00 UTC)

**Логика:**
1. Удаление истекших invite ссылок (старше 7 дней)
2. Архивирование старых логов (старше 90 дней)
3. Очистка временных файлов

**Реализация:**
- Функция: `cleanupOldData()`

### Технологии для реализации
**Варианты:**
1. **Node.js:**
   - `node-cron` для простых задач
   - `Bull` + Redis для сложных очередей

2. **Python:**
   - `Celery` + Redis/RabbitMQ
   - `APScheduler`

3. **Отдельный сервис:**
   - Микросервис для задач
   - REST API для управления задачами

**Рекомендация для MVP:**
- Node.js + `node-cron` для простоты
- Отдельный процесс для scheduler

---

## STEP 10 — IMPLEMENTATION ROADMAP

### Phase 1 — Database (Неделя 1)
**Задачи:**
1. Выбор БД (PostgreSQL рекомендуется)
2. Создание схемы БД
3. Миграции для всех таблиц
4. Индексы и ограничения
5. Seed данные (тестовые планы)

**Результат:**
- Готовая структура БД
- Миграции для развертывания

### Phase 2 — Authentication (Неделя 2)
**Задачи:**
1. Реализация Auth Module
2. Верификация Telegram данных
3. JWT токены (генерация/валидация)
4. API endpoints для auth
5. Middleware для защиты routes
6. Интеграция в Mini App

**Результат:**
- Работающая авторизация через Telegram
- Защищенные API endpoints

### Phase 3 — Subscriptions (Неделя 3)
**Задачи:**
1. Реализация Subscriptions Module
2. CRUD для планов
3. Создание/управление подписками
4. API endpoints для подписок
5. Интеграция в Mini App (страница подписки)

**Результат:**
- Управление подписками через API
- Отображение в Mini App

### Phase 4 — Payments (Неделя 4)
**Задачи:**
1. Выбор платежного провайдера (ЮKassa/Stripe)
2. Реализация Payments Module
3. Интеграция с провайдером
4. Webhook обработка
5. Активация подписки после оплаты
6. Тестирование платежного потока

**Результат:**
- Работающие платежи
- Автоматическая активация подписок

### Phase 5 — Telegram Bot (Неделя 5)
**Задачи:**
1. Настройка Telegram Bot
2. Реализация Telegram Module
3. Обработчики команд бота
4. Интеграция с Backend API
5. Отправка сообщений
6. Inline кнопки и меню

**Результат:**
- Работающий бот с основными командами
- Интеграция с системой

### Phase 6 — Channel Access (Неделя 6)
**Задачи:**
1. Реализация управления доступом к каналу
2. Генерация invite ссылок
3. Добавление/удаление пользователей
4. Интеграция с подписками
5. Тестирование потока

**Результат:**
- Автоматическое управление доступом
- Работающие invite ссылки

### Phase 7 — Mini App Integration (Неделя 7)
**Задачи:**
1. Интеграция Telegram WebApp SDK
2. Подключение к Backend API
3. Реализация всех страниц с реальными данными
4. Обработка ошибок
5. Загрузочные состояния
6. Тестирование на реальных устройствах

**Результат:**
- Полностью функциональная Mini App
- Интеграция с ботом

### Phase 8 — Admin Panel (Неделя 8)
**Задачи:**
1. Реализация Admin API endpoints
2. Аутентификация администраторов
3. Все разделы админ панели
4. CRUD операции
5. Статистика и графики
6. Тестирование

**Результат:**
- Работающая админ панель
- Все необходимые функции

### Phase 9 — Scheduler (Неделя 9)
**Задачи:**
1. Настройка task scheduler
2. Реализация всех background jobs
3. Тестирование задач
4. Мониторинг и логирование
5. Обработка ошибок в задачах

**Результат:**
- Автоматизированные фоновые задачи
- Надежная работа системы

### Дополнительные фазы (Post-MVP)

**Phase 10 — Testing & Optimization**
- Unit тесты
- Integration тесты
- Нагрузочное тестирование
- Оптимизация производительности

**Phase 11 — Monitoring & Logging**
- Настройка мониторинга
- Логирование
- Алерты

**Phase 12 — Documentation**
- API документация
- Руководство пользователя
- Руководство администратора

---

## ДОПОЛНИТЕЛЬНЫЕ РЕКОМЕНДАЦИИ

### Безопасность
- Валидация всех входных данных
- Защита от SQL инъекций (ORM)
- Rate limiting на API
- HTTPS везде
- Валидация Telegram данных (hash проверка)
- Безопасное хранение токенов

### Масштабируемость
- Использование кэша (Redis) для частых запросов
- Индексы в БД для производительности
- Пагинация для списков
- Асинхронная обработка тяжелых задач

### Мониторинг
- Логирование всех важных событий
- Метрики производительности
- Алерты на критические ошибки
- Дашборд для мониторинга

---

**Документ подготовлен:** 2026-03-08
**Версия:** 1.0 MVP
