#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iFlow CLI 通信模块
用于向已打开的 iFlow CLI 发送文件和提示词
"""

import os
import json
from typing import Dict, Any, Optional


class IFlowCLIClient:
    """iFlow CLI 客户端"""
    
    def __init__(self, ipc_dir: str = ".iflow_ipc"):
        """
        初始化 iFlow CLI 客户端
        
        Args:
            ipc_dir: IPC（进程间通信）目录
        """
        self.ipc_dir = ipc_dir
        self.requests_dir = os.path.join(ipc_dir, "requests")
        self.responses_dir = os.path.join(ipc_dir, "responses")
        
        # 确保 IPC 目录存在
        os.makedirs(self.requests_dir, exist_ok=True)
        os.makedirs(self.responses_dir, exist_ok=True)
    
    def send_message(self, 
                    content: str,
                    files: Optional[Dict[str, str]] = None,
                    file_lines: Optional[Dict[str, int]] = None) -> Dict[str, Any]:
        """
        向 iFlow CLI 发送消息
        
        Args:
            content: 提示词内容
            files: 文件路径字典 {文件名: 文件路径}
            file_lines: 文件行数字典 {文件名: 行数}，用于发送文件的后N行
            
        Returns:
            dict: 发送结果
        """
        import time
        import uuid
        
        # 生成唯一的请求ID
        request_id = str(uuid.uuid4())
        
        # 准备消息
        message = {
            'request_id': request_id,
            'timestamp': time.time(),
            'content': content,
            'files': {},
            'metadata': {
                'source': 'run.py',
                'mode': 'ai_analysis'
            }
        }
        
        # 处理文件
        if files:
            for file_name, file_path in files.items():
                if os.path.exists(file_path):
                    # 检查是否只发送后N行
                    lines_to_read = file_lines.get(file_name) if file_lines else None
                    
                    if lines_to_read:
                        # 读取后N行
                        content_lines = self._read_last_n_lines(file_path, lines_to_read)
                        message['files'][file_name] = {
                            'content': content_lines,
                            'type': 'partial',
                            'lines': lines_to_read,
                            'total_lines': self._count_lines(file_path)
                        }
                    else:
                        # 读取整个文件
                        with open(file_path, 'r', encoding='utf-8') as f:
                            message['files'][file_name] = {
                                'content': f.read(),
                                'type': 'full',
                                'lines': self._count_lines(file_path)
                            }
                else:
                    message['files'][file_name] = {
                        'error': f'文件不存在: {file_path}',
                        'type': 'error'
                    }
        
        # 写入请求文件
        request_file = os.path.join(self.requests_dir, f"{request_id}.json")
        try:
            with open(request_file, 'w', encoding='utf-8') as f:
                json.dump(message, f, ensure_ascii=False, indent=2)
        except Exception as e:
            return {
                'success': False,
                'message': f'写入请求文件失败: {str(e)}',
                'request_id': request_id
            }
        
        # 等待响应（简单轮询）
        response_file = os.path.join(self.responses_dir, f"{request_id}.json")
        max_wait = 300  # 最大等待5分钟
        check_interval = 1  # 每秒检查一次
        waited = 0
        
        while waited < max_wait:
            if os.path.exists(response_file):
                try:
                    with open(response_file, 'r', encoding='utf-8') as f:
                        response = json.load(f)
                    
                    # 清理响应文件
                    os.remove(response_file)
                    
                    return {
                        'success': True,
                        'message': '消息已发送并收到响应',
                        'request_id': request_id,
                        'response': response
                    }
                except Exception as e:
                    return {
                        'success': False,
                        'message': f'读取响应文件失败: {str(e)}',
                        'request_id': request_id
                    }
            
            time.sleep(check_interval)
            waited += check_interval
        
        return {
            'success': False,
            'message': '等待响应超时',
            'request_id': request_id,
            'waited_seconds': waited
        }
    
    def send_error_analysis(self,
                          error_code: int,
                          step_name: str,
                          log_file_path: str,
                          prompt: str,
                          log_lines: int = 200) -> Dict[str, Any]:
        """
        发送错误分析请求
        
        Args:
            error_code: 错误代码
            step_name: 步骤名称
            log_file_path: 日志文件路径
            prompt: 提示词
            log_lines: 读取日志文件的后N行
            
        Returns:
            dict: 发送结果
        """
        # 构建上下文信息
        context = {
            'error_code': error_code,
            'step_name': step_name,
            'current_directory': os.getcwd()
        }
        
        # 构建完整提示词
        full_prompt = f"""错误分析请求

错误代码: {error_code}
步骤名称: {step_name}

{prompt}

上下文信息:
- 错误代码: {error_code}
- 步骤名称: {step_name}
- 工作目录: {context['current_directory']}

请分析以下日志文件内容并提供解决方案。
"""
        
        # 发送消息
        return self.send_message(
            content=full_prompt,
            files={'log_file': log_file_path},
            file_lines={'log_file': log_lines}
        )
    
    def _read_last_n_lines(self, file_path: str, n: int) -> str:
        """
        读取文件的后N行
        
        Args:
            file_path: 文件路径
            n: 行数
            
        Returns:
            str: 后N行的内容
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                return ''.join(lines[-n:]) if len(lines) > n else ''.join(lines)
        except Exception as e:
            return f'读取文件失败: {str(e)}'
    
    def _count_lines(self, file_path: str) -> int:
        """
        计算文件的行数
        
        Args:
            file_path: 文件路径
            
        Returns:
            int: 行数
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return sum(1 for _ in f)
        except Exception as e:
            return 0


# 全局客户端实例
iflow_client = IFlowCLIClient()