#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
步骤1.4：合并图片
进入Interval_plot目录，进入容器，执行convert命令合并PNG图片为PDF
"""

import os
from typing import Dict, Any, Optional
from topup_ssh import TopupSSH


def step1_4_merge_images(
    ssh: TopupSSH,
    date: str,
    round: str,
    local_file_dir: str,
    download_files: bool = True
) -> Dict[str, Any]:
    """
    合并Interval_plot目录中的PNG图片为PDF

    进入Interval_plot目录，使用容器中的convert命令将所有PNG图片合并为一个PDF文件
    可选择性地将PDF文件下载到本地

    Args:
        ssh: TopupSSH 实例，用于执行远程命令和文件传输
        date: 日期参数（如250624），必需参数
        round: 轮次标识符（如round7），用于构建目录路径
        local_file_dir: 本地文件下载目录（如downloads/123_4）
        download_files: 是否下载PDF文件到本地，默认为True

    Returns:
        包含以下键的字典：
            - success (bool, 必需): 是否成功
            - message (str, 必需): 人类可读的消息
            - step_name (str, 推荐): 步骤名称
            - date (str, 推荐): 使用的日期
            - pdf_remote_path (str, 可选): 远程PDF文件路径
            - pdf_local_path (str, 可选): 本地PDF文件路径
            - output (str, 可选): 命令输出
            - error (str, 可选): 失败时的错误详情
    """
    print("\n" + "="*60)
    print("步骤1.4：合并图片")
    print("="*60)
    print(f"日期: {date}")
    print(f"轮次: {round}")
    print(f"本地目录: {local_file_dir}")

    # 构建远程目录路径
    base_dir = f"/besfs5/groups/cal/topup/{round}/DataValid/InjSigTimeCal"
    interval_plot_dir = f"{base_dir}/{date}/Interval_plot"

    try:
        # 检查Interval_plot目录是否存在
        print(f"\n检查Interval_plot目录: {interval_plot_dir}")
        check_result = ssh.execute_command(f"ls -d {interval_plot_dir} 2>/dev/null")

        if not check_result['success'] or not check_result['output'].strip():
            return {
                'success': False,
                'message': f'Interval_plot目录不存在: {interval_plot_dir}',
                'step_name': 'step1_4',
                'date': date,
                'error': check_result.get('error', '目录不存在')
            }

        print(f"✓ 目录存在")

        # 检查是否有PNG文件
        print(f"\n检查PNG文件...")
        png_check = ssh.execute_command(f"cd {interval_plot_dir} && ls *.png 2>/dev/null | wc -l")

        if not png_check['success']:
            return {
                'success': False,
                'message': '检查PNG文件失败',
                'step_name': 'step1_4',
                'date': date,
                'error': png_check.get('error', '')
            }

        png_count = int(png_check['output'].strip())
        print(f"找到 {png_count} 个PNG文件")

        if png_count == 0:
            return {
                'success': False,
                'message': 'Interval_plot目录中没有PNG文件',
                'step_name': 'step1_4',
                'date': date
            }

        # 进入容器并执行convert命令合并PNG为PDF
        print(f"\n执行convert命令合并PNG为PDF...")

        # 使用heredoc在容器中执行命令
        command = f"""cd {interval_plot_dir} && /cvmfs/container.ihep.ac.cn/bin/hep_container shell SL6 << 'EOF'
convert *.png mergedd_IST.pdf
exit
EOF"""

        result = ssh.execute_command(command)

        if not result['success']:
            return {
                'success': False,
                'message': '执行convert命令失败',
                'step_name': 'step1_4',
                'date': date,
                'output': result['output'],
                'error': result.get('error', '')
            }

        print(f"✓ convert命令执行成功")
        print(f"输出:\n{result['output']}")

        # 检查PDF文件是否生成
        pdf_path = f"{interval_plot_dir}/mergedd_IST.pdf"
        print(f"\n检查PDF文件: {pdf_path}")

        check_pdf = ssh.execute_command(f"ls -lh {pdf_path} 2>/dev/null")

        if not check_pdf['success'] or not check_pdf['output'].strip():
            return {
                'success': False,
                'message': 'PDF文件未生成',
                'step_name': 'step1_4',
                'date': date,
                'output': result['output']
            }

        print(f"✓ PDF文件已生成")
        print(f"文件信息:\n{check_pdf['output']}")

        # 下载PDF文件到本地
        if download_files:
            print(f"\n下载PDF文件到本地...")
            print(f"本地目录: {local_file_dir}")

            # 创建本地下载目录
            os.makedirs(local_file_dir, exist_ok=True)

            # 本地文件路径
            local_pdf_path = os.path.join(local_file_dir, f"mergedd_IST_{date}.pdf")

            # 使用SFTP下载文件
            download_result = ssh.download_file(pdf_path, local_pdf_path)

            if not download_result['success']:
                return {
                    'success': True,
                    'message': '图片合并成功，但文件下载失败（文件已保存在服务器上）',
                    'step_name': 'step1_4',
                    'date': date,
                    'pdf_remote_path': pdf_path,
                    'output': result['output'],
                    'download_error': download_result.get('error', '')
                }

            print(f"✓ 文件已下载到: {local_pdf_path}")

            return {
                'success': True,
                'message': f'图片合并成功，PDF文件已下载到本地',
                'step_name': 'step1_4',
                'date': date,
                'pdf_remote_path': pdf_path,
                'pdf_local_path': local_pdf_path,
                'output': result['output']
            }
        else:
            # 不下载文件
            return {
                'success': True,
                'message': '图片合并成功，文件已保存在服务器上',
                'step_name': 'step1_4',
                'date': date,
                'pdf_remote_path': pdf_path,
                'output': result['output']
            }

    except Exception as e:
        return {
            'success': False,
            'message': f'合并图片异常: {str(e)}',
            'step_name': 'step1_4',
            'date': date,
            'error': str(e)
        }
