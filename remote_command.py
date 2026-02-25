#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
远程命令执行脚本
支持通过SSH双跳连接在远程服务器上执行ls和cat命令

功能说明：
1. ls命令：列出远程服务器上指定目录的内容，使用ls -lah显示详细信息
   - 显示文件权限、所有者、大小、修改时间等
   - 支持相对路径和绝对路径
   
2. cat命令：查看远程服务器上指定文件的内容
   - 支持文本文件查看
   - 显示完整文件内容

使用方法：
  python remote_command.py <command> <path>
  
参数说明：
  command: 要执行的命令，只能是 "ls" 或 "cat"
  path: 远程服务器上的路径（目录或文件）

SSH连接：
- 使用SSH双跳连接：跳板机(lxlogin) → 目标服务器(beslogin)
- 连接配置从config.py读取
- 需要在.env文件中配置SSH密码

返回值：
- 成功：退出码 0
- 失败：退出码 1
- 用户中断：退出码 130

示例：
  # 列出目录内容
  python remote_command.py ls /besfs5/groups/cal/topup/round18/DataValid
  
  # 查看文件内容
  python remote_command.py cat /besfs5/groups/cal/topup/round18/DataValid/test.txt
  
  # 列出当前目录
  python remote_command.py ls .
"""

import sys
import argparse
from topup_ssh import TopupSSH


def execute_ls(ssh, path: str):
    """
    执行ls命令，列出远程服务器上指定目录的内容

    功能：
    - 使用 ls -lah 命令显示详细信息
    - 显示文件权限、所有者、组、大小、修改时间
    - 隐藏文件也会显示（以.开头的文件）
    
    Args:
        ssh: SSH连接实例
        path: 要列出的路径（相对路径或绝对路径）
    
    Returns:
        bool: 执行是否成功
    
    Example:
        execute_ls(ssh, "/besfs5/groups/cal/topup/round18/DataValid")
        execute_ls(ssh, ".")
    """
    command = f"ls -lah {path}"
    print(f"\n执行命令: {command}")
    print("="*60)
    
    result = ssh.execute_command(command, timeout=30)
    
    if result['success']:
        print("\n✓ 执行成功")
        if result['output']:
            print(result['output'])
    else:
        print("\n✗ 执行失败")
        if result['error']:
            print(f"错误: {result['error']}")
    
    return result['success']


def execute_cat(ssh, path: str):
    """
    执行cat命令，查看远程服务器上指定文件的内容

    功能：
    - 读取并显示文本文件的完整内容
    - 支持任意文本文件格式
    - 适合查看日志、配置文件等
    
    Args:
        ssh: SSH连接实例
        path: 要查看的文件路径（相对路径或绝对路径）
    
    Returns:
        bool: 执行是否成功
    
    Example:
        execute_cat(ssh, "/besfs5/groups/cal/topup/round18/DataValid/InjSigTimeCal/250519/rec85383_1.txt.bosslog")
        execute_cat(ssh, "./config.txt")
    """
    command = f"cat {path}"
    print(f"\n执行命令: {command}")
    print("="*60)
    
    result = ssh.execute_command(command, timeout=30)
    
    if result['success']:
        print("\n✓ 执行成功")
        if result['output']:
            print(result['output'])
    else:
        print("\n✗ 执行失败")
        if result['error']:
            print(f"错误: {result['error']}")
    
    return result['success']


def main():
    """
    主函数：处理命令行参数并执行远程命令

    流程：
    1. 解析命令行参数（command和path）
    2. 建立SSH双跳连接
    3. 根据command类型执行对应命令
    4. 显示执行结果
    5. 关闭SSH连接
    6. 返回相应的退出码

    异常处理：
    - SSH连接失败：退出码 1
    - 命令执行失败：退出码 1
    - 用户中断（Ctrl+C）：退出码 130
    - 其他异常：退出码 1
    """
    parser = argparse.ArgumentParser(
        description='远程命令执行脚本 - 通过SSH双跳连接在远程服务器上执行ls和cat命令',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 列出目录内容
  python remote_command.py ls /besfs5/groups/cal/topup/round18/DataValid

  # 查看文件内容
  python remote_command.py cat /besfs5/groups/cal/topup/round18/DataValid/test.txt

  # 列出当前目录
  python remote_command.py ls .

  # 查看日志文件
  python remote_command.py cat /besfs5/groups/cal/topup/round18/DataValid/InjSigTimeCal/250519/rec85383_1.txt.bosslog
        """
    )
    
    parser.add_argument(
        'command',
        type=str,
        choices=['ls', 'cat'],
        help='要执行的命令：ls（列出目录）或cat（查看文件）'
    )
    
    parser.add_argument(
        'path',
        type=str,
        help='远程服务器上的路径（目录或文件）'
    )
    
    args = parser.parse_args()
    
    # 建立SSH连接
    print("="*60)
    print("远程命令执行脚本")
    print("="*60)
    print(f"命令: {args.command}")
    print(f"路径: {args.path}")
    print("="*60)
    
    ssh = TopupSSH()
    
    if not ssh.connect():
        print("\n✗ SSH连接失败，程序退出")
        sys.exit(1)
    
    try:
        # 根据命令类型执行
        if args.command == 'ls':
            success = execute_ls(ssh, args.path)
        elif args.command == 'cat':
            success = execute_cat(ssh, args.path)
        else:
            print(f"\n✗ 不支持的命令: {args.command}")
            success = False
        
        # 根据执行结果返回退出码
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n✗ 用户中断")
        sys.exit(130)
    except Exception as e:
        print(f"\n✗ 执行异常: {str(e)}")
        sys.exit(1)
    finally:
        ssh.close()


if __name__ == "__main__":
    main()