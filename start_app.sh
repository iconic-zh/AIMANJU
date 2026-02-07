#!/bin/bash

echo "========================================"
echo "   正在初始化 AI 漫剧洗剧本智能体..."
echo "========================================"

# 0. 配置 Streamlit 环境变量以跳过交互式提示
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
export STREAMLIT_SERVER_HEADLESS=true

# 1. 安装依赖
echo ">>> [1/2] 正在安装/更新依赖库..."
python3 -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn

if [ $? -ne 0 ]; then
    echo "❌ 依赖安装失败，尝试使用官方源..."
    python3 -m pip install -r requirements.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org
fi

# 2. 启动 Streamlit 应用
echo ">>> [2/2] 正在启动可视化界面..."
echo "请在浏览器中访问下方显示的 URL (通常是 http://localhost:8501)"
python3 -m streamlit run app.py --server.address=localhost
