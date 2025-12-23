#!/bin/bash

# Glam Cart Builder - 部署打包脚本
# 排除 Python 和 JS 包，只打包部署所需文件

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
PACKAGE_NAME="glam-cart-deployment-$(date +%Y%m%d-%H%M%S)"
TEMP_DIR="/tmp/$PACKAGE_NAME"

echo "🚀 开始打包 Glam Cart Builder 部署文件..."
echo "📁 项目目录: $PROJECT_DIR"
echo "📦 打包文件名: $PACKAGE_NAME.tar.gz"
echo ""

# 创建临时目录
echo "📂 创建临时目录: $TEMP_DIR"
mkdir -p "$TEMP_DIR"

# 复制文件，排除不需要的目录和文件
echo "📋 复制项目文件（排除 Python 和 JS 包）..."

rsync -av \
    --exclude="node_modules/" \
    --exclude="__pycache__/" \
    --exclude="*.pyc" \
    --exclude="*.pyo" \
    --exclude=".git/" \
    --exclude=".github/" \
    --exclude="venv/" \
    --exclude="env/" \
    --exclude=".env.local" \
    --exclude=".env.development" \
    --exclude="nohup.out" \
    --exclude="*.log" \
    --exclude=".DS_Store" \
    --exclude="Thumbs.db" \
    --exclude="*.tmp" \
    --exclude="*.swp" \
    --exclude="*.swo" \
    --exclude=".vscode/settings.json" \
    --exclude=".idea/" \
    --exclude="coverage/" \
    --exclude=".nyc_output/" \
    --exclude="dist/assets/*.map" \
    --progress \
    "$PROJECT_DIR/" "$TEMP_DIR/"

echo ""
echo "📊 打包文件统计:"

# 显示各个主要目录的大小
echo "  前端源码: $(du -sh "$TEMP_DIR/frontend" 2>/dev/null | cut -f1 || echo "不存在")"
echo "  后端源码: $(du -sh "$TEMP_DIR/backend" 2>/dev/null | cut -f1 || echo "不存在")"
echo "  配置文件: $(du -sh "$TEMP_DIR"/*.conf "$TEMP_DIR"/*.sh "$TEMP_DIR"/*.md 2>/dev/null | awk '{sum+=$1} END {print sum "K"}' || echo "计算失败")"

# 创建部署说明文件
echo "📝 创建部署说明文件..."
cat > "$TEMP_DIR/DEPLOYMENT_INSTRUCTIONS.md" << 'EOF'
# Glam Cart Builder - 部署说明

## 📦 包含内容

此部署包包含以下内容：
- ✅ 前端源代码 (React + TypeScript)
- ✅ 后端源代码 (Python FastAPI)
- ✅ 数据库文件 (SQLite)
- ✅ 配置文件 (Nginx配置等)
- ✅ 启动脚本
- ✅ 产品数据文件
- ✅ 文档文件

## ❌ 已排除内容

- ❌ node_modules/ (JS包)
- ❌ __pycache__/ (Python缓存)
- ❌ 日志文件
- ❌ 临时文件
- ❌ 开发环境配置

## 🚀 部署步骤

### 1. 环境准备
```bash
# 安装 Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# 安装 Python 3.8+
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv

# 安装 Nginx
sudo apt-get install -y nginx
```

### 2. 部署前端
```bash
cd frontend
npm install
npm run build
```

### 3. 部署后端
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. 配置 Nginx
```bash
# 复制配置文件
sudo cp nginx-glam-cart.conf /etc/nginx/sites-available/glam-cart
sudo ln -s /etc/nginx/sites-available/glam-cart /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
```

### 5. 启动服务
```bash
# 启动后端
cd backend
source venv/bin/activate
python main.py

# 或使用启动脚本
./start-services.sh
```

### 6. 访问应用
- 主应用: http://your-domain
- API文档: http://your-domain/docs
- 健康检查: http://your-domain/health

## 📚 更多信息

请查看以下文件获取更多信息：
- README.md - 项目介绍和功能说明
- DEPLOYMENT_STATUS.md - 部署状态和配置详情
- CHANGELOG.md - 版本更新记录

## 🔧 故障排除

如果遇到问题，请检查：
1. 端口是否被占用
2. 权限是否正确
3. 依赖是否安装完整
4. 配置文件路径是否正确

EOF

# 创建压缩包
echo ""
echo "🗜️  创建压缩包..."
cd /tmp
tar -czf "$PACKAGE_NAME.tar.gz" "$PACKAGE_NAME"

# 计算压缩包大小
PACKAGE_SIZE=$(du -sh "$PACKAGE_NAME.tar.gz" | cut -f1)
TEMP_SIZE=$(du -sh "$PACKAGE_NAME" | cut -f1)

echo ""
echo "✅ 打包完成！"
echo ""
echo "📊 打包结果:"
echo "  📁 解压后大小: $TEMP_SIZE"
echo "  📦 压缩包大小: $PACKAGE_SIZE"
echo "  📍 压缩包位置: /tmp/$PACKAGE_NAME.tar.gz"
echo ""
echo "🚚 传输命令示例:"
echo "  # 通过 scp 传输到目标服务器"
echo "  scp /tmp/$PACKAGE_NAME.tar.gz user@target-server:/path/to/destination/"
echo ""
echo "  # 在目标服务器解压"
echo "  cd /path/to/destination"
echo "  tar -xzf $PACKAGE_NAME.tar.gz"
echo "  cd $PACKAGE_NAME"
echo "  cat DEPLOYMENT_INSTRUCTIONS.md"
echo ""
echo "💡 建议: 传输完成后请删除临时文件："
echo "  rm /tmp/$PACKAGE_NAME.tar.gz"
echo "  rm -rf /tmp/$PACKAGE_NAME"

# 清理临时目录
echo ""
echo "🧹 清理临时目录..."
rm -rf "$TEMP_DIR"

echo "🎉 所有操作完成！" 