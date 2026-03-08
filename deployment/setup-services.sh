#!/bin/bash

# Setup systemd services for Bella platform
# Run this script once to install services

set -e

PROJECT_DIR="/var/www/bella"
SERVICES_DIR="$PROJECT_DIR/deployment"

echo "=== Setting up systemd services ==="

# Copy service files to systemd directory
cp "$SERVICES_DIR/bella-backend.service" /etc/systemd/system/
cp "$SERVICES_DIR/bella-bot.service" /etc/systemd/system/
cp "$SERVICES_DIR/bella-scheduler.service" /etc/systemd/system/

# Reload systemd
systemctl daemon-reload

# Enable services to start on boot
systemctl enable bella-backend.service
systemctl enable bella-bot.service
systemctl enable bella-scheduler.service

echo "Services installed and enabled"
echo ""
echo "To start services:"
echo "  systemctl start bella-backend"
echo "  systemctl start bella-bot"
echo "  systemctl start bella-scheduler"
echo ""
echo "To check status:"
echo "  systemctl status bella-backend"
echo "  systemctl status bella-bot"
echo "  systemctl status bella-scheduler"
