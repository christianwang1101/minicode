#!/bin/bash
echo "======================================"
echo "         一键启动前后端项目"
echo "======================================"
echo ""

# ===================== 启动前端 =====================
echo "正在启动前端 Vue..."
osascript -e 'tell app "Terminal" to do script "cd '"$(pwd)"'/frontend/Vue && npm run dev"'

# ===================== 启动后端 =====================
echo "正在启动后端 Python..."
osascript -e 'tell app "Terminal" to do script "cd '"$(pwd)"'/backend && source .venv/bin/activate && python start_api.py"'

echo ""
echo "启动完成！前端和后端窗口已分别打开"