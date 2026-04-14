# IQ Assessment Project（GitHub 部署版）

面向大众体验的在线智力检测 Demo，重点展示数理推理、逻辑推理、言语理解与空间想象四个维度的综合认知表现。

本项目用于产品原型、课程设计、演示站点和轻量测评体验，不等同于正式标准化 IQ 测验、心理诊断或教育评估。

## 当前版本亮点

- 结果页改为 **综合认知表现指数（CPI）**、能力等级、百分位和四维能力画像为主展示
- 评分逻辑由正确率、难度加权、作答完整度、作答质量四部分组成
- 题库支持按维度与难度结构随机抽题
- 后台支持登录、概览统计、筛选记录、单次详情和 CSV 导出
- 启动时会执行轻量数据库字段补齐，兼容旧版 SQLite 数据库

## 访问地址

- 前台：`/iq/`
- 后台：`/iq/admin.html`
- 单次详情页：`/iq/admin-attempt.html?id=<attempt_id>`
- 健康检查：`/api/health`

## 部署方式（SQLite 单容器）

1. 准备环境：Git、Docker、Docker Compose
2. 拉取仓库并配置环境变量

```bash
cd /opt
git clone https://github.com/fengbule/IQtest.git iq-assessment-project
cd /opt/iq-assessment-project
cp .env.example .env
```

3. 修改 `.env` 中的密码和密钥

```env
DATABASE_URL=sqlite:////app/data/iq.db
JWT_SECRET=change_this_jwt_secret_to_a_long_random_string
ADMIN_USERNAME=admin
ADMIN_PASSWORD=ChangeThisAdminPassword123!
```

4. 启动服务

```bash
./install.sh
```

启动后访问：

- 前台：`http://你的服务器IP:8000/iq/`
- 后台：`http://你的服务器IP:8000/iq/admin.html`

## 更新项目

```bash
cd /opt/iq-assessment-project
./update.sh
```

## 本地开发

后端位于 `services/iq/backend/app`，前端静态页位于 `services/iq/frontend`。

题库与核心逻辑：

- `question_bank.py`：题库定义
- `question_selector.py`：固定结构随机抽题
- `scoring.py`：CPI、等级、百分位、可信度等评分逻辑
- `main.py`：公开接口、后台接口和导出接口

## 仓库结构

```text
iq-assessment-project/
├─ services/
│  └─ iq/
│     ├─ backend/
│     │  ├─ app/
│     │  ├─ Dockerfile
│     │  └─ requirements.txt
│     └─ frontend/
├─ docker-compose.yml
├─ .env.example
├─ install.sh
└─ update.sh
```

## 开发文档

仓库根目录已包含中文开发文档：

- `DEVELOPMENT_GUIDE.zh-CN.md`

## 免责声明

项目输出的“参考 IQ 区间”仅为站内解释型映射，用于帮助普通用户理解结果层级，不代表正式 IQ 测验结论，也不能替代医疗、教育、招聘或心理测评中的专业判断。
