#!/bin/bash

# Glam Cart Builder - Service Stop Script
# This script stops both backend and nginx services

echo "🛑 Stopping Glam Cart Builder Services..."

# Stop Backend Service
if [ -f /tmp/backend.pid ]; then
    BACKEND_PID=$(cat /tmp/backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo "🔧 Stopping backend service (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        rm -f /tmp/backend.pid
        echo "✅ Backend service stopped"
    else
        echo "⚠️  Backend service was not running"
        rm -f /tmp/backend.pid
    fi
else
    echo "⚠️  Backend PID file not found"
fi

# Stop Nginx
if pgrep nginx > /dev/null; then
    echo "🔧 Stopping Nginx..."
    sudo nginx -s quit
    echo "✅ Nginx stopped"
else
    echo "⚠️  Nginx was not running"
fi

echo ""
echo "✅ All services stopped successfully!"
