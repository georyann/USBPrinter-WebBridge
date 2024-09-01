#!/bin/bash
# 安装必需的软件包
sudo yum install -y python3 python3-pip cups
# 安装Python虚拟环境工具
sudo pip3 install virtualenv
# 创建并激活虚拟环境
python3 -m venv venv
source venv/bin/activate
# 安装Python依赖包
pip install flask pycups
# 确保CUPS服务正在运行
sudo systemctl start cups
sudo systemctl enable cups
# 运行Flask应用
export FLASK_APP=app.py
flask run --host=0.0.0.0 --port=5000
