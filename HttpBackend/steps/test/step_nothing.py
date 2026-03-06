#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 
一个什么也不做的step

"""
from topup_ssh import TopupSSH

def do_nothing(ssh : TopupSSH) :
    """
    这个步骤什么也不做 

    Args:
        ssh: TopupSSH 实例，用于执行远程命令

    Returns:
        包含以下键的字典：
            - success (bool, 必需): 是否成功
            - message (str, 必需): 人类可读的消息
            - console_logs (list, 必需): 执行过程日志
            - step_nothing: str nothing

    """
    console_logs = []
    print("run a do nothing step")
    console_logs.append("run a do nothing step")



    return {
        "success" : True,
        "message" : "do nothing step finished",
        "step_name" : "do_nothing",
        "console_logs" : console_logs,
        "step_nothing" : "do_nothing",

    }