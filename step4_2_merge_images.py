#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
步骤4.2：合并图片（checkShieldCalib）
进入checkShieldCalib目录，进入容器，执行merged.sh脚本，然后退出容器
"""

from typing import Dict, Any, Optional
from topup_ssh import TopupSSH
import config


def step4_2_merge_images(ssh: TopupSSH, date: Optional[str] = None) -> Dict[str, Any]:
    """
    进入checkShieldCalib目录，进入容器，执行merged.sh脚本，然后退出容器

    Args:
        ssh: SSH连接实例
        date: 日期参数（如250519），可选。如果未提供，从进度文件读取

    Returns:
        dict: 执行结果
    """
    print("\n" + "="*60)
    print("步骤4.2：合并图片（checkShieldCalib）")
    print("="*60)

    # 确定使用的日期
    selected_date = None

    if date is not None:
        # 情况1：传递了date参数，更新进度文件并使用
        print(f"\n使用传入的日期参数: {date}")
        selected_date = date
        # 将日期写入进度文件
        config.save_step_progress('4.2', selected_date)
        print(f"✓ 已将日期 {selected_date} 写入进度文件")
    else:
        # 情况2：未传递date参数，从进度文件读取
        print("\n未传入日期参数，从进度文件读取...")
        progress = config.load_step_progress()

        if not progress or not progress.get('date'):
            return {
                'success': False,
                'message': '进度文件中没有日期信息，请指定日期参数',
                'step_name': '步骤4.2：合并图片（checkShieldCalib）'
            }

        selected_date = progress['date']
        print(f"✓ 从进度文件读取到日期: {selected_date}")

    try:
        # 进入checkShieldCalib目录，进入容器，执行图片合并命令
        print(f"\n进入目录 {config.CHECK_SHIELD_CALIB_DIR} 并执行图片合并...")

        # 在容器中执行4个convert命令
        command = f"cd {config.CHECK_SHIELD_CALIB_DIR} && /cvmfs/container.ihep.ac.cn/bin/hep_container shell SL6 << 'EOF'\nconvert *cut_detail.png cut_detail.pdf\nconvert *after_cut.png after_cut.pdf\nconvert *before_cut.png before_cut.pdf\nconvert *check.png check.pdf\nexit\nEOF"
        result = ssh.execute_command(command)

        if not result['success']:
            return {
                'success': False,
                'message': '执行merged.sh脚本失败',
                'step_name': '步骤4.2：合并图片（checkShieldCalib）',
                'date': selected_date,
                'output': result['output'],
                'error': result.get('error', '')
            }

        print(f"\n✓ merged.sh脚本执行成功")

        # 检查生成的4个PDF文件
        pdf_files = ['cut_detail.pdf', 'after_cut.pdf', 'before_cut.pdf', 'check.pdf']
        remote_pdf_paths = []
        
        for pdf_file in pdf_files:
            pdf_path = f"{config.CHECK_SHIELD_CALIB_DIR}/{pdf_file}"
            check_result = ssh.execute_command(f"ls -lh {pdf_path}")
            if check_result['success'] and check_result['output'].strip():
                print(f"{pdf_file}:\n{check_result['output']}")
                remote_pdf_paths.append(pdf_path)
            else:
                print(f"⚠ {pdf_file} 未找到（非topup模式下可能不会生成）")

        # 使用SFTP下载PDF文件到本地
        print(f"\n开始下载PDF文件到本地...")
        import os

        # 创建本地下载目录
        local_download_dir = config.get_local_download_dir()
        os.makedirs(local_download_dir, exist_ok=True)

        downloaded_files = []
        failed_files = []

        for pdf_path in remote_pdf_paths:
            pdf_file = pdf_path.split('/')[-1]
            local_pdf_path = os.path.join(local_download_dir, f"{pdf_file[:-4]}_{selected_date}.pdf")
            
            download_result = ssh.download_file(pdf_path, local_pdf_path)
            if download_result['success']:
                downloaded_files.append(local_pdf_path)
                print(f"✓ {pdf_file} 下载成功: {local_pdf_path}")
            else:
                failed_files.append(pdf_file)
                print(f"✗ {pdf_file} 下载失败")

        if not remote_pdf_paths:
            # 没有生成任何PDF文件（非topup模式）
            return {
                'success': True,
                'message': '没有生成PDF文件（非topup模式）',
                'step_name': '步骤4.2：合并图片（checkShieldCalib）',
                'date': selected_date,
                'output': result['output']
            }

        if failed_files:
            return {
                'success': True,
                'message': f'部分PDF文件下载失败。成功: {len(downloaded_files)}, 失败: {len(failed_files)}',
                'step_name': '步骤4.2：合并图片（checkShieldCalib）',
                'date': selected_date,
                'output': result['output'],
                'downloaded_files': downloaded_files,
                'failed_files': failed_files
            }

        return {
            'success': True,
            'message': '图片合并成功，所有PDF文件已下载到本地',
            'step_name': '步骤4.2：合并图片（checkShieldCalib）',
            'date': selected_date,
            'output': result['output'],
            'downloaded_files': downloaded_files
        }

    except Exception as e:
        return {
            'success': False,
            'message': f'执行图片合并异常: {str(e)}',
            'step_name': '步骤4.2：合并图片（checkShieldCalib）',
            'date': selected_date,
            'error': str(e)
        }


if __name__ == "__main__":
    # 测试步骤4.2
    with TopupSSH() as ssh:
        if ssh.connected:
            result = step4_2_merge_images(ssh, "250519")
            print("\n" + "="*60)
            print("步骤4.2执行结果:")
            print("="*60)
            print(f"成功: {result['success']}")
            print(f"消息: {result['message']}")