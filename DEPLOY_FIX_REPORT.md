# Отчёт: Исправление деплоя (externally-managed-environment)

**Дата:** 2025-03-10  
**Проблема:** Деплой останавливался на этапе установки backend-зависимостей с ошибкой `externally-managed-environment`.

---

## 1. Причина проблемы

### 1.1 Что произошло
При выполнении `deploy.ps1` скрипт на сервере вызывал **устаревший** `deploy.sh`, расположенный по пути `/var/www/bella/deploy.sh`. Этот файл:
- **Не обновлялся через git** (либо был создан вручную, либо взят из старой версии)
- Использовал **системный pip**: `/usr/bin/python3 -m pip install`
- Не создавал и не использовал virtualenv

### 1.2 Почему это привело к ошибке
В **Debian/Ubuntu** с Python 3.12+ действует [PEP 668](https://peps.python.org/pep-0668/): системный Python считается «externally managed», и `pip install` глобально блокируется, чтобы не сломать системные пакеты.

Результат: при попытке `python3 -m pip install -r requirements.txt` pip выдавал:
```
error: externally-managed-environment
× This environment is externally managed
```

### 1.3 Что обнаружено на сервере
| Параметр | Значение |
|----------|----------|
| Python | 3.12.3 |
| Путь к старому deploy.sh | `/var/www/bella/deploy.sh` (8162 байт, без venv) |
| Путь к актуальному deploy.sh | `/var/www/bella/deployment/deploy.sh` (12855 байт, с venv) |
| Backend venv | Существует (`/var/www/bella/backend/venv`) |
| bella-backend.service | Уже использует venv: `venv/bin/python` |

---

## 2. Внесённые исправления

### 2.1 deploy.ps1
Путь не менялся: deploy.ps1 вызывает `/var/www/bella/deploy.sh`. Важно, что этот файл теперь в репозитории и при `git pull` заменит устаревший скрипт на сервере.

### 2.2 deploy.sh в корне репозитория
Добавлен `deploy.sh` в корень проекта:
```bash
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec bash "$SCRIPT_DIR/deployment/deploy.sh"
```
При `git pull` этот файл заменит старый скрипт и будет вызывать актуальный `deployment/deploy.sh` с поддержкой venv.

### 2.3 deployment/deploy.sh (backend)
- Создаётся venv, если его нет: `python3 -m venv venv`
- Установка зависимостей: `./venv/bin/pip install -r requirements.txt`

### 2.4 deployment/deploy.sh (bot)
- Добавлено создание venv для бота, если его нет
- Всегда используется `./venv/bin/pip` вместо системного pip
- Добавлен `pip install --upgrade pip` перед установкой зависимостей

---

## 3. Рекомендации

1. **Проверить `python3-venv` на сервере** (если venv не создаётся):
   ```bash
   apt install python3-venv
   ```

2. **Удалить старый lock**, если деплой прервался:
   ```bash
   rm -f /tmp/bella_deploy.lock
   ```

3. **Повторный деплой** после коммита и пуша:
   ```powershell
   .\deploy.ps1 -SkipCommit
   ```

---

## 4. Итог

| До | После |
|----|-------|
| Вызывался устаревший deploy.sh | Используется `deploy.sh` из репозитория → `deployment/deploy.sh` |
| Backend: системный pip | Backend: `./venv/bin/pip` в venv |
| Bot: fallback на системный pip | Bot: всегда `./venv/bin/pip` в venv |
| Ошибка externally-managed-environment | Установка в изолированном venv без конфликтов с системой |
