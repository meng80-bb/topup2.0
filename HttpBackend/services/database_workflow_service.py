#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库工作流服务 - 从数据库生成工作流配置
"""

import json
from typing import Dict, Any, List
from pathlib import Path

try:
    from models.task import Workflow, WorkflowStep
except ImportError:
    # 如果无法导入模型（在非Flask上下文中），使用None
    Workflow = None
    WorkflowStep = None

from services.notification_service import logger

class DatabaseWorkflowService:
    """数据库工作流服务"""

    def __init__(self):
        self.config_dir = Path(__file__).parent.parent / 'workflows'

    def load_workflow_from_db(self, workflow_name: str) -> Dict[str, Any]:
        """
        从数据库加载工作流配置

        Args:
            workflow_name: 工作流名称

        Returns:
            工作流配置字典
        """
        if not Workflow:
            # 如果无法导入模型，回退到文件
            return self._load_from_file(workflow_name)

        try:
            from app import app
            with app.app_context():
                return self._load_with_context(workflow_name)
        except ImportError:
            # 无法导入app，回退到文件
            return self._load_from_file(workflow_name)

    def _load_with_context(self, workflow_name: str) -> Dict[str, Any]:
        """在应用上下文中加载工作流"""
        workflow = Workflow.query.filter_by(name=workflow_name).first()
        if not workflow:
            raise ValueError(f"Workflow not found: {workflow_name}")

        # 读取基础配置文件
        config_path = self.config_dir / f'{workflow_name}.json'
        if not config_path.exists():
            # 如果没有配置文件，创建基础配置
            config = self._create_base_config(workflow)
        else:
            # 读取并增强配置文件
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

        # 从数据库加载步骤
        steps = WorkflowStep.query.filter_by(workflow_id=workflow.id, status='active').order_by(WorkflowStep.step_order).all()

        # 转换步骤格式
        config['steps'] = []
        for step in steps:
            step_config = {
                'id': step.step_name,
                'order': step.step_order,
                'display_name': step.step_display_name,
                'module': step.step_module,
                'function': step.step_function,
                'description': step.description,
                'timeout_minutes': step.timeout_minutes,
                'retry_count': step.retry_count,
                'parameters': step.required_files or {}
            }
            config['steps'].append(step_config)

        return config

    def _load_from_file(self, workflow_name: str) -> Dict[str, Any]:
        """从文件加载工作流（回退方案）"""
        config_path = self.config_dir / f'{workflow_name}.json'
        if not config_path.exists():
            raise FileNotFoundError(f"Workflow config not found: {workflow_name}")

        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _create_base_config(self, workflow: Workflow) -> Dict[str, Any]:
        """
        创建基础工作流配置

        Args:
            workflow: 工作流模型

        Returns:
            基础配置字典
        """
        return {
            'workflow': {
                'name': workflow.name,
                'display_name': workflow.name.replace('_', ' ').title(),
                'description': workflow.description,
                'version': workflow.version,
                'author': 'Topup Team',
                'created_at': workflow.created_at.strftime('%Y-%m-%d') if workflow.created_at else '2026-02-24',
                'updated_at': workflow.updated_at.strftime('%Y-%m-%d') if workflow.updated_at else '2026-02-24'
            },
            'execution': {
                'max_parallel_tasks': 1,
                'default_timeout_minutes': 30,
                'retry_on_failure': True,
                'max_retries': 3,
                'retry_delay_seconds': 60,
                'continue_on_error': False,
                'cleanup_on_success': False,
                'cleanup_on_failure': False
            },
            'environment': {
                'python_version': '3.8+',
                'required_modules': ['paramiko', 'python-dotenv', 'flask', 'flask-cors', 'flask-sqlalchemy']
            },
            'parameters': {
                'required': ['user_id'],
                'optional': []
            },
            'steps': [],
            'notifications': {
                'on_start': {'enabled': True, 'message': '任务 {task_name} 开始执行'},
                'on_complete': {'enabled': True, 'message': '任务 {task_name} 执行完成，耗时 {duration}秒'},
                'on_failure': {'enabled': True, 'message': '任务 {task_name} 执行失败，错误：{error}'},
                'on_step_complete': {'enabled': False, 'message': '步骤 {step_name} 完成'}
            },
            'output': {
                'base_dir': '/besfs5/groups/cal/topup/{round}/DataValid',
                'result_format': {
                    'success': 'boolean',
                    'message': 'string'
                }
            }
        }

# 全局实例
database_workflow_service = DatabaseWorkflowService()