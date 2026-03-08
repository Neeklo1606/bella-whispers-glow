#!/bin/bash

# Install systemd services on server
# Run this once to set up services

set -e

echo "=== Installing systemd services ==="

# Copy service files
cp /tmp/bella-backend.service /etc/systemd/system/
cp /tmp/bella-bot.service /etc/systemd/system/
cp /tmp/bella-scheduler.service /etc/systemd/system/

# Reload systemd
systemctl daemon-reload

# Enable services
systemctl enable bella-backend.service
systemctl enable bella-bot.service
systemctl enable bella-scheduler.service

echo "Services installed and enabled"
echo ""
echo "To start services:"
echo "  systemctl start bella-backend"
echo "  systemctl start bella-bot"
echo "  systemctl start bella-scheduler"
