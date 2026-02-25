#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志记录器
用于记录操作步骤和执行时间
"""

import os
from datetime import datetime
from typing import Dict, Any


class StepLogger:
    """步骤日志记录器（通用）"""
    
    def __init__(self, log_dir: str = "logs"):
        """
        初始化日志记录器
        
        Args:
            log_dir: 日志目录路径
        """
        self.log_dir = log_dir
        self.log_file = os.path.join(log_dir, "step_execution.log")
        self.enabled = False
        self.current_mode = None
        
        # 确保日志目录存在
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
    
    def enable(self, mode: str):
        """
        启用日志记录
        
        Args:
            mode: 执行模式（single, continue, all, total）
        """
        self.enabled = True
        self.current_mode = mode
        
        # 清空旧日志
        self._clear_log()
        
        self._write_separator()
        self._log(f"步骤日志记录器已启用")
        self._log(f"执行模式: {mode}")
        self._log(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self._write_separator()
    
    def disable(self):
        """禁用日志记录"""
        if self.enabled:
            self._write_separator()
            self._log(f"步骤日志记录器已禁用")
            self._log(f"执行模式: {self.current_mode}")
            self._log(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            self._write_separator()
        self.enabled = False
        self.current_mode = None
    
    def log_step_start(self, step_key: str, step_name: str, date: str = None):
        """
        记录步骤开始
        
        Args:
            step_key: 步骤键值（如 '1.1'）
            step_name: 步骤名称
            date: 日期参数（如果适用）
        """
        if not self.enabled:
            return
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        
        log_entry = f"[{timestamp}] 步骤开始"
        if date:
            log_entry += f" | 日期: {date}"
        log_entry += f"\n  步骤编号: {step_key}"
        log_entry += f"\n  步骤名称: {step_name}"
        
        self._write_log_entry(log_entry)
    
    def log_step_complete(self, step_key: str, step_name: str, result: Dict[str, Any]):
        """
        记录步骤完成
        
        Args:
            step_key: 步骤键值
            step_name: 步骤名称
            result: 步骤执行结果
        """
        if not self.enabled:
            return
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        
        log_entry = f"[{timestamp}] 步骤完成"
        log_entry += f"\n  步骤编号: {step_key}"
        log_entry += f"\n  步骤名称: {step_name}"
        log_entry += f"\n  执行结果: {'成功' if result.get('success') else '失败'}"
        log_entry += f"\n  消息: {result.get('message', 'N/A')}"
        
        if 'exit_code' in result:
            log_entry += f"\n  退出码: {result['exit_code']}"
        
        if 'ai_analysis' in result:
            analysis = result['ai_analysis']
            log_entry += f"\n  AI分析:"
            log_entry += f"\n    should_continue: {analysis.get('should_continue')}"
            log_entry += f"\n    action: {analysis.get('action')}"
            log_entry += f"\n    message: {analysis.get('message')}"
            
            # 记录错误字典信息
            if 'error_code' in analysis and 'error_info' in analysis:
                error_code = analysis['error_code']
                error_info = analysis['error_info']
                log_entry += f"\n  错误字典信息:"
                log_entry += f"\n    错误码: {error_code}"
                log_entry += f"\n    错误名称: {error_info.get('name', 'N/A')}"
                log_entry += f"\n    错误描述: {error_info.get('description', 'N/A')}"
                log_entry += f"\n    错误详细说明: {error_info.get('message', 'N/A')}"
        
        self._write_log_entry(log_entry)
    
    def log_loop_start(self, loop_number: int, date: str = None):
        """
        记录循环开始
        
        Args:
            loop_number: 循环编号
            date: 当前日期
        """
        if not self.enabled:
            return
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        
        log_entry = f"\n{'='*60}\n"
        log_entry += f"[{timestamp}] Total模式循环开始"
        log_entry += f"\n  循环编号: {loop_number}"
        if date:
            log_entry += f"\n  当前日期: {date}"
        log_entry += f"\n{'='*60}\n"
        
        self._write_log_entry(log_entry)
    
    def log_loop_complete(self, loop_number: int, processed_dates: list = None):
        """
        记录循环完成
        
        Args:
            loop_number: 循环编号
            processed_dates: 已处理的日期列表
        """
        if not self.enabled:
            return
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        
        log_entry = f"\n{'='*60}\n"
        log_entry += f"[{timestamp}] 循环完成"
        log_entry += f"\n  循环编号: {loop_number}"
        if processed_dates:
            log_entry += f"\n  已处理日期: {', '.join(processed_dates)}"
        log_entry += f"\n{'='*60}\n"
        
        self._write_log_entry(log_entry)
    
    def log_error(self, step_key: str, step_name: str, error_message: str):
        """
        记录错误
        
        Args:
            step_key: 步骤键值
            step_name: 步骤名称
            error_message: 错误消息
        """
        if not self.enabled:
            return
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        
        log_entry = f"\n[{timestamp}] ❌ 错误"
        log_entry += f"\n  步骤编号: {step_key}"
        log_entry += f"\n  步骤名称: {step_name}"
        log_entry += f"\n  错误消息: {error_message}\n"
        
        self._write_log_entry(log_entry)
    
    def log_execution_complete(self, message: str):
        """
        记录执行完成
        
        Args:
            message: 完成消息
        """
        if not self.enabled:
            return
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        
        log_entry = f"\n{'#'*60}\n"
        log_entry += f"[{timestamp}] ✓ {message}"
        log_entry += f"\n{'#'*60}\n"
        
        self._write_log_entry(log_entry)
    
    def log_total_complete(self, total_loops: int, total_dates: int):
        """
        记录Total模式完成
        
        Args:
            total_loops: 总循环次数
            total_dates: 总处理日期数
        """
        if not self.enabled:
            return
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        
        log_entry = f"\n{'#'*60}\n"
        log_entry += f"[{timestamp}] ✓ Total模式完成"
        log_entry += f"\n  总循环次数: {total_loops}"
        log_entry += f"\n  总处理日期数: {total_dates}"
        log_entry += f"\n{'#'*60}\n"
        
        self._write_log_entry(log_entry)
    
    def log_custom(self, message: str):
        """
        记录自定义消息
        
        Args:
            message: 自定义消息
        """
        if not self.enabled:
            return
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        log_entry = f"\n[{timestamp}] {message}\n"
        
        self._write_log_entry(log_entry)
    
    def log_command(self, command: str):
        """
        记录执行的命令
        
        Args:
            command: 执行的命令
        """
        if not self.enabled:
            return
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        log_entry = f"\n[{timestamp}] 💻 执行命令:\n  $ {command}\n"
        
        self._write_log_entry(log_entry)
    
    def log_command_output(self, output: str):
        """
        记录命令输出
        
        Args:
            output: 命令输出
        """
        if not self.enabled:
            return
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        log_entry = f"[{timestamp}] 📤 命令输出:\n{output}\n"
        
        self._write_log_entry(log_entry)
    
    def _write_log_entry(self, log_entry: str):
        """写入日志条目"""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry + '\n')
        except Exception as e:
            print(f"写入日志失败: {e}")
    
    def _clear_log(self):
        """清空日志文件"""
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write("")
        except Exception as e:
            print(f"清空日志文件失败: {e}")
    
    def _write_separator(self):
        """写入分隔符"""
        if not self.enabled:
            return
        
        separator = "\n" + "-"*60 + "\n"
        self._write_log_entry(separator)
    
    def _log(self, message: str):
        """内部日志方法"""
        self._write_log_entry(message)
    
    def log_mode_exit(self, mode: str, has_error: bool = False):
        """
        记录模式退出状态

        Args:
            mode: 执行模式（single, all, total）
            has_error: 是否出现错误
        """
        if not self.enabled:
            return

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

        if has_error:
            # 读取进度文件获取当前处理的日期和步骤
            date = None
            step_name = None
            try:
                import os
                import json
                import config
                progress = config.load_step_progress()
                date = progress.get('date')
                step_name = progress.get('step_name')
            except Exception as e:
                print(f"读取进度文件失败: {e}")

            log_entry = f"\n{'#'*60}\n"
            log_entry += f"[{timestamp}] ✗ 出现了错误，{mode}已退出"
            if date or step_name:
                log_entry += f"\n"
                if step_name:
                    log_entry += f"当前步骤: {step_name}\n"
                if date:
                    log_entry += f"当前日期: {date}\n"
            log_entry += f"{'#'*60}\n"
        else:
            log_entry = f"\n{'#'*60}\n"
            log_entry += f"[{timestamp}] ✓ 没出现任何错误，{mode}正常退出"
            log_entry += f"\n{'#'*60}\n"

        self._write_log_entry(log_entry)

    def clear_log(self):
        """清空日志文件"""
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write("")
            print(f"日志文件已清空: {self.log_file}")
        except Exception as e:
            print(f"清空日志文件失败: {e}")


# 全局日志记录器实例
step_logger = StepLogger()