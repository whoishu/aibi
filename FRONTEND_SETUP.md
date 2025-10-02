# Frontend Setup Guide

快速开始指南 / Quick Start Guide

## 前置要求 (Prerequisites)

- Node.js 18+ and npm
- Python 3.8+
- Docker and Docker Compose (for backend dependencies)

## 快速启动 (Quick Start)

### 1. 启动后端依赖 (Start Backend Dependencies)

```bash
# 启动 OpenSearch 和 Redis
docker compose up -d

# 等待服务就绪（约 10-15 秒）
sleep 15

# 验证服务状态
docker compose ps
```

### 2. 初始化示例数据 (Initialize Sample Data)

```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 加载示例数据
python scripts/init_data.py
```

### 3. 构建前端 (Build Frontend)

```bash
cd frontend
npm install
npm run build
cd ..
```

### 4. 启动服务 (Start Service)

```bash
# 启动 FastAPI 服务
python app/main.py
```

服务启动后，访问：
- Frontend Demo: http://localhost:8000/demo
- API Documentation: http://localhost:8000/docs
- API Base: http://localhost:8000/api/v1

## 开发模式 (Development Mode)

如果你想修改前端代码并实时预览：

```bash
# 终端 1: 启动后端
python app/main.py

# 终端 2: 启动前端开发服务器
cd frontend
npm run dev
```

前端开发服务器会在 http://localhost:3000 运行，支持热重载。

## 常见问题 (Common Issues)

### 端口已被占用

如果端口 8000、9200 或 6379 已被占用，可以：
1. 修改 `config.yaml` 中的端口配置
2. 修改 `docker-compose.yml` 中的端口映射
3. 修改 `frontend/vite.config.ts` 中的代理配置

### 后端连接失败

检查：
1. 后端服务是否正常运行
2. OpenSearch 和 Redis 容器是否启动
3. 防火墙是否阻止了端口访问

### 前端构建失败

尝试：
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

## 构建优化 (Build Optimization)

### 生产环境构建

```bash
cd frontend
npm run build
```

构建文件会输出到 `frontend/dist/` 目录。

### 预览构建结果

```bash
cd frontend
npm run preview
```

## 自定义配置 (Customization)

### 修改 API 端点

编辑 `frontend/src/components/Autocomplete.tsx`：

```typescript
const Autocomplete: React.FC<AutocompleteProps> = ({
  apiUrl = '/api/v1/autocomplete',  // 修改这里
  userId = 'demo-user',
  limit = 10,
}) => {
  // ...
}
```

### 修改样式

编辑 `frontend/src/App.css` 来自定义颜色、字体等。

### 添加新功能

1. 在 `frontend/src/components/` 创建新组件
2. 在 `App.tsx` 中引入并使用
3. 运行 `npm run build` 重新构建

## 更多信息

- [Backend API Documentation](API.md)
- [Architecture Overview](ARCHITECTURE.md)
- [Frontend README](frontend/README.md)
