#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
步骤2.4：检查png文件
每30秒检查hist目录下是否每一个hist文件对应一个png文件
"""

import time
import re
from typing import Dict, Any
from topup_ssh import TopupSSH
import config


def step2_4_check_png_files(ssh: TopupSSH, max_wait_minutes: int = None) -> Dict[str, Any]:
    """
    检查png文件

    每30秒检查hist目录下是否每一个hist文件对应一个png文件

    Args:
        ssh: SSH连接实例
        max_wait_minutes: 最大等待时间（分钟），默认使用配置文件中的值（10分钟）

    Returns:
        dict: 执行结果
    """
    # 使用配置文件中的默认值
    if max_wait_minutes is None:
        max_wait_minutes = config.DEFAULT_MAX_WAIT_MINUTES

    print("\n" + "="*60)
    print("步骤2.4：检查png文件")
    print("="*60)
    print(f"最大等待时间: {max_wait_minutes} 分钟")
    print(f"检查间隔: {config.CHECK_INTERVAL_SECONDS} 秒")

    try:
        # 使用配置文件中的目录
        hist_dir = config.HIST_DIR
        print(f"\n进入hist目录: {hist_dir}")

        # 获取hist文件列表
        result = ssh.execute_command(f"cd {hist_dir} && ls hist*.root")

        if not result['success']:
            return {
                'success': False,
                'message': '获取hist文件列表失败',
                'step_name': '步骤2.4：检查png文件',
                'output': result['output'],
                'error': result.get('error', '')
            }

        # 解析hist文件列表
        # ls输出可能是多行，每行包含多个文件名，用空格分隔
        hist_files = []
        for line in result['output'].split('\n'):
            if line.strip():
                # 分割每行中的多个文件名
                hist_files.extend(line.strip().split())

        if not hist_files:
            return {
                'success': False,
                'message': '未找到hist文件',
                'step_name': '步骤2.4：检查png文件',
                'hist_files': []
            }

        print(f"找到 {len(hist_files)} 个hist文件")

        # 定期检查文件
        max_wait_seconds = max_wait_minutes * 60
        check_interval = config.CHECK_INTERVAL_SECONDS  # 使用配置文件中的检查间隔
        elapsed_time = 0

        while elapsed_time < max_wait_seconds:
            print(f"\n检查进度: {elapsed_time}/{max_wait_seconds}秒")

            # 获取png文件列表
            result_png = ssh.execute_command(f"cd {hist_dir} && ls check*.png")

            if result_png['success']:
                # ls输出可能是多行，每行包含多个文件名，用空格分隔
                png_files = []
                for line in result_png['output'].split('\n'):
                    if line.strip():
                        # 分割每行中的多个文件名
                        png_files.extend(line.strip().split())
                print(f"  已生成 {len(png_files)}/{len(hist_files)} 个png文件")

                if len(png_files) >= len(hist_files):
                    print(f"\n✓ 所有 {len(hist_files)} 个png文件都已生成")
                    return {
                        'success': True,
                        'message': f'所有 {len(hist_files)} 个png文件都已生成',
                        'step_name': '步骤2.4：检查png文件',
                        'total_hist_files': len(hist_files),
                        'total_png_files': len(png_files),
                        'elapsed_time': elapsed_time
                    }

            # 等待检查间隔
            time.sleep(check_interval)
            elapsed_time += check_interval

        # 超时
        return {
            'success': False,
            'message': f'在 {max_wait_minutes} 分钟内未完成所有png文件的生成',
            'step_name': '步骤2.4：检查png文件',
            'total_hist_files': len(hist_files),
            'total_png_files': len(png_files) if 'png_files' in locals() else 0,
            'elapsed_time': elapsed_time
        }

    except Exception as e:
        return {
            'success': False,
            'message': f'检查png文件异常: {str(e)}',
            'step_name': '步骤2.4：检查png文件',
            'error': str(e)
        }


if __name__ == "__main__":
    # 测试步骤2.4
    with TopupSSH() as ssh:
        if ssh.connected:
            result = step2_4_check_png_files(ssh)
            print("\n" + "="*60)
            print("步骤2.4执行结果:")
            print("="*60)
            print(f"成功: {result['success']}")
            print(f"消息: {result['message']}")
