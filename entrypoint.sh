#!/bin/bash

# Check if Nginx is installed, and install if not
if ! command -v /usr/sbin/nginx &> /dev/null; then
    echo "Nginx not found, installing..."
    sudo apt-get update && sudo apt-get install -y nginx
fi

# Start Nginx in the background
echo "Starting Nginx..."
sudo /usr/sbin/nginx -c /home/devbox/project/nginx-glam-cart.conf

# Activate Python virtual environment
echo "Activating Python virtual environment..."
cd /home/devbox/project && source bin/activate

# Start the backend server in the background
echo "Starting backend server..."
cd /home/devbox/project/backend && nohup python3 run.py > /tmp/backend.log 2>&1 &

echo "Services started."