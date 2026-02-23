#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
步骤4.1：第四次作业提交
进入checkShieldCalib目录，删除旧文件，执行./genJob.sh脚本，检查生成的图片文件
"""

from typing import Dict, Any
from topup_ssh import TopupSSH
import config
import time


def step4_1_fourth_job_submission(
    ssh: TopupSSH,
    date: str,
    submit_job: bool = True,
    check: bool = False,
    max_wait_minutes: int = None
) -> Dict[str, Any]:
    """
    提交第四次作业并检查生成的图片文件

    Args:
        ssh: SSH连接实例
        date: 日期参数（如250519）
        submit_job: 是否提交作业，默认True
        check: 是否检查生成的图片文件，默认False（非topup模式不需要检查）
        max_wait_minutes: 最大等待时间（分钟），默认使用配置文件的值

    Returns:
        dict: 执行结果
    """
    print("\n" + "="*60)
    print("步骤4.1：第四次作业提交")
    print("="*60)

    if max_wait_minutes is None:
        max_wait_minutes = config.DEFAULT_MAX_WAIT_MINUTES

    print(f"参数: submit_job={submit_job}, check={check}, max_wait_minutes={max_wait_minutes}")

    try:
        checkShieldCalib_dir = config.CHECK_SHIELD_CALIB_DIR

        # 阶段1：删除旧文件
        print(f"\n进入checkShieldCalib目录: {checkShieldCalib_dir}")
        print(f"删除旧文件（PDF和run开头的文件）...")
        result_rm = ssh.execute_command(f"cd {checkShieldCalib_dir} && rm -f *.pdf && rm -f run*")
        if not result_rm['success']:
            return {
                'success': False,
                'message': '删除旧文件失败',
                'step_name': '步骤4.1：第四次作业提交',
                'date': date,
                'output': result_rm['output'],
                'error': result_rm.get('error', '')
            }
        print(f"✓ 旧文件已删除")

        # 阶段2：提交作业（如果submit_job=True）
        if submit_job:
            print(f"\n执行genJob.sh脚本...")
            result = ssh.execute_interactive_command(
                f"cd {checkShieldCalib_dir} && source {config.ENV_SCRIPT} && ./genJob.sh",
                completion_marker="DONE"
            )

            if not result['success']:
                return {
                    'success': False,
                    'message': '执行genJob.sh脚本失败',
                    'step_name': '步骤4.1：第四次作业提交',
                    'date': date,
                    'output': result['output'],
                    'error': result.get('error', '')
                }

            print(f"✓ 作业提交成功")
            print(f"输出:\n{result['output']}")
        else:
            print(f"\nskip_job=True，跳过作业提交")
            result = {'success': True, 'output': ''}

        # 阶段3：检查文件（如果check=True）
        if check:
            # 获取作业文件列表以确定run号
            print(f"\n获取作业文件列表...")
            result_files = ssh.execute_command(f"cd {checkShieldCalib_dir} && ls run_*_4.txt")
            if not result_files['success']:
                return {
                    'success': False,
                    'message': '获取作业文件列表失败',
                    'step_name': '步骤4.1：第四次作业提交',
                    'date': date,
                    'output': result_files['output'],
                    'error': result_files.get('error', '')
                }

            # 提取run号
            run_numbers = []
            for line in result_files['output'].split('\n'):
                if line.strip() and 'run_' in line:
                    # 从文件名中提取run号（格式：run_XXXXX_4.txt）
                    parts = line.strip().split('_')
                    if len(parts) >= 2:
                        run_numbers.append(parts[1])

            if not run_numbers:
                return {
                    'success': False,
                    'message': '未找到作业文件',
                    'step_name': '步骤4.1：第四次作业提交',
                    'date': date,
                    'output': result_files['output']
                }

            print(f"找到 {len(run_numbers)} 个run号: {run_numbers}")

            # 检查每个run的4个文件
            required_files = [
                'cut_detail.png',   # 滤波窗口详细图
                'after_cut.png',    # 应用滤波后的结果图
                'before_cut.png',   # 应用滤波前的对比图
                'check.png'         # 整体检查图
            ]

            total_runs = len(run_numbers)
            complete_runs = []
            incomplete_runs = []

            print(f"\n开始检查文件，最大等待时间: {max_wait_minutes} 分钟...")
            start_time = time.time()
            check_interval = config.CHECK_INTERVAL_SECONDS

            while True:
                complete_runs = []
                incomplete_runs = []

                for run in run_numbers:
                    all_files_exist = True
                    missing_files = []

                    for file_suffix in required_files:
                        file_name = f"run{run}_{file_suffix}"
                        file_path = f"{checkShieldCalib_dir}/{file_name}"
                        result_check = ssh.execute_command(f"ls {file_path}")
                        if not result_check['success'] or not result_check['output'].strip():
                            all_files_exist = False
                            missing_files.append(file_suffix)

                    if all_files_exist:
                        complete_runs.append(run)
                    else:
                        incomplete_runs.append({
                            'run': run,
                            'missing': missing_files
                        })

                elapsed_time = time.time() - start_time

                # 如果所有文件都已生成，退出循环
                if len(complete_runs) == total_runs:
                    print(f"✓ 所有 {total_runs} 个run的文件都已生成")
                    break

                # 检查是否超时
                if elapsed_time >= max_wait_minutes * 60:
                    print(f"\n✗ 文件检查超时")
                    print(f"总run数: {total_runs}")
                    print(f"已完成run数: {len(complete_runs)}")
                    print(f"未完成run数: {len(incomplete_runs)}")
                    for item in incomplete_runs[:5]:  # 只显示前5个
                        print(f"  - run{item['run']}: 缺少 {', '.join(item['missing'])}")
                    if len(incomplete_runs) > 5:
                        print(f"  ... 还有 {len(incomplete_runs) - 5} 个run未完成")

                    return {
                        'success': False,
                        'message': f'文件检查超时（等待{max_wait_minutes}分钟）',
                        'step_name': '步骤4.1：第四次作业提交',
                        'date': date,
                        'output': result['output'],
                        'total_runs': total_runs,
                        'complete_runs': len(complete_runs),
                        'incomplete_runs': [item['run'] for item in incomplete_runs],
                        'elapsed_time': elapsed_time
                    }

                # 显示进度
                print(f"[{int(elapsed_time)}秒] 完成: {len(complete_runs)}/{total_runs} run", end='\r')

                # 等待一段时间后再次检查
                time.sleep(check_interval)

            print(f"\n✓ 文件检查完成，耗时: {int(elapsed_time)} 秒")

            return {
                'success': True,
                'message': f'作业提交成功，所有 {total_runs} 个run的文件都已生成',
                'step_name': '步骤4.1：第四次作业提交',
                'date': date,
                'output': result['output'],
                'total_runs': total_runs,
                'complete_runs': len(complete_runs),
                'elapsed_time': elapsed_time
            }
        else:
            print(f"\ncheck=False，跳过文件检查")
            return {
                'success': True,
                'message': '作业提交成功（未检查文件）',
                'step_name': '步骤4.1：第四次作业提交',
                'date': date,
                'output': result['output']
            }

    except Exception as e:
        return {
            'success': False,
            'message': f'作业提交异常: {str(e)}',
            'step_name': '步骤4.1：第四次作业提交',
            'date': date,
            'error': str(e)
        }


if __name__ == "__main__":
    # 测试步骤4.1
    with TopupSSH() as ssh:
        if ssh.connected:
            result = step4_1_fourth_job_submission(ssh, "250519", submit_job=True, check=False, max_wait_minutes=25)
            print("\n" + "="*60)
            print("步骤4.1执行结果:")
            print("="*60)
            print(f"成功: {result['success']}")
            print(f"消息: {result['message']}")