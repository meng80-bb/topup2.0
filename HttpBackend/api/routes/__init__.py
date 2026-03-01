#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API 路由包
"""

# 从各个路由模块导入蓝图
from .tasks import tasks_bp
from .workflows import workflows_bp
from .executions import executions_bp
from .logs import logs_bp
from .downloads import downloads_bp