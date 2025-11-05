#!/bin/bash

# 实时语音 Bash 智能体启动脚本

echo "=================================="
echo "实时语音 Bash 智能体"
echo "=================================="
echo ""

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 Python 3"
    echo "请先安装 Python 3.8 或更高版本"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "未找到虚拟环境，正在创建..."
    python3 -m venv venv
    echo "✓ 虚拟环境创建完成"
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 检查依赖
if ! python -c "import agents" &> /dev/null; then
    echo "正在安装依赖..."
    pip install -r requirements.txt
    echo "✓ 依赖安装完成"
fi

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "警告: 未找到 .env 文件"
    echo "请复制 .env.example 到 .env 并设置 OPENAI_API_KEY"
    echo ""
    read -p "是否现在创建 .env 文件? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp .env.example .env
        echo "✓ 已创建 .env 文件"
        echo "请编辑 .env 文件，设置你的 OPENAI_API_KEY"
        echo ""
        read -p "按回车键继续..."
    else
        exit 1
    fi
fi

# 启动智能体
echo ""
echo "正在启动实时语音 Bash 智能体..."
echo ""
python voice_agent.py
