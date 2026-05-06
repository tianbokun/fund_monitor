#!/bin/bash
# 基金限购监控APP - 启动脚本

# 激活conda环境
source /opt/miniconda/etc/profile.d/conda.sh
conda activate fund_monitor

cd /home/tianbo/home/各类文件/投资/fund_monitor_app

echo "启动基金限购监控APP..."
echo "访问地址: http://localhost:8550"
echo "使用 Desktop 客户端: flet"  

# 启动APP (Web视图)
python main.py