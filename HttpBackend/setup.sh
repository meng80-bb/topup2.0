#!/bin/bash
# Topup HTTP API 快速启动脚本

echo "=========================================="
echo "Topup HTTP API - 快速启动"
echo "=========================================="

# 检查Python版本
echo "1. 检查Python版本..."
python3 --version

# 创建虚拟环境（可选）
read -p "是否创建虚拟环境? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "2. 创建虚拟环境..."
    python3 -m venv venv
    source venv/bin/activate
    echo "   虚拟环境已激活"
fi

# 安装依赖
echo "3. 安装依赖..."
pip install -r requirements.txt

# 检查环境变量文件
if [ ! -f .env ]; then
    echo "4. 创建环境变量文件..."
    cp .env.example .env
    echo "   请编辑 .env 文件设置必要的环境变量"
    echo "   特别是 SSH_PASS_LXLOGIN 和 SSH_PASS_BESLOGIN"
else
    echo "4. 环境变量文件已存在"
fi

# 创建必要的目录
echo "5. 创建必要的目录..."
mkdir -p logs
mkdir -p uploads
mkdir -p downloads

echo ""
echo "=========================================="
echo "安装完成！"
echo "=========================================="
echo ""
echo "请执行以下步骤："
echo "1. 编辑 .env 文件设置环境变量"
echo "2. 运行启动命令: python run.py"
echo ""
echo "API将运行在: http://0.0.0.0:5000"
echo ""