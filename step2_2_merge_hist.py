#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
步骤2.2：合并hist文件
进入日期目录，执行./mergeHist.sh脚本
"""

from typing import Dict, Any
from topup_ssh import TopupSSH
import config


def step2_2_merge_hist(ssh: TopupSSH, date: str) -> Dict[str, Any]:
    """
    合并hist文件
    
    进入日期目录，执行./mergeHist.sh脚本
    
    Args:
        ssh: SSH连接实例
        date: 日期参数（如250624）
        
    Returns:
        dict: 执行结果
    """
    print("\n" + "="*60)
    print("步骤2.2：合并hist文件")
    print("="*60)
    
    try:
        # 进入日期目录
        date_dir = config.get_date_dir(config.DATA_VALID_DIR, date)
        print(f"\n进入日期目录: {date_dir}")

        # 执行mergeHist.sh脚本
        print(f"\n执行mergeHist.sh脚本...")
        result = ssh.execute_command(f"cd {date_dir} && ./mergeHist.sh")

        if not result['success']:
            return {
                'success': False,
                'message': '执行mergeHist.sh脚本失败',
                'step_name': '步骤2.2：合并hist文件',
                'date': date,
                'output': result['output'],
                'error': result.get('error', '')
            }

        print(f"\n✓ hist文件合并成功")
        print(f"输出:\n{result['output']}")
        
        return {
            'success': True,
            'message': 'hist文件合并成功',
            'step_name': '步骤2.2：合并hist文件',
            'date': date,
            'output': result['output']
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'合并hist文件异常: {str(e)}',
            'step_name': '步骤2.2：合并hist文件',
            'date': date,
            'error': str(e)
        }


if __name__ == "__main__":
    # 测试步骤2.2
    with TopupSSH() as ssh:
        if ssh.connected:
            # 使用测试日期
            result = step2_2_merge_hist(ssh, "250624")
            print("\n" + "="*60)
            print("步骤2.2执行结果:")
            print("="*60)
            print(f"成功: {result['success']}")
            print(f"消息: {result['message']}")