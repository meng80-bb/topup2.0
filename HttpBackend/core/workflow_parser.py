#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作流解析器 - 解析工作流配置文件
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from services.database_workflow_service import database_workflow_service

logger = logging.getLogger(__name__)


class WorkflowParser:
    """工作流解析器"""

    def __init__(self, config_dir: str = None):
        """
        初始化工作流解析器

        Args:
            config_dir: 工作流配置目录路径
        """
        self.config_dir = Path(config_dir) if config_dir else Path(__file__).parent.parent / 'workflows'
        self._cache = {}

    def load_workflow(self, workflow_name: str) -> Dict[str, Any]:
        """
        加载工作流配置

        Args:
            workflow_name: 工作流名称

        Returns:
            工作流配置字典
        """
        # 检查缓存
        if workflow_name in self._cache:
            return self._cache[workflow_name]

        # 首先尝试从数据库加载
        try:
            config = database_workflow_service.load_workflow_from_db(workflow_name)
            self._cache[workflow_name] = config
            logger.info(f"Loaded workflow '{workflow_name}' from database")
            return config
        except Exception as e:
            logger.warning(f"Failed to load workflow from database: {e}")

        # 回退到文件加载
        config_path = self.config_dir / f'{workflow_name}.json'
        if not config_path.exists():
            config_path = self.config_dir / 'topup_standard.json'

        if not config_path.exists():
            raise FileNotFoundError(f"Workflow config not found: {workflow_name}")

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # 验证配置
            self._validate_workflow_config(config)

            # 缓存配置
            self._cache[workflow_name] = config

            logger.info(f"Loaded workflow config: {workflow_name}")
            return config

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in workflow config {workflow_name}: {e}")
            raise ValueError(f"Invalid workflow config: {e}")

    def _validate_workflow_config(self, config: Dict[str, Any]):
        """
        验证工作流配置

        Args:
            config: 工作流配置字典

        Raises:
            ValueError: 配置无效
        """
        required_fields = ['workflow', 'execution', 'steps']

        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field: {field}")

        # 验证工作流信息
        workflow_info = config['workflow']
        required_workflow_fields = ['name', 'version', 'steps']

        for field in required_workflow_fields:
            if field not in workflow_info:
                raise ValueError(f"Missing workflow field: {field}")

        # 验证步骤
        if not config['steps']:
            raise ValueError("Workflow must have at least one step")

        # 验证步骤定义
        for step in config['steps']:
            required_step_fields = ['id', 'order', 'module', 'function']

            for field in required_step_fields:
                if field not in step:
                    raise ValueError(f"Missing step field: {field} in step {step.get('id', 'unknown')}")

        logger.info("Workflow config validated successfully")

    def get_workflow_info(self, workflow_name: str) -> Dict[str, Any]:
        """
        获取工作流基本信息

        Args:
            workflow_name: 工作流名称

        Returns:
            工作流信息字典
        """
        config = self.load_workflow(workflow_name)
        return config['workflow']

    def get_workflow_steps(self, workflow_name: str) -> List[Dict[str, Any]]:
        """
        获取工作流所有步骤

        Args:
            workflow_name: 工作流名称

        Returns:
            步骤列表
        """
        config = self.load_workflow(workflow_name)
        return config['steps']

    def get_step_by_id(self, workflow_name: str, step_id: str) -> Optional[Dict[str, Any]]:
        """
        根据ID获取步骤

        Args:
            workflow_name: 工作流名称
            step_id: 步骤ID

        Returns:
            步骤配置字典，如果不存在返回None
        """
        steps = self.get_workflow_steps(workflow_name)

        for step in steps:
            if step['id'] == step_id:
                return step

        return None

    def get_step_dependencies(self, workflow_name: str, step_id: str) -> List[str]:
        """
        获取步骤的依赖

        Args:
            workflow_name: 工作流名称
            step_id: 步骤ID

        Returns:
            依赖步骤ID列表
        """
        step = self.get_step_by_id(workflow_name, step_id)

        if not step:
            return []

        return step.get('depends_on', [])

    def get_execution_config(self, workflow_name: str) -> Dict[str, Any]:
        """
        获取执行配置

        Args:
            workflow_name: 工作流名称

        Returns:
            执行配置字典
        """
        config = self.load_workflow(workflow_name)
        return config.get('execution', {})

    def get_parameters_config(self, workflow_name: str) -> Dict[str, Any]:
        """
        获取参数配置

        Args:
            workflow_name: 工作流名称

        Returns:
            参数配置字典
        """
        config = self.load_workflow(workflow_name)
        return config.get('parameters', {})

    def validate_parameters(self, workflow_name: str, parameters: Dict[str, Any]) -> tuple[bool, str]:
        """
        验证任务参数

        Args:
            workflow_name: 工作流名称
            parameters: 参数字典

        Returns:
            (是否有效, 错误消息)
        """
        params_config = self.get_parameters_config(workflow_name)

        # 检查必需参数
        required = params_config.get('required', [])

        for param_name in required:
            if param_name not in parameters:
                return False, f"Missing required parameter: {param_name}"

        # TODO: 可以添加更多参数验证逻辑

        return True, ""

    def get_steps_in_order(self, workflow_name: str) -> List[Dict[str, Any]]:
        """
        获取按执行顺序排列的步骤

        Args:
            workflow_name: 工作流名称

        Returns:
            排序后的步骤列表
        """
        steps = self.get_workflow_steps(workflow_name)

        # 按order排序
        sorted_steps = sorted(steps, key=lambda x: x['order'])

        return sorted_steps

    def clear_cache(self):
        """清除缓存"""
        self._cache.clear()
        logger.info("Workflow parser cache cleared")


# 全局工作流解析器实例
workflow_parser = WorkflowParser()