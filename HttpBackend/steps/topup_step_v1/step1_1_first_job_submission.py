#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
步骤1.1：第一次作业提交并检查结果文件

将原始脚本转换为符合 HttpBackend Step 函数规范的格式。
将复杂逻辑拆分为多个辅助函数以提高可读性和可维护性。
"""

import time
import re
from typing import Dict, Any, List, Optional, Tuple
from topup_ssh import TopupSSH
import config


def _get_processed_dates(ssh: TopupSSH) -> Tuple[bool, List[str], str]:
    """
    获取已处理数据目录的日期列表

    Args:
        ssh: SSH连接实例

    Returns:
        Tuple[是否成功, 日期列表, 错误信息]
    """
    result = ssh.execute_command(f"ls -1 {config.INJ_SIG_TIME_CAL_DIR}")

    if not result['success']:
        return False, [], result.get('error', '获取已处理数据目录失败')

    # 解析已处理日期列表（只保留6位数字的目录名）
    processed_dates = [
        line.strip() for line in result['output'].split('\n')
        if line.strip() and re.match(r'^\d{6}$', line.strip())
    ]

    return True, processed_dates, ''


def _get_all_available_dates(ssh: TopupSSH) -> Tuple[bool, List[str], str]:
    """
    获取所有可用数据目录的日期列表

    Args:
        ssh: SSH连接实例

    Returns:
        Tuple[是否成功, 日期列表, 错误信息]
    """
    result = ssh.execute_command(f"ls -1 {config.DATA_DIR}")

    if not result['success']:
        return False, [], result.get('error', '获取所有可用数据目录失败')

    # 解析所有可用日期列表（只保留6位数字的目录名）
    all_dates = [
        line.strip() for line in result['output'].split('\n')
        if line.strip() and re.match(r'^\d{6}$', line.strip())
    ]

    return True, all_dates, ''


def _find_smallest_unprocessed_date(
    processed_dates: List[str],
    all_dates: List[str]
) -> Tuple[bool, Optional[str], str]:
    """
    找出最小的未处理日期

    Args:
        processed_dates: 已处理的日期列表
        all_dates: 所有可用日期列表

    Returns:
        Tuple[是否成功, 选中的日期, 错误信息]
    """
    # 找出未处理的日期
    unprocessed_dates = [
        date_item for date_item in all_dates
        if date_item not in processed_dates
    ]

    if not unprocessed_dates:
        return False, None, '没有找到未处理的日期'

    # 选择最小的未处理日期
    selected_date = min(unprocessed_dates)
    return True, selected_date, ''


def _determine_date_parameter(
    ssh: TopupSSH,
    date: Optional[str]
) -> Dict[str, Any]:
    """
    确定使用的日期参数

    如果提供了 date 参数，直接使用并保存到进度文件。
    否则，通过对比已处理和未处理日期来找出最小的未处理日期。

    Args:
        ssh: SSH连接实例
        date: 可选的日期参数

    Returns:
        dict: 包含 success, date (成功时), 或 error (失败时)
    """
    if date is not None:
        # 情况1：传递了date参数，直接使用
        print(f"使用传入的日期参数: {date}")
        config.save_step_progress('1.1', date)
        print(f"✓ 已将日期 {date} 写入进度文件")

        return {
            'success': True,
            'date': date
        }

    # 情况2：未传递date参数，使用原来的逻辑对比获取
    print("未传入日期参数，开始对比获取日期...")

    try:
        # 获取已处理数据目录的日期列表
        print("\n获取已处理数据目录...")
        success, processed_dates, error = _get_processed_dates(ssh)

        if not success:
            return {
                'success': False,
                'message': '获取已处理数据目录失败',
                'error': error
            }

        print(f"已处理日期: {processed_dates}")

        # 获取所有可用数据目录的日期列表
        print("\n获取所有可用数据目录...")
        success, all_dates, error = _get_all_available_dates(ssh)

        if not success:
            return {
                'success': False,
                'message': '获取所有可用数据目录失败',
                'error': error
            }

        print(f"所有可用日期: {all_dates}")

        # 找出未处理的日期
        print(f"未处理日期: {[d for d in all_dates if d not in processed_dates]}")

        success, selected_date, error = _find_smallest_unprocessed_date(
            processed_dates,
            all_dates
        )

        if not success:
            return {
                'success': False,
                'message': error,
                'processed_dates': processed_dates,
                'all_dates': all_dates
            }

        print(f"\n✓ 选中的日期: {selected_date}")

        # 将获取的日期写入进度文件
        config.save_step_progress('1.1', selected_date)
        print(f"✓ 已将日期 {selected_date} 写入进度文件")

        return {
            'success': True,
            'date': selected_date
        }

    except Exception as e:
        return {
            'success': False,
            'message': f'数据确认异常: {str(e)}',
            'error': str(e)
        }


def _submit_first_job(
    ssh: TopupSSH,
    selected_date: str
) -> Dict[str, Any]:
    """
    提交第一次作业

    删除已存在的日期目录，然后执行 genJob.sh 脚本提交作业。

    Args:
        ssh: SSH连接实例
        selected_date: 选中的日期

    Returns:
        dict: 执行结果
    """
    print("\n" + "="*60)
    print("提交第一次作业")
    print("="*60)
    print(f"使用日期: {selected_date}")

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
        result = ssh.execute_interactive_command(
            f"cd {config.INJ_SIG_TIME_CAL_DIR} && source {config.ENV_SCRIPT} && ./genJob.sh {selected_date}",
            completion_marker="DONE"
        )

        if not result['success']:
            return {
                'success': False,
                'message': '执行genJob.sh脚本失败',
                'date': selected_date,
                'output': result['output'],
                'error': result.get('error', '')
            }

        # 检查日期目录是否创建
        print(f"\n检查日期目录是否创建...")
        check_result = ssh.execute_command(f"ls -la {date_dir}")

        if not check_result['success']:
            return {
                'success': False,
                'message': f'日期目录 {selected_date} 未创建',
                'date': selected_date,
                'output': check_result['output'],
                'error': check_result.get('error', '')
            }

        print(f"\n✓ 作业提交成功，日期目录 {selected_date} 已创建")
        print(f"目录内容:\n{check_result['output']}")

        return {
            'success': True,
            'date': selected_date,
            'date_dir': date_dir
        }

    except Exception as e:
        return {
            'success': False,
            'message': f'作业提交异常: {str(e)}',
            'date': selected_date,
            'error': str(e)
        }


def _get_run_numbers(ssh: TopupSSH, date_dir: str) -> Tuple[bool, List[str], str]:
    """
    从日期目录中获取 run 号列表

    Args:
        ssh: SSH连接实例
        date_dir: 日期目录路径

    Returns:
        Tuple[是否成功, run号列表, 错误信息]
    """
    result = ssh.execute_command(f"cd {date_dir} && ls rec*_1.txt")

    if not result['success']:
        return False, [], result.get('error', '获取作业文件列表失败')

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
        return False, [], '未找到作业文件'

    return True, run_numbers, ''


def _check_files_for_run(
    ssh: TopupSSH,
    date_dir: str,
    run_num: str
) -> Tuple[bool, int]:
    """
    检查单个 run 号的所有必需文件

    Args:
        ssh: SSH连接实例
        date_dir: 日期目录路径
        run_num: run 号

    Returns:
        Tuple[是否完成, 已生成的文件数量]
    """
    # 检查6个必需文件
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
        is_complete = file_count == len(files_to_check)
        return is_complete, file_count

    return False, 0


def _check_anomaly_file(ssh: TopupSSH, date_dir: str) -> bool:
    """
    检查是否存在异常文件（Interval_run0.png）

    Args:
        ssh: SSH连接实例
        date_dir: 日期目录路径

    Returns:
        bool: True 表示检测到异常
    """
    check_cmd = f"cd {date_dir} && ls Interval_run0.png 2>/dev/null"
    result = ssh.execute_command(check_cmd)

    return result['success'] and result['output'].strip()


def _wait_for_job_completion(
    ssh: TopupSSH,
    date_dir: str,
    run_numbers: List[str],
    max_wait_minutes: int
) -> Dict[str, Any]:
    """
    等待作业完成并定期检查结果文件

    Args:
        ssh: SSH连接实例
        date_dir: 日期目录路径
        run_numbers: run 号列表
        max_wait_minutes: 最大等待时间（分钟）

    Returns:
        dict: 执行结果
    """
    print("\n" + "="*60)
    print("检查结果文件")
    print("="*60)
    print(f"最大等待时间: {max_wait_minutes} 分钟")
    print(f"检查间隔: {config.CHECK_INTERVAL_SECONDS} 秒")

    try:
        print(f"\n进入日期目录: {date_dir}")
        print(f"找到 {len(run_numbers)} 个run号: {run_numbers}")

        # 先列出目录中的所有文件（用于诊断）
        print(f"\n列出目录中的所有文件:")
        list_cmd = f"cd {date_dir} && ls -la"
        result = ssh.execute_command(list_cmd)
        if result['success']:
            print(f"目录内容:\n{result['output']}")

        # 定期检查文件
        max_wait_seconds = max_wait_minutes * 60
        check_interval = config.CHECK_INTERVAL_SECONDS
        elapsed_time = 0

        incomplete_runs = run_numbers.copy()

        while elapsed_time < max_wait_seconds and incomplete_runs:
            print(f"\n检查进度: {elapsed_time}/{max_wait_seconds}秒")
            print(f"未完成的run号: {incomplete_runs}")

            # 检查每个run号的文件
            complete_runs = []
            still_incomplete = []

            for run_num in incomplete_runs:
                is_complete, file_count = _check_files_for_run(ssh, date_dir, run_num)

                if is_complete:
                    complete_runs.append(run_num)
                else:
                    still_incomplete.append(run_num)
                    print(f"  Run {run_num}: {file_count}/6 文件已生成")

            incomplete_runs = still_incomplete

            if not incomplete_runs:
                print(f"\n✓ 所有 {len(run_numbers)} 个run号的文件都已生成")
                break

            # 检查是否出现了Interval_run0.png文件（数据异常）
            if _check_anomaly_file(ssh, date_dir):
                return {
                    'success': False,
                    'message': '出现了Interval_run0.png的文件，该日期数据不正常',
                    'anomaly_file': 'Interval_run0.png',
                    'requires_manual_intervention': True
                }

            # 等待
            time.sleep(check_interval)
            elapsed_time += check_interval

        # 返回结果
        if incomplete_runs:
            return {
                'success': False,
                'message': f'在 {max_wait_minutes} 分钟内未完成所有文件的生成',
                'total_runs': len(run_numbers),
                'complete_runs': run_numbers[:-len(incomplete_runs)],
                'incomplete_runs': incomplete_runs,
                'elapsed_time': elapsed_time
            }
        else:
            return {
                'success': True,
                'message': f'成功检查结果文件',
                'total_runs': len(run_numbers),
                'complete_runs': run_numbers,
                'incomplete_runs': [],
                'elapsed_time': elapsed_time
            }

    except Exception as e:
        return {
            'success': False,
            'message': f'检查结果文件异常: {str(e)}',
            'error': str(e)
        }


def step1_1_first_job_submission(
    ssh: TopupSSH,
    date: Optional[str] = None,
    submit_job: bool = True,
    max_wait_minutes: Optional[int] = None
) -> Dict[str, Any]:
    """
    步骤1.1：第一次作业提交并检查结果文件

    此步骤负责：
    1. 确定日期参数（可通过参数传入或自动检测）
    2. 如果 submit_job=True，提交第一次作业
    3. 检查结果文件是否生成完成

    Args:
        ssh: TopupSSH 实例，用于执行远程命令
        date: 日期参数（如250624），可选。如果不提供，将自动检测最小的未处理日期
        submit_job: 是否提交作业，默认为True。如果为False，只检查已存在的文件
        max_wait_minutes: 最大等待时间（分钟），默认使用配置文件中的值

    Returns:
        包含以下键的字典：
            - success (bool, 必需): 是否成功
            - message (str, 必需): 人类可读的消息
            - date (str, 可选): 使用的日期
            - date_dir (str, 可选): 日期目录路径
            - total_runs (int, 可选): 总run数
            - complete_runs (list, 可选): 完成的run号列表
            - incomplete_runs (list, 可选): 未完成的run号列表
            - error (str, 可选): 失败时的错误详情
            - requires_manual_intervention (bool, 可选): 是否需要人工干预
    """
    print("\n" + "="*60)
    print("步骤1.1：第一次作业提交并检查结果文件")
    print("="*60)
    print(f"提交作业: {submit_job}")

    # 使用配置文件中的默认值
    if max_wait_minutes is None:
        max_wait_minutes = config.DEFAULT_MAX_WAIT_MINUTES

    # 1. 确定使用的日期
    date_result = _determine_date_parameter(ssh, date)

    if not date_result['success']:
        return {
            'success': False,
            'message': date_result.get('message', '确定日期参数失败'),
            'step_name': 'step1_1',
            'error': date_result.get('error', '')
        }

    selected_date = date_result['date']

    # 获取日期目录
    date_dir = config.get_date_dir(config.INJ_SIG_TIME_CAL_DIR, selected_date)

    # 2. 判断是否需要提交作业
    if submit_job is None:
        # 检查日期目录是否存在
        check_result = ssh.execute_command(f"ls -d {date_dir} 2>/dev/null")
        if check_result['success'] and check_result['output'].strip():
            submit_job = False
            print(f"\n检测到日期目录已存在，将只检查文件而不提交作业")
        else:
            submit_job = True
            print(f"\n检测到日期目录不存在，将提交作业")

    # 3. 提交作业（如果需要）
    if submit_job:
        submit_result = _submit_first_job(ssh, selected_date)

        if not submit_result['success']:
            return {
                'success': False,
                'message': submit_result['message'],
                'step_name': 'step1_1',
                'date': selected_date,
                'error': submit_result.get('error', '')
            }
    else:
        print("\n" + "="*60)
        print("跳过作业提交（submit_job=False）")
        print("="*60)
        print(f"将检查已存在的日期目录: {date_dir}")

    # 4. 检查结果文件
    # 获取 run 号列表
    success, run_numbers, error = _get_run_numbers(ssh, date_dir)

    if not success:
        return {
            'success': False,
            'message': error,
            'step_name': 'step1_1',
            'date': selected_date,
            'error': error
        }

    # 等待作业完成并检查文件
    completion_result = _wait_for_job_completion(
        ssh,
        date_dir,
        run_numbers,
        max_wait_minutes
    )

    # 添加日期信息到结果
    completion_result['date'] = selected_date
    completion_result['step_name'] = 'step1_1'

    return completion_result
