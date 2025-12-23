# Glam Cart 项目梳理与优化建议

## 现状概览
- 数据库默认使用 SQLite，`DATABASE_URL` 未设置时回退到 `sqlite:///./glam_cart.db`。参考 `backend/database.py:9`。
- 图片存储在后端本地 `static` 目录并通过 `/static` 对外提供，后端启动时确保目录存在并挂载静态路由。参考 `backend/main.py:60`、`backend/file_utils.py:21`。
- 前端会把数据库里的相对路径转成 `/static/...` 访问，并根据用途/网络情况选择尺寸与 WebP/JPG，组件有懒加载和 `srcset`。参考 `frontend/src/lib/api.ts:157`、`frontend/src/utils/imageUtils.ts:72`、`frontend/src/components/OptimizedImage.tsx:38`。
- Nginx 负责前端 `dist` 目录与 `/static` 反代，且已经对静态资源设置长缓存/开启 gzip。参考 `nginx-glam-cart.conf:42`、`nginx-glam-cart.conf:86`、`nginx-glam-cart.conf:140`。

## 脚本清理建议

### 建议保留（运行/部署会用到）
- `manage-services.sh:6`：统一启动/停止后端与 Nginx（适合当前 /data 环境）。
- `backend/start_backend.sh:9` + `backend/stop_backend.sh:8`：仅后端启动/停止的简化脚本。
- `backend/run.py:13`：后端启动入口，CI 或 systemd 也可直接调用。
- `package-for-deployment.sh:1`：手工打包脚本（如果还在用离线打包流程）。
- `backend/tests/run_tests.py:37`：后端一键启动 + pytest 测试脚本（CI 可以直接复用）。

### 可归档/删除（一次性或数据处理）
- `backend/import_products.py:1`：Excel 批量导入（历史数据导入一次即可）。
- `backend/import_cde_products.py:1`：C/D/E/F/I/U/Y 系列导入脚本（一次性）。
- `backend/clean_categories.py:1`：分类字段清洗脚本（一次性）。
- `backend/migrate_add_image_sort_order.py:1`：SQLite 迁移脚本（迁移完成即可归档）。
- `backend/test_image_sort.py:1`：图片排序手工测试脚本（一次性）。
- `backend/verify_import.py:1`：导入后验证脚本（一次性）。
- `backend/create_admin.py:1`：手工创建管理员；但启动时已经自动创建管理员。参考 `backend/main.py:68`。

### 可能过时/环境特定（建议删除或重写）
- `start-services.sh:8`：硬编码 `/home/devbox/project` 路径且依赖 sudo。
- `stop-services.sh:1`：与 `start-services.sh` 配套，主要用于旧环境。
- `entrypoint.sh:11`：硬编码路径并自动 apt 安装，适合旧容器/云开发环境。
- `package-for-deployment.sh:127`：说明仍引用 `./start-services.sh`，若保留脚本建议同步更新说明。

## 数据库梳理
- 运行时数据库默认是 SQLite 文件 `glam_cart.db`（由 `DATABASE_URL` 决定），当前没有看到标准化迁移体系。参考 `backend/database.py:9`。
- 手工迁移脚本会自动生成 `glam_cart_backup_YYYYMMDD_*.db` 备份。参考 `backend/migrate_add_image_sort_order.py:12`。
- 如果准备做 CI/CD 或多实例部署，建议提前规划：从 SQLite 迁移到 PostgreSQL/MySQL，并补齐 Alembic 迁移流程（现有依赖已包含 alembic）。参考 `backend/requirements.txt:1`。

## CI/CD 准备清单（不改代码的前置事项）
- 构建命令：前端 `npm run build` 与 `npm run lint`，后端 `pip install -r requirements.txt`。参考 `frontend/package.json:6`、`backend/requirements.txt:1`。
- 测试命令：后端可以用 `backend/tests/run_tests.py` 一键启动 + pytest。参考 `backend/tests/run_tests.py:37`。
- 环境变量整理：后端读取 `HOST/PORT/DEBUG` 与 `DATABASE_URL`，前端读取 `VITE_API_BASE_URL`。参考 `backend/run.py:15`、`backend/database.py:9`、`frontend/src/lib/api.ts:6`。
- 产物交付：Nginx 直接指向 `frontend/dist`，所以 CI/CD 需要产出该目录并同步到服务器。参考 `nginx-glam-cart.conf:42`。
- 健康检查：后端有 `/health`，可用于部署后验证。参考 `backend/main.py:168`。
- 部署方式建议（按优先级）：1) systemd + Nginx；2) 容器化（Dockerfile + compose）；3) 使用现有打包脚本。

## 图片存储与加速建议
- 现状：图片写入本地 `static/images`，前端通过 `/static/...` 访问；前端已做多尺寸/格式和懒加载。参考 `backend/file_utils.py:21`、`backend/main.py:60`、`frontend/src/utils/imageUtils.ts:72`、`frontend/src/components/OptimizedImage.tsx:38`。
- 短期改进（不引入对象存储）：让 Nginx 直接 `alias` 后端 `static` 目录（代替反代 FastAPI），并为 `/static` 设置缓存头；这能显著减少后端压力并提升图片加载。参考 `nginx-glam-cart.conf:86`。
- 中长期方案（推荐）：接入对象存储（OSS/S3/MinIO）+ CDN；数据库只存 URL/元数据；上传后由存储服务生成多尺寸/格式（或继续在后端生成后上传）。前端已有 WebP + srcset 适配逻辑，可直接复用。参考 `frontend/src/utils/imageUtils.ts:72`。

## 构建与性能优化方案建议
- 静态资源压缩与缓存：Nginx 已开启 gzip，可考虑补充 brotli 与 `Cache-Control`/`immutable` 覆盖 `/static`。参考 `nginx-glam-cart.conf:49`、`nginx-glam-cart.conf:140`。
- 前端构建优化：维持 Vite build + 产出 hash 资源；可用 rollup 拆分 admin 入口和公共依赖，减少首屏 bundle。参考 `frontend/package.json:6`。
- 图片与首屏：继续使用现有 `srcset` 与懒加载；对首屏大图可提前 preload，对非关键图片延迟加载（现有组件已支持）。参考 `frontend/src/components/OptimizedImage.tsx:90`。
- 后端响应：可给图片/列表接口添加缓存或 ETag，减少重复拉取；可视情况加 CDN/反代缓存。
