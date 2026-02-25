#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
步骤3.1：第三次作业提交并检查shield文件（合并版）
进入search_peak目录，执行./genJob.sh脚本，然后检查shield文件
支持submit_job参数控制是否提交作业
"""

import time
import re
from typing import Dict, Any, Optional
from topup_ssh import TopupSSH
import config


def step3_1_third_job_submission(
    ssh: TopupSSH,
    submit_job: bool = True,
    max_wait_minutes: int = None
) -> Dict[str, Any]:
    """
    提交第三次作业并检查shield文件（合并版）

    进入search_peak目录，执行./genJob.sh脚本，然后检查shield文件

    submit_job参数控制：
    - 如果submit_job=True（默认）：先提交作业，然后检查shield文件
    - 如果submit_job=False：跳过作业提交，直接检查shield文件

    Args:
        ssh: SSH连接实例
        submit_job: 是否提交作业，默认为True。如果为True，提交作业并检查文件；如果为False，只检查文件，不提交作业
        max_wait_minutes: 最大等待时间（分钟），默认使用配置文件中的值（25分钟）

    Returns:
        dict: 执行结果
    """
    print("\n" + "="*60)
    print("步骤3.1：第三次作业提交并检查shield文件（合并版）")
    print("="*60)
    print(f"提交作业: {submit_job}")

    # 使用配置文件中的默认值
    if max_wait_minutes is None:
        max_wait_minutes = config.DEFAULT_MAX_WAIT_MINUTES

    try:
        # 进入search_peak目录
        search_peak_dir = config.SEARCH_PEAK_DIR
        print(f"\n进入search_peak目录: {search_peak_dir}")

        # 阶段1：提交作业（如果submit_job=True）
        if submit_job:
            print(f"\n{'='*60}")
            print("阶段1：提交作业")
            print(f"{'='*60}")

            # 清理目录中的旧文件（以run开头和shield开头的文件）
            print(f"\n清理目录中的旧文件...")
            result_clean = ssh.execute_command(f"cd {search_peak_dir} && rm -f shield* run*")
            print(f"✓ 清理完成")

            # 执行genJob.sh脚本（包含环境激活）
            print(f"\n执行genJob.sh脚本...")
            result = ssh.execute_interactive_command(f"cd {search_peak_dir} && source {config.ENV_SCRIPT} && ./genJob.sh", completion_marker="DONE")

            if not result['success']:
                return {
                    'success': False,
                    'message': '执行genJob.sh脚本失败',
                    'step_name': '步骤3.1：第三次作业提交并检查shield文件',
                    'output': result['output'],
                    'error': result.get('error', '')
                }

            # 检查生成的作业文件
            result_check = ssh.execute_command(f"cd {search_peak_dir} && ls run_*_3.txt")

            print(f"\n✓ 作业提交成功")
            print(f"生成的作业文件:\n{result_check['output']}")
        else:
            print(f"\n{'='*60}")
            print("跳过作业提交（submit_job=False）")
            print(f"{'='*60}")
            print(f"直接检查shield文件...")

        # 阶段2：检查shield文件
        print(f"\n{'='*60}")
        print("阶段2：检查shield文件")
        print(f"{'='*60}")
        print(f"最大等待时间: {max_wait_minutes} 分钟")
        print(f"检查间隔: {config.CHECK_INTERVAL_SECONDS} 秒")

        # 获取作业文件列表
        result = ssh.execute_command(f"cd {search_peak_dir} && ls run_*_3.txt")

        if not result['success']:
            return {
                'success': False,
                'message': '获取作业文件列表失败',
                'step_name': '步骤3.1：第三次作业提交并检查shield文件',
                'output': result['output'],
                'error': result.get('error', '')
            }

        # 解析作业文件列表，提取run号
        # ls输出可能是多行，每行包含多个文件名，用空格分隔
        job_files = []
        for line in result['output'].split('\n'):
            if line.strip():
                # 分割每行中的多个文件名
                job_files.extend(line.strip().split())
        run_numbers = []
        for filename in job_files:
            match = re.match(r'run_(\d+)_3\.txt', filename)
            if match:
                run_numbers.append(match.group(1))

        if not run_numbers:
            return {
                'success': False,
                'message': '未找到作业文件',
                'step_name': '步骤3.1：第三次作业提交并检查shield文件',
                'run_numbers': []
            }

        print(f"找到 {len(run_numbers)} 个作业文件")

        # 定期检查文件
        max_wait_seconds = max_wait_minutes * 60
        check_interval = config.CHECK_INTERVAL_SECONDS  # 使用配置文件中的检查间隔
        elapsed_time = 0

        incomplete_runs = run_numbers.copy()

        while elapsed_time < max_wait_seconds and incomplete_runs:
            print(f"\n检查进度: {elapsed_time}/{max_wait_seconds}秒")
            print(f"未完成的run号: {incomplete_runs}")

            # 检查每个run号的shield文件
            complete_runs = []
            still_incomplete = []

            for run_num in incomplete_runs:
                shield_file = f"shield_run{run_num}.txt"
                result_check = ssh.execute_command(f"cd {search_peak_dir} && ls {shield_file} 2>/dev/null")

                if result_check['success'] and shield_file in result_check['output']:
                    complete_runs.append(run_num)
                else:
                    still_incomplete.append(run_num)
                    print(f"  Run {run_num}: shield文件未生成")

            incomplete_runs = still_incomplete

            if not incomplete_runs:
                print(f"\n✓ 所有 {len(run_numbers)} 个shield文件都已生成")
                break

            # 等待检查间隔
            time.sleep(check_interval)
            elapsed_time += check_interval

        # 返回结果
        if incomplete_runs:
            return {
                'success': False,
                'message': f'在 {max_wait_minutes} 分钟内未完成所有shield文件的生成',
                'step_name': '步骤3.1：第三次作业提交并检查shield文件',
                'total_runs': len(run_numbers),
                'complete_runs': run_numbers[:-len(incomplete_runs)],
                'incomplete_runs': incomplete_runs,
                'elapsed_time': elapsed_time
            }
        else:
            return {
                'success': True,
                'message': f'成功提交作业并检查shield文件',
                'step_name': '步骤3.1：第三次作业提交并检查shield文件',
                'total_runs': len(run_numbers),
                'complete_runs': run_numbers,
                'incomplete_runs': [],
                'elapsed_time': elapsed_time
            }

    except Exception as e:
        return {
            'success': False,
            'message': f'作业提交或检查异常: {str(e)}',
            'step_name': '步骤3.1：第三次作业提交并检查shield文件',
            'error': str(e)
        }


if __name__ == "__main__":
    # 测试步骤3.1
    with TopupSSH() as ssh:
        if ssh.connected:
            # 测试1：提交作业并检查（默认）
            print("\n测试1：提交作业并检查（submit_job=True）")
            result = step3_1_third_job_submission(ssh, submit_job=True)
            print("\n" + "="*60)
            print("步骤3.1执行结果:")
            print("="*60)
            print(f"成功: {result['success']}")
            print(f"消息: {result['message']}")
            if 'total_runs' in result:
                print(f"总run数: {result['total_runs']}")
                print(f"完成run数: {result['complete_runs']}")
                print(f"未完成run数: {result['incomplete_runs']}")

            # 测试2：只检查，不提交作业
            print("\n\n测试2：只检查，不提交作业（submit_job=False）")
            result2 = step3_1_third_job_submission(ssh, submit_job=False)
            print("\n" + "="*60)
            print("步骤3.1执行结果:")
            print("="*60)
            print(f"成功: {result2['success']}")
            print(f"消息: {result2['message']}")