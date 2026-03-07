#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
步骤1.4：合并图片
进入Interval_plot目录，进入容器，执行convert命令合并图片，然后下载到本地
"""

from typing import Dict, Any, Optional
from topup_ssh import TopupSSH
import os


def step1_4_merge_images(
    ssh: TopupSSH,
    round: str,
    date: str,
    local_file_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """
    进入Interval_plot目录，进入容器，执行convert命令合并图片，然后下载到本地

    Args:
        ssh: TopupSSH 实例，用于执行远程命令（必需，自动注入）
        round: 轮次标识符（必需，从工作流配置获取）
        date: 任务的日期参数（自动注入）
        local_file_dir: 本地文件下载目录（自动注入，格式：downloads/{task_id}_{step_order}）

    Returns:
        包含以下键的字典：
            - success (bool): 是否成功
            - message (str): 人类可读的消息
            - console_logs (list): 执行过程日志列表
            - error (str, 可选): 失败时的错误详情
            - pdf_remote_path (str): 远程PDF文件路径
            - pdf_local_path (str): 本地PDF文件路径
    """
    console_logs = []
    console_logs.append("="*60)
    console_logs.append("步骤1.4：合并图片")
    console_logs.append("="*60)
    console_logs.append(f"日期参数: {date}")
    console_logs.append(f"轮次: {round}")

    # 从 round 参数构建路径
    base_dir = f"/besfs5/groups/cal/topup/{round}/DataValid"
    interval_plot_dir = f"{base_dir}/InjSigTimeCal/Interval_plot"

    try:
        # 进入Interval_plot目录，进入容器，执行图片合并
        console_logs.append(f"\n进入目录 {interval_plot_dir} 并执行图片合并...")

        # 在容器中执行convert命令合并图片
        command = f"cd {interval_plot_dir} && /cvmfs/container.ihep.ac.cn/bin/hep_container shell SL6 << 'EOF'\nconvert *.png mergedd_IST.pdf\nexit\nEOF"
        console_logs.append(f"执行命令: cd {interval_plot_dir} && hep_container shell SL6 -> convert *.png mergedd_IST.pdf")

        result = ssh.execute_command(command)

        if not result['success']:
            console_logs.append("✗ 图片合并失败")
            return {
                'success': False,
                'message': '执行图片合并失败',
                'step_name': '步骤1.4：合并图片',
                'date': date,
                'console_logs': console_logs,
                'error': result.get('error', '未知错误')
            }

        console_logs.append("✓ 图片合并成功")

        # 检查PDF文件是否生成
        pdf_path = f"{interval_plot_dir}/mergedd_IST.pdf"
        check_result = ssh.execute_command(f"ls -lh {pdf_path}")
        if check_result['success']:
            console_logs.append(f"PDF文件信息: {check_result['output'].strip()}")

        # 使用SFTP下载PDF文件到本地
        if local_file_dir:
            console_logs.append(f"\n开始下载PDF文件到本地...")

            # 创建本地下载目录
            os.makedirs(local_file_dir, exist_ok=True)

            # 本地文件路径
            local_pdf_path = os.path.join(local_file_dir, f"mergedd_IST_{date}.pdf")

            # 使用SFTP下载文件
            download_result = ssh.download_file(pdf_path, local_pdf_path)

            if not download_result['success']:
                console_logs.append("⚠ 文件下载失败（文件已保存在服务器上）")
                return {
                    'success': True,
                    'message': '图片合并成功，但文件下载失败（文件已保存在服务器上）',
                    'step_name': '步骤1.4：合并图片',
                    'date': date,
                    'console_logs': console_logs,
                    'pdf_remote_path': pdf_path,
                    'download_error': download_result.get('error', '')
                }

            console_logs.append(f"✓ 文件已下载到: {local_pdf_path}")

            return {
                'success': True,
                'message': '图片合并成功，文件已下载到本地',
                'step_name': '步骤1.4：合并图片',
                'date': date,
                'console_logs': console_logs,
                'pdf_remote_path': pdf_path,
                'pdf_local_path': local_pdf_path
            }
        else:
            console_logs.append("⚠ 未提供本地下载目录，跳过下载")
            return {
                'success': True,
                'message': '图片合并成功（未下载到本地）',
                'step_name': '步骤1.4：合并图片',
                'date': date,
                'console_logs': console_logs,
                'pdf_remote_path': pdf_path
            }

    except Exception as e:
        console_logs.append(f"✗ 异常: {str(e)}")
        return {
            'success': False,
            'message': f'执行图片合并异常: {str(e)}',
            'step_name': '步骤1.4：合并图片',
            'date': date,
            'console_logs': console_logs,
            'error': str(e)
        }


if __name__ == "__main__":
    # 测试步骤1.4
    from topup_ssh import TopupSSH

    with TopupSSH() as ssh:
        if ssh.connected:
            result = step1_4_merge_images(
                ssh=ssh,
                round="round18",
                date="250519",
                local_file_dir="./test_downloads"
            )
            print("\n" + "="*60)
            print("步骤1.4执行结果:")
            print("="*60)
            print(f"成功: {result['success']}")
            print(f"消息: {result['message']}")
            if result.get('console_logs'):
                print("\n执行日志:")
                for log in result['console_logs']:
                    print(log)
