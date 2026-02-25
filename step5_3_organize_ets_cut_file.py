#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
步骤5.3：整理ets_cut.txt文件
1. 删除只有一个数字的行
2. 根据每行的第一个数字排序
3. 删除重复的行
"""

from typing import Dict, Any
from topup_ssh import TopupSSH
import config


def step5_3_organize_ets_cut_file(ssh: TopupSSH, date: str = None) -> Dict[str, Any]:
    """
    整理ets_cut.txt文件

    1. 删除只有一个数字的行
    2. 根据每行的第一个数字排序
    3. 删除重复的行

    Args:
        ssh: SSH连接实例
        date: 日期参数（保留接口兼容性）

    Returns:
        dict: 执行结果
    """
    print("\n" + "="*60)
    print("步骤5.3：整理ets_cut.txt文件")
    print("="*60)

    try:
        # 进入ETS_cut目录
        ets_cut_dir = config.ETS_CUT_DIR
        print(f"\n进入ETS_cut目录: {ets_cut_dir}")

        # 步骤1：删除只有一个数字的行
        print("\n步骤1：删除只有一个数字的行...")
        result1 = ssh.execute_command(
            f"cd {ets_cut_dir} && "
            f"grep -vE '^[0-9]+$' ets_cut.txt > ets_cut_temp.txt && "
            f"mv ets_cut_temp.txt ets_cut.txt"
        )

        if not result1['success']:
            return {
                'success': False,
                'message': '删除单数字行失败',
                'step_name': '步骤5.3：整理ets_cut.txt文件',
                'output': result1['output'],
                'error': result1.get('error', '')
            }

        print("✓ 删除单数字行成功")

        # 步骤2：根据每行的第一个数字排序
        print("\n步骤2：根据每行的第一个数字排序...")
        result2 = ssh.execute_command(
            f"cd {ets_cut_dir} && "
            f"sort -n -k1,1 ets_cut.txt > ets_cut_temp.txt && "
            f"mv ets_cut_temp.txt ets_cut.txt"
        )

        if not result2['success']:
            return {
                'success': False,
                'message': '排序失败',
                'step_name': '步骤5.3：整理ets_cut.txt文件',
                'output': result2['output'],
                'error': result2.get('error', '')
            }

        print("✓ 排序成功")

        # 步骤3：删除重复的行
        print("\n步骤3：删除重复的行...")
        result3 = ssh.execute_command(
            f"cd {ets_cut_dir} && "
            f"uniq ets_cut.txt > ets_cut_temp.txt && "
            f"mv ets_cut_temp.txt ets_cut.txt"
        )

        if not result3['success']:
            return {
                'success': False,
                'message': '删除重复行失败',
                'step_name': '步骤5.3：整理ets_cut.txt文件',
                'output': result3['output'],
                'error': result3.get('error', '')
            }

        print("✓ 删除重复行成功")

        # 验证整理后的文件
        print("\n验证整理后的文件...")
        result_verify = ssh.execute_command(f"cd {ets_cut_dir} && cat ets_cut.txt")

        print(f"\n✓ ets_cut.txt文件整理完成")
        print(f"文件内容:\n{result_verify['output']}")

        return {
            'success': True,
            'message': 'ets_cut.txt文件整理完成',
            'step_name': '步骤5.3：整理ets_cut.txt文件',
            'file_content': result_verify['output']
        }

    except Exception as e:
        return {
            'success': False,
            'message': f'整理ets_cut.txt文件异常: {str(e)}',
            'step_name': '步骤5.3：整理ets_cut.txt文件',
            'error': str(e)
        }


if __name__ == "__main__":
    # 测试步骤5.3
    with TopupSSH() as ssh:
        if ssh.connected:
            result = step5_3_organize_ets_cut_file(ssh)
            print("\n" + "="*60)
            print("步骤5.3执行结果:")
            print("="*60)
            print(f"成功: {result['success']}")
            print(f"消息: {result['message']}")