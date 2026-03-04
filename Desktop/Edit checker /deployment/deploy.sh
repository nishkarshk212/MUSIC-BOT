#!/bin/bash

# Deployment script for Edit Checker Bot
# This script sets up the environment and starts the bot

echo "Starting Edit Checker Bot deployment..."

# Update system packages
echo "Updating system packages..."
sudo apt-get update -y

# Install Python 3 and pip if not already installed
echo "Installing Python and pip..."
sudo apt-get install -y python3 python3-pip python3-venv

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install requirements
echo "Installing Python requirements..."
pip install -r requirements.txt

# Create logs directory
mkdir -p logs

# Start the bot
echo "Starting the bot..."
python bot.py