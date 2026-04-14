# IQtest

一个面向大众体验的在线智力检测 Demo，支持：

- 前台测评页
- CPI / 参考 IQ 值 / 参考 IQ 区间展示
- 四维能力画像
- 管理员后台
- 作答记录详情
- CSV 导出
- Docker / 1Panel 部署

本项目用于 Demo、课程设计、产品原型和轻量体验，不等同于正式标准化 IQ 测验、心理诊断或教育评估。

## 已修复的部署问题

- 修复了容器内前端静态目录路径错误，容器启动后 `/iq/`、`/iq/admin.html`、`/api/health` 可正常访问
- Dockerfile 与 FastAPI 静态目录路径统一为 `/app/frontend`
- `docker-compose.yml` 支持通过环境变量覆盖端口、数据目录、build context 和 Dockerfile 路径
- `install.sh` / `update.sh` 增强了环境检测、`.env` 自动生成、`data` 目录创建和错误提示
- 新增 `services/iq/.dockerignore`，减少无关文件进入镜像构建上下文

## 访问路径

- 前台：`/iq/`
- 后台：`/iq/admin.html`
- 单次详情：`/iq/admin-attempt.html?id=<attempt_id>`
- 健康检查：`/api/health`

## 目录要求

**必须在仓库根目录执行 `docker compose`。**

也就是下面这个目录：

```text
IQtest/
├─ docker-compose.yml
├─ .env
├─ install.sh
├─ update.sh
└─ services/
   └─ iq/
```

如果把 `docker-compose.yml` 单独拎到别的目录，再直接使用相对路径构建，`build context` 很容易失效。

## 环境变量

请把配置写进 **文件 `.env`**，不要只在当前 shell 里 `export` 或 `set` 一次。

示例：

```env
DATABASE_URL=sqlite:////app/data/iq.db
JWT_SECRET=change_this_jwt_secret_to_a_long_random_string
ADMIN_USERNAME=admin
ADMIN_PASSWORD=ChangeThisAdminPassword123!
PUBLIC_BASE_URL=http://127.0.0.1:8000

HOST_BIND=0.0.0.0
HOST_PORT=8000

IQ_BUILD_CONTEXT=./services/iq
IQ_DOCKERFILE=./backend/Dockerfile
IQ_DATA_DIR=./data
```

说明：

- `HOST_BIND=0.0.0.0`：对外监听
- `HOST_BIND=127.0.0.1`：仅本机监听，适合 Nginx / OpenResty / 1Panel 网站反向代理
- `HOST_PORT=8741`：可以改成 `127.0.0.1:8741:8000` 这种部署方式

## 1. 普通命令行部署

### 1.1 拉取项目

```bash
cd /opt
git clone https://github.com/fengbule/IQtest.git
cd /opt/IQtest
```

### 1.2 准备 `.env`

```bash
cp .env.example .env
nano .env
```

如果你不想手工先复制，也可以直接运行：

```bash
bash install.sh
```

脚本会自动从 `.env.example` 生成 `.env`。

### 1.3 执行安装

推荐：

```bash
bash install.sh
```

如果你想直接执行：

```bash
chmod +x install.sh update.sh
./install.sh
```

如果 `./install.sh` 报 `Permission denied`，先执行：

```bash
chmod +x install.sh update.sh
```

或者直接用：

```bash
bash install.sh
```

### 1.4 部署后检查

```bash
docker compose ps
docker compose logs -f
curl http://127.0.0.1:8000/api/health
```

如果你把端口改成了 `HOST_BIND=127.0.0.1` 和 `HOST_PORT=8741`，则检查命令改为：

```bash
curl http://127.0.0.1:8741/api/health
```

### 1.5 默认访问示例

公网直接访问示例：

- `http://你的服务器IP:8000/iq/`
- `http://你的服务器IP:8000/iq/admin.html`

仅本机监听示例：

- `http://127.0.0.1:8741/iq/`
- `http://127.0.0.1:8741/iq/admin.html`

## 2. 1Panel 部署

### 2.1 推荐方式

最稳的方式是：

1. 先在服务器上把项目完整克隆到固定目录
2. **不要把 compose 文件单独拎出来**
3. 让 1Panel 使用仓库根目录中的 `docker-compose.yml`

推荐目录：

```bash
/opt/IQtest
```

### 2.2 1Panel 用户怎么放置目录

推荐结构：

```text
/opt/IQtest
├─ docker-compose.yml
├─ .env
├─ install.sh
├─ update.sh
└─ services/iq
```

也就是说：

- 项目源码目录放在 `/opt/IQtest`
- `docker-compose.yml` 也放在 `/opt/IQtest`
- `docker compose` 的执行根目录就是 `/opt/IQtest`

### 2.3 如果 1Panel 的 compose 文件必须单独存放

如果 1Panel 编排界面把 compose 文件保存到了别的位置，你需要把下面三个变量改成**绝对路径**：

```env
IQ_BUILD_CONTEXT=/opt/IQtest/services/iq
IQ_DOCKERFILE=/opt/IQtest/services/iq/backend/Dockerfile
IQ_DATA_DIR=/opt/IQtest/data
```

否则 `build context` 很容易失效，导致构建失败。

### 2.4 1Panel 端口建议

更推荐在 1Panel 里使用仅本机监听，然后用网站 / 反向代理转发：

```env
HOST_BIND=127.0.0.1
HOST_PORT=8741
PUBLIC_BASE_URL=https://你的域名
```

这样容器只监听本机：

```text
127.0.0.1:8741 -> 容器 8000
```

然后由 1Panel 网站、Nginx 或 OpenResty 反代到：

```text
http://127.0.0.1:8741
```

## 3. 反向代理示例

### 3.1 Nginx / OpenResty

```nginx
location / {
    proxy_pass http://127.0.0.1:8741;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

### 3.2 1Panel 网站

- 站点域名指向你的服务器
- 反向代理目标填：`http://127.0.0.1:8741`
- 之后访问：
  - `https://你的域名/iq/`
  - `https://你的域名/iq/admin.html`

## 4. 更新项目

```bash
cd /opt/IQtest
bash update.sh
```

更新后建议检查：

```bash
docker compose ps
docker compose logs -f
curl http://127.0.0.1:8000/api/health
```

## 5. 本地开发

后端目录：

- `services/iq/backend/app`

前端目录：

- `services/iq/frontend`

关键文件：

- `services/iq/backend/app/main.py`
- `services/iq/backend/app/scoring.py`
- `services/iq/backend/app/question_selector.py`
- `services/iq/backend/app/migrations.py`
- `services/iq/backend/Dockerfile`
- `docker-compose.yml`
- `install.sh`
- `update.sh`

## 6. 免责声明

结果页中的“参考 IQ 值”和“参考 IQ 区间”属于站内解释型映射，用于帮助普通用户理解结果层级，不代表正式 IQ 测验结论，也不能替代医疗、教育、招聘或心理测评中的专业判断。
