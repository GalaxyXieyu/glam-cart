#!/bin/bash

# Glam Cart Builder - Service Startup Script
# This script starts both backend and nginx services

set -e

PROJECT_DIR="/home/devbox/project"
BACKEND_DIR="$PROJECT_DIR/backend"
VENV_DIR="$PROJECT_DIR/bin"

echo "🚀 Starting Glam Cart Builder Services..."

# Function to check if a service is running
check_service() {
    local service_name=$1
    local port=$2
    local url=$3
    
    echo "⏳ Checking $service_name on port $port..."
    
    if curl -s "$url" > /dev/null 2>&1; then
        echo "✅ $service_name is already running on port $port"
        return 0
    else
        echo "❌ $service_name is not running on port $port"
        return 1
    fi
}

# Start Backend Service
echo "📡 Starting Backend Service..."
if ! check_service "Backend API" "8000" "http://localhost:8000/health"; then
    echo "🔧 Starting backend server..."
    cd "$BACKEND_DIR"
    source "$VENV_DIR/activate"
    nohup python run.py > /tmp/backend.log 2>&1 &
    echo $! > /tmp/backend.pid
    
    # Wait for backend to start
    sleep 5
    
    if check_service "Backend API" "8000" "http://localhost:8000/health"; then
        echo "✅ Backend started successfully"
    else
        echo "❌ Failed to start backend"
        exit 1
    fi
else
    echo "✅ Backend is already running"
fi

# Start/Restart Nginx
echo "🌐 Starting Nginx..."
if pgrep nginx > /dev/null; then
    echo "🔄 Nginx is running, reloading configuration..."
    sudo nginx -s reload
else
    echo "🔧 Starting Nginx..."
    sudo nginx
fi

# Verify Nginx is running
if pgrep nginx > /dev/null; then
    echo "✅ Nginx started successfully"
else
    echo "❌ Failed to start Nginx"
    exit 1
fi

echo ""
echo "🎉 All services started successfully!"
echo ""
echo "📍 Application URLs:"
echo "   🌐 Frontend: http://localhost"
echo "   📡 Backend API: http://localhost:8000"
echo "   📚 API Docs: http://localhost/docs"
echo "   🔍 Health Check: http://localhost/health"
echo ""
echo "📝 Log files:"
echo "   Backend: /tmp/backend.log"
echo "   Nginx: /var/log/nginx/"
echo ""
echo "🛑 To stop services, run: ./stop-services.sh"
