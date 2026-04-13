#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if ! command -v git >/dev/null 2>&1; then
  echo "[ERROR] git 未安装"
  exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "[ERROR] Docker 未安装"
  exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
  echo "[ERROR] Docker Compose 不可用"
  exit 1
fi

if [ ! -d .git ]; then
  echo "[ERROR] 当前目录不是 Git 仓库，无法执行 git pull"
  exit 1
fi

if [ ! -f .env ]; then
  echo "[ERROR] 未找到 .env，请先复制 .env.example 为 .env 并完成配置"
  exit 1
fi

branch=$(git rev-parse --abbrev-ref HEAD)

echo "[INFO] 拉取远程更新..."
git pull --ff-only origin "$branch"

echo "[INFO] 重建并重启服务..."
docker compose up -d --build

echo "[OK] 更新完成"
