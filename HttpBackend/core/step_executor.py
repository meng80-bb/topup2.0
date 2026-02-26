#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
步骤执行器 - 执行单个步骤
"""

import importlib
import time
import traceback
import hashlib
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from topup_ssh import TopupSSH

logger = logging.getLogger(__name__)


class StepExecutor:
    """步骤执行器"""

    def __init__(self, ssh_client: TopupSSH):
        """
        初始化步骤执行器

        Args:
            ssh_client: SSH客户端实例
        """
        self.ssh_client = ssh_client
        self.step_results = {}

    def execute_step(
        self,
        task_id: int,
        step_config: Dict[str, Any],
        parameters: Dict[str, Any],
        step_order: int,
        step_name: str
    ) -> Dict[str, Any]:
        """
        执行单个步骤

        Args:
            task_id: 任务ID
            step_config: 步骤配置
            parameters: 任务参数
            step_order: 步骤顺序
            step_name: 步骤名称

        Returns:
            执行结果字典
        """
        start_time = datetime.utcnow()
        execution_id = f"{task_id}_{step_name}"

        try:
            # 记录开始执行
            logger.info(f"Starting step {step_name} for task {task_id}")
            result = {
                'success': False,
                'step_name': step_name,
                'step_display_name': step_config.get('display_name', step_name),
                'step_order': step_order,
                'start_time': start_time.isoformat(),
                'end_time': None,
                'duration_seconds': None,
                'output_summary': None,
                'error_details': None,
                'outputs': [],
                'requires_manual_intervention': False
            }

            # 准备步骤参数
            step_params = self._prepare_step_parameters(step_config, parameters)

            # 动态导入步骤模块
            module_name = step_config['module']
            function_name = step_config['function']

            module = importlib.import_module(f'steps.{module_name}')
            step_function = getattr(module, function_name)

            # 执行步骤
            logger.info(f"Executing {module_name}.{function_name}")
            execution_result = step_function(
                ssh=self.ssh_client,
                **step_params
            )

            # 处理执行结果
            result.update(self._process_execution_result(execution_result))

            # 检查输出文件
            if result['success']:
                result['outputs'] = self._check_output_files(
                    task_id, step_config.get('required_files', [])
                )

            # 记录结束时间
            end_time = datetime.utcnow()
            result['end_time'] = end_time.isoformat()
            result['duration_seconds'] = int((end_time - start_time).total_seconds())

            logger.info(f"Step {step_name} completed in {result['duration_seconds']} seconds")

            return result

        except Exception as e:
            # 处理异常
            end_time = datetime.utcnow()
            error_message = str(e)
            error_traceback = traceback.format_exc()

            result.update({
                'success': False,
                'end_time': end_time.isoformat(),
                'duration_seconds': int((end_time - start_time).total_seconds()),
                'error_details': error_message,
                'error_traceback': error_traceback
            })

            logger.error(f"Step {step_name} failed for task {task_id}: {error_message}")
            logger.debug(f"Traceback for step {step_name}:\n{error_traceback}")

            return result

    def _prepare_step_parameters(self, step_config: Dict[str, Any], task_parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        准备步骤参数

        Args:
            step_config: 步骤配置
            task_parameters: 任务参数

        Returns:
            步骤参数字典
        """
        step_params = {}

        # 从步骤配置中获取参数映射
        param_mapping = step_config.get('parameters', {})

        # 映射参数
        for param_name, mapped_value in param_mapping.items():
            if mapped_value in task_parameters:
                step_params[param_name] = task_parameters[mapped_value]
            else:
                # 如果参数不存在，使用默认值
                logger.warning(f"Parameter {mapped_value} not found in task parameters")

        # 添加一些常用参数
        step_params.update({
            'submit_job': task_parameters.get('submit_job', True),
            'max_wait_minutes': task_parameters.get('max_wait_minutes', 25)
        })

        return step_params

    def _process_execution_result(self, execution_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理执行结果

        Args:
            execution_result: 步骤执行结果

        Returns:
            处理后的结果
        """
        result = {
            'success': execution_result.get('success', False),
            'output_summary': execution_result.get('message', ''),
            'requires_manual_intervention': execution_result.get('requires_manual_intervention', False)
        }

        if not result['success']:
            result['error_details'] = execution_result.get('message', 'Unknown error')
            if 'error' in execution_result:
                result['error_details'] = execution_result['error']

        return result

    def _check_output_files(self, task_id: int, required_files: List[str]) -> List[Dict[str, Any]]:
        """
        检查输出文件

        Args:
            task_id: 任务ID
            required_files: 必需文件列表

        Returns:
            输出文件信息列表
        """
        outputs = []

        if not required_files:
            return outputs

        try:
            # 这里需要根据实际任务目录来检查文件
            # 临时实现，后续需要根据任务信息确定目录
            for file_pattern in required_files:
                # 这里应该实现实际的文件检查逻辑
                # 现在只返回示例数据
                output_info = {
                    'output_type': 'file',
                    'output_path': f'/path/to/{file_pattern}',
                    'file_size_bytes': None,
                    'file_hash': None,
                    'content_type': self._get_content_type(file_pattern)
                }
                outputs.append(output_info)

        except Exception as e:
            logger.error(f"Failed to check output files: {str(e)}")

        return outputs

    def _get_content_type(self, file_path: str) -> str:
        """
        获取文件内容类型

        Args:
            file_path: 文件路径

        Returns:
            内容类型
        """
        suffix = Path(file_path).suffix.lower()
        content_types = {
            '.txt': 'text/plain',
            '.log': 'text/plain',
            '.png': 'image/png',
            '.root': 'application/root',
            '.json': 'application/json'
        }
        return content_types.get(suffix, 'application/octet-stream')

    def calculate_file_hash(self, file_path: str) -> Optional[str]:
        """
        计算文件哈希值

        Args:
            file_path: 文件路径

        Returns:
            文件哈希值
        """
        try:
            # 这里需要实现实际的文件哈希计算
            # 由于是远程文件，可能需要下载到本地计算
            return None
        except Exception as e:
            logger.error(f"Failed to calculate hash for {file_path}: {str(e)}")
            return None

    def get_step_result(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """
        获取步骤执行结果

        Args:
            execution_id: 执行ID

        Returns:
            执行结果
        """
        return self.step_results.get(execution_id)

    def clear_step_results(self, task_id: str):
        """
        清除任务相关的步骤结果

        Args:
            task_id: 任务ID
        """
        keys_to_remove = [k for k in self.step_results.keys() if k.startswith(f"{task_id}_")]
        for key in keys_to_remove:
            del self.step_results[key]
        logger.info(f"Cleared step results for task {task_id}")