#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API 路由包
"""

from flask import Blueprint

# 创建蓝图
tasks_bp = Blueprint('tasks', __name__)
workflows_bp = Blueprint('workflows', __name__)
executions_bp = Blueprint('executions', __name__)
logs_bp = Blueprint('logs', __name__)