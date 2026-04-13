# IQ Assessment Project（GitHub 拉取部署版）

娱乐性认知推理测评项目，支持 GitHub 拉取与 Docker Compose 一键部署。
**非标准化 IQ 诊断**，仅用于展示、课程设计、娱乐测试。

## 部署（服务器，统一 Docker Compose）
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
- IQ 测评前台：`http://你的服务器IP/iq/`
- IQ 管理后台：`http://你的服务器IP/iq/admin.html`

## 更新
```bash
cd /opt/iq-assessment-project
./update.sh
```

## 环境变量（示例模板）
`.env.example` 与 `backend/app/config.py` 里的值为**模板示例**，请务必改为自己的强密码与密钥：
```env
POSTGRES_PASSWORD=改成强密码
DATABASE_URL=postgresql+psycopg2://iq_user:改成强密码@db:5432/iq_app
JWT_SECRET=改成长随机字符串
ADMIN_USERNAME=admin
ADMIN_PASSWORD=改成你自己的后台密码
PUBLIC_BASE_URL=http://你的域名或IP/iq
```

## 默认地址
- IQ 前台：`/iq/`
- IQ 后台：`/iq/admin.html`
- IQ 健康检查：`/iq/api/health`

## 推荐目录结构（可扩展多项目）
```
iq-assessment-project/
├─ services/
│  ├─ iq/               # 当前 IQ 测评项目
│  │  ├─ backend/        # FastAPI 后端
│  │  ├─ frontend/       # 静态前端（Nginx 托管）
│  │  ├─ nginx/          # Nginx 子项目配置
│  │  └─ docs/           # 项目文档
│  └─ eq/                # 未来新增项目示例（可按需新增）
│     ├─ backend/
│     ├─ frontend/
│     └─ nginx/
├─ .env.example          # 环境变量模板
├─ docker-compose.yml    # 统一编排
├─ install.sh
└─ update.sh
```

## 新增测试项目指引
1) 在 `services/` 下新增项目目录（如 `eq`）。
2) 为该项目准备 `backend/`、`frontend/`、`nginx/`。
3) 在 `docker-compose.yml` 中新增对应服务。
4) 在 Nginx 配置中新增路由前缀（例如 `/eq/`）。

## 题库理论依据
详见：[`services/iq/docs/question-theory.md`](services/iq/docs/question-theory.md)

## 免责声明
项目输出的“参考 IQ”属于站内内部换算结果，仅用于娱乐展示，不等同于正式心理测验结论，不能替代教育、医疗或招聘中的专业评估。
