# IQ Assessment Project（GitHub 拉取部署版）

娱乐性认知推理测评项目，支持 GitHub 拉取与 Docker Compose 一键部署。
**非标准化 IQ 诊断**，仅用于展示、课程设计、娱乐测试。

## 部署（服务器）
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
- 前台：`http://你的服务器IP/`
- 后台：`http://你的服务器IP/admin.html`

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
PUBLIC_BASE_URL=http://你的域名或IP
```

## 默认地址
- 前台：`/`
- 后台：`/admin.html`
- 健康检查：`/api/health`

## 推荐目录结构
```
iq-assessment-project/
├─ backend/            # FastAPI 后端
│  ├─ app/             # 业务代码
│  ├─ Dockerfile
│  └─ requirements.txt
├─ frontend/           # 静态前端（Nginx 托管）
│  ├─ index.html
│  ├─ admin.html
│  ├─ app.js
│  └─ styles.css
├─ nginx/              # 反向代理配置
│  └─ default.conf
├─ docs/               # 说明文档
│  └─ question-theory.md
├─ .env.example         # 环境变量模板
├─ docker-compose.yml
├─ install.sh
└─ update.sh
```

## 题库理论依据
详见：[`docs/question-theory.md`](docs/question-theory.md)

## 免责声明
项目输出的“参考 IQ”属于站内内部换算结果，仅用于娱乐展示，不等同于正式心理测验结论，不能替代教育、医疗或招聘中的专业评估。
