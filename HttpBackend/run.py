#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动脚本
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app import init_database, app
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    # 初始化数据库
    init_database()

    # 获取端口号
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    debug = os.getenv('DEBUG', 'False').lower() == 'true'

    logger.info(f"Starting Topup HTTP API on {host}:{port}")
    logger.info(f"Debug mode: {debug}")

    # 运行应用
    app.run(
        host=host,
        port=port,
        debug=debug,
        use_reloader=False
    )