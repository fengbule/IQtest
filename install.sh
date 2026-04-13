#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if ! command -v docker >/dev/null 2>&1; then
  echo "[ERROR] Docker 未安装"
  exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
  echo "[ERROR] Docker Compose 不可用"
  exit 1
fi

if [ ! -f .env ]; then
  cp .env.example .env
  echo "[INFO] 已生成 .env，请先修改其中的密码与密钥后再执行一次本脚本。"
  exit 0
fi

docker compose up -d --build

echo "[OK] 部署完成"
echo "前台: http://服务器IP:8000/iq/"
echo "后台: http://服务器IP:8000/admin.html"
echo "后续更新: ./update.sh"
