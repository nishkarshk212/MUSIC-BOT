#!/bin/bash

# Improved deployment script for Edit Checker Bot
# Handles sudo requirements and missing packages

echo "=== Edit Checker Bot Deployment Started ==="

# Update system packages (requires sudo)
echo "Updating system packages..."
sudo apt-get update -y
sudo apt-get upgrade -y

# Install required packages
echo "Installing required packages..."
sudo apt-get install -y python3 python3-pip python3-venv unzip

# Create bot directory with proper permissions
echo "Creating bot directory..."
sudo mkdir -p /opt/edit_checker_bot
sudo chown ubuntu:ubuntu /opt/edit_checker_bot
cd /opt/edit_checker_bot

# Extract deployment files
echo "Extracting deployment files..."
unzip /tmp/edit_checker_deployment.zip -d .

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Set proper permissions
chmod +x deploy.sh

# Create logs directory
mkdir -p logs

# Install systemd service (requires sudo)
echo "Installing systemd service..."
sudo cp edit_checker_bot.service /etc/systemd/system/
sudo systemctl daemon-reload

# Enable and start the service
echo "Starting bot service..."
sudo systemctl enable edit_checker_bot
sudo systemctl start edit_checker_bot

echo "=== Deployment Complete ==="
echo "Bot status: $(systemctl is-active edit_checker_bot)"
echo "Service enabled: $(systemctl is-enabled edit_checker_bot)"