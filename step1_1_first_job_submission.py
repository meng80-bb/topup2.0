#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
步骤1.1：第一次作业提交并检查结果文件（合并版）
对比两个目录找出最小的未处理日期，然后提交第一次作业，并检查结果文件
支持date参数、进度文件管理和submit_job参数控制是否提交作业
"""

import time
import re
from typing import Dict, Any, List, Optional
from topup_ssh import TopupSSH
import config


def step1_1_first_job_submission(
    ssh: TopupSSH,
    date: Optional[str] = None,
    submit_job: bool = True,
    max_wait_minutes: int = None
) -> Dict[str, Any]:
    """
    确定日期参数，提交第一次作业（如果submit_job=True），并检查结果文件

    如果传递了date参数：
    1. 首先将date参数写入进度文件
    2. 如果submit_job=True，使用进度文件中的date参数提交作业
    3. 检查结果文件

    如果不传入date参数：
    1. 使用原来的步骤1.1逻辑，对比两个日期获取date参数
    2. 将获取的date参数写入进度文件
    3. 如果submit_job=True，使用进度文件中的date参数提交作业
    4. 检查结果文件

    Args:
        ssh: SSH连接实例
        date: 日期参数（如250624），可选
        submit_job: 是否提交作业，默认为True。如果为True，提交作业并检查文件；如果为False，只检查文件，不提交作业
        max_wait_minutes: 最大等待时间（分钟），默认使用配置文件中的值

    Returns:
        dict: 执行结果，包含selected_date（选中的日期）
    """
    print("\n" + "="*60)
    print("步骤1.1：第一次作业提交并检查结果文件（合并版）")
    print("="*60)
    print(f"提交作业: {submit_job}")

    # 使用配置文件中的默认值
    if max_wait_minutes is None:
        max_wait_minutes = config.DEFAULT_MAX_WAIT_MINUTES

    # 确定使用的日期
    selected_date = None

    if date is not None:
        # 情况1：传递了date参数，直接使用
        print(f"\n使用传入的日期参数: {date}")
        selected_date = date
        # 将日期写入进度文件
        config.save_step_progress('1.1', selected_date)
        print(f"✓ 已将日期 {selected_date} 写入进度文件")
    else:
        # 情况2：未传递date参数，使用原来的逻辑对比获取
        print("\n未传入日期参数，开始对比获取日期...")

        try:
            # 获取已处理数据目录的日期列表
            print("\n获取已处理数据目录...")
            result1 = ssh.execute_command(f"ls -1 {config.INJ_SIG_TIME_CAL_DIR}")

            if not result1['success']:
                return {
                    'success': False,
                    'message': '获取已处理数据目录失败',
                    'step_name': '步骤1.1：第一次作业提交并检查结果文件',
                    'output': result1['output'],
                    'error': result1.get('error', '')
                }

            # 解析已处理日期列表（只保留6位数字的目录名）
            processed_dates = [line.strip() for line in result1['output'].split('\n')
                             if line.strip() and re.match(r'^\d{6}$', line.strip())]
            print(f"已处理日期: {processed_dates}")

            # 获取所有可用数据目录的日期列表
            print("\n获取所有可用数据目录...")
            result2 = ssh.execute_command(f"ls -1 {config.DATA_DIR}")

            if not result2['success']:
                return {
                    'success': False,
                    'message': '获取所有可用数据目录失败',
                    'step_name': '步骤1.1：第一次作业提交并检查结果文件',
                    'output': result2['output'],
                    'error': result2.get('error', '')
                }

            # 解析所有可用日期列表（只保留6位数字的目录名）
            all_dates = [line.strip() for line in result2['output'].split('\n')
                        if line.strip() and re.match(r'^\d{6}$', line.strip())]
            print(f"所有可用日期: {all_dates}")

            # 找出未处理的日期
            unprocessed_dates = [date_item for date_item in all_dates if date_item not in processed_dates]
            print(f"未处理日期: {unprocessed_dates}")

            if not unprocessed_dates:
                return {
                    'success': False,
                    'message': '没有找到未处理的日期',
                    'step_name': '步骤1.1：第一次作业提交并检查结果文件',
                    'processed_dates': processed_dates,
                    'all_dates': all_dates,
                    'unprocessed_dates': [],
                    'selected_date': None
                }

            # 选择最小的未处理日期
            selected_date = min(unprocessed_dates)
            print(f"\n✓ 选中的日期: {selected_date}")

            # 将获取的日期写入进度文件
            config.save_step_progress('1.1', selected_date)
            print(f"✓ 已将日期 {selected_date} 写入进度文件")

        except Exception as e:
            return {
                'success': False,
                'message': f'数据确认异常: {str(e)}',
                'step_name': '步骤1.1：第一次作业提交并检查结果文件',
                'error': str(e)
            }

    # 如果submit_job=True或None（根据日期目录是否存在决定），提交第一次作业
    # submit_job=None时：如果日期目录存在则只检查，不存在则提交
    if submit_job is None:
        # 检查日期目录是否存在
        date_dir = config.get_date_dir(config.INJ_SIG_TIME_CAL_DIR, selected_date)
        check_result = ssh.execute_command(f"ls -d {date_dir} 2>/dev/null")
        if check_result['success'] and check_result['output'].strip():
            # 目录存在，只检查文件
            submit_job = False
            print(f"\n检测到日期目录已存在，将只检查文件而不提交作业")
        else:
            # 目录不存在，提交作业
            submit_job = True
            print(f"\n检测到日期目录不存在，将提交作业")

    if submit_job:
        print("\n" + "="*60)
        print("提交第一次作业")
        print("="*60)
        print(f"使用进度文件中的日期: {selected_date}")

        try:
            # 删除已存在的日期目录（自动重新提交模式）
            print(f"\n删除已存在的日期目录 {selected_date}...")
            date_dir = config.get_date_dir(config.INJ_SIG_TIME_CAL_DIR, selected_date)
            delete_result = ssh.execute_command(f"rm -rf {date_dir}")
            if delete_result['success']:
                print(f"✓ 已删除日期目录 {selected_date}")
            else:
                print(f"⚠ 删除日期目录失败（可能目录不存在），继续执行...")

            # 执行genJob.sh脚本
            print(f"\n执行genJob.sh脚本 (日期: {selected_date})...")
            result2 = ssh.execute_interactive_command(
                f"cd {config.INJ_SIG_TIME_CAL_DIR} && source {config.ENV_SCRIPT} && ./genJob.sh {selected_date}",
                completion_marker="DONE"
            )

            if not result2['success']:
                return {
                    'success': False,
                    'message': '执行genJob.sh脚本失败',
                    'step_name': '步骤1.1：第一次作业提交并检查结果文件',
                    'date': selected_date,
                    'output': result2['output'],
                    'error': result2.get('error', '')
                }

            # 检查日期目录是否创建
            print(f"\n检查日期目录是否创建...")
            result3 = ssh.execute_command(f"ls -la {date_dir}")

            if not result3['success']:
                return {
                    'success': False,
                    'message': f'日期目录 {selected_date} 未创建',
                    'step_name': '步骤1.1：第一次作业提交并检查结果文件',
                    'date': selected_date,
                    'output': result3['output'],
                    'error': result3.get('error', '')
                }

            print(f"\n✓ 作业提交成功，日期目录 {selected_date} 已创建")
            print(f"目录内容:\n{result3['output']}")

        except Exception as e:
            return {
                'success': False,
                'message': f'作业提交异常: {str(e)}',
                'step_name': '步骤1.1：第一次作业提交并检查结果文件',
                'date': selected_date,
                'error': str(e)
            }
    else:
        print("\n" + "="*60)
        print("跳过作业提交（submit_job=False）")
        print("="*60)
        date_dir = config.get_date_dir(config.INJ_SIG_TIME_CAL_DIR, selected_date)
        print(f"将检查已存在的日期目录: {date_dir}")

    # 检查结果文件
    print("\n" + "="*60)
    print("检查结果文件")
    print("="*60)
    print(f"最大等待时间: {max_wait_minutes} 分钟")
    print(f"检查间隔: {config.CHECK_INTERVAL_SECONDS} 秒")

    try:
        print(f"\n进入日期目录: {date_dir}")

        # 获取作业文件列表，确定run号
        result = ssh.execute_command(f"cd {date_dir} && ls rec*_1.txt")

        if not result['success']:
            return {
                'success': False,
                'message': '获取作业文件列表失败',
                'step_name': '步骤1.1：第一次作业提交并检查结果文件',
                'date': selected_date,
                'output': result['output'],
                'error': result.get('error', '')
            }

        # 解析run号列表
        # ls输出可能是多行，每行包含多个文件名，用空格分隔
        rec_files = []
        for line in result['output'].split('\n'):
            if line.strip():
                # 分割每行中的多个文件名
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
                'step_name': '步骤1.1：第一次作业提交并检查结果文件',
                'date': selected_date,
                'run_numbers': []
            }

        print(f"找到 {len(run_numbers)} 个run号: {run_numbers}")

        # 定期检查文件
        max_wait_seconds = max_wait_minutes * 60
        check_interval = config.CHECK_INTERVAL_SECONDS  # 使用配置文件中的检查间隔
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
                # 检查6个必需文件（使用配置文件中的格式）
                files_to_check = [
                    f"rec{run_num}_1.txt",
                    f"rec{run_num}_1.txt.bosserr",
                    f"rec{run_num}_1.txt.bosslog",
                    config.REQUIRED_FILES_STEP1["root_file"].format(run=run_num),
                    config.REQUIRED_FILES_STEP1["png_file"].format(run=run_num),
                    config.REQUIRED_FILES_STEP1["txt_file"].format(run=run_num)
                ]

                # 检查文件是否存在
                check_cmd = f"cd {date_dir} && ls {' '.join(files_to_check)} 2>/dev/null | wc -l"
                result = ssh.execute_command(check_cmd)

                if result['success']:
                    file_count = int(result['output'].strip())
                    if file_count == len(files_to_check):
                        complete_runs.append(run_num)
                    else:
                        still_incomplete.append(run_num)
                        print(f"  Run {run_num}: {file_count}/{len(files_to_check)} 文件已生成")
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
                    'step_name': '步骤1.1：第一次作业提交并检查结果文件',
                    'date': selected_date,
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
                'step_name': '步骤1.1：第一次作业提交并检查结果文件',
                'date': selected_date,
                'total_runs': len(run_numbers),
                'complete_runs': run_numbers[:-len(incomplete_runs)],
                'incomplete_runs': incomplete_runs,
                'elapsed_time': elapsed_time
            }
        else:
            return {
                'success': True,
                'message': f'成功提交作业并检查结果文件: {selected_date}',
                'step_name': '步骤1.1：第一次作业提交并检查结果文件',
                'date': selected_date,
                'total_runs': len(run_numbers),
                'complete_runs': run_numbers,
                'incomplete_runs': [],
                'elapsed_time': elapsed_time
            }

    except Exception as e:
        return {
            'success': False,
            'message': f'检查结果文件异常: {str(e)}',
            'step_name': '步骤1.1：第一次作业提交并检查结果文件',
            'date': selected_date,
            'error': str(e)
        }


if __name__ == "__main__":
    # 测试步骤1.1
    with TopupSSH() as ssh:
        if ssh.connected:
            # 测试1：提交作业并检查（默认）
            print("\n测试1：提交作业并检查（submit_job=True）")
            result = step1_1_first_job_submission(ssh, "250624", submit_job=True)
            print("\n" + "="*60)
            print("步骤1.1执行结果:")
            print("="*60)
            print(f"成功: {result['success']}")
            print(f"消息: {result['message']}")
            if 'date' in result:
                print(f"使用的日期: {result['date']}")
            if 'total_runs' in result:
                print(f"总run数: {result['total_runs']}")
                print(f"完成run数: {result['complete_runs']}")
                print(f"未完成run数: {result['incomplete_runs']}")

            # 测试2：只检查，不提交作业
            print("\n\n测试2：只检查，不提交作业（submit_job=False）")
            result2 = step1_1_first_job_submission(ssh, "250624", submit_job=False)
            print("\n" + "="*60)
            print("步骤1.1执行结果:")
            print("="*60)
            print(f"成功: {result2['success']}")
            print(f"消息: {result2['message']}")
            if 'date' in result2:
                print(f"使用的日期: {result2['date']}")