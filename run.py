#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BESIII Topup 数据验证执行脚本

功能：
- 支持单步执行（step模式）
- 支持批量执行（all模式）
- 支持批量处理所有日期（total模式）
- 集成AI分析和错误码匹配
- 增强的日志记录功能
- 支持与iFlow CLI通信
- 自动重试机制（最多3次）

使用方式：
- 单步执行：python run.py --step 1.4 --date 250519
- 批量执行：python run.py --all --date 250519
- Total模式：python run.py --total
- 列出步骤：python run.py --list

超时配置说明：
- 作业提交步骤（1.1, 2.1, 3.1, 4, 5.1, 6.1）：300秒（5分钟）
- 定时检查步骤（1.1, 2.2, 2.5, 3.1, 5.1, 6.2）：使用--max-wait参数，默认1500秒（25分钟）
- 快速步骤（1.2, 1.3, 1.4, 2.3, 2.4, 2.6, 3.3, 5.2, 5.3, 5.4, 6.3, 7）：600秒（10分钟）
"""

import sys
import argparse
import time
import re

# 导入核心模块
from topup_ssh import TopupSSH
import config
import error_codes
from logger import step_logger
from iflow_cli_client import iflow_client

# 导入步骤模块
import step1_1_first_job_submission
import step1_2_move_files
import step1_3_ist_analysis
import step1_4_merge_images
import step2_1_second_job_submission
import step2_2_merge_hist
import step2_3_generate_png
import step2_4_check_png_files
import step2_5_merge_images
import step3_1_third_job_submission
import step3_2_run_add_script
import step4_1_fourth_job_submission
import step4_2_merge_images
import step5_1_fifth_job_submission
import step5_2_run_add_shield_script
import step5_3_organize_ets_cut_file
import step5_4_merge_images
import step6_1_sixth_job_submission
import step6_2_merge_images
import step7_run_reset_script
import step8_submit_injsiginterval_db


# ============================================================================
# 步骤定义
# ============================================================================

STEPS = {
    '1.1': {
        'name': '步骤1.1：第一次作业提交并检查结果文件',
        'func': step1_1_first_job_submission.step1_1_first_job_submission,
        'needs_date': True,
        'is_check_step': True
    },
    '1.2': {
        'name': '步骤1.2：移动文件',
        'func': step1_2_move_files.step1_2_move_files,
        'needs_date': True,
        'is_check_step': False
    },
    '1.3': {
        'name': '步骤1.3：IST分析',
        'func': step1_3_ist_analysis.step1_3_ist_analysis,
        'needs_date': True,
        'is_check_step': False
    },
    '1.4': {
        'name': '步骤1.4：合并图片',
        'func': step1_4_merge_images.step1_4_merge_images,
        'needs_date': False,
        'is_check_step': False
    },
    '2.1': {
        'name': '步骤2.1：第二次作业提交并检查hist文件（合并版）',
        'func': step2_1_second_job_submission.step2_1_second_job_submission,
        'needs_date': True,
        'is_check_step': True
    },
    '2.2': {
        'name': '步骤2.2：合并hist文件',
        'func': step2_2_merge_hist.step2_2_merge_hist,
        'needs_date': True,
        'is_check_step': False
    },
    '2.3': {
        'name': '步骤2.3：生成png文件',
        'func': step2_3_generate_png.step2_3_generate_png,
        'needs_date': False,
        'is_check_step': False
    },
    '2.4': {
        'name': '步骤2.4：检查png文件',
        'func': step2_4_check_png_files.step2_4_check_png_files,
        'needs_date': False,
        'is_check_step': True
    },
    '2.5': {
        'name': '步骤2.5：合并hist图片',
        'func': step2_5_merge_images.step2_5_merge_images,
        'needs_date': False,
        'is_check_step': False
    },
    '3.1': {
        'name': '步骤3.1：第三次作业提交并检查shield文件（合并版）',
        'func': step3_1_third_job_submission.step3_1_third_job_submission,
        'needs_date': False,
        'is_check_step': True
    },
    '3.2': {
        'name': '步骤3.2：运行add脚本',
        'func': step3_2_run_add_script.step3_2_run_add_script,
        'needs_date': False,
        'is_check_step': False
    },
    '4.1': {
        'name': '步骤4.1：第四次作业提交并检查文件',
        'func': step4_1_fourth_job_submission.step4_1_fourth_job_submission,
        'needs_date': True,
        'is_check_step': True
    },
    '4.2': {
        'name': '步骤4.2：合并checkShieldCalib图片',
        'func': step4_2_merge_images.step4_2_merge_images,
        'needs_date': False,
        'is_check_step': False
    },
    '5.1': {
        'name': '步骤5.1：第五次作业提交并检查cut和all文件（合并版）',
        'func': step5_1_fifth_job_submission.step5_1_fifth_job_submission,
        'needs_date': True,
        'is_check_step': True
    },
    '5.2': {
        'name': '步骤5.2：运行add_shield.sh脚本',
        'func': step5_2_run_add_shield_script.step5_2_run_add_shield_script,
        'needs_date': True,
        'is_check_step': False
    },
    '5.3': {
        'name': '步骤5.3：整理ets_cut.txt文件',
        'func': step5_3_organize_ets_cut_file.step5_3_organize_ets_cut_file,
        'needs_date': True,
        'is_check_step': False
    },
    '5.4': {
        'name': '步骤5.4：合并ETS_cut图片',
        'func': step5_4_merge_images.step5_4_merge_images,
        'needs_date': False,
        'is_check_step': False
    },
    '6.1': {
        'name': '步骤6.1：第六次作业提交与文件检查',
        'func': step6_1_sixth_job_submission.step6_1_sixth_job_submission,
        'needs_date': False,
        'is_check_step': True
    },
    '6.2': {
        'name': '步骤6.2：合并Check ETScut图片',
        'func': step6_2_merge_images.step6_2_merge_images,
        'needs_date': False,
        'is_check_step': False
    },
    '7': {
        'name': '步骤7：运行reset.sh脚本',
        'func': step7_run_reset_script.step7_run_reset_script,
        'needs_date': False,
        'is_check_step': False
    },
    '8': {
        'name': '步骤8：提交InjSigInterval到数据库',
        'func': step8_submit_injsiginterval_db.step8_submit_injsiginterval_db,
        'needs_date': True,
        'is_check_step': False,
        'manual_only': True
    }
}


# 步骤执行顺序
STEP_ORDER = [
    '1.1', '1.2', '1.3', '1.4',
    '2.1', '2.2', '2.3', '2.4', '2.5',
    '3.1', '3.2',
    '4.1', '4.2',
    '5.1', '5.2', '5.3', '5.4',
    '6.1', '6.2',
    '7'
]


# ============================================================================
# 核心函数：分析结果
# ============================================================================

def analyze_result(step_name: str, result: dict, ssh=None) -> dict:
    """
    分析执行结果（使用错误码匹配）

    Args:
        step_name: 步骤名称
        result: 执行结果
        ssh: SSH连接实例（可选）

    Returns:
        dict: 分析结果，包含should_continue, message, action, error_code
    """
    print("\n" + "="*60)
    print(f"分析 - {step_name}")
    print("="*60)

    # 打印执行结果
    print("\n[执行结果]")
    print(f"成功: {result.get('success', False)}")
    print(f"信息: {result.get('message', 'N/A')}")
    print(f"退出码: {result.get('exit_code', 'N/A')}")

    # 使用错误码匹配引擎
    error_code = error_codes.match_error_code(step_name, result)
    error_info = error_codes.get_error_info(error_code)

    print(f"\n[错误信息]")
    print(f"错误码: {error_code}")
    print(f"错误名: {error_info['name']}")
    print(f"描述: {error_info['description']}")
    print(f"严重程度: {error_info['severity']}")

    # 如果action是ai，则向iFlow CLI发送错误分析请求
    if error_info.get('action') == 'ai':
        print("\n[处理中]")
        print(f"→ 检测到需要处理的错误")
        print(f"错误码: {error_code}")
        print(f"错误名称: {error_info['name']}")
        print(f"正在向iFlow CLI发送处理请求...")

        # 向iFlow CLI发送错误分析请求
        log_file_path = step_logger.log_file
        prompt = error_info.get('prompt', '请分析此错误')

        send_result = iflow_client.send_error_analysis(
            error_code=error_code,
            step_name=step_name,
            log_file_path=log_file_path,
            prompt=prompt,
            log_lines=500
        )

        if send_result.get('success'):
            print(f"✓ 请求已发送，等待iFlow CLI响应...")
            if 'response' in send_result:
                response = send_result['response']
                print(f"iFlow CLI响应: {response.get('message', 'N/A')}")
                # 根据响应返回一个结果
                if response.get('can_resolve'):
                    # iFlow CLI能够解决
                    print(f"✓ iFlow CLI可以自动解决此错误并修正配置文件")
                    return {
                        'should_continue': True,
                        'message': f'iFlow CLI正在处理: {error_info["name"]}',
                        'action': 'ai_resolve',
                        'error_code': error_code,
                        'error_info': error_info
                    }
                else:
                    # 需要人工干预
                    print(f"? iFlow CLI建议需要人工干预")
                    return {
                        'should_continue': False,
                        'message': f'iFlow CLI建议需要人工干预: {error_info["name"]}',
                        'action': 'manual',
                        'error_code': error_code,
                        'error_info': error_info
                    }
        else:
            print(f"✗ 发送请求失败: {send_result.get('message')}")
            print(f"切换到人工干预模式")

    # 检查是否需要人工干预
    if result.get('requires_manual_intervention', False):
        print(f"\n[分析]")
        print(f"→ 步骤执行需要人工干预")
        print(f"原因: {result.get('message', 'N/A')}")
        if 'invalid_runs' in result:
            print(f"无效run号: {result['invalid_runs']}")

        return {
            'should_continue': False,
            'message': result.get('message', '需要人工干预'),
            'action': 'manual',
            'error_code': error_code,
            'error_info': error_info
        }

    # 检查是否成功
    if result.get('success', False):
        print("\n→分析完成")
        print(f"✓ 步骤执行成功")
        print(f"成功信息: {result.get('message', 'N/A')}")

        print("\n[推荐操作]")
        print(f"推荐操作: {error_info['action']}")
        print(f"说明: {result.get('message', '可以继续下一步')}")

        return {
            'should_continue': True,
            'message': result.get('message', '执行成功'),
            'action': error_info['action'],
            'error_code': error_code,
            'error_info': error_info
        }
    else:
        print("\n→分析完成")
        print(f"✗ 步骤执行失败")
        print(f"失败原因: {error_info['message']}")

        # 显示错误详情
        if result.get('error'):
            print(f"错误详情: {result['error']}")

        # 显示是否有未完成的run号
        if 'incomplete_runs' in result and result['incomplete_runs']:
            print(f"未完成的run号: {result['incomplete_runs']}")

        print("\n推荐操作")
        print(f"推荐操作: {error_info['action']}")
        print(f"说明: {error_info['description']}")

        return {
            'should_continue': error_info['action'] == 'continue',
            'message': error_info['message'],
            'action': error_info['action'],
            'error_code': error_code,
            'error_info': error_info
        }


# ============================================================================
# 核心函数：执行步骤
# ============================================================================

def execute_step(ssh, step_key, date=None, max_wait=None, retry_params=None, submit_job_arg=None, check_arg=None):
    """
    执行单个步骤（含分析和自动重试）

    Args:
        ssh: SSH连接实例
        step_key: 步骤键值
        date: 日期参数
        max_wait: 最大等待时间（分钟），用于定时检查步骤
        retry_params: 重试参数（用于retry时保持参数一致）
        submit_job_arg: submit_job参数（用于步骤1.1、2.1、3.1、4.1）
        check_arg: check参数（用于步骤4.1）

    Returns:
        dict: 执行结果
    """
    # 验证步骤
    if step_key not in STEPS:
        print(f"✗ 未知的步骤: {step_key}")
        return None

    step_info = STEPS[step_key]
    print("\n" + "="*60)
    print(step_info['name'])
    print("="*60)

    # 记录步骤开始
    if step_logger.enabled:
        step_logger.log_step_start(step_key, step_info['name'], date)

    # 保存进度
    if retry_params:
        config.save_step_progress(step_key, date, retry_params)
    else:
        config.save_step_progress(step_key, date)

    # 自动重试逻辑：最多重试3次
    max_retries = 3
    retry_count = 0
    result = None

    while retry_count <= max_retries:
        # 记录步骤开始（包括重试）
        if step_logger.enabled:
            step_name_with_retry = f"{step_info['name']}"
            if retry_count > 0:
                step_name_with_retry += f" (重试 {retry_count}/{max_retries})"
            step_logger.log_step_start(step_key, step_name_with_retry, date)

        # 调用步骤函数
        result = _call_step_function(ssh, step_key, step_info, date, max_wait, retry_params, submit_job_arg, check_arg)

        # 如果成功，跳出重试循环
        if result and result.get('success', False):
            break

        # 如果失败，进行分析
        if result:
            analysis = analyze_result(step_info['name'], result, ssh)
            result['analysis'] = analysis

            # 检查是否需要重试
            if analysis.get('action') == 'retry' and retry_count < max_retries:
                retry_count += 1
                print(f"\n⚠ 步骤执行失败，将进行第 {retry_count} 次重试...")
                print(f"失败原因: {analysis.get('message', 'N/A')}")
                print(f"推荐操作: retry")
                time.sleep(2)  # 等待2秒后重试
                config.save_step_progress(step_key, date)
                continue
            else:
                # 不需要重试或已达到重试上限，跳出循环
                if analysis.get('action') == 'retry' and retry_count >= max_retries:
                    print(f"\n⚠ 步骤执行失败，已达到最大重试次数（{max_retries}次）")
                    print(f"将重试模式切换为AI处理模式")

                    # 获取错误信息
                    error_info = analysis.get('error_info', {})
                    error_code = analysis.get('error_code')

                    # 直接调用iFlow CLI
                    print(f"\n[AI处理]")
                    print(f"→ 检测到需要处理的错误")
                    print(f"错误码: {error_code}")
                    print(f"错误名称: {error_info.get('name', 'N/A')}")
                    print(f"正在向iFlow CLI发送处理请求...")

                    # 向iFlow CLI发送错误分析请求
                    log_file_path = step_logger.log_file
                    prompt = '重试已达最大次数，但还是没成功，请分析原因并处理'

                    send_result = iflow_client.send_error_analysis(
                        error_code=error_code,
                        step_name=step_info['name'],
                        log_file_path=log_file_path,
                        prompt=prompt,
                        log_lines=500
                    )

                    # 创建新的analysis结果
                    if send_result.get('success'):
                        print(f"✓ 请求已发送，等待iFlow CLI响应...")
                        if 'response' in send_result:
                            response = send_result['response']
                            print(f"iFlow CLI响应: {response.get('message', 'N/A')}")
                            # 根据响应返回一个结果
                            if response.get('can_resolve'):
                                # iFlow CLI能够解决
                                print(f"✓ iFlow CLI可以自动解决此错误并修正配置文件")
                                new_analysis = {
                                    'should_continue': True,
                                    'message': f'iFlow CLI正在处理: {error_info.get("name", "未知错误")}',
                                    'action': 'ai_resolve',
                                    'error_code': error_code,
                                    'error_info': error_info
                                }
                            else:
                                # 需要人工干预
                                print(f"? iFlow CLI建议需要人工干预")
                                new_analysis = {
                                    'should_continue': False,
                                    'message': f'iFlow CLI建议需要人工干预: {error_info.get("name", "未知错误")}',
                                    'action': 'manual',
                                    'error_code': error_code,
                                    'error_info': error_info
                                }
                        else:
                            # 没有响应
                            print(f"? iFlow CLI没有返回响应")
                            new_analysis = {
                                'should_continue': False,
                                'message': f'iFlow CLI未返回响应: {error_info.get("name", "未知错误")}',
                                'action': 'manual',
                                'error_code': error_code,
                                'error_info': error_info
                            }
                    else:
                        # 发送请求失败
                        print(f"✗ 发送请求失败: {send_result.get('message')}")
                        new_analysis = {
                            'should_continue': False,
                            'message': f'无法连接到iFlow CLI: {send_result.get("message")}',
                            'action': 'manual',
                            'error_code': error_code,
                            'error_info': error_info
                        }

                    # 更新result中的analysis
                    result['analysis'] = new_analysis
                break
        else:
            break

    # 记录步骤完成
    if step_logger.enabled and result:
        step_name_with_retry = f"{step_info['name']}"
        if retry_count > 0:
            step_name_with_retry += f" (重试 {retry_count}/{max_retries})"
        step_logger.log_step_complete(step_key, step_name_with_retry, result)

    # 清除重试参数（无论成功还是失败）
    if retry_params:
        config.save_step_progress(step_key, date)

    # 保存进度（如果返回值包含日期信息）
    if result and 'date' in result and result['date']:
        config.save_step_progress(step_key, result['date'])
    else:
        config.save_step_progress(step_key, date)

    return result


def _call_step_function(ssh, step_key, step_info, date, max_wait, retry_params, submit_job_arg=None, check_arg=None):
    """
    调用步骤函数的辅助函数

    Args:
        ssh: SSH连接实例
        step_key: 步骤键值
        step_info: 步骤信息
        date: 日期参数
        max_wait: 最大等待时间
        retry_params: 重试参数
        submit_job_arg: submit_job参数
        check_arg: check参数

    Returns:
        dict: 执行结果
    """
    if step_key == '1.1':
        # 步骤1.1特殊处理：如果有重试参数且包含submit_job，则使用该值；否则使用submit_job_arg或默认值（True）
        if retry_params and 'submit_job' in retry_params:
            return step_info['func'](ssh, date, retry_params['submit_job'], max_wait_minutes=max_wait)
        else:
            # 使用submit_job_arg（如果提供）或函数的默认值
            if submit_job_arg is not None:
                return step_info['func'](ssh, date, submit_job_arg, max_wait_minutes=max_wait)
            else:
                return step_info['func'](ssh, date, max_wait_minutes=max_wait)
    elif step_key == '2.1':
        # 步骤2.1特殊处理：如果有重试参数且包含submit_job，则使用该值；否则使用submit_job_arg或默认值（True）
        if retry_params and 'submit_job' in retry_params:
            return step_info['func'](ssh, date, retry_params['submit_job'], max_wait_minutes=max_wait)
        else:
            # 使用submit_job_arg（如果提供）或函数的默认值
            if submit_job_arg is not None:
                return step_info['func'](ssh, date, submit_job_arg, max_wait_minutes=max_wait)
            else:
                return step_info['func'](ssh, date, max_wait_minutes=max_wait)
    elif step_key == '3.1':
        # 步骤3.1特殊处理：如果有重试参数且包含submit_job，则使用该值；否则使用submit_job_arg或默认值（True）
        if retry_params and 'submit_job' in retry_params:
            return step_info['func'](ssh, retry_params['submit_job'], max_wait_minutes=max_wait)
        else:
            # 使用submit_job_arg（如果提供）或函数的默认值
            if submit_job_arg is not None:
                return step_info['func'](ssh, submit_job_arg, max_wait_minutes=max_wait)
            else:
                return step_info['func'](ssh, max_wait_minutes=max_wait)
    elif step_key == '5.1':
        # 步骤5.1特殊处理：如果有重试参数且包含submit_job，则使用该值；否则使用submit_job_arg或默认值（True）
        if retry_params and 'submit_job' in retry_params:
            return step_info['func'](ssh, date, retry_params['submit_job'], max_wait_minutes=max_wait)
        else:
            # 使用submit_job_arg（如果提供）或函数的默认值
            if submit_job_arg is not None:
                return step_info['func'](ssh, date, submit_job_arg, max_wait_minutes=max_wait)
            else:
                return step_info['func'](ssh, date, max_wait_minutes=max_wait)
    elif step_key == '6.1':
        # 步骤6.1特殊处理：如果有重试参数且包含submit_job，则使用该值；否则使用submit_job_arg或默认值（True）
        if retry_params and 'submit_job' in retry_params:
            return step_info['func'](ssh, retry_params['submit_job'], max_wait_minutes=max_wait)
        else:
            # 使用submit_job_arg（如果提供）或函数的默认值
            if submit_job_arg is not None:
                return step_info['func'](ssh, submit_job_arg, max_wait_minutes=max_wait)
            else:
                return step_info['func'](ssh, max_wait_minutes=max_wait)
    elif step_key == '4.1':
        # 步骤4.1特殊处理：支持submit_job和check参数
        submit_job_val = True  # 默认值
        check_val = False  # 默认值

        # 从重试参数获取
        if retry_params:
            if 'submit_job' in retry_params:
                submit_job_val = retry_params['submit_job']
            if 'check' in retry_params:
                check_val = retry_params['check']
        else:
            # 从命令行参数获取
            if submit_job_arg is not None:
                submit_job_val = submit_job_arg
            if check_arg is not None:
                check_val = check_arg

        return step_info['func'](ssh, date, submit_job_val, check_val, max_wait_minutes=max_wait)
    elif step_info['is_check_step']:
        # 定时检查步骤
        if step_info['needs_date']:
            return step_info['func'](ssh, date, max_wait)
        else:
            return step_info['func'](ssh, max_wait)
    elif step_info['needs_date']:
        # 需要日期的非检查步骤
        return step_info['func'](ssh, date)
    else:
        # 不需要日期的非检查步骤
        return step_info['func'](ssh)


# ============================================================================
# 辅助函数：处理分析结果
# ============================================================================

def handle_analysis_result(analysis, step_key, date, mode='all'):
    """
    处理分析结果

    Args:
        analysis: 分析结果
        step_key: 步骤键值
        date: 日期
        mode: 执行模式（'all' 或 'total'）

    Returns:
        str: 用户选择的指令
             - 'retry': 重试当前步骤
             - 'quit': 退出执行
    """
    print(f"\n✗ 分析建议: {analysis['message']}")
    print(f"推荐操作: {analysis['action']}")

    # 处理action='retry'的情况
    if analysis['action'] == 'retry':
        print(f"\n⚠ 步骤 {step_key} 重试失败，已达到最大重试次数")
        print(f"交给iFlow CLI处理...")

    # 处理action='ai'或'retry'的情况
    if analysis['action'] == 'ai' or analysis['action'] == 'retry':
        print(f"\n? iFlow CLI正在处理错误...")
        print(f"说明: {analysis.get('message')}")
        print(f"等待iFlow CLI解决...")
        return 'quit'  # 停止执行

    # 处理action='manual'的情况
    if analysis['action'] == 'manual':
        return _handle_manual_intervention(step_key, date, mode)

    # 其他情况
    print(f"使用: python run.py --step {step_key} --date {date} 单独执行此步骤")
    return 'quit'  # 停止执行


def _handle_manual_intervention(step_key, date, mode):
    """
    处理人工干预（已禁用交互功能）

    Args:
        step_key: 步骤键值
        date: 日期
        mode: 执行模式（'step', 'all' 或 'total'）

    Returns:
        str: 用户选择的指令
             - 'quit': 退出执行（交互功能已禁用）
    """
    print("\n" + "="*60)
    print("? 分析建议需要人工干预")
    print("="*60)
    print("⚠ 交互功能已禁用，自动选择退出执行")
    print("请查看日志文件了解详细错误信息")
    print("="*60)
    return 'quit'  # 直接退出执行


# ============================================================================
# 辅助函数：获取日期
# ============================================================================

def get_date_for_step(ssh, step_key, args_date):
    """
    获取步骤所需的日期

    Args:
        ssh: SSH连接实例
        step_key: 步骤键值
        args_date: 命令行参数中的日期

    Returns:
        str: 日期
    """
    # 如果步骤不需要日期，返回None
    if not STEPS[step_key]['needs_date']:
        return None

    # 如果用户指定了日期，直接使用
    if args_date:
        return args_date

    # 步骤1.1：使用对比逻辑获取日期
    if step_key == '1.1':
        return _get_date_by_comparison(ssh)

    # 其他步骤：从进度文件读取
    progress = config.load_step_progress()
    date = progress.get('date')
    if not date:
        print("✗ 未找到日期信息，请先执行步骤1.1或使用 --date 参数")
        return None
    print(f"从进度文件读取日期: {date}")
    return date


def _get_date_by_comparison(ssh):
    """
    通过对比已处理和未处理的日期来获取日期

    Args:
        ssh: SSH连接实例

    Returns:
        str: 选中的日期
    """
    print("步骤1.1未指定日期，使用对比逻辑获取日期...")

    # 获取已处理数据的目录
    result1 = ssh.execute_command(f"ls -1 {config.INJ_SIG_TIME_CAL_DIR}")
    if not result1['success']:
        print("✗ 获取已处理数据目录失败")
        return None

    processed_dates = [line.strip() for line in result1['output'].split('\n')
                      if line.strip() and re.match(r'^\d{6}$', line.strip())]
    print(f"已处理日期: {processed_dates}")

    # 获取所有可能处理日期的目录
    result2 = ssh.execute_command(f"ls -1 {config.DATA_DIR}")
    if not result2['success']:
        print("✗ 获取所有可用数据目录失败")
        return None

    all_dates = [line.strip() for line in result2['output'].split('\n')
                if line.strip() and re.match(r'^\d{6}$', line.strip())]
    print(f"所有可用日期: {all_dates}")

    # 找出未处理的日期
    unprocessed_dates = [date_item for date_item in all_dates if date_item not in processed_dates]
    print(f"未处理日期: {unprocessed_dates}")

    if not unprocessed_dates:
        print("✗ 没有找到未处理的日期")
        return None

    # 选择最小的未处理日期
    date = min(unprocessed_dates)
    print(f"\n✓ 选中的日期: {date}")
    return date


# ============================================================================
# 执行模式：step模式
# ============================================================================

def execute_single_step(ssh, args):
    """
    执行单个步骤

    Args:
        ssh: SSH连接实例
        args: 命令行参数
    """
    step_key = args.step
    has_error = False  # 跟踪是否出现错误

    if step_key not in STEPS:
        print(f"✗ 未知的步骤: {step_key}")
        print("使用 --list 查看所有可用步骤")
        return

    print(f"\n执行步骤: {step_key} - {STEPS[step_key]['name']}")

    # 启用日志记录
    step_logger.enable("single")

    # 获取日期
    date = get_date_for_step(ssh, step_key, args.date)
    if date is None and STEPS[step_key]['needs_date']:
        return

    # 处理submit_job参数
    submit_job_arg = None
    if hasattr(args, 'submit_job') and args.submit_job:
        submit_job_arg = args.submit_job == 'true'

    # 处理check参数
    check_arg = None
    if hasattr(args, 'check') and args.check:
        check_arg = args.check == 'true'

    # 执行步骤
    result = execute_step(ssh, step_key, date, args.max_wait, submit_job_arg=submit_job_arg, check_arg=check_arg)

    if not result:
        print(f"\n✗ 步骤 {step_key} 返回None，停止执行")
        has_error = True
        step_logger.log_mode_exit("single", has_error)
        step_logger.disable()
        return

    # 显示结果
    if result.get('success'):
        print(f"\n✓ {result.get('message', '步骤执行成功')}")
    else:
        print(f"\n✗ {result.get('message', '步骤执行失败')}")
        has_error = True

        # 如果有分析结果
        if 'analysis' in result:
            analysis = result['analysis']
            print(f"\n[分析结果]")
            for key, value in analysis.items():
                print(f"  {key}: {value}")

            # 如果 action=manual，提供交互式选择
            if analysis.get('action') == 'manual':
                user_choice = _handle_manual_intervention(step_key, date, 'step')

                # 处理用户选择
                if user_choice == 'retry':
                    # 用户选择重试，重新执行当前步骤（不循环）
                    print(f"\n⚠ 重新执行步骤 {step_key}...")
                    result = execute_step(ssh, step_key, date, args.max_wait, submit_job_arg=submit_job_arg)

                    if result and result.get('success'):
                        print(f"\n✓ {result.get('message', '步骤执行成功')}")
                        has_error = False  # 重试成功，清除错误标志
                    else:
                        print(f"\n✗ {result.get('message', '步骤执行失败')}")
                        has_error = True
                        if 'analysis' in result:
                            print(f"\n[分析结果]")
                            for key, value in result['analysis'].items():
                                print(f"  {key}: {value}")
                elif user_choice == 'quit':
                    print(f"\n✓ 用户选择退出执行")
                    has_error = True
                    step_logger.log_mode_exit("single", has_error)
                    step_logger.disable()
                    return

    # 记录模式退出状态
    step_logger.log_mode_exit("single", has_error)
    step_logger.disable()


# ============================================================================
# 执行模式：all模式
# ============================================================================

def execute_all_steps(ssh, args):
    """
    执行所有步骤

    Args:
        ssh: SSH连接实例
        args: 命令行参数
    """
    print("\n执行所有步骤（含分析）...")

    # 启用日志记录
    step_logger.enable("all")

    date = args.date
    has_error = False  # 跟踪是否出现错误

    # 执行所有步骤（含分析）
    for step_key in STEP_ORDER:
        # 获取日期
        if STEPS[step_key]['needs_date'] and not date:
            progress = config.load_step_progress()
            date = progress.get('date')

        # 执行步骤（支持重试）
        while True:
            # 执行步骤
            result = execute_step(ssh, step_key, date, args.max_wait, submit_job_arg=getattr(args, 'submit_job_arg', True), check_arg=getattr(args, 'check_arg', False))

            if not result:
                print(f"\n✗ 步骤 {step_key} 返回None，停止执行")
                has_error = True
                step_logger.log_mode_exit("all", has_error)
                step_logger.disable()
                return

            # 保存日期
            if result and 'date' in result and result['date']:
                config.save_step_progress(step_key, result['date'])

            # 检查分析结果
            if 'analysis' in result:
                analysis = result['analysis']
                if not analysis['should_continue']:
                    user_choice = handle_analysis_result(analysis, step_key, date, 'all')

                    # 处理用户选择
                    if user_choice == 'quit':
                        has_error = True
                        step_logger.log_mode_exit("all", has_error)
                        step_logger.disable()
                        return
                    elif user_choice == 'retry':
                        # 用户选择重试，继续 while 循环，重新执行当前步骤
                        print(f"\n⚠ 重新执行步骤 {step_key}...")
                        continue
                else:
                    # 分析建议继续执行，跳出 while 循环，执行下一个步骤
                    break
            else:
                # 没有分析结果，检查步骤是否成功
                if result.get('success'):
                    # 步骤成功，跳出 while 循环，执行下一个步骤
                    break
                else:
                    # 步骤失败但没有分析结果，停止执行
                    print(f"\n✗ 步骤 {step_key} 执行失败，停止执行")
                    print(f"使用: python run.py --step {step_key} --date {date} 单独执行此步骤")
                    has_error = True
                    step_logger.log_mode_exit("all", has_error)
                    step_logger.disable()
                    return

    # 清除进度
    config.clear_step_progress()

    # 记录执行完成
    step_logger.log_execution_complete("所有步骤执行完成")

    # 记录模式退出状态
    step_logger.log_mode_exit("all", has_error)

    # 关闭日志记录
    step_logger.disable()

    print("\n✓ 所有步骤执行完成")
    print(f"日志文件: {step_logger.log_file}")


# ============================================================================
# 执行模式：total模式
# ============================================================================

def execute_total_mode(ssh, args):
    """
    执行Total模式（批量处理所有日期）

    Args:
        ssh: SSH连接实例
        args: 命令行参数
    """
    print("\n执行Total模式（批量处理所有日期）...")

    # 启用日志记录
    step_logger.enable("total")

    date = None
    loop_count = 0
    processed_dates = []
    has_error = False  # 跟踪是否出现错误

    while True:
        loop_count += 1
        print(f"\n{'='*60}")
        print(f"Total模式 - 第 {loop_count} 次执行")
        print(f"{'='*60}")

        if date:
            print(f"当前日期: {date}")
        else:
            print("等待步骤1.1自动获取日期...")

        # 记录循环开始
        step_logger.log_loop_start(loop_count, date)

        # 执行所有步骤（含分析）
        for step_key in STEP_ORDER:
            # 获取日期
            if STEPS[step_key]['needs_date'] and not date:
                progress = config.load_step_progress()
                date = progress.get('date')

            # 执行步骤（支持重试）
            while True:
                # 执行步骤
                result = execute_step(ssh, step_key, date, args.max_wait, submit_job_arg=getattr(args, 'submit_job_arg', True), check_arg=getattr(args, 'check_arg', False))

                if not result:
                    print(f"\n✗ 步骤 {step_key} 返回None，停止执行")
                    has_error = True
                    step_logger.log_mode_exit("total", has_error)
                    step_logger.disable()
                    return

                # 保存日期
                if result and 'date' in result and result['date']:
                    config.save_step_progress(step_key, result['date'])
                    date = result['date']

                # 检查分析结果
                if 'analysis' in result:
                    analysis = result['analysis']

                    # 处理ai_resolve
                    if analysis.get('action') == 'ai_resolve':
                        print(f"\n? iFlow CLI正在处理错误...")
                        print(f"说明: {analysis.get('message')}")
                        print(f"等待iFlow CLI解决...")
                        has_error = True
                        step_logger.log_mode_exit("total", has_error)
                        step_logger.disable()
                        return

                    # 处理exit
                    if analysis.get('action') == 'exit':
                        print(f"\n{'='*60}")
                        print(f"✓ Total模式退出")
                        print(f"{'='*60}")
                        print(f"原因: {analysis.get('message', '所有日期都已处理完成')}")
                        print(f"已处理 {loop_count - 1} 个日期")

                        # 记录Total模式完成
                        step_logger.log_execution_complete(f"Total模式完成，共处理 {loop_count - 1} 个日期")

                        # 记录模式退出状态（正常退出，无错误）
                        step_logger.log_mode_exit("total", has_error)

                        # 关闭日志记录
                        step_logger.disable()

                        # 清除进度
                        config.clear_step_progress()

                        return

                    # 处理其他情况
                    if not analysis['should_continue']:
                        user_choice = handle_analysis_result(analysis, step_key, date, 'total')

                        # 处理用户选择
                        if user_choice == 'quit':
                            has_error = True
                            step_logger.log_mode_exit("total", has_error)
                            step_logger.disable()
                            return
                        elif user_choice == 'retry':
                            # 用户选择重试，继续 while 循环，重新执行当前步骤
                            print(f"\n⚠ 重新执行步骤 {step_key}...")
                            continue
                    else:
                        # 分析建议继续执行，跳出 while 循环，执行下一个步骤
                        break
                else:
                    # 没有分析结果，检查步骤是否成功
                    if result.get('success'):
                        # 步骤成功，跳出 while 循环，执行下一个步骤
                        break
                    else:
                        # 步骤失败但没有分析结果，停止执行
                        print(f"\n✗ 步骤 {step_key} 执行失败，停止执行")
                        print(f"使用: python run.py --step {step_key} --date {date} 单独执行此步骤")
                        has_error = True
                        step_logger.log_mode_exit("total", has_error)
                        step_logger.disable()
                        return

        # 记录循环完成
        step_logger.log_loop_complete(loop_count, processed_dates)

        # 清除当前日期，准备下一个日期
        processed_dates.append(date)
        date = None
        config.clear_step_progress()


# ============================================================================
# 主函数
# ============================================================================

def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='执行Topup数据验证的各个步骤（增强版）')
    parser.add_argument('--step', type=str, help='要执行的步骤（例如：1.4）')
    parser.add_argument('--date', type=str, help='日期参数（例如：250624）')
    parser.add_argument('--list', action='store_true', help='列出所有可用步骤')
    parser.add_argument('--all', action='store_true', help='执行所有步骤（含分析）')
    parser.add_argument('--total', action='store_true', help='Total模式：批量处理所有日期，处理完步骤7后自动重新从步骤1开始')
    parser.add_argument('--no-analysis', action='store_true', help='（已弃用）分析始终启用')
    parser.add_argument('--max-wait', type=int, help='最大等待时间（分钟），用于定时检查步骤（1.1、2.2、2.5、3.1、5.1、6.2）')
    parser.add_argument('--submit-job', type=str, choices=['true', 'false'], help='是否提交作业（true/false），用于步骤1.1、2.1、3.1、4.1、5.1、6.1。默认为true')
    parser.add_argument('--check', type=str, choices=['true', 'false'], help='是否检查生成的文件（true/false），用于步骤4.1。默认为false（非topup模式）')

    args = parser.parse_args()

    # 处理submit_job参数
    submit_job_arg = True  # 默认值
    if args.submit_job:
        submit_job_arg = args.submit_job == 'true'

    # 处理check参数
    check_arg = False  # 默认值
    if args.check:
        check_arg = args.check == 'true'

    # 将参数附加到args对象，供execute_all_steps和execute_total_mode使用
    args.submit_job_arg = submit_job_arg
    args.check_arg = check_arg

    # 列出所有可用步骤
    if args.list:
        print("\n所有可用步骤：")
        print("="*60)
        for step_key, step_info in STEPS.items():
            print(f"  {step_key}: {step_info['name']}")
            if step_info.get('manual_only'):
                print(f"    (只能单步执行)")
        print("="*60)
        return

    # 检查参数
    if not any([args.step, args.all, args.total]):
        print("✗ 请指定执行模式：--step、--all 或 --total")
        print("使用 --list 查看所有可用步骤")
        print("使用 --help 查看帮助信息")
        return

    # 如果指定了日期但没有指定执行模式，默认为all模式
    if args.date and not any([args.step, args.all, args.total]):
        args.all = True

    # 建立SSH连接
    print("\n正在建立SSH连接...")
    ssh = TopupSSH()

    if not ssh.connect():
        print("\n✗ SSH连接失败")
        return

    print("✓ SSH连接成功")

    try:
        # 根据模式执行
        if args.step:
            execute_single_step(ssh, args)
        elif args.all:
            execute_all_steps(ssh, args)
        elif args.total:
            execute_total_mode(ssh, args)

    finally:
        ssh.close()
        # 关闭日志记录
        step_logger.disable()

    return


if __name__ == "__main__":
    main()
