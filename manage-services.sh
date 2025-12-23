#!/bin/bash

# Glam Cart Builder - Service Management Script
# 用于管理前后端服务的启动、停止和状态检查

PROJECT_DIR="/data/glam-cart-deployment"
BACKEND_DIR="$PROJECT_DIR/backend"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

# 检查服务状态
check_backend() {
    print_header "检查后端服务状态"
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_status "后端服务运行正常 ✅"
        curl -s http://localhost:8000/health | jq . 2>/dev/null || curl -s http://localhost:8000/health
    else
        print_error "后端服务未运行 ❌"
        return 1
    fi
}

check_nginx() {
    print_header "检查Nginx服务状态"
    if pgrep nginx > /dev/null; then
        print_status "Nginx服务运行正常 ✅"
        nginx -t 2>/dev/null && print_status "Nginx配置文件正确 ✅"
    else
        print_error "Nginx服务未运行 ❌"
        return 1
    fi
}

check_https() {
    print_header "检查HTTPS访问"
    if curl -s https://bojie.shop/health > /dev/null 2>&1; then
        print_status "HTTPS访问正常 ✅"
        echo "网站地址: https://bojie.shop"
    else
        print_warning "HTTPS访问可能有问题 ⚠️"
        return 1
    fi
}

# 启动后端服务
start_backend() {
    print_header "启动后端服务"
    cd "$BACKEND_DIR"
    if ! pgrep -f "python.*main:app" > /dev/null; then
        print_status "正在启动后端服务..."
        source venv/bin/activate
        nohup python -c "import uvicorn; uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=False)" > /tmp/backend.log 2>&1 &
        echo $! > /tmp/backend.pid
        sleep 3
        if check_backend; then
            print_status "后端服务启动成功 ✅"
        else
            print_error "后端服务启动失败 ❌"
            return 1
        fi
    else
        print_status "后端服务已在运行 ✅"
    fi
}

# 启动Nginx服务
start_nginx() {
    print_header "启动Nginx服务"
    if ! pgrep nginx > /dev/null; then
        print_status "正在启动Nginx服务..."
        nginx
        if check_nginx; then
            print_status "Nginx服务启动成功 ✅"
        else
            print_error "Nginx服务启动失败 ❌"
            return 1
        fi
    else
        print_status "Nginx服务已在运行 ✅"
    fi
}

# 停止服务
stop_backend() {
    print_header "停止后端服务"
    if [ -f /tmp/backend.pid ]; then
        PID=$(cat /tmp/backend.pid)
        if kill $PID 2>/dev/null; then
            print_status "后端服务已停止 ✅"
            rm -f /tmp/backend.pid
        else
            print_warning "无法停止后端服务，尝试强制停止..."
            pkill -f "python.*main:app" && print_status "后端服务已强制停止 ✅"
        fi
    else
        pkill -f "python.*main:app" && print_status "后端服务已停止 ✅" || print_warning "后端服务未运行"
    fi
}

stop_nginx() {
    print_header "停止Nginx服务"
    if pgrep nginx > /dev/null; then
        nginx -s quit && print_status "Nginx服务已停止 ✅"
    else
        print_warning "Nginx服务未运行"
    fi
}

# 重启服务
restart_services() {
    print_header "重启所有服务"
    stop_backend
    stop_nginx
    sleep 2
    start_backend
    start_nginx
    check_all
}

# 检查所有服务
check_all() {
    print_header "系统状态检查"
    check_backend
    echo
    check_nginx
    echo
    check_https
    echo
    print_header "服务摘要"
    echo "🌐 网站地址: https://bojie.shop"
    echo "📡 API地址: https://bojie.shop/api/"
    echo "📚 API文档: https://bojie.shop/docs"
    echo "🔍 健康检查: https://bojie.shop/health"
}

# 显示帮助信息
show_help() {
    echo "Glam Cart Builder - 服务管理脚本"
    echo
    echo "用法: $0 [命令]"
    echo
    echo "命令:"
    echo "  start     启动所有服务"
    echo "  stop      停止所有服务"
    echo "  restart   重启所有服务"
    echo "  status    检查服务状态"
    echo "  backend   仅管理后端服务 (start|stop|status)"
    echo "  nginx     仅管理Nginx服务 (start|stop|status)"
    echo "  help      显示此帮助信息"
    echo
    echo "示例:"
    echo "  $0 start          # 启动所有服务"
    echo "  $0 status         # 检查所有服务状态"
    echo "  $0 backend start  # 仅启动后端服务"
}

# 主逻辑
case "$1" in
    "start")
        start_backend
        start_nginx
        check_all
        ;;
    "stop")
        stop_backend
        stop_nginx
        ;;
    "restart")
        restart_services
        ;;
    "status")
        check_all
        ;;
    "backend")
        case "$2" in
            "start") start_backend ;;
            "stop") stop_backend ;;
            "status") check_backend ;;
            *) echo "用法: $0 backend [start|stop|status]" ;;
        esac
        ;;
    "nginx")
        case "$2" in
            "start") start_nginx ;;
            "stop") stop_nginx ;;
            "status") check_nginx ;;
            *) echo "用法: $0 nginx [start|stop|status]" ;;
        esac
        ;;
    "help"|"--help"|"-h")
        show_help
        ;;
    *)
        show_help
        ;;
esac
