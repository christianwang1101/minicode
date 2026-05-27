#!/usr/bin/env zsh
# shellcheck shell=zsh

set -euo pipefail

# Ensure UTF-8 locale
export LANG=en_US.UTF-8

base_dir="$(cd "$(dirname "$0")" && pwd)"

echo "======================================"
echo "         一键启动前后端项目"
echo "======================================"
echo

echo "按 Enter 继续..." && read -r

echo
echo "正在启动前端 Vue..."
if [[ "$OSTYPE" == darwin* ]]; then
	osascript -e 'tell application "Terminal" to do script "cd \"'"$base_dir"'\"/frontend/Vue; npm run dev"'
else
	(cd "$base_dir/frontend/Vue" && npm run dev) &
fi

echo
echo "正在启动后端 Python..."
if [[ "$OSTYPE" == darwin* ]]; then
	osascript -e 'tell application "Terminal" to do script "cd \"'"$base_dir"'\"/backend; if [ -f .venv/bin/activate ]; then source .venv/bin/activate; fi; python start_api.py"'
else
	(
		cd "$base_dir/backend" || exit 1
		if [ -f .venv/bin/activate ]; then
			source .venv/bin/activate
		fi
		python start_api.py
	) &
fi

echo
echo "启动命令已执行。"
echo "如果在 macOS 上，前后端会在新的 Terminal 窗口中打开。"
echo
exit 0