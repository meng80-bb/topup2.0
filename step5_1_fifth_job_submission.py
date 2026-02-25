#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
步骤5.1：第五次作业提交并检查cut和all文件（合并版）
进入ETS_cut目录，执行./genJob.sh脚本，然后检查cut和all文件
"""

import time
import re
from typing import Dict, Any, Optional
from topup_ssh import TopupSSH
import config


def step5_1_fifth_job_submission(ssh: TopupSSH, date: str, submit_job: bool = True, max_wait_minutes: Optional[int] = None) -> Dict[str, Any]:
    """
    第五次作业提交并检查cut和all文件（合并版）

    Args:
        ssh: SSH连接实例
        date: 日期参数（如250519）
        submit_job: 是否提交作业，默认为True
                   - True: 先提交作业，然后检查文件
                   - False: 跳过提交，直接检查文件
        max_wait_minutes: 最大等待时间（分钟），默认使用配置文件中的值（25分钟）

    Returns:
        dict: 执行结果
    """
    print("\n" + "="*60)
    print("步骤5.1：第五次作业提交并检查cut和all文件（合并版）")
    print("="*60)
    print(f"submit_job参数: {submit_job}")
    print(f"日期参数: {date}")

    # 使用配置文件中的默认值
    if max_wait_minutes is None:
        max_wait_minutes = config.DEFAULT_MAX_WAIT_MINUTES

    print(f"最大等待时间: {max_wait_minutes} 分钟")
    print(f"检查间隔: {config.CHECK_INTERVAL_SECONDS} 秒")

    try:
        # 进入ETS_cut目录
        ets_cut_dir = config.ETS_CUT_DIR
        print(f"\n进入ETS_cut目录: {ets_cut_dir}")

        # 步骤A：提交作业（如果submit_job=True）
        if submit_job:
            print(f"\n[步骤A] 提交作业...")

            # 删除以plot和run开头的旧文件
            print(f"清理旧文件（删除以plot和run开头的文件）...")
            result_clean = ssh.execute_command(f"cd {ets_cut_dir} && rm -f plot* run*")
            if result_clean['success']:
                print(f"✓ 旧文件清理完成")
            else:
                print(f"⚠ 旧文件清理警告: {result_clean.get('error', '')}")

            print(f"执行genJob.sh脚本...")
            result = ssh.execute_interactive_command(f"cd {ets_cut_dir} && source {config.ENV_SCRIPT} && ./genJob.sh", completion_marker="DONE")

            if not result['success']:
                return {
                    'success': False,
                    'message': '执行genJob.sh脚本失败',
                    'step_name': '步骤5.1：第五次作业提交并检查cut和all文件',
                    'date': date,
                    'submit_job': submit_job,
                    'output': result['output'],
                    'error': result.get('error', '')
                }

            # 检查生成的作业文件
            result_check = ssh.execute_command(f"cd {ets_cut_dir} && ls plot_ETS_*.txt")

            print(f"\n✓ 作业提交成功")
            print(f"生成的作业文件:\n{result_check['output']}")
        else:
            print(f"\n[步骤A] 跳过作业提交（submit_job=False）")
            print(f"直接进入文件检查阶段...")

        # 步骤B：检查cut和all文件
        print(f"\n[步骤B] 检查cut和all文件...")

        # 获取作业文件列表
        result = ssh.execute_command(f"cd {ets_cut_dir} && ls plot_ETS_*.txt")

        if not result['success']:
            return {
                'success': False,
                'message': '获取作业文件列表失败',
                'step_name': '步骤5.1：第五次作业提交并检查cut和all文件',
                'date': date,
                'submit_job': submit_job,
                'output': result['output'],
                'error': result.get('error', '')
            }

        # 解析作业文件列表，提取run号
        job_files = []
        for line in result['output'].split('\n'):
            if line.strip():
                job_files.extend(line.strip().split())
        run_numbers = []
        for filename in job_files:
            match = re.match(r'plot_ETS_(\d+)\.txt', filename)
            if match:
                run_numbers.append(match.group(1))

        if not run_numbers:
            return {
                'success': False,
                'message': '未找到作业文件',
                'step_name': '步骤5.1：第五次作业提交并检查cut和all文件',
                'date': date,
                'submit_job': submit_job,
                'run_numbers': []
            }

        print(f"找到 {len(run_numbers)} 个作业文件")

        # 定期检查文件
        max_wait_seconds = max_wait_minutes * 60
        check_interval = config.CHECK_INTERVAL_SECONDS
        elapsed_time = 0

        incomplete_runs = run_numbers.copy()

        while elapsed_time < max_wait_seconds and incomplete_runs:
            print(f"\n检查进度: {elapsed_time}/{max_wait_seconds}秒")
            print(f"未完成的run号: {incomplete_runs}")

            # 检查每个run号的cut和all文件
            complete_runs = []
            still_incomplete = []

            for run_num in incomplete_runs:
                cut_file = f"run{run_num}_cut.png"
                all_file = f"run{run_num}_total.png"

                result_cut = ssh.execute_command(f"cd {ets_cut_dir} && ls {cut_file} 2>/dev/null")
                result_all = ssh.execute_command(f"cd {ets_cut_dir} && ls {all_file} 2>/dev/null")

                cut_exists = result_cut['success'] and cut_file in result_cut['output']
                all_exists = result_all['success'] and all_file in result_all['output']

                if cut_exists and all_exists:
                    complete_runs.append(run_num)
                else:
                    still_incomplete.append(run_num)
                    print(f"  Run {run_num}: cut文件={'✓' if cut_exists else '✗'}, all文件={'✓' if all_exists else '✗'}")

            incomplete_runs = still_incomplete

            if not incomplete_runs:
                print(f"\n✓ 所有 {len(run_numbers)} 个cut和all文件都已生成")
                break

            # 等待指定间隔
            time.sleep(check_interval)
            elapsed_time += check_interval

        # 返回结果
        if incomplete_runs:
            return {
                'success': False,
                'message': f'在 {max_wait_minutes} 分钟内未完成所有cut和all文件的生成',
                'step_name': '步骤5.1：第五次作业提交并检查cut和all文件',
                'date': date,
                'submit_job': submit_job,
                'total_runs': len(run_numbers),
                'complete_runs': run_numbers[:-len(incomplete_runs)],
                'incomplete_runs': incomplete_runs,
                'elapsed_time': elapsed_time
            }
        else:
            return {
                'success': True,
                'message': f'所有 {len(run_numbers)} 个cut和all文件都已生成',
                'step_name': '步骤5.1：第五次作业提交并检查cut和all文件',
                'date': date,
                'submit_job': submit_job,
                'total_runs': len(run_numbers),
                'complete_runs': run_numbers,
                'incomplete_runs': [],
                'elapsed_time': elapsed_time
            }

    except Exception as e:
        return {
            'success': False,
            'message': f'步骤5.1执行异常: {str(e)}',
            'step_name': '步骤5.1：第五次作业提交并检查cut和all文件',
            'date': date,
            'submit_job': submit_job,
            'error': str(e)
        }


if __name__ == "__main__":
    # 测试步骤5.1
    with TopupSSH() as ssh:
        if ssh.connected:
            # 测试提交作业并检查
            result = step5_1_fifth_job_submission(ssh, "250519", submit_job=True)
            print("\n" + "="*60)
            print("步骤5.1执行结果（submit_job=True）:")
            print("="*60)
            print(f"成功: {result['success']}")
            print(f"消息: {result['message']}")

            # 测试跳过提交，只检查
            result = step5_1_fifth_job_submission(ssh, "250519", submit_job=False)
            print("\n" + "="*60)
            print("步骤5.1执行结果（submit_job=False）:")
            print("="*60)
            print(f"成功: {result['success']}")
            print(f"消息: {result['message']}")