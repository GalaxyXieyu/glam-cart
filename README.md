# 🌟 Glam Cart Builder - 化妆品包装电商平台

一个现代化的化妆品包装展示与管理平台，提供完整的产品展示、轮播图管理和后台管理功能。

## ✨ 最新更新 (v1.2.0)

🎉 **轮播图管理功能完整上线！**

- ✅ 完整的轮播图CRUD管理系统
- ✅ 图片上传与实时预览功能
- ✅ 首页动态轮播图展示
- ✅ 管理员权限保护
- ✅ 响应式设计适配

查看详细更新内容：[CHANGELOG.md](./CHANGELOG.md)

## 🚀 功能特性

### 🎯 核心功能
- **产品展示系统**: 完整的化妆品包装产品展示
- **轮播图管理**: 动态轮播图创建、编辑、删除
- **管理员后台**: 安全的后台管理界面
- **响应式设计**: 完美适配桌面端和移动端

### 🛠️ 技术特性
- **现代化架构**: React + FastAPI + SQLAlchemy
- **类型安全**: 完整的TypeScript支持
- **安全认证**: JWT token认证机制
- **文件管理**: 安全的图片上传与管理

## 🏗️ 项目结构

```
glam-cart-builder/
├── frontend/          # React前端应用
│   ├── src/
│   │   ├── components/    # 可复用组件
│   │   ├── pages/         # 页面组件
│   │   ├── hooks/         # 自定义Hooks
│   │   ├── lib/           # 工具库
│   │   └── types/         # TypeScript类型定义
│   └── public/        # 静态资源
├── backend/           # FastAPI后端应用
│   ├── models.py      # 数据模型
│   ├── main.py        # 主应用文件
│   ├── auth.py        # 认证模块
│   └── file_utils.py  # 文件处理工具
└── test_images/       # 测试图片资源
```

## 🚀 快速开始

### 环境要求
- Node.js 18+
- Python 3.8+
- SQLite (开发环境)

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/GalaxyXieyu/glam-cart-builder.git
cd glam-cart-builder
```

2. **启动后端**
```bash
cd backend
pip install -r requirements.txt
python main.py
```

3. **启动前端**
```bash
cd frontend
npm install
npm run dev
```

4. **访问应用**
- 前端: http://localhost:8080
- 后端API: http://localhost:8000
- 管理后台: http://localhost:8080/admin

### 默认管理员账户
- 用户名: `admin`
- 密码: `admin123`

## 📱 功能演示

### 🖼️ 轮播图管理
- 访问 `/admin/carousels` 进行轮播图管理
- 支持拖拽上传图片
- 实时预览功能
- 排序和状态管理

### 🛍️ 产品展示
- 首页动态轮播图展示
- 产品筛选和搜索
- 详细产品信息页面
- 购物车功能

### 🔧 管理后台
- 安全的管理员登录
- 产品管理界面
- 轮播图管理
- 精选产品管理

## 🔧 API文档

### 轮播图API
```
GET    /api/carousels          # 获取轮播图列表
POST   /api/carousels          # 创建轮播图 (需认证)
PUT    /api/carousels/{id}     # 更新轮播图 (需认证)
DELETE /api/carousels/{id}     # 删除轮播图 (需认证)
```

### 认证API
```
POST   /api/auth/login         # 管理员登录
POST   /api/auth/verify        # 验证token
```

更多API文档请查看：[API_INTEGRATION_GUIDE.md](./frontend/API_INTEGRATION_GUIDE.md)

## 🎨 技术栈

### 前端
- **React 18** - 用户界面框架
- **TypeScript** - 类型安全
- **Tailwind CSS** - 样式框架
- **React Hook Form** - 表单管理
- **Zod** - 数据验证

### 后端
- **FastAPI** - 现代Python Web框架
- **SQLAlchemy** - ORM数据库操作
- **JWT** - 安全认证
- **Pillow** - 图片处理

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系方式

- **开发者**: GalaxyXieyu
- **邮箱**: galaxyxieyu@example.com
- **GitHub**: [GalaxyXieyu](https://github.com/GalaxyXieyu)

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者和用户！

---

⭐ 如果这个项目对您有帮助，请给我们一个星标！
