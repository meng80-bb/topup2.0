#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
步骤2.3：生成png文件
进入hist目录，执行./01go.sh脚本
"""

from typing import Dict, Any
from topup_ssh import TopupSSH
import config


def step2_3_generate_png(ssh: TopupSSH) -> Dict[str, Any]:
    """
    生成png文件
    
    进入hist目录，执行./01go.sh脚本
    
    Args:
        ssh: SSH连接实例
        
    Returns:
        dict: 执行结果
    """
    print("\n" + "="*60)
    print("步骤2.3：生成png文件")
    print("="*60)
    
    try:
        # 进入hist目录
        hist_dir = config.HIST_DIR
        print(f"\n进入hist目录: {hist_dir}")

        # 执行01go.sh脚本
        print(f"\n执行01go.sh脚本...")
        result = ssh.execute_command(f"cd {hist_dir} && ./01go.sh")

        if not result['success']:
            return {
                'success': False,
                'message': '执行01go.sh脚本失败',
                'step_name': '步骤2.3：生成png文件',
                'output': result['output'],
                'error': result.get('error', '')
            }

        print(f"\n✓ png文件生成成功")
        print(f"输出:\n{result['output']}")
        
        return {
            'success': True,
            'message': 'png文件生成成功',
            'step_name': '步骤2.3：生成png文件',
            'output': result['output']
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'生成png文件异常: {str(e)}',
            'step_name': '步骤2.3：生成png文件',
            'error': str(e)
        }


if __name__ == "__main__":
    # 测试步骤2.3
    with TopupSSH() as ssh:
        if ssh.connected:
            result = step2_3_generate_png(ssh)
            print("\n" + "="*60)
            print("步骤2.3执行结果:")
            print("="*60)
            print(f"成功: {result['success']}")
            print(f"消息: {result['message']}")