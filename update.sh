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

require_command git "未检测到 git，请先安装 Git。"
require_command docker "未检测到 docker，请先安装 Docker。"

if ! docker info >/dev/null 2>&1; then
  echo "[ERROR] Docker 已安装，但当前 daemon 不可用。请先启动 Docker 服务。"
  exit 1
fi

pick_compose_cmd

if [ ! -d .git ]; then
  echo "[ERROR] 当前目录不是 Git 仓库根目录，无法执行更新。"
  exit 1
fi

if [ ! -f .env ]; then
  echo "[ERROR] 未找到 .env。请先复制 .env.example 并完成配置。"
  exit 1
fi

mkdir -p data

branch="$(git rev-parse --abbrev-ref HEAD)"

echo "[INFO] 拉取远程更新..."
git pull --ff-only origin "$branch"

echo "[INFO] 重新构建并启动容器..."
"${compose_cmd[@]}" -f docker-compose.yml --project-directory "$SCRIPT_DIR" up -d --build

echo "[OK] 更新完成"
echo "[INFO] 查看状态: ${compose_cmd[*]} ps"
echo "[INFO] 查看日志: ${compose_cmd[*]} logs -f"
