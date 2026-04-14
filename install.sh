#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

compose_cmd=()

pick_compose_cmd() {
  if docker compose version >/dev/null 2>&1; then
    compose_cmd=(docker compose)
    return
  fi
  if command -v docker-compose >/dev/null 2>&1; then
    compose_cmd=(docker-compose)
    return
  fi

  echo "[ERROR] Docker Compose 不可用，请先安装 docker compose 插件或 docker-compose。"
  exit 1
}

require_command() {
  local command_name="$1"
  local message="$2"
  if ! command -v "$command_name" >/dev/null 2>&1; then
    echo "[ERROR] ${message}"
    exit 1
  fi
}

env_value() {
  local key="$1"
  local fallback="$2"
  local value
  value="$(grep -E "^${key}=" .env 2>/dev/null | tail -n 1 | cut -d '=' -f 2- || true)"
  if [ -n "$value" ]; then
    printf '%s' "$value"
  else
    printf '%s' "$fallback"
  fi
}

require_command docker "未检测到 docker，请先安装 Docker。"

if ! docker info >/dev/null 2>&1; then
  echo "[ERROR] Docker 已安装，但当前 daemon 不可用。请先启动 Docker 服务。"
  exit 1
fi

pick_compose_cmd

if [ ! -f .env ]; then
  cp .env.example .env
  echo "[INFO] 未找到 .env，已自动从 .env.example 复制生成。"
  echo "[INFO] 你可以直接先部署，再按需修改 .env 中的密码、端口和域名。"
fi

mkdir -p data

if ! "${compose_cmd[@]}" -f docker-compose.yml --project-directory "$SCRIPT_DIR" config >/dev/null; then
  echo "[ERROR] docker-compose.yml 校验失败，请确认你正在仓库根目录执行，且 .env 配置正确。"
  exit 1
fi

echo "[INFO] 开始构建并启动容器..."
"${compose_cmd[@]}" -f docker-compose.yml --project-directory "$SCRIPT_DIR" up -d --build

host_bind="$(env_value HOST_BIND "0.0.0.0")"
host_port="$(env_value HOST_PORT "8000")"
public_base_url="$(env_value PUBLIC_BASE_URL "http://127.0.0.1:${host_port}")"

echo
echo "[OK] 部署完成"
echo "[INFO] 健康检查: ${public_base_url%/}/api/health"

if [ "$host_bind" = "127.0.0.1" ]; then
  echo "[INFO] 当前仅监听本机 ${host_bind}:${host_port}，适合反向代理或 1Panel 网站转发。"
  echo "[INFO] 前台地址: http://127.0.0.1:${host_port}/iq/"
  echo "[INFO] 后台地址: http://127.0.0.1:${host_port}/iq/admin.html"
else
  echo "[INFO] 前台地址: ${public_base_url%/}/iq/"
  echo "[INFO] 后台地址: ${public_base_url%/}/iq/admin.html"
fi

echo "[INFO] 查看状态: ${compose_cmd[*]} ps"
echo "[INFO] 查看日志: ${compose_cmd[*]} logs -f"
