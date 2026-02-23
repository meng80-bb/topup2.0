#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
步骤6.1：第六次作业提交与文件检查
进入check_ETScut_CalibConst目录，执行./genJob.sh脚本，然后检查png和root文件
"""

import time
import re
from typing import Dict, Any, Optional
from topup_ssh import TopupSSH
import config


def step6_1_sixth_job_submission(ssh: TopupSSH, submit_job: bool = True, max_wait_minutes: Optional[int] = None) -> Dict[str, Any]:
    """
    第六次作业提交与文件检查
    
    进入check_ETScut_CalibConst目录，执行./genJob.sh脚本，然后检查png和root文件
    
    Args:
        ssh: SSH连接实例
        submit_job: 是否提交作业，默认为True。如果为False，则跳过提交作业，直接检查文件
        max_wait_minutes: 最大等待时间（分钟），默认使用配置文件中的值（25分钟）
        
    Returns:
        dict: 执行结果
    """
    print("\n" + "="*60)
    print("步骤6.1：第六次作业提交与文件检查")
    print("="*60)
    
    check_dir = config.CHECK_ETSCUT_CALIBCONST_DIR
    
    # 步骤1：提交作业（如果submit_job为True）
    if submit_job:
        print(f"\n[子步骤1] 提交作业")
        print(f"进入check_ETScut_CalibConst目录: {check_dir}")

        # 删除旧文件（ETScut开头的文件、png文件、root文件）
        print(f"\n清理旧文件...")
        result_clean = ssh.execute_command(f"cd {check_dir} && rm -f ETScut* *png *root")
        if not result_clean['success']:
            print(f"⚠ 清理旧文件时出现警告: {result_clean.get('error', '')}")
        else:
            print(f"✓ 旧文件清理完成")

        # 执行genJob.sh脚本（包含环境激活）
        print(f"\n执行genJob.sh脚本...")
        result = ssh.execute_interactive_command(f"cd {check_dir} && source {config.ENV_SCRIPT} && ./genJob.sh", completion_marker="DONE")

        if not result['success']:
            return {
                'success': False,
                'message': '执行genJob.sh脚本失败',
                'step_name': '步骤6.1：第六次作业提交与文件检查',
                'output': result['output'],
                'error': result.get('error', '')
            }

        # 检查生成的作业文件
        result_check = ssh.execute_command(f"cd {check_dir} && ls ETScut_check_*.txt")

        print(f"\n✓ 作业提交成功")
        print(f"生成的作业文件:\n{result_check['output']}")
    else:
        print(f"\n[子步骤1] 跳过作业提交（submit_job=False）")
        # 检查作业文件是否存在
        result_check = ssh.execute_command(f"cd {check_dir} && ls ETScut_check_*.txt")
        if not result_check['success'] or not result_check['output'].strip():
            return {
                'success': False,
                'message': '未找到作业文件，请先提交作业',
                'step_name': '步骤6.1：第六次作业提交与文件检查',
                'error': 'No job files found'
            }
        print(f"✓ 找到已有作业文件:\n{result_check['output']}")
    
    # 步骤2：检查png和root文件
    print(f"\n[子步骤2] 检查png和root文件")
    
    # 使用配置文件中的默认值
    if max_wait_minutes is None:
        max_wait_minutes = config.DEFAULT_MAX_WAIT_MINUTES

    print(f"最大等待时间: {max_wait_minutes} 分钟")
    print(f"检查间隔: {config.CHECK_INTERVAL_SECONDS} 秒")

    try:
        print(f"\n进入check_ETScut_CalibConst目录: {check_dir}")

        # 解析作业文件列表，提取run号
        job_files = []
        for line in result_check['output'].split('\n'):
            if line.strip():
                # 分割每行中的多个文件名
                job_files.extend(line.strip().split())
        run_numbers = []
        for filename in job_files:
            match = re.match(r'ETScut_check_(\d+)\.txt', filename)
            if match:
                run_numbers.append(match.group(1))

        if not run_numbers:
            return {
                'success': False,
                'message': '未找到作业文件',
                'step_name': '步骤6.1：第六次作业提交与文件检查',
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
            
            # 检查每个run号的png和root文件
            complete_runs = []
            still_incomplete = []

            for run_num in incomplete_runs:
                png_file = f"run{run_num}.png"
                root_file = f"run{run_num}.root"

                result_png = ssh.execute_command(f"cd {check_dir} && ls {png_file} 2>/dev/null")
                result_root = ssh.execute_command(f"cd {check_dir} && ls {root_file} 2>/dev/null")

                png_exists = result_png['success'] and png_file in result_png['output']
                root_exists = result_root['success'] and root_file in result_root['output']

                if png_exists and root_exists:
                    complete_runs.append(run_num)
                else:
                    still_incomplete.append(run_num)
                    print(f"  Run {run_num}: png文件={'✓' if png_exists else '✗'}, root文件={'✓' if root_exists else '✗'}")
            
            incomplete_runs = still_incomplete
            
            if not incomplete_runs:
                print(f"\n✓ 所有 {len(run_numbers)} 个png和root文件都已生成")
                break
            
            # 等待
            time.sleep(check_interval)
            elapsed_time += check_interval
        
        # 返回结果
        if incomplete_runs:
            return {
                'success': False,
                'message': f'在 {max_wait_minutes} 分钟内未完成所有png和root文件的生成',
                'step_name': '步骤6.1：第六次作业提交与文件检查',
                'total_runs': len(run_numbers),
                'complete_runs': run_numbers[:-len(incomplete_runs)],
                'incomplete_runs': incomplete_runs,
                'elapsed_time': elapsed_time,
                'submit_job': submit_job
            }
        else:
            return {
                'success': True,
                'message': f'所有 {len(run_numbers)} 个png和root文件都已生成',
                'step_name': '步骤6.1：第六次作业提交与文件检查',
                'total_runs': len(run_numbers),
                'complete_runs': run_numbers,
                'incomplete_runs': [],
                'elapsed_time': elapsed_time,
                'submit_job': submit_job
            }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'检查png和root文件异常: {str(e)}',
            'step_name': '步骤6.1：第六次作业提交与文件检查',
            'error': str(e),
            'submit_job': submit_job
        }


if __name__ == "__main__":
    # 测试步骤6.1
    with TopupSSH() as ssh:
        if ssh.connected:
            # 测试1：提交作业并检查
            result = step6_1_sixth_job_submission(ssh, submit_job=True)
            print("\n" + "="*60)
            print("步骤6.1执行结果（submit_job=True）:")
            print("="*60)
            print(f"成功: {result['success']}")
            print(f"消息: {result['message']}")
            
            # 测试2：仅检查文件（不提交作业）
            # result = step6_1_sixth_job_submission(ssh, submit_job=False)
            # print("\n" + "="*60)
            # print("步骤6.1执行结果（submit_job=False）:")
            # print("="*60)
            # print(f"成功: {result['success']}")
            # print(f"消息: {result['message']}")