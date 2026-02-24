#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通知服务 - 处理WebSocket通知
"""

from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# 这些函数将在app模块中实现
def emit_progress_update(task_id, progress):
    """发送进度更新"""
    # 这里只是占位符，实际实现在app模块中
    logger.debug(f"Progress update for task {task_id}: {progress}")

def emit_status_update(task_id, status, message=None):
    """发送状态更新"""
    # 这里只是占位符，实际实现在app模块中
    logger.debug(f"Status update for task {task_id}: {status}")