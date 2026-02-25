#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
状态管理器 - 管理任务状态和进度
"""

from enum import Enum
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = 'pending'
    RUNNING = 'running'
    SUCCESS = 'success'
    FAILED = 'failed'
    PAUSED = 'paused'
    CANCELLED = 'cancelled'
    TIMEOUT = 'timeout'


class StepStatus(Enum):
    """步骤状态枚举"""
    PENDING = 'pending'
    RUNNING = 'running'
    SUCCESS = 'success'
    FAILED = 'failed'
    TIMEOUT = 'timeout'
    CANCELLED = 'cancelled'
    SKIPPED = 'skipped'


class StateManager:
    """状态管理器"""

    def __init__(self):
        self._task_states = {}  # task_id -> TaskStatus
        self._step_states = {}  # (task_id, step_name) -> StepStatus
        self._task_locks = {}  # task_id -> lock
        self._step_locks = {}  # (task_id, step_name) -> lock

    def get_task_status(self, task_id):
        """获取任务状态"""
        return self._task_states.get(task_id, TaskStatus.PENDING)

    def set_task_status(self, task_id, status):
        """设置任务状态"""
        old_status = self._task_states.get(task_id)
        self._task_states[task_id] = status
        logger.info(f"Task {task_id} status changed: {old_status} -> {status}")

    def get_step_status(self, task_id, step_name):
        """获取步骤状态"""
        return self._step_states.get((task_id, step_name), StepStatus.PENDING)

    def set_step_status(self, task_id, step_name, status):
        """设置步骤状态"""
        old_status = self._step_states.get((task_id, step_name))
        self._step_states[(task_id, step_name)] = status
        logger.info(f"Task {task_id} step {step_name} status changed: {old_status} -> {status}")

    def is_task_running(self, task_id):
        """检查任务是否正在运行"""
        return self.get_task_status(task_id) == TaskStatus.RUNNING

    def is_step_running(self, task_id, step_name):
        """检查步骤是否正在运行"""
        return self.get_step_status(task_id, step_name) == StepStatus.RUNNING

    def can_start_task(self, task_id):
        """检查任务是否可以启动"""
        current_status = self.get_task_status(task_id)
        return current_status in [TaskStatus.PENDING, TaskStatus.PAUSED]

    def can_pause_task(self, task_id):
        """检查任务是否可以暂停"""
        return self.is_task_running(task_id)

    def can_resume_task(self, task_id):
        """检查任务是否可以恢复"""
        return self.get_task_status(task_id) == TaskStatus.PAUSED

    def can_cancel_task(self, task_id):
        """检查任务是否可以取消"""
        current_status = self.get_task_status(task_id)
        return current_status in [TaskStatus.PENDING, TaskStatus.RUNNING, TaskStatus.PAUSED]

    def remove_task(self, task_id):
        """移除任务状态"""
        if task_id in self._task_states:
            del self._task_states[task_id]

        # 移除该任务的所有步骤状态
        keys_to_remove = [k for k in self._step_states if k[0] == task_id]
        for key in keys_to_remove:
            del self._step_states[key]

        logger.info(f"Task {task_id} states removed")

    def get_all_step_statuses(self, task_id):
        """获取任务所有步骤的状态"""
        return {
            step_name: status.value
            for (tid, step_name), status in self._step_states.items()
            if tid == task_id
        }

    def clear_all(self):
        """清除所有状态"""
        self._task_states.clear()
        self._step_states.clear()
        logger.info("All states cleared")


# 全局状态管理器实例
state_manager = StateManager()