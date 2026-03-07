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
    round: str,
    date: str,
) -> Dict[str, Any]:
    """
    移动文件

    将 InjSigTime*.root 移动到 calibConst 目录
    将 Interval*.png 移动到 Interval_plot 目录

    Args:
        ssh: TopupSSH 实例（必需，自动注入）
        round: 轮次标识符（如 round18），用于构建路径
        date: 任务的日期参数（必需，自动注入）

    Returns:
        包含以下键的字典：
            - success (bool): 是否成功
            - message (str): 人类可读的消息
            - console_logs (list): 执行过程日志
            - date (str): 使用的日期
            - remaining_files (str): 移动后日期目录剩余文件列表
    """
    console_logs = []
    console_logs.append("=" * 60)
    console_logs.append("步骤1.2：移动文件")
    console_logs.append("=" * 60)
    console_logs.append(f"日期参数: {date}")

    # 从 round 参数构建路径（参考 config.py）
    base_dir = f"/besfs5/groups/cal/topup/{round}/DataValid"
    inj_sig_time_cal_dir = f"{base_dir}/InjSigTimeCal"
    calib_const_dir = f"{inj_sig_time_cal_dir}/calibConst"
    interval_plot_dir = f"{inj_sig_time_cal_dir}/Interval_plot"
    date_dir = f"{inj_sig_time_cal_dir}/{date}"

    console_logs.append(f"\n日期目录: {date_dir}")

    try:
        # 移动root文件
        console_logs.append(f"\n移动root文件到calibConst目录...")
        result1 = ssh.execute_command(f"cd {date_dir} && mv InjSigTime*.root {calib_const_dir}")

        if not result1['success']:
            console_logs.append(f"✗ 移动root文件失败")
            return {
                'success': False,
                'message': '移动root文件失败',
                'error': result1.get('error', ''),
                'console_logs': console_logs,
                'step_name': 'step1_2_move_files',
                'date': date,
            }

        console_logs.append(f"[OK] root文件移动成功")

        # 移动png文件
        console_logs.append(f"\n移动png文件到Interval_plot目录...")
        result2 = ssh.execute_command(f"cd {date_dir} && mv Interval*.png {interval_plot_dir}")

        if not result2['success']:
            console_logs.append(f"✗ 移动png文件失败")
            return {
                'success': False,
                'message': '移动png文件失败',
                'error': result2.get('error', ''),
                'console_logs': console_logs,
                'step_name': 'step1_2_move_files',
                'date': date,
            }

        console_logs.append(f"[OK] png文件移动成功")

        # 验证文件移动
        console_logs.append(f"\n验证文件移动...")
        result3 = ssh.execute_command(f"cd {date_dir} && ls -la")
        remaining_files = result3['output'] if result3['success'] else ''
        console_logs.append(f"日期目录剩余文件:\n{remaining_files}")
        console_logs.append(f"\n[OK] 文件移动完成")

        return {
            'success': True,
            'message': f'文件移动成功: {date}',
            'console_logs': console_logs,
            'step_name': 'step1_2_move_files',
            'date': date,
            'remaining_files': remaining_files,
        }

    except Exception as e:
        console_logs.append(f"✗ 移动文件异常: {str(e)}")
        return {
            'success': False,
            'message': f'移动文件异常: {str(e)}',
            'error': str(e),
            'console_logs': console_logs,
            'step_name': 'step1_2_move_files',
            'date': date,
        }
