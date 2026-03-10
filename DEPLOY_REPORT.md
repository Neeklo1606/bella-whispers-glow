# Отчёт о деплое — 2026-03-08

## Выполнено

### 1. Коммит
- **Коммит:** `f349ca5`
- **Сообщение:** `feat: MiniApp content from API, admin content management, tariffs bootstrap`
- **Изменения:** 13 файлов, +412 / -49 строк

**Файлы:**
- `backend/src/main.py` — подключён miniapp router
- `backend/src/modules/system_settings/bootstrap.py` — дефолтные настройки контента и план
- `backend/src/modules/miniapp/` — новый модуль (router, __init__)
- `src/App.tsx` — роут `/admin/content`
- `src/components/layout/AdminLayout.tsx` — пункт "Контент MiniApp"
- `src/components/layout/BottomNav.tsx` — ссылка из API
- `src/lib/api.ts` — `getMiniappContent()`, типы `MiniappContent`
- `src/hooks/useMiniappContent.ts` — хук загрузки контента
- `src/pages/Index.tsx`, `Pricing.tsx`, `Profile.tsx` — контент из API
- `src/pages/AdminContent.tsx` — страница управления контентом MiniApp

### 2. Push
- **Репозиторий:** `https://github.com/Neeklo1606/bella-whispers-glow.git`
- **Ветка:** `main`
- **Статус:** успешно

### 3. Деплой на сервер
- **Сервер:** root@155.212.210.214
- **Путь:** /var/www/bella

**Результат:**
- Код обновлён с git (pull успешен, HEAD: f349ca5)
- Установка backend-зависимостей: **ошибка** — `externally-managed-environment`

Причина: Python 3.12 на сервере — externally-managed environment, системный `pip install` блокируется.

**Рекомендация:** настроить venv в `/var/www/bella` и в `deploy.sh` вызывать:
```bash
source /var/www/bella/venv/bin/activate
pip install -r backend/requirements.txt
```

---

## Что внедрено в коде

1. **MiniApp контент через API** — вся конфигурация из `/api/miniapp/content`
2. **Админка → Контент MiniApp** — редактирование ссылок, текстов, FEATURES, FAQ
3. **Bootstrap тарифа** — создание плана «1 месяц» при отсутствии активных планов
4. **Удаление статики** — Index, Pricing, Profile, BottomNav берут данные из API
