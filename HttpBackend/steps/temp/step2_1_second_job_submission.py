#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
步骤2.1：第二次作业提交并检查hist文件（合并版）
进入DataValid目录，执行./genJob<日期>脚本，然后检查hist文件
支持submit_job参数控制是否提交作业
"""

import time
import re
from typing import Dict, Any, List, Optional
from topup_ssh import TopupSSH
import config


def step2_1_second_job_submission(
    ssh: TopupSSH,
    date: Optional[str] = None,
    submit_job: bool = True,
    max_wait_minutes: int = None
) -> Dict[str, Any]:
    """
    提交第二次作业并检查hist文件（合并版）

    进入DataValid目录，执行./genJob<日期>脚本，然后检查hist文件

    日期参数处理逻辑：
    - 如果指定了date参数：更新进度文件中的日期，使用指定的日期
    - 如果未指定date参数：从进度文件中读取日期，如果进度文件为空则返回错误

    submit_job参数控制：
    - 如果submit_job=True（默认）：先提交作业，然后检查hist文件
    - 如果submit_job=False：跳过作业提交，直接检查hist文件

    Args:
        ssh: SSH连接实例
        date: 日期参数（如250624），可选
        submit_job: 是否提交作业，默认为True
        max_wait_minutes: 最大等待时间（分钟），用于hist文件检查，默认使用配置文件中的值

    Returns:
        dict: 执行结果
    """
    print("\n" + "="*60)
    print("步骤2.1：第二次作业提交并检查hist文件（合并版）")
    print("="*60)
    print(f"提交作业: {submit_job}")

    # 使用配置文件中的默认值
    if max_wait_minutes is None:
        max_wait_minutes = config.DEFAULT_MAX_WAIT_MINUTES

    # 确定使用的日期
    selected_date = None

    if date is not None:
        # 情况1：传递了date参数，更新进度文件并使用
        print(f"\n使用传入的日期参数: {date}")
        selected_date = date
        # 将日期写入进度文件
        config.save_step_progress('2.1', selected_date)
        print(f"[OK] 已将日期 {selected_date} 写入进度文件")
    else:
        # 情况2：未传递date参数，从进度文件读取
        print("\n未传入日期参数，从进度文件读取...")
        progress = config.load_step_progress()

        if not progress or not progress.get('date'):
            return {
                'success': False,
                'message': '进度文件中没有日期信息，请指定日期参数',
                'step_name': '步骤2.1：第二次作业提交并检查hist文件'
            }

        selected_date = progress['date']
        print(f"[OK] 从进度文件读取到日期: {selected_date}")

    try:
        date_dir = config.get_date_dir(config.DATA_VALID_DIR, selected_date)

        # 阶段1：提交作业（如果submit_job=True）
        if submit_job:
            print(f"\n{'='*60}")
            print("阶段1：提交作业")
            print(f"{'='*60}")

            # 删除已存在的日期目录
            print(f"\n删除已存在的日期目录 {selected_date}...")
            delete_result = ssh.execute_command(f"rm -rf {date_dir}")
            if delete_result['success']:
                print(f"[OK] 已删除日期目录 {selected_date}")
            else:
                print(f"⚠ 删除日期目录失败（可能目录不存在），继续执行...")

            # 执行genJob脚本
            print(f"\n执行genJob脚本 (日期: {selected_date})...")
            result = ssh.execute_interactive_command(f"source {config.ENV_SCRIPT} && cd {config.DATA_VALID_DIR} && ./genJob.sh {selected_date}", completion_marker="DONE")

            if not result['success']:
                return {
                    'success': False,
                    'message': '执行genJob脚本失败',
                    'step_name': '步骤2.1：第二次作业提交并检查hist文件',
                    'date': selected_date,
                    'output': result['output'],
                    'error': result.get('error', '')
                }

            # 检查日期目录是否创建
            print(f"\n检查日期目录是否创建...")
            result3 = ssh.execute_command(f"ls -la {date_dir}")

            if not result3['success']:
                return {
                    'success': False,
                    'message': f'日期目录 {selected_date} 未创建',
                    'step_name': '步骤2.1：第二次作业提交并检查hist文件',
                    'date': selected_date,
                    'output': result3['output'],
                    'error': result3.get('error', '')
                }

            print(f"\n[OK] 作业提交成功，日期目录 {selected_date} 已创建")
        else:
            print(f"\n{'='*60}")
            print("跳过作业提交（submit_job=False）")
            print(f"{'='*60}")
            print(f"直接检查hist文件...")

        # 阶段2：检查hist文件
        print(f"\n{'='*60}")
        print("阶段2：检查hist文件")
        print(f"{'='*60}")
        print(f"最大等待时间: {max_wait_minutes} 分钟")
        print(f"检查间隔: {config.CHECK_INTERVAL_SECONDS} 秒")

        print(f"\n进入日期目录: {date_dir}")

        # 获取run号子目录列表
        result = ssh.execute_command(f"cd {date_dir} && ls -d */ | sed 's|/||'")

        if not result['success']:
            return {
                'success': False,
                'message': '获取run号子目录列表失败',
                'step_name': '步骤2.1：第二次作业提交并检查hist文件',
                'date': selected_date,
                'output': result['output'],
                'error': result.get('error', '')
            }

        # 解析run号列表
        run_numbers = [line.strip() for line in result['output'].split('\n') if line.strip()]

        if not run_numbers:
            return {
                'success': False,
                'message': '未找到run号子目录',
                'step_name': '步骤2.1：第二次作业提交并检查hist文件',
                'date': selected_date,
                'run_numbers': []
            }

        print(f"找到 {len(run_numbers)} 个run号子目录: {run_numbers}")

        # 定期检查文件
        max_wait_seconds = max_wait_minutes * 60
        check_interval = config.CHECK_INTERVAL_SECONDS  # 使用配置文件中的检查间隔
        elapsed_time = 0

        all_run_numbers = run_numbers.copy()  # 记录所有run号
        incomplete_runs = run_numbers.copy()  # 记录未完成的run号
        
        # 跟踪稳定性检查状态
        runs_needing_stability = {}  # {run_num: {'last_size': int, 'start_time': time}}
        
        while elapsed_time < max_wait_seconds and incomplete_runs:
            print(f"\n检查进度: {elapsed_time}/{max_wait_seconds}秒")
            print(f"未完成的run号: {incomplete_runs}")

            # 检查每个run号的hist文件
            complete_runs = []
            still_incomplete = []

            for run_num in incomplete_runs:
                # 如果已经通过稳定性检查，跳过
                if run_num in runs_needing_stability and runs_needing_stability[run_num].get('stable'):
                    complete_runs.append(run_num)
                    continue
                    
                run_dir = f"{date_dir}/{run_num}"

                # 获取该run号下的作业文件数量
                result_jobs = ssh.execute_command(r"cd " + run_dir + r" && ls rec* 2>/dev/null | grep -v '\.' | wc -l")

                if result_jobs['success']:
                    job_count = int(result_jobs['output'].strip())

                    # 获取hist文件数量
                    result_hist = ssh.execute_command(f"cd {run_dir} && ls hist*.root 2>/dev/null | wc -l")

                    if result_hist['success']:
                        hist_count = int(result_hist['output'].strip())

                        # 检查hist文件是否完全生成
                        # 条件：hist_count >= job_count 且 job_count > 0
                        if hist_count >= job_count and job_count > 0:
                            # 文件数量达标，进行稳定性检查
                            if run_num not in runs_needing_stability:
                                # 第一次达到条件，开始稳定性检查
                                runs_needing_stability[run_num] = {
                                    'last_size': None,
                                    'start_time': time.time(),
                                    'run_dir': run_dir,
                                    'stable': False
                                }
                                print(f"  Run {run_num}: {hist_count}/{job_count} hist文件已生成，等待稳定性检查...")
                            still_incomplete.append(run_num)
                        else:
                            still_incomplete.append(run_num)
                            if job_count > 0:
                                print(f"  Run {run_num}: {hist_count}/{job_count} hist文件已生成")
                            else:
                                print(f"  Run {run_num}: {hist_count} hist文件已生成，等待作业文件...")
                    else:
                        still_incomplete.append(run_num)
                        print(f"  Run {run_num}: 检查hist文件失败")
                else:
                    still_incomplete.append(run_num)
                    print(f"  Run {run_num}: 检查作业文件失败")

            # 批量进行稳定性检查
            if runs_needing_stability:
                print(f"\n--- 稳定性检查 (待检查: {len([r for r in runs_needing_stability if not runs_needing_stability[r].get('stable')])}) ---")
                
                for run_num, info in runs_needing_stability.items():
                    # 跳过已稳定的
                    if info.get('stable'):
                        continue
                    
                    # 检查是否超时（使用总剩余时间）
                    remaining_time = max_wait_seconds - elapsed_time
                    if remaining_time <= 0:
                        print(f"    Run {run_num}: 总等待时间已达上限")
                        del runs_needing_stability[run_num]
                        continue
                    
                    run_dir = info['run_dir']
                    
                    # 获取当前文件总大小
                    result_size = ssh.execute_command(
                        f"cd {run_dir} && ls -l hist*.root | awk '{{sum+=$5}} END {{print sum}}'"
                    )
                    
                    if result_size['success'] and result_size['output'].strip():
                        current_size = int(result_size['output'].strip())
                        last_size = info['last_size']
                        
                        if last_size is not None:
                            size_diff = abs(current_size - last_size)
                            print(f"    Run {run_num}: 当前大小 = {current_size} bytes, 差异 = {size_diff} bytes")
                            
                            if size_diff < 1024:
                                # 差异小于1KB，认为稳定
                                runs_needing_stability[run_num]['stable'] = True
                                print(f"    Run {run_num}: [OK] 文件大小稳定（差异 < 1KB）")
                            else:
                                # 更新大小，继续监控
                                runs_needing_stability[run_num]['last_size'] = current_size
                        else:
                            # 第一次检查，记录大小
                            runs_needing_stability[run_num]['last_size'] = current_size
                            print(f"    Run {run_num}: 初始大小 = {current_size} bytes")
                
                print(f"--- 稳定性检查完成 ---")

            # 检查是否有所有run都稳定
            stable_runs = [r for r in runs_needing_stability if runs_needing_stability[r].get('stable')]
            if len(stable_runs) == len(all_run_numbers):
                print(f"\n[OK] 所有 {len(run_numbers)} 个run号的hist文件都已生成且大小稳定")
                break

            incomplete_runs = still_incomplete

            # 等待检查间隔
            time.sleep(check_interval)
            elapsed_time += check_interval

        # 构建最终检查结果（只有在超时后才判断成功/失败）
        # 再次检查所有run的最终状态
        final_check_result = {}
        
        for run_num in all_run_numbers:
            run_dir = f"{date_dir}/{run_num}"
            
            # 获取作业文件数量
            result_jobs = ssh.execute_command(r"cd " + run_dir + r" && ls rec* 2>/dev/null | grep -v '\.' | wc -l")
            if not result_jobs['success']:
                final_check_result[run_num] = {
                    'status': 'error',
                    'message': '检查作业文件失败'
                }
                continue
                
            job_count = int(result_jobs['output'].strip())
            
            # 获取hist文件数量
            result_hist = ssh.execute_command(f"cd {run_dir} && ls hist*.root 2>/dev/null | wc -l")
            if not result_hist['success']:
                final_check_result[run_num] = {
                    'status': 'error',
                    'message': '检查hist文件失败'
                }
                continue
                
            hist_count = int(result_hist['output'].strip())
            
            # 检查是否全部生成
            if hist_count >= job_count and job_count > 0:
                final_check_result[run_num] = {
                    'status': 'complete',
                    'hist_count': hist_count,
                    'job_count': job_count,
                    'message': f'hist文件全部生成 ({hist_count}/{job_count})'
                }
            else:
                final_check_result[run_num] = {
                    'status': 'incomplete',
                    'hist_count': hist_count,
                    'job_count': job_count,
                    'message': f'hist文件未全部生成 ({hist_count}/{job_count})'
                }

        # 统计结果
        complete_runs_final = [k for k, v in final_check_result.items() if v['status'] == 'complete']
        incomplete_runs_final = [k for k, v in final_check_result.items() if v['status'] == 'incomplete']
        error_runs_final = [k for k, v in final_check_result.items() if v['status'] == 'error']

        # 构建错误消息
        error_messages = []
        
        if incomplete_runs_final:
            incomplete_details = ', '.join([f"Run {k}: {v['message']}" for k, v in final_check_result.items() if k in incomplete_runs_final])
            error_messages.append(f"在规定的时间内，以下hist文件未产生: {incomplete_details}")
        
        if error_runs_final:
            error_details = ', '.join([f"Run {k}: {v['message']}" for k, v in final_check_result.items() if k in error_runs_final])
            error_messages.append(f"检查过程中出现错误: {error_details}")

        # 判断最终结果
        if incomplete_runs_final or error_runs_final:
            error_message = '; '.join(error_messages)
            error_code = 2106  # hist文件检查失败
            
            return {
                'success': False,
                'message': error_message,
                'step_name': '步骤2.1：第二次作业提交并检查hist文件',
                'date': selected_date,
                'total_runs': len(all_run_numbers),
                'complete_runs': complete_runs_final,
                'incomplete_runs': incomplete_runs_final,
                'error_runs': error_runs_final,
                'final_check_result': final_check_result,
                'error_code': error_code,
                'elapsed_time': elapsed_time
            }
        else:
            return {
                'success': True,
                'message': f'成功提交作业并检查hist文件: {selected_date}',
                'step_name': '步骤2.1：第二次作业提交并检查hist文件',
                'date': selected_date,
                'total_runs': len(all_run_numbers),
                'complete_runs': complete_runs_final,
                'incomplete_runs': [],
                'elapsed_time': elapsed_time
            }

    except Exception as e:
        return {
            'success': False,
            'message': f'作业提交或检查异常: {str(e)}',
            'step_name': '步骤2.1：第二次作业提交并检查hist文件',
            'date': selected_date,
            'error': str(e)
        }


if __name__ == "__main__":
    # 测试步骤2.1
    with TopupSSH() as ssh:
        if ssh.connected:
            # 测试1：提交作业并检查（默认）
            print("\n测试1：提交作业并检查（submit_job=True）")
            result = step2_1_second_job_submission(ssh, "250519", submit_job=True)
            print("\n" + "="*60)
            print("步骤2.1执行结果:")
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
            result2 = step2_1_second_job_submission(ssh, "250519", submit_job=False)
            print("\n" + "="*60)
            print("步骤2.1执行结果:")
            print("="*60)
            print(f"成功: {result2['success']}")
            print(f"消息: {result2['message']}")
            if 'date' in result2:
                print(f"使用的日期: {result2['date']}")
