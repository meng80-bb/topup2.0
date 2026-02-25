#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
步骤1.3：IST分析
检查每个run号的Interval文件中的interval值，验证是否都等于15000000
"""

import config
import re
from typing import Dict, Any, List
from topup_ssh import TopupSSH


def step1_3_ist_analysis(ssh: TopupSSH, date: str, check: bool = True) -> Dict[str, Any]:
    """
    IST分析

    检查每个run号的Interval文件中的interval值
    如果所有run号的ist值都等于15000000，将结果追加到interval.txt文件
    如果有任何run号的ist值不等于15000000且check=True，停止运行并提示人工干预

    Args:
        ssh: SSH连接实例
        date: 日期参数（如250624）
        check: 是否检查IST值是否等于15000000，默认为True。如果为True，IST值不等于15000000时会返回错误；如果为False，不进行检查

    Returns:
        dict: 执行结果
    """
    print("\n" + "="*60)
    print("步骤1.3：IST分析")
    print("="*60)

    try:
        # 进入日期目录
        date_dir = config.get_date_dir(config.INJ_SIG_TIME_CAL_DIR, date)
        print(f"\n进入日期目录: {date_dir}")

        # 获取Interval文件列表
        result = ssh.execute_command(f"cd {date_dir} && ls Interval_run*.txt")

        if not result['success']:
            return {
                'success': False,
                'message': '获取Interval文件列表失败',
                'step_name': '步骤1.3：IST分析',
                'date': date,
                'output': result['output'],
                'error': result.get('error', '')
            }

        # 解析run号列表
        # ls输出可能是多行，每行包含多个文件名，用空格分隔
        interval_files = []
        for line in result['output'].split('\n'):
            if line.strip():
                # 分割每行中的多个文件名
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
                'step_name': '步骤1.3：IST分析',
                'date': date,
                'run_numbers': []
            }

        print(f"找到 {len(run_numbers)} 个Interval文件")

        # 检查每个run号的ist值
        ist_results = {}
        invalid_runs = []

        for run_num in run_numbers:
            print(f"\n检查Run {run_num}的Interval文件...")

            # 执行grep命令获取ist值
            filename = f"Interval_run{run_num}.txt"

            # 获取interval_From_DB
            result1 = ssh.execute_command(f"cd {date_dir} && grep interval_From_DB {filename}")
            # 获取interval_before_sorting
            result2 = ssh.execute_command(f"cd {date_dir} && grep interval_before_sorting {filename}")
            # 获取interval_after_sorting
            result3 = ssh.execute_command(f"cd {date_dir} && grep interval_after_sorting {filename}")

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
                'step_name': '步骤1.3：IST分析',
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
        global_interval_file = f"{config.INJ_SIG_TIME_CAL_DIR}/interval.txt"
        result_append = ssh.execute_command(f"echo '{content_to_append}' >> {global_interval_file}")

        if not result_append['success']:
            return {
                'success': False,
                'message': '追加到全局interval.txt文件失败',
                'step_name': '步骤1.3：IST分析',
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
            'step_name': '步骤1.3：IST分析',
            'date': date,
            'ist_results': ist_results,
            'interval_file_content': result_verify['output']
        }

    except Exception as e:
        return {
            'success': False,
            'message': f'IST分析异常: {str(e)}',
            'step_name': '步骤1.3：IST分析',
            'date': date,
            'error': str(e)
        }


if __name__ == "__main__":
    # 测试步骤1.3
    with TopupSSH() as ssh:
        if ssh.connected:
            # 使用测试日期
            result = step1_3_ist_analysis(ssh, "250624")
            print("\n" + "="*60)
            print("步骤1.3执行结果:")
            print("="*60)
            print(f"成功: {result['success']}")
            print(f"消息: {result['message']}")
            if 'invalid_runs' in result and result['invalid_runs']:
                print(f"无效run号: {result['invalid_runs']}")
            if 'interval_file_content' in result:
                print(f"interval.txt内容:\n{result['interval_file_content']}")