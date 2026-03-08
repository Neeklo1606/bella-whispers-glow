#!/bin/bash
SECRET=$(openssl rand -hex 32)
cat > /var/www/bella/backend/.env << EOF
DATABASE_URL=postgresql+asyncpg://bella_user:secure_password@localhost:5432/bella
SECRET_KEY=$SECRET
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHANNEL_ID=
YOOKASSA_SHOP_ID=
YOOKASSA_SECRET_KEY=
EOF
