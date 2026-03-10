# Отчёт о деплое — 2026-03-08

## Статус: ✅ Успешно

**Коммит:** `0977d55`  
**Сообщение:** `fix: add useMiniappContent and variables to Index - fix telegramLink is not defined`

---

## Изменения
- **src/pages/Index.tsx** — восстановлены `useMiniappContent()`, переменные `telegramLink`, `contactLink`, `faqItems`, `planTitle`, `priceNote`, `plan`, `price`; исправлена ошибка `ReferenceError: telegramLink is not defined`

---

## Сервер
- **URL:** https://app.bellahasias.ru
- **Сервисы:** Backend, Bot, Scheduler — активны
- **Frontend:** собран (index-BR7OVjCb.js), доступен
