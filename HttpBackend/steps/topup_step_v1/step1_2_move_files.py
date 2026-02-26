#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
步骤1.2：移动文件
将root文件移动到calibConst目录，将png文件移动到Interval_plot目录
"""

from typing import Dict, Any
from topup_ssh import TopupSSH


def step1_2_move_files(
    ssh: TopupSSH,
    date: str,
    round: str
) -> Dict[str, Any]:
    """
    移动文件

    将root文件移动到calibConst目录
    将png文件移动到Interval_plot目录

    Args:
        ssh: TopupSSH 实例，用于执行远程命令
        date: 日期参数（如250624），必需参数
        round: 轮次标识符，用于构建目录路径

    Returns:
        包含以下键的字典：
            - success (bool, 必需): 是否成功
            - message (str, 必需): 人类可读的消息
            - step_name (str, 推荐): 步骤名称
            - date (str, 推荐): 使用的日期
            - remaining_files (str, 可选): 剩余文件列表
            - error (str, 可选): 失败时的错误详情
    """
    print("\n" + "="*60)
    print("步骤1.2：移动文件")
    print("="*60)
    print(f"日期: {date}")
    print(f"轮次: {round}")

    # 计算路径
    base_dir = f"/besfs5/groups/cal/topup/{round}/DataValid"
    inj_sig_time_cal_dir = f"{base_dir}/InjSigTimeCal"
    date_dir = f"{inj_sig_time_cal_dir}/{date}"
    calib_const_dir = f"{base_dir}/calibConst"
    interval_plot_dir = f"{base_dir}/Interval_plot"

    try:
        print(f"\n进入日期目录: {date_dir}")

        # 移动root文件
        print("\n移动root文件到calibConst目录...")
        result1 = ssh.execute_command(
            f"cd {date_dir} && mv InjSigTime*.root {calib_const_dir}"
        )

        if not result1['success']:
            return {
                'success': False,
                'message': '移动root文件失败',
                'step_name': 'step1_2',
                'date': date,
                'output': result1['output'],
                'error': result1.get('error', '')
            }

        print("✓ root文件移动成功")

        # 移动png文件
        print("\n移动png文件到Interval_plot目录...")
        result2 = ssh.execute_command(
            f"cd {date_dir} && mv Interval*.png {interval_plot_dir}"
        )

        if not result2['success']:
            return {
                'success': False,
                'message': '移动png文件失败',
                'step_name': 'step1_2',
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
            'step_name': 'step1_2',
            'date': date,
            'remaining_files': result3['output']
        }

    except Exception as e:
        return {
            'success': False,
            'message': f'移动文件异常: {str(e)}',
            'step_name': 'step1_2',
            'date': date,
            'error': str(e)
        }