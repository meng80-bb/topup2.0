#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
步骤1.1：第一次作业提交并检查结果文件
基于提供的日期参数提交作业，并检查结果文件是否生成完成
"""

import time
import re
from typing import Dict, Any, List, Optional
from topup_ssh import TopupSSH


def step1_1_first_job_submission(
    ssh: TopupSSH,
    date: str,
    round: str,
    submit_job: bool = True,
    max_wait_minutes: int = 25
) -> Dict[str, Any]:
    """
    提交第一次作业并检查结果文件

    根据提供的日期和轮次信息，提交作业并监控结果文件生成。

    Args:
        ssh: TopupSSH 实例，用于执行远程命令
        date: 日期参数（如250624），必需参数
        round: 轮次标识符，用于构建目录路径
        submit_job: 是否提交作业，默认为True
        max_wait_minutes: 最大等待时间（分钟），默认25分钟

    Returns:
        包含以下键的字典：
            - success (bool, 必需): 是否成功
            - message (str, 必需): 人类可读的消息
            - step_name (str, 推荐): 步骤名称
            - date (str, 推荐): 使用的日期
            - total_runs (int, 可选): 总run数
            - complete_runs (list, 可选): 完成的run数
            - incomplete_runs (list, 可选): 未完成的run数
            - elapsed_time (int, 可选): 耗时（秒）
            - error (str, 可选): 失败时的错误详情
            - requires_manual_intervention (bool, 可选): 是否需要人工干预
    """
    print("\n" + "="*60)
    print("步骤1.1：第一次作业提交并检查结果文件")
    print("="*60)
    print(f"日期: {date}")
    print(f"轮次: {round}")
    print(f"提交作业: {submit_job}")
    print(f"最大等待时间: {max_wait_minutes} 分钟")

    # 计算路径
    data_dir = f"/bes3fs/offline/data/cal/{round}"
    base_dir = f"/besfs5/groups/cal/topup/{round}/DataValid"
    inj_sig_time_cal_dir = f"{base_dir}/InjSigTimeCal"
    date_dir = f"{inj_sig_time_cal_dir}/{date}"
    env_script = "~/w720"

    # 检查数据目录是否存在
    print(f"\n检查数据目录是否存在...")
    data_check = ssh.execute_command(f"ls -d {data_dir}/{date} 2>/dev/null")
    if not data_check['success'] or not data_check['output'].strip():
        return {
            'success': False,
            'message': f'数据目录不存在: {data_dir}/{date}',
            'step_name': 'step1_1',
            'date': date,
            'error': '指定的日期数据不存在'
        }

    # 提交作业
    if submit_job:
        print("\n" + "="*60)
        print("提交第一次作业")
        print("="*60)

        try:
            # 删除已存在的日期目录（自动重新提交模式）
            print(f"\n删除已存在的日期目录 {date}...")
            delete_result = ssh.execute_command(f"rm -rf {date_dir}")
            if delete_result['success']:
                print(f"✓ 已删除日期目录 {date}")
            else:
                print(f"⚠ 删除日期目录失败（可能目录不存在），继续执行...")

            # 执行genJob.sh脚本
            print(f"\n执行genJob.sh脚本 (日期: {date})...")
            result = ssh.execute_interactive_command(
                f"cd {inj_sig_time_cal_dir} && source {env_script} && ./genJob.sh {date}",
                completion_marker="DONE"
            )

            if not result['success']:
                return {
                    'success': False,
                    'message': '执行genJob.sh脚本失败',
                    'step_name': 'step1_1',
                    'date': date,
                    'output': result['output'],
                    'error': result.get('error', '')
                }

            # 检查日期目录是否创建
            print(f"\n检查日期目录是否创建...")
            check_result = ssh.execute_command(f"ls -la {date_dir}")

            if not check_result['success']:
                return {
                    'success': False,
                    'message': f'日期目录 {date} 未创建',
                    'step_name': 'step1_1',
                    'date': date,
                    'output': check_result['output'],
                    'error': check_result.get('error', '')
                }

            print(f"\n✓ 作业提交成功，日期目录 {date} 已创建")
            print(f"目录内容:\n{check_result['output']}")

        except Exception as e:
            return {
                'success': False,
                'message': f'作业提交异常: {str(e)}',
                'step_name': 'step1_1',
                'date': date,
                'error': str(e)
            }
    else:
        print("\n" + "="*60)
        print("跳过作业提交（submit_job=False）")
        print("="*60)
        print(f"将检查已存在的日期目录: {date_dir}")

    # 检查结果文件
    print("\n" + "="*60)
    print("检查结果文件")
    print("="*60)
    print(f"最大等待时间: {max_wait_minutes} 分钟")
    print(f"检查间隔: 30 秒")

    try:
        print(f"\n进入日期目录: {date_dir}")

        # 获取作业文件列表，确定run号
        result = ssh.execute_command(f"cd {date_dir} && ls rec*_1.txt")

        if not result['success']:
            return {
                'success': False,
                'message': '获取作业文件列表失败',
                'step_name': 'step1_1',
                'date': date,
                'output': result['output'],
                'error': result.get('error', '')
            }

        # 解析run号列表
        rec_files = []
        for line in result['output'].split('\n'):
            if line.strip():
                rec_files.extend(line.strip().split())

        run_numbers = []
        for filename in rec_files:
            match = re.match(r'rec(\d+)_1\.txt', filename)
            if match:
                run_numbers.append(match.group(1))

        if not run_numbers:
            return {
                'success': False,
                'message': '未找到作业文件',
                'step_name': 'step1_1',
                'date': date,
                'run_numbers': []
            }

        print(f"找到 {len(run_numbers)} 个run号: {run_numbers}")

        # 定期检查文件
        max_wait_seconds = max_wait_minutes * 60
        check_interval = 30
        elapsed_time = 0
        incomplete_runs = run_numbers.copy()

        # 先列出目录中的所有文件（用于诊断）
        print(f"\n列出目录中的所有文件:")
        list_cmd = f"cd {date_dir} && ls -la"
        result = ssh.execute_command(list_cmd)
        if result['success']:
            print(f"目录内容:\n{result['output']}")

        while elapsed_time < max_wait_seconds and incomplete_runs:
            print(f"\n检查进度: {elapsed_time}/{max_wait_seconds}秒")
            print(f"未完成的run号: {incomplete_runs}")

            # 检查每个run号的文件
            complete_runs = []
            still_incomplete = []

            for run_num in incomplete_runs:
                # 检查6个必需文件
                files_to_check = [
                    f"rec{run_num}_1.txt",
                    f"rec{run_num}_1.txt.bosserr",
                    f"rec{run_num}_1.txt.bosslog",
                    f"rec{run_num}_1.root",
                    f"rec{run_num}_1.png",
                    f"rec{run_num}_1.txt"
                ]

                # 检查文件是否存在
                check_cmd = f"cd {date_dir} && ls {' '.join(files_to_check)} 2>/dev/null | wc -l"
                file_check_result = ssh.execute_command(check_cmd)

                if file_check_result['success']:
                    file_count = int(file_check_result['output'].strip())
                    if file_count >= 3:  # 至少检查rec文件、bosserr、bosslog
                        complete_runs.append(run_num)
                    else:
                        still_incomplete.append(run_num)
                        print(f"  Run {run_num}: {file_count}/6 文件已生成")
                else:
                    still_incomplete.append(run_num)
                    print(f"  Run {run_num}: 检查失败")

            incomplete_runs = still_incomplete

            if not incomplete_runs:
                print(f"\n✓ 所有 {len(run_numbers)} 个run号的文件都已生成")
                break

            # 检查是否出现了Interval_run0.png文件（数据异常）
            check_anomaly_cmd = f"cd {date_dir} && ls Interval_run0.png 2>/dev/null"
            anomaly_result = ssh.execute_command(check_anomaly_cmd)
            if anomaly_result['success'] and anomaly_result['output'].strip():
                return {
                    'success': False,
                    'message': '出现了Interval_run0.png的文件，该日期数据不正常',
                    'step_name': 'step1_1',
                    'date': date,
                    'anomaly_file': 'Interval_run0.png',
                    'requires_manual_intervention': True
                }

            # 等待30秒
            time.sleep(check_interval)
            elapsed_time += check_interval

        # 返回结果
        if incomplete_runs:
            return {
                'success': False,
                'message': f'在 {max_wait_minutes} 分钟内未完成所有文件的生成',
                'step_name': 'step1_1',
                'date': date,
                'total_runs': len(run_numbers),
                'complete_runs': run_numbers[:-len(incomplete_runs)],
                'incomplete_runs': incomplete_runs,
                'elapsed_time': elapsed_time
            }
        else:
            return {
                'success': True,
                'message': f'成功提交作业并检查结果文件: {date}',
                'step_name': 'step1_1',
                'date': date,
                'total_runs': len(run_numbers),
                'complete_runs': run_numbers,
                'incomplete_runs': [],
                'elapsed_time': elapsed_time
            }

    except Exception as e:
        return {
            'success': False,
            'message': f'检查结果文件异常: {str(e)}',
            'step_name': 'step1_1',
            'date': date,
            'error': str(e)
        }