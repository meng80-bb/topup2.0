#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
步骤1.1：第一次作业提交并检查结果文件
提交第一次作业，并等待检查结果文件生成
"""

import time
import re
from typing import Dict, Any
from topup_ssh import TopupSSH


def step1_1_first_job_submission(
    ssh: TopupSSH,
    round: str,
    date: str,
    submit_job: bool = True,
    max_wait_minutes: int = 25,
) -> Dict[str, Any]:
    """
    提交第一次作业（如果submit_job=True），并检查结果文件

    Args:
        ssh: TopupSSH 实例（必需，自动注入）
        round: 轮次标识符（如 round18），用于构建路径
        date: 任务的日期参数（必需，自动注入）
        submit_job: 是否提交作业，默认True。False时只检查文件不提交
        max_wait_minutes: 最大等待时间（分钟），默认25

    Returns:
        包含以下键的字典：
            - success (bool): 是否成功
            - message (str): 人类可读的消息
            - console_logs (list): 执行过程日志
            - date (str): 使用的日期
            - total_runs (int): 总run数
            - complete_runs (list): 已完成的run号列表
            - incomplete_runs (list): 未完成的run号列表
            - elapsed_time (int): 已等待秒数
    """
    console_logs = []
    console_logs.append("=" * 60)
    console_logs.append("步骤1.1：第一次作业提交并检查结果文件")
    console_logs.append("=" * 60)
    console_logs.append(f"日期参数: {date}")
    console_logs.append(f"提交作业: {submit_job}")

    # 从 round 参数构建路径（参考 config.py）
    base_dir = f"/besfs5/groups/cal/topup/{round}/DataValid"
    inj_sig_time_cal_dir = f"{base_dir}/InjSigTimeCal"
    date_dir = f"{inj_sig_time_cal_dir}/{date}"
    env_script = "~/w720"

    # 提交作业
    if submit_job:
        console_logs.append("\n" + "=" * 60)
        console_logs.append("提交第一次作业")
        console_logs.append("=" * 60)

        try:
            # 删除已存在的日期目录
            console_logs.append(f"\n删除已存在的日期目录 {date}...")
            delete_result = ssh.execute_command(f"rm -rf {date_dir}")
            if delete_result['success']:
                console_logs.append(f"[OK] 已删除日期目录 {date}")
            else:
                console_logs.append(f"⚠ 删除日期目录失败（可能目录不存在），继续执行...")

            # 执行genJob.sh脚本
            console_logs.append(f"\n执行genJob.sh脚本 (日期: {date})...")
            result = ssh.execute_interactive_command(
                f"cd {inj_sig_time_cal_dir} && source {env_script} && ./genJob.sh {date}",
                completion_marker="DONE"
            )

            if not result['success']:
                console_logs.append(f"✗ 执行genJob.sh脚本失败")
                return {
                    'success': False,
                    'message': '执行genJob.sh脚本失败',
                    'error': result.get('error', ''),
                    'console_logs': console_logs,
                    'step_name': 'step1_1_first_job_submission',
                    'date': date,
                }

            # 检查日期目录是否创建
            console_logs.append(f"\n检查日期目录是否创建...")
            check_result = ssh.execute_command(f"ls -la {date_dir}")

            if not check_result['success']:
                console_logs.append(f"✗ 日期目录 {date} 未创建")
                return {
                    'success': False,
                    'message': f'日期目录 {date} 未创建',
                    'error': check_result.get('error', ''),
                    'console_logs': console_logs,
                    'step_name': 'step1_1_first_job_submission',
                    'date': date,
                }

            console_logs.append(f"[OK] 作业提交成功，日期目录 {date} 已创建")
            console_logs.append(f"目录内容:\n{check_result['output']}")

        except Exception as e:
            console_logs.append(f"✗ 作业提交异常: {str(e)}")
            return {
                'success': False,
                'message': f'作业提交异常: {str(e)}',
                'error': str(e),
                'console_logs': console_logs,
                'step_name': 'step1_1_first_job_submission',
                'date': date,
            }
    else:
        console_logs.append("\n" + "=" * 60)
        console_logs.append("跳过作业提交（submit_job=False）")
        console_logs.append("=" * 60)
        console_logs.append(f"将检查已存在的日期目录: {date_dir}")

    # 检查结果文件
    console_logs.append("\n" + "=" * 60)
    console_logs.append("检查结果文件")
    console_logs.append("=" * 60)
    console_logs.append(f"最大等待时间: {max_wait_minutes} 分钟")

    try:
        # 获取作业文件列表，确定run号
        result = ssh.execute_command(f"cd {date_dir} && ls rec*_1.txt 2>/dev/null")

        if not result['success'] or not result['output'].strip():
            console_logs.append(f"✗ 获取作业文件列表失败或无作业文件")
            return {
                'success': False,
                'message': '获取作业文件列表失败或无作业文件',
                'error': result.get('error', '未找到rec*_1.txt文件'),
                'console_logs': console_logs,
                'step_name': 'step1_1_first_job_submission',
                'date': date,
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
            console_logs.append(f"✗ 未找到作业文件")
            return {
                'success': False,
                'message': '未找到作业文件',
                'console_logs': console_logs,
                'step_name': 'step1_1_first_job_submission',
                'date': date,
                'run_numbers': [],
            }

        console_logs.append(f"找到 {len(run_numbers)} 个run号: {run_numbers}")

        # 列出目录中的所有文件（用于诊断）
        console_logs.append(f"\n列出目录中的所有文件:")
        list_result = ssh.execute_command(f"cd {date_dir} && ls -la")
        if list_result['success']:
            console_logs.append(f"目录内容:\n{list_result['output']}")

        # 定期检查文件
        max_wait_seconds = int(max_wait_minutes) * 60
        check_interval = 30
        elapsed_time = 0
        incomplete_runs = run_numbers.copy()


        while elapsed_time < max_wait_seconds and incomplete_runs:
            console_logs.append(f"\n检查进度: {elapsed_time}/{max_wait_seconds}秒")
            console_logs.append(f"未完成的run号: {incomplete_runs}")

            still_incomplete = []

            for run_num in incomplete_runs:
                # 根据 config.py 中的 REQUIRED_FILES_STEP1 定义文件列表
                files_to_check = [
                    f"rec{run_num}_1.txt",
                    f"rec{run_num}_1.txt.bosserr",
                    f"rec{run_num}_1.txt.bosslog",
                    f"InjSigTime_00{run_num}_720.root",
                    f"Interval_run{run_num}.png",
                    f"Interval_run{run_num}.txt",
                ]

                check_cmd = f"cd {date_dir} && ls {' '.join(files_to_check)} 2>/dev/null | wc -l"
                check_result = ssh.execute_command(check_cmd)

                if check_result['success']:
                    file_count = int(check_result['output'].strip())
                    if file_count == len(files_to_check):
                        console_logs.append(f"  ✓ Run {run_num}: 所有文件已生成")
                    else:
                        still_incomplete.append(run_num)
                        console_logs.append(f"  Run {run_num}: {file_count}/{len(files_to_check)} 文件已生成")
                else:
                    still_incomplete.append(run_num)
                    console_logs.append(f"  Run {run_num}: 检查失败")

            incomplete_runs = still_incomplete

            if not incomplete_runs:
                console_logs.append(f"\n[OK] 所有 {len(run_numbers)} 个run号的文件都已生成")
                break

            # 检查数据异常文件（Interval_run0.png）
            anomaly_result = ssh.execute_command(f"cd {date_dir} && ls Interval_run0.png 2>/dev/null")
            if anomaly_result['success'] and anomaly_result['output'].strip():
                console_logs.append(f"✗ 出现了Interval_run0.png，该日期数据不正常")
                return {
                    'success': False,
                    'message': '出现了Interval_run0.png的文件，该日期数据不正常',
                    'error': '数据异常，需要人工干预',
                    'console_logs': console_logs,
                    'step_name': 'step1_1_first_job_submission',
                    'date': date,
                    'anomaly_file': 'Interval_run0.png',
                    'requires_manual_intervention': True,
                }

            time.sleep(check_interval)
            elapsed_time += check_interval

        complete_runs = [r for r in run_numbers if r not in incomplete_runs]

        if incomplete_runs:
            console_logs.append(f"✗ 超时: 等待超过 {max_wait_minutes} 分钟")
            return {
                'success': False,
                'message': f'在 {max_wait_minutes} 分钟内未完成所有文件的生成',
                'console_logs': console_logs,
                'step_name': 'step1_1_first_job_submission',
                'date': date,
                'total_runs': len(run_numbers),
                'complete_runs': complete_runs,
                'incomplete_runs': incomplete_runs,
                'elapsed_time': elapsed_time,
            }

        return {
            'success': True,
            'message': f'成功提交作业并检查结果文件: {date}',
            'console_logs': console_logs,
            'step_name': 'step1_1_first_job_submission',
            'date': date,
            'total_runs': len(run_numbers),
            'complete_runs': complete_runs,
            'incomplete_runs': [],
            'elapsed_time': elapsed_time,
        }

    except Exception as e:
        console_logs.append(f"✗ 检查结果文件异常: {str(e)}")
        return {
            'success': False,
            'message': f'检查结果文件异常: {str(e)}',
            'error': str(e),
            'console_logs': console_logs,
            'step_name': 'step1_1_first_job_submission',
            'date': date,
        }
