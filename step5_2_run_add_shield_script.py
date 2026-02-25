#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
步骤5.2：运行add_shield.sh脚本
运行ETS_cut目录下的add_shield.sh脚本
"""

from typing import Dict, Any
from topup_ssh import TopupSSH
import config


def step5_2_run_add_shield_script(ssh: TopupSSH, date: str = None) -> Dict[str, Any]:
    """
    运行add_shield.sh脚本

    运行ETS_cut目录下的add_shield.sh脚本

    Args:
        ssh: SSH连接实例
        date: 日期参数（保留接口兼容性）

    Returns:
        dict: 执行结果
    """
    print("\n" + "="*60)
    print("步骤5.2：运行add_shield.sh脚本")
    print("="*60)

    try:
        # 进入ETS_cut目录
        ets_cut_dir = config.ETS_CUT_DIR
        print(f"\n进入ETS_cut目录: {ets_cut_dir}")

        # 执行add_shield.sh脚本
        print(f"\n执行add_shield.sh脚本...")
        result = ssh.execute_command(f"cd {ets_cut_dir} && ./add_shield.sh")

        if not result['success']:
            return {
                'success': False,
                'message': '执行add_shield.sh脚本失败',
                'step_name': '步骤5.2：运行add_shield.sh脚本',
                'output': result['output'],
                'error': result.get('error', '')
            }

        print(f"\n✓ add_shield.sh脚本执行成功")
        print(f"输出:\n{result['output']}")

        return {
            'success': True,
            'message': 'add_shield.sh脚本执行成功',
            'step_name': '步骤5.2：运行add_shield.sh脚本',
            'output': result['output']
        }

    except Exception as e:
        return {
            'success': False,
            'message': f'运行add_shield.sh脚本异常: {str(e)}',
            'step_name': '步骤5.2：运行add_shield.sh脚本',
            'error': str(e)
        }


if __name__ == "__main__":
    # 测试步骤5.2
    with TopupSSH() as ssh:
        if ssh.connected:
            result = step5_2_run_add_shield_script(ssh)
            print("\n" + "="*60)
            print("步骤5.2执行结果:")
            print("="*60)
            print(f"成功: {result['success']}")
            print(f"消息: {result['message']}")