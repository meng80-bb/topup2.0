#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Topup SSH连接管理模块
支持SSH双跳连接：通过跳板机(lxlogin)连接到目标服务器(beslogin)
"""

import paramiko
import os
import time
from typing import Optional, Tuple, Dict, Any
import config
import logging

# 创建logger
logger = logging.getLogger(__name__)


class TopupSSH:
    """SSH双跳连接管理类"""

    def __init__(self):
        """
        初始化SSH连接管理器
        """
        # 服务器配置（从config.py导入）
        self.server1_config = config.SSH_CONFIG['servers']['server1']
        self.server2_config = config.SSH_CONFIG['servers']['server2']
        
        # SSH连接
        self.ssh1: Optional[paramiko.SSHClient] = None
        self.ssh2: Optional[paramiko.SSHClient] = None
        
        # 传输通道
        self.transport: Optional[paramiko.Transport] = None
        
        # 连接状态
        self.connected = False
    
    def connect(self) -> bool:
        """
        建立SSH双跳连接
        
        Returns:
            bool: 连接是否成功
        """
        try:
            # 创建第一个SSH客户端（连接到跳板机）
            self.ssh1 = paramiko.SSHClient()
            self.ssh1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # 跳板机密码
            password1 = os.getenv(self.server1_config['env_password'])
            
            # 连接到跳板机
            print(f"正在连接到跳板机 {self.server1_config['host']}...")
            self.ssh1.connect(
                hostname=self.server1_config['host'],
                port=self.server1_config['port'],
                username=self.server1_config['username'],
                password=password1,
                timeout=30,
                auth_timeout=30,
                banner_timeout=30
            )
            print(f"✓ 成功连接到跳板机 {self.server1_config['host']}")
            
            # 创建传输通道到目标服务器
            self.transport = self.ssh1.get_transport()
            dest_addr = (self.server2_config['host'], self.server2_config['port'])
            local_addr = ('localhost', 22)
            print("正在创建SSH通道...")
            # 默认超时60秒，避免长时间卡在这里
            channel = self.transport.open_channel("direct-tcpip", dest_addr, local_addr , timeout=60)
            print(f"正在通过跳板机连接到目标服务器 {self.server2_config['host']}...")
            
            # 创建第二个SSH客户端（连接到目标服务器）
            self.ssh2 = paramiko.SSHClient()
            self.ssh2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # 目标服务器密码
            password2 = os.getenv(self.server2_config['env_password'])
            
            # 通过通道连接到目标服务器
            self.ssh2.connect(
                hostname=self.server2_config['host'],
                port=self.server2_config['port'],
                username=self.server2_config['username'],
                password=password2,
                sock=channel,
                timeout=30,
                auth_timeout=30,
                banner_timeout=30
            )
            print(f"✓ 成功连接到目标服务器 {self.server2_config['host']}")
            
            self.connected = True
            return True
            
        except Exception as e:
            print(f"✗ SSH连接失败: {str(e)}")
            self.close()
            return False
    
    def execute_command(self, command: str, timeout: int = 600, use_pty: bool = False) -> Dict[str, Any]:
        """
        在远程服务器上执行命令

        Args:
            command: 要执行的命令
            timeout: 超时时间（秒），默认600秒
            use_pty: 是否使用PTY伪终端，默认False。对于简单命令（如reset.sh）不需要PTY

        Returns:
            dict: 执行结果，包含success, message, exit_code, output, error
        """
        if not self.connected or self.ssh2 is None:
            return {
                'success': False,
                'message': 'SSH未连接',
                'exit_code': -1,
                'output': '',
                'error': 'SSH连接未建立'
            }

        try:
            print(f"\n执行命令: {command}")

            # 记录命令到日志
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"执行命令: {command}")

            stdin, stdout, stderr = self.ssh2.exec_command(command, get_pty=use_pty)

            # 等待命令完成，带超时
            import time
            start_time = time.time()
            while not stdout.channel.exit_status_ready():
                if time.time() - start_time > timeout:
                    # 超时，关闭连接
                    stdout.channel.close()

                    # 记录超时到日志
                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug(f"命令执行超时（{timeout}秒）")

                    return {
                        'success': False,
                        'message': f'命令执行超时（{timeout}秒）',
                        'exit_code': -1,
                        'output': '',
                        'error': '命令执行超时'
                    }
                time.sleep(0.1)

            # 获取退出码
            exit_code = stdout.channel.recv_exit_status()

            # 读取输出（设置读取超时，避免阻塞）
            import select
            output = ""
            error = ""

            # 非阻塞读取stdout
            if use_pty:
                # 使用PTY时，需要特殊处理
                import socket
                stdout.channel.setblocking(0)
                while True:
                    if stdout.channel.recv_ready():
                        data = stdout.channel.recv(1024)
                        if len(data) == 0:
                            break
                        output += data.decode('utf-8', errors='ignore')
                    else:
                        time.sleep(0.01)
                        break
            else:
                # 不使用PTY时，直接读取
                output = stdout.read().decode('utf-8', errors='ignore')

            # 读取stderr
            error = stderr.read().decode('utf-8', errors='ignore')

            # 记录输出到日志
            if logger.isEnabledFor(logging.DEBUG):
                output_log = f"退出码: {exit_code}\n"
                if output.strip():
                    output_log += f"输出:\n{output.strip()}\n"
                if error.strip():
                    output_log += f"错误:\n{error.strip()}\n"
                logger.debug(output_log)

            result = {
                'success': exit_code == 0,
                'message': '命令执行成功' if exit_code == 0 else '命令执行失败',
                'exit_code': exit_code,
                'output': output,
                'error': error
            }

            if exit_code == 0:
                print(f"✓ 命令执行成功 (退出码: {exit_code})")
                if output.strip():
                    print(f"输出: {output.strip()}")
            else:
                print(f"✗ 命令执行失败 (退出码: {exit_code})")
                if error.strip():
                    print(f"错误: {error.strip()}")

            return result

        except Exception as e:
            print(f"✗ 命令执行异常: {str(e)}")
            
            # 记录异常到日志
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"命令执行异常: {str(e)}")
            
            return {
                'success': False,
                'message': f'命令执行异常: {str(e)}',
                'exit_code': -1,
                'output': '',
                'error': str(e)
            }
    
    def execute_interactive_command(self, command: str, completion_marker: str) -> Dict[str, Any]:
        """
        使用交互式shell执行命令
        
        Args:
            command: 要执行的命令
            completion_marker: 完成标记字符串，检测到此字符串时关闭shell（必选）
            
        Returns:
            dict: 执行结果，包含success, message, output, error
        """
        if not self.connected or self.ssh2 is None:
            return {
                'success': False,
                'message': 'SSH未连接',
                'output': '',
                'error': 'SSH连接未建立'
            }
        
        try:
            # 创建交互式shell
            shell = self.ssh2.invoke_shell()
            time.sleep(2)  # 等待shell初始化
            
            # 清空初始输出
            while shell.recv_ready():
                shell.recv(4096)
            
            # 发送命令
            print(f"\n执行命令: {command}")
            print(f"完成标记: {completion_marker}")
            
            # 记录命令到日志
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"{command} (交互式)")
                logger.debug(f"完成标记: {completion_marker}")
            
            shell.send(f"{command}\n")
            
            # 读取输出（无时间限制）
            full_output = ""
            
            while True:
                if shell.recv_ready():
                    chunk = shell.recv(4096).decode('utf-8', errors='ignore')
                    full_output += chunk
                    print(chunk, end='', flush=True)
                    
                    # 检查是否在输出中检测到完成标记
                    if completion_marker in chunk:
                        print(f"\n✓ 检测到完成标记: {completion_marker}")
                        break
                time.sleep(0.1)
            
            # 关闭shell
            shell.close()
            
            # 记录输出到日志
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"输出:\n{full_output}")
            
            result = {
                'success': True,
                'message': '命令执行完成',
                'output': full_output
            }
            
            print(f"\n✓ 命令执行完成")
            return result
            
        except Exception as e:
            print(f"✗ 命令执行异常: {str(e)}")
            
            # 记录异常到日志
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"命令执行异常: {str(e)}")
            
            return {
                'success': False,
                'message': f'命令执行异常: {str(e)}',
                'output': '',
                'error': str(e)
            }
    
    def close(self):
        """关闭SSH连接"""
        if self.ssh2:
            self.ssh2.close()
            self.ssh2 = None
        
        if self.ssh1:
            self.ssh1.close()
            self.ssh1 = None
        
        if self.transport:
            self.transport.close()
            self.transport = None
        
        self.connected = False
        print("SSH连接已关闭")
    
    def download_file(self, remote_path: str, local_path: str) -> Dict[str, Any]:
        """
        使用SFTP从远程服务器下载文件
        
        Args:
            remote_path: 远程文件路径
            local_path: 本地文件路径
            
        Returns:
            dict: 下载结果，包含success, message, error
        """
        if not self.connected or self.ssh2 is None:
            return {
                'success': False,
                'message': 'SSH未连接',
                'error': 'SSH连接未建立'
            }
        
        try:
            # 创建SFTP客户端
            sftp = self.ssh2.open_sftp()
            
            print(f"\n使用SFTP下载文件:")
            print(f"  远程路径: {remote_path}")
            print(f"  本地路径: {local_path}")
            
            # 下载文件
            sftp.get(remote_path, local_path)
            
            # 关闭SFTP
            sftp.close()
            
            print(f"✓ 文件下载成功")
            
            return {
                'success': True,
                'message': f'文件下载成功: {local_path}',
                'remote_path': remote_path,
                'local_path': local_path
            }
            
        except Exception as e:
            print(f"✗ 文件下载失败: {str(e)}")
            return {
                'success': False,
                'message': f'文件下载失败: {str(e)}',
                'error': str(e)
            }
    
    def __enter__(self):
        """上下文管理器入口"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()
        return False


if __name__ == "__main__":
    # 测试SSH连接
    with TopupSSH() as ssh:
        if ssh.connected:
            # 测试执行命令
            result = ssh.execute_command("hostname")
            print("\n" + "="*60)
            print("测试命令执行结果:")
            print("="*60)
            print(f"退出码: {result['exit_code']}")
            print(f"标准输出:\n{result['output']}")
            if result['error']:
                print(f"标准错误:\n{result['error']}")