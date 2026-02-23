#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
步骤1.2：移动文件
将root文件移动到../calibConst目录，将png文件移动到../Interval_plot目录
"""

from typing import Dict, Any
from topup_ssh import TopupSSH
import config


def step1_2_move_files(ssh: TopupSSH, date: str) -> Dict[str, Any]:
    """
    移动文件

    将root文件移动到../calibConst目录
    将png文件移动到../Interval_plot目录

    Args:
        ssh: SSH连接实例
        date: 日期参数（如250624）

    Returns:
        dict: 执行结果
    """
    print("\n" + "="*60)
    print("步骤1.2：移动文件")
    print("="*60)

    try:
        # 进入日期目录
        date_dir = config.get_date_dir(config.INJ_SIG_TIME_CAL_DIR, date)
        print(f"\n进入日期目录: {date_dir}")

        # 移动root文件
        print("\n移动root文件到calibConst目录...")
        result1 = ssh.execute_command(f"cd {date_dir} && mv InjSigTime*.root {config.CALIB_CONST_DIR}")

        if not result1['success']:
            return {
                'success': False,
                'message': '移动root文件失败',
                'step_name': '步骤1.2：移动文件',
                'date': date,
                'output': result1['output'],
                'error': result1.get('error', '')
            }

        print("✓ root文件移动成功")

        # 移动png文件
        print("\n移动png文件到Interval_plot目录...")
        result2 = ssh.execute_command(f"cd {date_dir} && mv Interval*.png {config.INTERVAL_PLOT_DIR}")

        if not result2['success']:
            return {
                'success': False,
                'message': '移动png文件失败',
                'step_name': '步骤1.2：移动文件',
                'date': date,
                'output': result2['output'],
                'error': result2.get('error', '')
            }

        print("✓ png文件移动成功")

        # 验证文件移动
        print("\n验证文件移动...")
        result3 = ssh.execute_command(f"cd {date_dir} && ls -la")
        print(f"日期目录剩余文件:\n{result3['output']}")

        print("\n✓ 文件移动完成")

        return {
            'success': True,
            'message': '文件移动成功',
            'step_name': '步骤1.2：移动文件',
            'date': date,
            'remaining_files': result3['output']
        }

    except Exception as e:
        return {
            'success': False,
            'message': f'移动文件异常: {str(e)}',
            'step_name': '步骤1.2：移动文件',
            'date': date,
            'error': str(e)
        }


if __name__ == "__main__":
    # 测试步骤1.2
    with TopupSSH() as ssh:
        if ssh.connected:
            # 使用测试日期
            result = step1_2_move_files(ssh, "250624")
            print("\n" + "="*60)
            print("步骤1.2执行结果:")
            print("="*60)
            print(f"成功: {result['success']}")
            print(f"消息: {result['message']}")