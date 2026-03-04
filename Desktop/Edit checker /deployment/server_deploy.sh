#!/bin/bash

# Edit Checker Bot Deployment Script for 45.194.2.99
# This script will be executed on the remote server

echo "=== Edit Checker Bot Deployment Started ==="

# Update system
apt-get update -y
apt-get upgrade -y

# Install required packages
apt-get install -y python3 python3-pip python3-venv git unzip

# Create bot directory
mkdir -p /opt/edit_checker_bot
cd /opt/edit_checker_bot

# Download deployment package (this would be uploaded first)
# For now, assuming files are already uploaded to /tmp/edit_checker_deployment/
# Using SSH key authentication with the provided private key

# Extract deployment files
unzip /tmp/edit_checker_deployment.zip -d .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Set proper permissions
chown -R root:root /opt/edit_checker_bot
chmod +x deploy.sh

# Create logs directory
mkdir -p logs

# Install systemd service
cp edit_checker_bot.service /etc/systemd/system/
systemctl daemon-reload

# Enable and start the service
systemctl enable edit_checker_bot
systemctl start edit_checker_bot

echo "=== Deployment Complete ==="
echo "Bot status: $(systemctl is-active edit_checker_bot)"
echo "Service enabled: $(systemctl is-enabled edit_checker_bot)"