# IQ Assessment Project（GitHub 拉取部署版）

娱乐性认知推理测评项目，支持 GitHub 拉取与 Docker Compose 一键部署。
**非标准化 IQ 诊断**，仅用于展示、课程设计、娱乐测试。

## 部署（极简 SQLite 单容器）
1) 依赖：Git、Docker、Docker Compose

2) 拉取与启动：
```bash
cd /opt
git clone https://github.com/fengbule/IQtest.git iq-assessment-project
cd /opt/iq-assessment-project
cp .env.example .env
nano .env
./install.sh
```

访问：
- IQ 测评前台：`http://你的服务器IP:8000/iq/`
- IQ 管理后台：`http://你的服务器IP:8000/admin.html`

## 更新
```bash
cd /opt/iq-assessment-project
./update.sh
```

## 环境变量（示例模板）
`.env.example` 为**模板示例**，请务必改为自己的强密码与密钥：
```env
DATABASE_URL=sqlite:////app/data/iq.db
JWT_SECRET=改成长随机字符串
ADMIN_USERNAME=admin
ADMIN_PASSWORD=改成你自己的后台密码
```

## 默认地址
- IQ 前台：`/iq/`
- IQ 后台：`/admin.html`
- IQ 健康检查：`/api/health`

## 推荐目录结构（极简）
```
iq-assessment-project/
├─ services/
│  └─ iq/
│     ├─ backend/        # FastAPI 后端（包含静态前端构建）
│     ├─ frontend/       # 直接挂载为静态资源
│     └─ docs/
├─ data/                 # SQLite 数据库文件
├─ .env.example
├─ docker-compose.yml    # 单容器编排
├─ install.sh
└─ update.sh
```

## 题库理论依据
详见：[`services/iq/docs/question-theory.md`](services/iq/docs/question-theory.md)

## 免责声明
项目输出的“参考 IQ”属于站内内部换算结果，仅用于娱乐展示，不等同于正式心理测验结论，不能替代教育、医疗或招聘中的专业评估。
