#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务执行引擎 - 管理整个任务的执行流程
"""

import time
import threading
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

from models.database import db
from models.task import Task, TaskExecution, StepOutput, TaskLog
from core.workflow_parser import workflow_parser
from core.step_executor import StepExecutor
from core.state_manager import state_manager, TaskStatus
from topup_ssh import TopupSSH
from services.notification_service import emit_progress_update, emit_status_update

logger = logging.getLogger(__name__)


class TaskEngine:
    """任务执行引擎"""

    def __init__(self, max_workers: int = 3):
        """
        初始化任务引擎

        Args:
            max_workers: 最大工作线程数
        """
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.active_tasks = {}  # task_id -> future
        self.running_locks = {}  # task_id -> threading.Lock
        self.ssh_clients = {}  # task_id -> TopupSSH

    def start_task(self, task_id: int) -> Dict[str, Any]:
        """
        启动任务执行

        Args:
            task_id: 任务ID

        Returns:
            执行结果
        """
        task = Task.query.get(task_id)
        if not task:
            return {'success': False, 'error': 'Task not found'}

        # 检查任务状态
        if not state_manager.can_start_task(task_id):
            return {'success': False, 'error': f'Cannot start task in {task.status} state'}

        # 检查是否已有任务在运行
        if task_id in self.active_tasks:
            return {'success': False, 'error': 'Task is already running'}

        try:
            # 创建任务锁
            self.running_locks[task_id] = threading.Lock()

            # 创建SSH连接
            ssh_client = TopupSSH()
            if not ssh_client.connect():
                return {'success': False, 'error': 'Failed to connect to SSH server'}

            self.ssh_clients[task_id] = ssh_client

            # 启动任务线程
            future = self.executor.submit(self._execute_task, task_id)
            self.active_tasks[task_id] = future

            # 更新任务状态
            state_manager.set_task_status(task_id, TaskStatus.RUNNING)
            task.status = 'running'
            task.started_at = datetime.now(datetime.timezone.utc)
            db.session.commit()

            # 发送状态更新
            emit_status_update(task_id, 'running', 'Task started')

            return {'success': True, 'message': 'Task started', 'task_id': task_id}

        except Exception as e:
            logger.error(f"Failed to start task {task_id}: {str(e)}")
            return {'success': False, 'error': str(e)}

    def pause_task(self, task_id: int) -> Dict[str, Any]:
        """
        暂停任务

        Args:
            task_id: 任务ID

        Returns:
            执行结果
        """
        task = Task.query.get(task_id)
        if not task:
            return {'success': False, 'error': 'Task not found'}

        if not state_manager.can_pause_task(task_id):
            return {'success': False, 'error': f'Cannot pause task in {task.status} state'}

        try:
            # 实现暂停逻辑
            state_manager.set_task_status(task_id, TaskStatus.PAUSED)
            task.status = 'paused'
            db.session.commit()

            emit_status_update(task_id, 'paused', 'Task paused')
            return {'success': True, 'message': 'Task paused'}

        except Exception as e:
            logger.error(f"Failed to pause task {task_id}: {str(e)}")
            return {'success': False, 'error': str(e)}

    def resume_task(self, task_id: int) -> Dict[str, Any]:
        """
        恢复任务

        Args:
            task_id: 任务ID

        Returns:
            执行结果
        """
        task = Task.query.get(task_id)
        if not task:
            return {'success': False, 'error': 'Task not found'}

        if not state_manager.can_resume_task(task_id):
            return {'success': False, 'error': f'Cannot resume task in {task.status} state'}

        try:
            # 实现恢复逻辑
            state_manager.set_task_status(task_id, TaskStatus.RUNNING)
            task.status = 'running'
            db.session.commit()

            emit_status_update(task_id, 'running', 'Task resumed')
            return {'success': True, 'message': 'Task resumed'}

        except Exception as e:
            logger.error(f"Failed to resume task {task_id}: {str(e)}")
            return {'success': False, 'error': str(e)}

    def cancel_task(self, task_id: int) -> Dict[str, Any]:
        """
        取消任务

        Args:
            task_id: 任务ID

        Returns:
            执行结果
        """
        task = Task.query.get(task_id)
        if not task:
            return {'success': False, 'error': 'Task not found'}

        if not state_manager.can_cancel_task(task_id):
            return {'success': False, 'error': f'Cannot cancel task in {task.status} state'}

        try:
            # 取消正在执行的任务
            if task_id in self.active_tasks:
                future = self.active_tasks[task_id]
                future.cancel()
                del self.active_tasks[task_id]

            # 关闭SSH连接
            if task_id in self.ssh_clients:
                self.ssh_clients[task_id].close()
                del self.ssh_clients[task_id]

            # 更新任务状态
            state_manager.set_task_status(task_id, TaskStatus.CANCELLED)
            task.status = 'cancelled'
            task.completed_at = datetime.utcnow()
            db.session.commit()

            emit_status_update(task_id, 'cancelled', 'Task cancelled')
            return {'success': True, 'message': 'Task cancelled'}

        except Exception as e:
            logger.error(f"Failed to cancel task {task_id}: {str(e)}")
            return {'success': False, 'error': str(e)}

    def get_task_progress(self, task_id: int) -> Dict[str, Any]:
        """
        获取任务进度

        Args:
            task_id: 任务ID

        Returns:
            进度信息
        """
        task = Task.query.get(task_id)
        if not task:
            return {'success': False, 'error': 'Task not found'}

        # 获取所有步骤的状态
        step_statuses = state_manager.get_all_step_statuses(task_id)
        total_steps = len(step_statuses)
        completed_steps = sum(1 for status in step_statuses.values() if status == 'success')
        failed_steps = sum(1 for status in step_statuses.values() if status == 'failed')

        progress = 0
        if total_steps > 0:
            progress = int((completed_steps / total_steps) * 100)

        return {
            'success': True,
            'task_id': task_id,
            'progress_percentage': progress,
            'total_steps': total_steps,
            'completed_steps': completed_steps,
            'failed_steps': failed_steps,
            'current_step': task.current_step,
            'step_statuses': step_statuses
        }

    def _execute_task(self, task_id: int):
        """
        执行任务的核心逻辑

        Args:
            task_id: 任务ID
        """
        task = Task.query.get(task_id)
        if not task:
            logger.error(f"Task {task_id} not found")
            return

        try:
            # 更新开始时间
            task.started_at = datetime.utcnow()
            db.session.commit()

            # 获取工作流配置
            config = workflow_parser.load_workflow(task.workflow.name)
            steps = workflow_parser.get_steps_in_order(task.workflow.name)

            total_steps = len(steps)
            completed_steps = 0

            for i, step_config in enumerate(steps, 1):
                if state_manager.get_task_status(task_id) != TaskStatus.RUNNING:
                    logger.info(f"Task {task_id} cancelled, stopping execution")
                    break

                step_name = step_config['id']
                step_order = step_config['order']

                # 创建执行记录
                execution = TaskExecution(
                    task_id=task_id,
                    step_name=step_name,
                    step_display_name=step_config.get('display_name', step_name),
                    step_order=step_order,
                    status='running',
                    start_time=datetime.utcnow()
                )
                db.session.add(execution)
                db.session.commit()

                # 执行步骤
                step_executor = StepExecutor(self.ssh_clients[task_id])
                result = step_executor.execute_step(
                    task_id=task_id,
                    step_config=step_config,
                    parameters=self._get_task_parameters(task),
                    step_order=step_order,
                    step_name=step_name
                )

                # 更新执行记录
                execution.status = 'success' if result['success'] else 'failed'
                execution.end_time = datetime.utcnow()
                execution.duration_seconds = result.get('duration_seconds', 0)
                execution.output_summary = result.get('output_summary', '')
                execution.error_details = result.get('error_details', '')
                db.session.commit()

                # 记录日志
                self._log_step_execution(task_id, execution, result)

                # 更新进度
                completed_steps = i
                progress = int((completed_steps / total_steps) * 100)
                task.progress_percentage = progress
                task.current_step = step_name
                db.session.commit()

                # 发送进度更新
                emit_progress_update(task_id, progress)

                # 更新状态管理器
                status = state_manager.StepStatus.SUCCESS if result['success'] else state_manager.StepStatus.FAILED
                state_manager.set_step_status(task_id, step_name, status)

                # 如果步骤失败，检查是否需要停止
                if not result['success']:
                    if step_config.get('on_failure', {}).get('action') == 'stop':
                        logger.error(f"Step {step_name} failed, stopping execution")
                        break

            # 完成任务
            self._complete_task(task_id)

        except Exception as e:
            logger.error(f"Error executing task {task_id}: {str(e)}")
            self._fail_task(task_id, str(e))
        finally:
            # 清理资源
            self._cleanup_task_resources(task_id)

    def _get_task_parameters(self, task: Task) -> Dict[str, Any]:
        """
        获取任务参数

        Args:
            task: 任务实例

        Returns:
            参数字典
        """
        parameters = {}

        # 从数据库获取参数
        for param in task.parameters:
            parameters[param.param_name] = param.param_value

        # 添加基本信息
        parameters.update({
            'date_param': task.date_param,
            'task_id': task.id,
            'user_id': task.user_id
        })

        return parameters

    def _complete_task(self, task_id: int):
        """
        完成任务

        Args:
            task_id: 任务ID
        """
        task = Task.query.get(task_id)
        if task:
            task.status = 'success'
            task.completed_at = datetime.utcnow()
            task.progress_percentage = 100
            task.current_step = None
            db.session.commit()

            state_manager.set_task_status(task_id, TaskStatus.SUCCESS)

            emit_status_update(task_id, 'success', 'Task completed successfully')
            logger.info(f"Task {task_id} completed successfully")

    def _fail_task(self, task_id: int, error_message: str):
        """
        标记任务失败

        Args:
            task_id: 任务ID
            error_message: 错误消息
        """
        task = Task.query.get(task_id)
        if task:
            task.status = 'failed'
            task.completed_at = datetime.utcnow()
            task.error_message = error_message
            db.session.commit()

            state_manager.set_task_status(task_id, TaskStatus.FAILED)

            emit_status_update(task_id, 'failed', f'Task failed: {error_message}')
            logger.error(f"Task {task_id} failed: {error_message}")

    def _cleanup_task_resources(self, task_id: int):
        """
        清理任务资源

        Args:
            task_id: 任务ID
        """
        # 移除活跃任务记录
        if task_id in self.active_tasks:
            del self.active_tasks[task_id]

        # 关闭SSH连接
        if task_id in self.ssh_clients:
            self.ssh_clients[task_id].close()
            del self.ssh_clients[task_id]

        # 移除锁
        if task_id in self.running_locks:
            del self.running_locks[task_id]

        logger.info(f"Cleaned up resources for task {task_id}")

    def _log_step_execution(self, task_id: int, execution: TaskExecution, result: Dict[str, Any]):
        """
        记录步骤执行日志

        Args:
            task_id: 任务ID
            execution: 执行记录
            result: 执行结果
        """
        # 记录信息日志
        log_message = f"Step {execution.step_display_name} {'completed successfully' if result['success'] else 'failed'}"
        log_level = 'info' if result['success'] else 'error'

        # 创建日志记录
        log = TaskLog(
            task_id=task_id,
            execution_id=execution.id,
            level=log_level,
            message=log_message,
            source=f"step_executor.{execution.step_name}"
        )
        db.session.add(log)
        db.session.commit()

        # 如果有错误，记录详细信息
        if not result['success']:
            error_log = TaskLog(
                task_id=task_id,
                execution_id=execution.id,
                level='error',
                message=result.get('error_details', 'Unknown error'),
                source=f"step_executor.{execution.step_name}"
            )
            db.session.add(error_log)
            db.session.commit()


# 全局任务引擎实例
task_engine = TaskEngine()