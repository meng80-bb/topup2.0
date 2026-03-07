#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 

一个执行交互式命令的step

"""
from topup_ssh import TopupSSH

def step_interactive_command(
        ssh : TopupSSH, 
        command : str, 
        completion_marker: str, 
        timeout: int = 3600
        ) :
    """
    执行一个交互式命令，直到输出中出现 completion_marker 或超时

    Args:
        ssh: TopupSSH 实例，用于执行远程命令
        command: 要执行的命令字符串
        completion_marker: 输出中表示命令完成的标记字符串
        timeout: 等待命令完成的最大时间（秒）

    Returns:
        包含以下键的字典：
            - success (bool, 必需): 是否成功
            - message (str, 必需): 人类可读的消息
            - console_logs (list, 必需): 执行过程日志
            - step_command: str 执行的命令
            - output: str 命令输出（如果有）
            - error: str 错误信息（如果有）

    """
    console_logs = []
    print(f"run interactive command: {command}")
    console_logs.append(f"run interactive command: {command}")

    try:
        result = ssh.execute_interactive_command(command, completion_marker, timeout)
        console_logs.append(f"command output: {result}")

        if result["success"]:
            console_logs.append(f"interactive command executed successfully")
            return {
                "success" : True,
                "message" : f"interactive command '{command}' executed successfully",
                "step_name" : "step_interactive_command",
                "console_logs" : console_logs,
                "step_command" : command,
                "output" : result["output"]
            }
        else:
            console_logs.append(f"interactive command execution failed: {result['error']}")
            return {
                "success" : False,
                "message" : f"interactive command '{command}' execution failed: {result['error']}",
                "step_name" : "step_interactive_command",
                "console_logs" : console_logs,
                "step_command" : command,
                "error" : result["error"],
                "output" : result["output"]
            }

    except Exception as e:
        console_logs.append(f"interactive command execution failed: {str(e)}")
        return {
            "success" : False,
            "message" : f"interactive command '{command}' execution failed: {str(e)}",
            "step_name" : "step_interactive_command",
            "console_logs" : console_logs,
            "step_command" : command,
            "error" : str(e)
        }
