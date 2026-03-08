# Инструкция по настройке VPS сервера для проекта Bella

## 1. SSH ключ для подключения

### Публичный ключ (ed25519) - добавьте в панель Beget:

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAICWdK6J93+pq2nOLGOkpiLXPlrDv9WgFT7wQlX6MQ2oL bella-vps-20260308
```

**Как добавить ключ в Beget:**
1. В панели создания сервера нажмите "Добавить новый SSH-ключ"
2. Вставьте ключ выше
3. Дайте ключу имя (например, "bella-vps-key")

### Альтернативный ключ (RSA) - если нужен:

```
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCfDT2nhPFvSoDEj6nOCr/kQKxnvCjUTzIh66JqTSoySMqVgJH44M0zEgtj/zM3f5rBBVtLq9vYNUbFnWA7sxrXasmzbYGSCZ1jG8Hm5BABN/Be6HSqganNlPHsVlQlVrpi7H2z8Tw7U5NYV/a4vF9FwToKGBTrhZFFmpGhp773pRDhwP2agzDXGoMrhHAjoTeGBcR1ao7gt5zUtiHxMBKwtV2RcLq0jOR8brWVQGAUweuhPOSzrAf1pvDYiIvvVZyF2Wv4QIKE4YpuGjhzTJlNaXMBeCtyPgNa/rxF2kZRmH5lLAlUmMt71I/n5dLbs60xJLSdWF7ec2I695e4sQi2ONkdJ1nhjNKZfK8tVJ4CoQIkThd8uJiqO+GLcjJscUt8v0JjzNxoMUPCOaOycsV0crEuq4mCXHbKrkGrPGFquaAM4/1b9goV7vOT6GdO2jUcIGUz6fGFIum3zMQ80IvdJUfQ1xc5UB4soIKkSTmhpTr3l2glhpt7+Nq3oGiKHrd/OKedy0SZf+YrcyW6zuMhm0duFA6mMVppjfae0CmWb+9i9U/ZVe1ytImXngtZT1PeOCmsUHihUTMOTNWE2cPKoWz+ssLeQWoGhCQYeHy6d8RmTLhbLhWfMzUvrGsaUorLgILjrp6+eIIovrUe3QcrKevhqH4q/Atec2AXCNpwvw== dsc-2@localhost
```

## 2. Подключение к серверу

После создания сервера подключитесь по SSH:

```bash
ssh root@<IP_АДРЕС_СЕРВЕРА>
```

Или если используется другой пользователь:
```bash
ssh <пользователь>@<IP_АДРЕС_СЕРВЕРА>
```

## 3. Настройка сервера (Ubuntu 24.04)

### Обновление системы

```bash
apt update && apt upgrade -y
```

### Установка необходимого ПО

```bash
# Node.js (через nvm - рекомендуется)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install --lts
nvm use --lts

# Или установка Node.js напрямую
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs

# Git
apt install -y git

# Nginx (для проксирования)
apt install -y nginx

# PM2 (для управления процессами Node.js)
npm install -g pm2

# Firewall
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw --force enable
```

### Настройка Nginx

Создайте конфигурацию для проекта:

```bash
nano /etc/nginx/sites-available/bella
```

Вставьте следующую конфигурацию (замените `your-domain.com` на ваш домен):

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Активируйте конфигурацию:

```bash
ln -s /etc/nginx/sites-available/bella /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

### Развертывание проекта

```bash
# Создайте директорию для проекта
mkdir -p /var/www/bella
cd /var/www/bella

# Клонируйте репозиторий (или загрузите файлы)
git clone https://github.com/Neeklo1606/bella-whispers-glow.git .

# Установите зависимости
npm install

# Соберите проект для продакшена
npm run build

# Запустите через PM2
pm2 start npm --name "bella" -- run preview
# Или для dev режима:
# pm2 start npm --name "bella-dev" -- run dev

# Сохраните конфигурацию PM2
pm2 save
pm2 startup
```

### Настройка SSL (Let's Encrypt)

```bash
apt install -y certbot python3-certbot-nginx
certbot --nginx -d your-domain.com -d www.your-domain.com
```

## 4. Полезные команды

### PM2
```bash
pm2 list              # Список процессов
pm2 logs bella        # Логи приложения
pm2 restart bella     # Перезапуск
pm2 stop bella        # Остановка
pm2 delete bella      # Удаление
```

### Nginx
```bash
systemctl status nginx    # Статус
systemctl restart nginx   # Перезапуск
nginx -t                  # Проверка конфигурации
```

### Мониторинг
```bash
htop                     # Мониторинг ресурсов
df -h                    # Использование диска
free -h                  # Использование памяти
```

## 5. Настройка Git на сервере (опционально)

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

## 6. Безопасность

- Отключите вход по паролю (используйте только SSH ключи)
- Настройте fail2ban для защиты от брутфорса
- Регулярно обновляйте систему
- Используйте сильные пароли для баз данных

```bash
apt install -y fail2ban
systemctl enable fail2ban
systemctl start fail2ban
```

## 7. Резервное копирование

Настройте автоматическое резервное копирование через cron:

```bash
crontab -e
```

Добавьте строку для ежедневного бэкапа (пример):
```
0 2 * * * tar -czf /backup/bella-$(date +\%Y\%m\%d).tar.gz /var/www/bella
```

---

**Примечание:** Замените `<IP_АДРЕС_СЕРВЕРА>` и `your-domain.com` на реальные значения после создания сервера.
