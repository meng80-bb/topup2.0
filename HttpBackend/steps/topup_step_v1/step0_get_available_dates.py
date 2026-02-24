#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
步骤0：获取所有可用数据目录的日期列表

此步骤用于获取数据目录中所有可用的日期列表，供用户选择或后续步骤使用。
"""

import re
from typing import Dict, Any, List, Optional
from topup_ssh import TopupSSH
import config


def _get_all_available_dates(ssh: TopupSSH) -> Dict[str, Any]:
    """
    获取所有可用数据目录的日期列表

    Args:
        ssh: SSH连接实例

    Returns:
        dict: 包含 success, dates (成功时), 或 error (失败时)
    """
    print("\n获取所有可用数据目录...")
    print(f"数据目录: {config.DATA_DIR}")

    result = ssh.execute_command(f"ls -1 {config.DATA_DIR}")

    if not result['success']:
        return {
            'success': False,
            'message': '获取所有可用数据目录失败',
            'error': result.get('error', '未知错误')
        }

    # 解析所有可用日期列表（只保留6位数字的目录名）
    all_dates = [
        line.strip() for line in result['output'].split('\n')
        if line.strip() and re.match(r'^\d{6}$', line.strip())
    ]

    # 按日期排序
    all_dates.sort()

    print(f"找到 {len(all_dates)} 个可用日期目录")
    print(f"日期列表: {all_dates}")

    return {
        'success': True,
        'dates': all_dates
    }


def _get_processed_dates(ssh: TopupSSH) -> Dict[str, Any]:
    """
    获取已处理数据目录的日期列表

    Args:
        ssh: SSH连接实例

    Returns:
        dict: 包含 success, dates (成功时), 或 error (失败时)
    """
    print("\n获取已处理数据目录...")
    print(f"处理结果目录: {config.INJ_SIG_TIME_CAL_DIR}")

    result = ssh.execute_command(f"ls -1 {config.INJ_SIG_TIME_CAL_DIR}")

    if not result['success']:
        return {
            'success': False,
            'message': '获取已处理数据目录失败',
            'error': result.get('error', '未知错误')
        }

    # 解析已处理日期列表（只保留6位数字的目录名）
    processed_dates = [
        line.strip() for line in result['output'].split('\n')
        if line.strip() and re.match(r'^\d{6}$', line.strip())
    ]

    # 按日期排序
    processed_dates.sort()

    print(f"找到 {len(processed_dates)} 个已处理日期目录")
    print(f"已处理日期: {processed_dates}")

    return {
        'success': True,
        'dates': processed_dates
    }


def _calculate_unprocessed_dates(
    all_dates: List[str],
    processed_dates: List[str]
) -> List[str]:
    """
    计算未处理的日期列表

    Args:
        all_dates: 所有可用日期列表
        processed_dates: 已处理日期列表

    Returns:
        List[str]: 未处理的日期列表
    """
    unprocessed_dates = [
        date for date in all_dates
        if date not in processed_dates
    ]
    return unprocessed_dates


def step0_get_available_dates(
    ssh: TopupSSH,
    include_processed: bool = True,
    sort_order: str = 'asc'
) -> Dict[str, Any]:
    """
    步骤0：获取所有可用数据目录的日期列表

    此步骤负责：
    1. 获取数据目录中所有可用的日期列表
    2. 如果 include_processed=True，同时获取已处理的日期列表
    3. 返回完整的日期信息供用户选择或后续步骤使用

    Args:
        ssh: TopupSSH 实例，用于执行远程命令
        include_processed: 是否包含已处理日期信息，默认为True
        sort_order: 排序方式，'asc'（升序）或'desc'（降序），默认为'asc'

    Returns:
        包含以下键的字典：
            - success (bool, 必需): 是否成功
            - message (str, 必需): 人类可读的消息
            - all_dates (list, 可选): 所有可用日期列表
            - processed_dates (list, 可选): 已处理日期列表（当include_processed=True时）
            - unprocessed_dates (list, 可选): 未处理日期列表（当include_processed=True时）
            - total_count (int, 可选): 总日期数量
            - processed_count (int, 可选): 已处理日期数量
            - unprocessed_count (int, 可选): 未处理日期数量
            - error (str, 可选): 失败时的错误详情
    """
    print("\n" + "="*60)
    print("步骤0：获取所有可用数据目录的日期列表")
    print("="*60)
    print(f"包含已处理日期信息: {include_processed}")
    print(f"排序方式: {sort_order}")

    try:
        # 1. 获取所有可用日期
        all_dates_result = _get_all_available_dates(ssh)

        if not all_dates_result['success']:
            return {
                'success': False,
                'message': all_dates_result['message'],
                'error': all_dates_result.get('error', ''),
                'step_name': 'step0'
            }

        all_dates = all_dates_result['dates']

        # 应用排序
        if sort_order == 'desc':
            all_dates.sort(reverse=True)

        # 2. 如果需要，获取已处理日期信息
        if include_processed:
            processed_dates_result = _get_processed_dates(ssh)

            if not processed_dates_result['success']:
                # 获取已处理日期失败，但只返回所有可用日期
                print("⚠ 获取已处理日期失败，仅返回所有可用日期")

                return {
                    'success': True,
                    'message': f'成功获取 {len(all_dates)} 个可用日期（无法获取已处理日期信息）',
                    'step_name': 'step0',
                    'all_dates': all_dates,
                    'total_count': len(all_dates),
                    'sort_order': sort_order,
                    'warning': '无法获取已处理日期信息'
                }

            processed_dates = processed_dates_result['dates']

            # 应用排序
            if sort_order == 'desc':
                processed_dates.sort(reverse=True)

            # 计算未处理日期
            unprocessed_dates = _calculate_unprocessed_dates(all_dates, processed_dates)

            # 应用排序
            if sort_order == 'desc':
                unprocessed_dates.sort(reverse=True)

            print(f"\n统计信息:")
            print(f"  总日期数: {len(all_dates)}")
            print(f"  已处理: {len(processed_dates)}")
            print(f"  未处理: {len(unprocessed_dates)}")

            return {
                'success': True,
                'message': f'成功获取日期信息：共{len(all_dates)}个，已处理{len(processed_dates)}个，未处理{len(unprocessed_dates)}个',
                'step_name': 'step0',
                'all_dates': all_dates,
                'processed_dates': processed_dates,
                'unprocessed_dates': unprocessed_dates,
                'total_count': len(all_dates),
                'processed_count': len(processed_dates),
                'unprocessed_count': len(unprocessed_dates),
                'sort_order': sort_order
            }

        else:
            # 只返回所有可用日期
            print(f"\n统计信息:")
            print(f"  总日期数: {len(all_dates)}")

            return {
                'success': True,
                'message': f'成功获取 {len(all_dates)} 个可用日期',
                'step_name': 'step0',
                'all_dates': all_dates,
                'total_count': len(all_dates),
                'sort_order': sort_order
            }

    except Exception as e:
        return {
            'success': False,
            'message': f'获取日期列表异常: {str(e)}',
            'error': str(e),
            'step_name': 'step0'
        }
