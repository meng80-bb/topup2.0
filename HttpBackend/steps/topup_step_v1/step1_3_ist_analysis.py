#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
步骤1.3：IST分析
检查每个run号的Interval文件中的interval值，验证是否都等于15000000
"""

import re
from typing import Dict, Any, List
from topup_ssh import TopupSSH


def step1_3_ist_analysis(
    ssh: TopupSSH,
    date: str,
    round: str,
    check: bool = True
) -> Dict[str, Any]:
    """
    IST分析

    检查每个run号的Interval文件中的interval值
    如果所有run号的ist值都等于15000000，将结果追加到interval.txt文件
    如果有任何run号的ist值不等于15000000且check=True，停止运行并提示人工干预

    Args:
        ssh: TopupSSH 实例，用于执行远程命令
        date: 日期参数（如250624），必需参数
        round: 轮次标识符，用于构建目录路径
        check: 是否检查IST值是否等于15000000，默认为True。
               如果为True，IST值不等于15000000时会返回错误；
               如果为False，不进行检查

    Returns:
        包含以下键的字典：
            - success (bool, 必需): 是否成功
            - message (str, 必需): 人类可读的消息
            - step_name (str, 推荐): 步骤名称
            - date (str, 推荐): 使用的日期
            - ist_results (dict, 可选): IST分析结果
            - invalid_runs (list, 可选): 无效的run号列表
            - interval_file_content (str, 可选): interval.txt文件内容
            - error (str, 可选): 失败时的错误详情
            - requires_manual_intervention (bool, 可选): 是否需要人工干预
    """
    print("\n" + "="*60)
    print("步骤1.3：IST分析")
    print("="*60)
    print(f"日期: {date}")
    print(f"轮次: {round}")
    print(f"检查IST值: {check}")

    # 计算路径
    base_dir = f"/besfs5/groups/cal/topup/{round}/DataValid"
    inj_sig_time_cal_dir = f"{base_dir}/InjSigTimeCal"
    date_dir = f"{inj_sig_time_cal_dir}/{date}"
    global_interval_file = f"{inj_sig_time_cal_dir}/interval.txt"

    try:
        print(f"\n进入日期目录: {date_dir}")

        # 获取Interval文件列表
        result = ssh.execute_command(f"cd {date_dir} && ls Interval_run*.txt")

        if not result['success']:
            return {
                'success': False,
                'message': '获取Interval文件列表失败',
                'step_name': 'step1_3',
                'date': date,
                'output': result['output'],
                'error': result.get('error', '')
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
            return {
                'success': False,
                'message': '未找到Interval文件',
                'step_name': 'step1_3',
                'date': date,
                'run_numbers': []
            }

        print(f"找到 {len(run_numbers)} 个Interval文件")

        # 检查每个run号的ist值
        ist_results = {}
        invalid_runs = []

        for run_num in run_numbers:
            print(f"\n检查Run {run_num}的Interval文件...")

            filename = f"Interval_run{run_num}.txt"

            # 获取interval_From_DB
            result1 = ssh.execute_command(
                f"cd {date_dir} && grep interval_From_DB {filename}"
            )
            # 获取interval_before_sorting
            result2 = ssh.execute_command(
                f"cd {date_dir} && grep interval_before_sorting {filename}"
            )
            # 获取interval_after_sorting
            result3 = ssh.execute_command(
                f"cd {date_dir} && grep interval_after_sorting {filename}"
            )

            # 解析ist值
            ist_values = []
            for res in [result1, result2, result3]:
                if res['success']:
                    match = re.search(r'(\d+)', res['output'])
                    if match:
                        ist_values.append(int(match.group(1)))

            ist_results[run_num] = ist_values
            print(f"  IST值: {ist_values}")

            # 检查是否所有ist值都等于15000000（仅在check=True时）
            if check:
                if ist_values and all(ist == 15000000 for ist in ist_values):
                    print(f"  ✓ Run {run_num}的IST值正常")
                else:
                    print(f"  ✗ Run {run_num}的IST值不等于15000000")
                    invalid_runs.append(run_num)
            else:
                # check=False时，只记录不检查
                if ist_values:
                    print(f"  已检查Run {run_num}的IST值（check=False，不进行验证）")

        # 如果有无效的run号且check=True，返回错误
        if check and invalid_runs:
            return {
                'success': False,
                'message': 'IST的值不全为15000000，不为非topup模式',
                'step_name': 'step1_3',
                'date': date,
                'ist_results': ist_results,
                'invalid_runs': invalid_runs,
                'requires_manual_intervention': True
            }

        # 所有run号的ist值都正常，将结果追加到interval.txt文件
        print(f"\n所有run号的IST值都正常，将结果追加到interval.txt文件...")

        # 按run号排序
        sorted_runs = sorted(run_numbers, key=int)

        # 构建要追加的内容
        content_to_append = '\n'.join([f"{run} 15000000" for run in sorted_runs])

        # 追加到全局的interval.txt文件
        result_append = ssh.execute_command(
            f"echo '{content_to_append}' >> {global_interval_file}"
        )

        if not result_append['success']:
            return {
                'success': False,
                'message': '追加到全局interval.txt文件失败',
                'step_name': 'step1_3',
                'date': date,
                'ist_results': ist_results,
                'output': result_append['output'],
                'error': result_append.get('error', '')
            }

        # 验证全局interval.txt文件内容（根据run号数量检查相应行数）
        tail_lines = len(sorted_runs)
        result_verify = ssh.execute_command(f"tail -{tail_lines} {global_interval_file}")

        print(f"\n✓ IST分析完成")
        print(f"全局interval.txt文件最后{tail_lines}行:\n{result_verify['output']}")

        return {
            'success': True,
            'message': 'IST分析完成，所有run号的IST值都等于15000000',
            'step_name': 'step1_3',
            'date': date,
            'ist_results': ist_results,
            'interval_file_content': result_verify['output']
        }

    except Exception as e:
        return {
            'success': False,
            'message': f'IST分析异常: {str(e)}',
            'step_name': 'step1_3',
            'date': date,
            'error': str(e)
        }