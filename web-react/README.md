# FlowLine Web - React 版本

这是 FlowLine GPU 管理系统的 React 重构版本，使用现代化的前端技术栈。

## 技术栈

- **React 18** - 前端框架
- **TypeScript** - 类型安全
- **Ant Design 5** - UI 组件库
- **React Router 6** - 路由管理
- **Zustand** - 状态管理
- **Axios** - HTTP 客户端
- **Vite** - 构建工具

## 功能特性

- 🖥️ **GPU 监控** - 实时显示 GPU 状态、温度、利用率等信息
- 📋 **任务管理** - 创建、监控和管理 GPU 任务
- 📊 **日志查看** - 查看系统日志，支持筛选和下载
- ⚙️ **系统设置** - 配置系统参数和用户偏好

## 项目结构

```
web-react/
├── src/
│   ├── components/          # 可复用组件
│   │   └── Layout/         # 布局组件
│   ├── pages/              # 页面组件
│   ├── services/           # API 服务
│   ├── store/              # Zustand 状态管理
│   ├── types/              # TypeScript 类型定义
│   ├── App.tsx             # 主应用组件
│   ├── main.tsx            # 应用入口
│   └── index.css           # 全局样式
├── public/                 # 静态资源
├── package.json            # 项目配置
├── vite.config.ts          # Vite 配置
└── tsconfig.json           # TypeScript 配置
```

## 开发指南

### 安装依赖

```bash
cd web-react
npm install
```

### 启动开发服务器

```bash
npm run dev
```

应用将在 http://localhost:3000 启动

### 构建生产版本

```bash
npm run build
```

构建文件将输出到 `dist/` 目录

### 预览生产版本

```bash
npm run preview
```

## API 配置

应用通过 Vite 代理将 `/api` 请求转发到后端服务器 `http://localhost:5000`。

如果需要修改后端地址，请编辑 `vite.config.ts` 文件中的 proxy 配置。

## 页面说明

### GPU 页面 (`/gpu`)
- 显示所有 GPU 的实时状态
- 查看 GPU 详细信息
- 监控活跃任务和进程

### 任务页面 (`/tasks`)
- 查看所有任务列表
- 创建新任务
- 管理任务状态

### 日志页面 (`/logs`)
- 查看系统日志
- 按级别和关键词筛选
- 下载和清空日志

### 设置页面 (`/settings`)
- 通用设置
- GPU 监控配置
- 任务管理配置
- 日志管理配置

## 状态管理

使用 Zustand 进行状态管理，主要状态包括：

- `gpus` - GPU 信息列表
- `tasks` - 任务信息列表
- `isSystemRunning` - 系统运行状态
- `settings` - 系统设置

## 开发注意事项

1. 所有组件都使用 TypeScript，确保类型安全
2. 使用 Ant Design 组件保持 UI 一致性
3. API 调用统一通过 `services/api.ts` 管理
4. 状态管理使用 Zustand，避免 prop drilling
5. 路由使用 React Router 6 的新 API

## 部署

1. 构建生产版本：`npm run build`
2. 将 `dist/` 目录部署到 Web 服务器
3. 确保后端 API 服务正常运行
4. 配置反向代理将 `/api` 请求转发到后端服务