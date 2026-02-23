#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务服务 - 提供任务相关的业务逻辑
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from models.database import db
from models.task import Task, Workflow, TaskParameter, TaskLog
from core.workflow_parser import workflow_parser

logger = logging.getLogger(__name__)


class TaskService:
    """任务服务类"""

    def create_task(
        self,
        user_id: str,
        workflow_name: str,
        task_name: str = None,
        parameters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        创建新任务

        Args:
            user_id: 用户ID
            workflow_name: 工作流名称
            task_name: 任务名称
            parameters: 任务参数

        Returns:
            创建结果
        """
        try:
            # 查找工作流
            workflow = Workflow.query.filter_by(name=workflow_name).first()
            if not workflow:
                return {'success': False, 'error': f'Workflow not found: {workflow_name}'}

            # 验证参数
            if parameters:
                is_valid, error_msg = workflow_parser.validate_parameters(
                    workflow_name,
                    parameters
                )
                if not is_valid:
                    return {'success': False, 'error': error_msg}

            # 创建任务实例
            task = Task(
                user_id=user_id,
                workflow_id=workflow.id,
                task_name=task_name or f'{workflow_name}_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}',
                date_param=parameters.get('date_param') if parameters else None,
                status='pending',
                progress_percentage=0,
                created_at=datetime.utcnow()
            )

            db.session.add(task)
            db.session.commit()

            # 保存任务参数
            if parameters:
                for param_name, param_value in parameters.items():
                    param = TaskParameter(
                        task_id=task.id,
                        param_name=param_name,
                        param_value=str(param_value),
                        param_type=self._get_param_type(param_value)
                    )
                    db.session.add(param)
                db.session.commit()

            logger.info(f"Created task {task.id} for user {user_id}")

            return {
                'success': True,
                'task_id': task.id,
                'status': 'pending',
                'message': 'Task created successfully',
                'task': task.to_dict()
            }

        except Exception as e:
            logger.error(f"Failed to create task: {str(e)}")
            db.session.rollback()
            return {'success': False, 'error': str(e)}

    def get_tasks(
        self,
        user_id: str,
        status: str = None,
        limit: int = 10,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        获取任务列表

        Args:
            user_id: 用户ID
            status: 任务状态筛选
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            任务列表
        """
        try:
            query = Task.query.filter_by(user_id=user_id)

            if status:
                query = query.filter_by(status=status)

            total = query.count()
            tasks = query.order_by(Task.created_at.desc()).offset(offset).limit(limit).all()

            return {
                'success': True,
                'tasks': [task.to_dict() for task in tasks],
                'total': total,
                'limit': limit,
                'offset': offset
            }

        except Exception as e:
            logger.error(f"Failed to get tasks: {str(e)}")
            return {'success': False, 'error': str(e)}

    def get_task(self, task_id: int, include_details: bool = False) -> Dict[str, Any]:
        """
        获取任务详情

        Args:
            task_id: 任务ID
            include_details: 是否包含详细信息

        Returns:
            任务详情
        """
        try:
            task = Task.query.get(task_id)
            if not task:
                return {'success': False, 'error': 'Task not found'}

            return {
                'success': True,
                'task': task.to_dict(include_details=include_details)
            }

        except Exception as e:
            logger.error(f"Failed to get task {task_id}: {str(e)}")
            return {'success': False, 'error': str(e)}

    def get_task_logs(
        self,
        task_id: int,
        level: str = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        获取任务日志

        Args:
            task_id: 任务ID
            level: 日志级别筛选
            limit: 返回数量限制

        Returns:
            日志列表
        """
        try:
            task = Task.query.get(task_id)
            if not task:
                return {'success': False, 'error': 'Task not found'}

            query = TaskLog.query.filter_by(task_id=task_id)

            if level:
                query = query.filter_by(level=level)

            logs = query.order_by(TaskLog.timestamp.desc()).limit(limit).all()

            return {
                'success': True,
                'logs': [log.to_dict() for log in logs],
                'total': len(logs)
            }

        except Exception as e:
            logger.error(f"Failed to get logs for task {task_id}: {str(e)}")
            return {'success': False, 'error': str(e)}

    def get_task_progress(self, task_id: int) -> Dict[str, Any]:
        """
        获取任务进度

        Args:
            task_id: 任务ID

        Returns:
            进度信息
        """
        try:
            task = Task.query.get(task_id)
            if not task:
                return {'success': False, 'error': 'Task not found'}

            return {
                'success': True,
                'task_id': task_id,
                'progress_percentage': task.progress_percentage,
                'current_step': task.current_step,
                'status': task.status,
                'created_at': task.created_at.isoformat() if task.created_at else None,
                'started_at': task.started_at.isoformat() if task.started_at else None,
                'completed_at': task.completed_at.isoformat() if task.completed_at else None,
                'estimated_completion_time': task.estimated_completion_time.isoformat() if task.estimated_completion_time else None
            }

        except Exception as e:
            logger.error(f"Failed to get progress for task {task_id}: {str(e)}")
            return {'success': False, 'error': str(e)}

    def delete_task(self, task_id: int) -> Dict[str, Any]:
        """
        删除任务

        Args:
            task_id: 任务ID

        Returns:
            删除结果
        """
        try:
            task = Task.query.get(task_id)
            if not task:
                return {'success': False, 'error': 'Task not found'}

            # 检查任务是否可以删除
            if task.status in ['running', 'paused']:
                return {'success': False, 'error': 'Cannot delete task in running state'}

            # 删除任务（级联删除相关记录）
            db.session.delete(task)
            db.session.commit()

            logger.info(f"Deleted task {task_id}")

            return {'success': True, 'message': 'Task deleted successfully'}

        except Exception as e:
            logger.error(f"Failed to delete task {task_id}: {str(e)}")
            db.session.rollback()
            return {'success': False, 'error': str(e)}

    def _get_param_type(self, value: Any) -> str:
        """
        获取参数类型

        Args:
            value: 参数值

        Returns:
            类型字符串
        """
        if isinstance(value, bool):
            return 'boolean'
        elif isinstance(value, int):
            return 'integer'
        else:
            return 'text'