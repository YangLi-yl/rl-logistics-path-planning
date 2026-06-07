# 基于强化学习的智能物流路径规划系统

## 项目简介

本项目是一个面向校园物流配送场景的智能路径规划系统，旨在通过路径优化提高校园内物流配送效率。系统支持配送点管理、路径规划、地图可视化展示和历史记录查询等功能，并提供贪心算法与强化学习模型两种路径规划方式，便于对不同算法的规划效果进行对比分析。

项目采用前后端分离架构，后端负责路径规划接口、数据处理和历史记录存储，前端负责交互界面展示和地图路径可视化。系统结合高德地图 API，实现配送路线、配送顺序和规划结果的直观展示。

## 主要功能

* **智能路径规划**：支持贪心算法和 PPO 强化学习模型两种规划方式。
* **配送点管理**：支持添加、编辑和删除配送点信息。
* **路径可视化展示**：基于高德地图展示配送路线和配送顺序。
* **历史记录查询**：保存路径规划历史，便于查看和分析过往规划结果。
* **多算法对比**：可对比不同算法在总距离、配送时间等指标上的效果。
* **前后端分离**：后端提供 API 服务，前端提供可视化交互界面。

## 技术栈

### 后端

* Python
* FastAPI
* Uvicorn
* SQLite
* Stable-Baselines3
* Gymnasium
* NumPy

### 前端

* Vue 3
* Vite
* Element Plus
* ECharts
* Axios
* Vue Router
* 高德地图 API

### 算法

* 贪心算法
* PPO 强化学习模型

## 项目结构

```text
rl-logistics-path-planning
├── backend/                 # 后端服务模块
├── frontend/                # 前端界面模块
├── model/                   # 强化学习模型与训练相关文件
├── 完整启动操作指南.md        # 项目启动步骤说明
├── 用户使用指南.md            # 系统功能与使用说明
├── README.md                # 项目说明文档
└── .gitignore               # Git 忽略配置
```

## 环境要求

### 后端环境

* Python 3.8 及以上版本
* FastAPI
* Uvicorn
* Stable-Baselines3
* Gymnasium
* NumPy
* SQLite

### 前端环境

* Node.js 16 及以上版本
* npm 或 yarn
* Vue 3
* Vite

## 后端启动方式

进入后端目录：

```powershell
cd backend
```

创建并激活虚拟环境：

```powershell
python -m venv .venv
.venv\Scripts\activate
```

安装后端依赖：

```powershell
pip install fastapi uvicorn pydantic[email]
pip install stable-baselines3 gymnasium numpy
```

启动后端服务：

```powershell
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

后端服务启动后，可访问：

```text
http://localhost:8000/api/health
```

如果返回健康检查结果，说明后端服务运行正常。

## 前端启动方式

进入前端目录：

```powershell
cd frontend
```

安装前端依赖：

```powershell
npm install
```

配置高德地图 API Key：

```text
src/envs/AMAP_KEY.ts
```

将其中的 Key 替换为自己的高德地图 API 密钥。

启动前端项目：

```powershell
npm run dev
```

启动成功后，在浏览器中访问命令行输出的地址，通常为：

```text
http://localhost:5173/
```

## 基本使用流程

1. 启动后端服务。
2. 启动前端应用。
3. 在浏览器中打开系统页面。
4. 设置配送起点。
5. 添加配送点信息。
6. 选择路径规划算法。
7. 点击开始规划。
8. 在地图中查看规划路线、配送顺序和统计结果。
9. 在历史记录中查看过往规划结果。

## 文档说明

项目中包含两份详细说明文档：

* `完整启动操作指南.md`：包含从电脑开机、环境检查、后端启动、前端启动到系统验证的完整流程。
* `用户使用指南.md`：包含系统功能介绍、环境要求、操作流程、常见问题和使用建议。

## 项目说明

本项目为大学生创新创业训练项目，主要用于探索强化学习算法在校园物流配送路径规划中的应用。系统通过结合传统路径规划算法与强化学习模型，实现对校园配送路径的智能规划和可视化展示。

本项目主要用于课程实践、科研训练和学习展示，实际应用时仍需结合真实配送场景进一步优化模型效果、数据规模和系统稳定性。
