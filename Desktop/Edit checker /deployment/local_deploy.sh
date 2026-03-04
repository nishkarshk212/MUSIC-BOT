#!/bin/bash

# Local deployment script for Edit Checker Bot
# This script runs from your local machine to deploy to 45.194.2.99

SERVER_IP="45.194.2.99"
SERVER_USER="ubuntu"
DEPLOY_DIR="/tmp/edit_checker_deployment"
SSH_KEY="./EDIT_CHECKER.pem"

echo "=== Starting Deployment to $SERVER_IP ==="

# Copy deployment files to server
echo "Uploading deployment files..."
scp -i "$SSH_KEY" -o StrictHostKeyChecking=no ../edit_checker_bot_deployment.zip $SERVER_USER@$SERVER_IP:$DEPLOY_DIR.zip

# Create deployment directory on server
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP "mkdir -p $DEPLOY_DIR"

# Extract files on server
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP "unzip -o $DEPLOY_DIR.zip -d $DEPLOY_DIR"

# Copy and execute deployment script
scp -i "$SSH_KEY" -o StrictHostKeyChecking=no improved_server_deploy.sh $SERVER_USER@$SERVER_IP:/tmp/server_deploy.sh
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP "chmod +x /tmp/server_deploy.sh && /tmp/server_deploy.sh"

# Check service status
echo "Checking bot status..."
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP "systemctl status edit_checker_bot --no-pager"

echo "=== Deployment Process Complete ==="
echo "Bot should now be running on $SERVER_IP"
echo "You can check logs with: ssh $SERVER_USER@$SERVER_IP 'journalctl -u edit_checker_bot -f'"