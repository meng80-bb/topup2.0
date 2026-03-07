#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
步骤1.3：IST分析
检查每个run号的Interval文件中的interval值，验证是否都等于15000000
"""

import re
from typing import Dict, Any
from topup_ssh import TopupSSH


def step1_3_ist_analysis(
    ssh: TopupSSH,
    round: str,
    date: str,
    check: bool = True,
) -> Dict[str, Any]:
    """
    IST分析

    检查每个run号的Interval文件中的interval值
    如果所有run号的ist值都等于15000000，将结果追加到interval.txt文件
    如果有任何run号的ist值不等于15000000且check=True，停止运行并提示人工干预

    Args:
        ssh: TopupSSH 实例（必需，自动注入）
        round: 轮次标识符（如 round18），用于构建路径
        date: 任务的日期参数（必需，自动注入）
        check: 是否检查IST值是否等于15000000，默认True。False时只记录不验证

    Returns:
        包含以下键的字典：
            - success (bool): 是否成功
            - message (str): 人类可读的消息
            - console_logs (list): 执行过程日志
            - date (str): 使用的日期
            - ist_results (dict): 每个run号对应的IST值列表
            - invalid_runs (list): IST值不正常的run号列表
            - interval_file_content (str): 追加后interval.txt末尾内容
    """
    console_logs = []
    console_logs.append("=" * 60)
    console_logs.append("步骤1.3：IST分析")
    console_logs.append("=" * 60)
    console_logs.append(f"日期参数: {date}")
    console_logs.append(f"检查IST值: {check}")

    # 从 round 参数构建路径（参考 config.py）
    base_dir = f"/besfs5/groups/cal/topup/{round}/DataValid"
    inj_sig_time_cal_dir = f"{base_dir}/InjSigTimeCal"
    date_dir = f"{inj_sig_time_cal_dir}/{date}"
    global_interval_file = f"{inj_sig_time_cal_dir}/interval.txt"

    console_logs.append(f"\n日期目录: {date_dir}")

    try:
        # 获取Interval文件列表
        result = ssh.execute_command(f"cd {date_dir} && ls Interval_run*.txt 2>/dev/null")

        if not result['success'] or not result['output'].strip():
            console_logs.append(f"✗ 获取Interval文件列表失败")
            return {
                'success': False,
                'message': '获取Interval文件列表失败',
                'error': result.get('error', '未找到Interval_run*.txt文件'),
                'console_logs': console_logs,
                'step_name': 'step1_3_ist_analysis',
                'date': date,
            }

        # 解析run号列表
        interval_files = []
        for line in result['output'].split('\n'):
            if line.strip():
                interval_files.extend(line.strip().split())

        run_numbers = []
        for filename in interval_files:
            match = re.match(r'Interval_run(\d+)\.txt', filename)
            if match:
                run_numbers.append(match.group(1))

        if not run_numbers:
            console_logs.append(f"✗ 未找到Interval文件")
            return {
                'success': False,
                'message': '未找到Interval文件',
                'console_logs': console_logs,
                'step_name': 'step1_3_ist_analysis',
                'date': date,
                'run_numbers': [],
            }

        console_logs.append(f"找到 {len(run_numbers)} 个Interval文件")

        # 检查每个run号的ist值
        ist_results = {}
        invalid_runs = []

        for run_num in run_numbers:
            console_logs.append(f"\n检查Run {run_num}的Interval文件...")
            filename = f"Interval_run{run_num}.txt"

            result1 = ssh.execute_command(f"cd {date_dir} && grep interval_From_DB {filename}")
            result2 = ssh.execute_command(f"cd {date_dir} && grep interval_before_sorting {filename}")
            result3 = ssh.execute_command(f"cd {date_dir} && grep interval_after_sorting {filename}")

            ist_values = []
            for res in [result1, result2, result3]:
                if res['success']:
                    match = re.search(r'(\d+)', res['output'])
                    if match:
                        ist_values.append(int(match.group(1)))

            ist_results[run_num] = ist_values
            console_logs.append(f"  IST值: {ist_values}")

            if check:
                if ist_values and all(ist == 15000000 for ist in ist_values):
                    console_logs.append(f"  ✓ Run {run_num}的IST值正常")
                else:
                    console_logs.append(f"  ✗ Run {run_num}的IST值不等于15000000")
                    invalid_runs.append(run_num)
            else:
                console_logs.append(f"  已记录Run {run_num}的IST值（check=False，不进行验证）")

        # 有无效run号且check=True，返回错误
        if check and invalid_runs:
            console_logs.append(f"\n✗ 以下run号的IST值不正常: {invalid_runs}")
            return {
                'success': False,
                'message': 'IST的值不全为15000000，不为非topup模式',
                'console_logs': console_logs,
                'step_name': 'step1_3_ist_analysis',
                'date': date,
                'ist_results': ist_results,
                'invalid_runs': invalid_runs,
                'requires_manual_intervention': True,
            }

        # 所有run号的ist值都正常，追加到interval.txt
        console_logs.append(f"\n所有run号的IST值都正常，将结果追加到interval.txt文件...")

        sorted_runs = sorted(run_numbers, key=int)
        content_to_append = '\n'.join([f"{run} 15000000" for run in sorted_runs])

        result_append = ssh.execute_command(f"echo '{content_to_append}' >> {global_interval_file}")

        if not result_append['success']:
            console_logs.append(f"✗ 追加到interval.txt文件失败")
            return {
                'success': False,
                'message': '追加到全局interval.txt文件失败',
                'error': result_append.get('error', ''),
                'console_logs': console_logs,
                'step_name': 'step1_3_ist_analysis',
                'date': date,
                'ist_results': ist_results,
            }

        # 验证追加内容
        tail_lines = len(sorted_runs)
        result_verify = ssh.execute_command(f"tail -{tail_lines} {global_interval_file}")
        interval_file_content = result_verify['output'] if result_verify['success'] else ''

        console_logs.append(f"\n[OK] IST分析完成")
        console_logs.append(f"全局interval.txt文件最后{tail_lines}行:\n{interval_file_content}")

        return {
            'success': True,
            'message': 'IST分析完成，所有run号的IST值都等于15000000',
            'console_logs': console_logs,
            'step_name': 'step1_3_ist_analysis',
            'date': date,
            'ist_results': ist_results,
            'invalid_runs': [],
            'interval_file_content': interval_file_content,
        }

    except Exception as e:
        console_logs.append(f"✗ IST分析异常: {str(e)}")
        return {
            'success': False,
            'message': f'IST分析异常: {str(e)}',
            'error': str(e),
            'console_logs': console_logs,
            'step_name': 'step1_3_ist_analysis',
            'date': date,
        }
