#!/usr/bin/env bash

# Resolve script directory and web root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WEB_DIR="${SCRIPT_DIR}/web"
PORT=8080

# Detect local LAN IP
LOCAL_IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo "127.0.0.1")

echo "========================================================"
echo " 📚 心理学导论 · 347 全章节复习刷题系统"
echo "========================================================"
echo " 本机访问地址:   http://localhost:${PORT}"
echo " 📱 手机局域网访问: http://${LOCAL_IP}:${PORT}"
echo "========================================================"
echo " 提示: 手机与电脑连接同一 Wi-Fi，即可在手机 Safari/Chrome 打开"
echo " 按 Ctrl + C 停止服务"
echo "========================================================"

exec python3 -m http.server "${PORT}" --directory "${WEB_DIR}"
