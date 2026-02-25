#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
步骤1.4：合并图片
进入Interval_plot目录，进入容器，执行merged.sh脚本，然后退出容器
"""

from typing import Dict, Any, Optional
from topup_ssh import TopupSSH
import config


def step1_4_merge_images(ssh: TopupSSH, date: Optional[str] = None) -> Dict[str, Any]:
    """
    进入Interval_plot目录，进入容器，执行merged.sh脚本，然后退出容器

    Args:
        ssh: SSH连接实例
        date: 日期参数（如250519），可选。如果未提供，从进度文件读取

    Returns:
        dict: 执行结果
    """
    print("\n" + "="*60)
    print("步骤1.4：合并图片")
    print("="*60)

    # 确定使用的日期
    selected_date = None
    
    if date is not None:
        # 情况1：传递了date参数，更新进度文件并使用
        print(f"\n使用传入的日期参数: {date}")
        selected_date = date
        # 将日期写入进度文件
        config.save_step_progress('1.4', selected_date)
        print(f"✓ 已将日期 {selected_date} 写入进度文件")
    else:
        # 情况2：未传递date参数，从进度文件读取
        print("\n未传入日期参数，从进度文件读取...")
        progress = config.load_step_progress()
        
        if not progress or not progress.get('date'):
            return {
                'success': False,
                'message': '进度文件中没有日期信息，请指定日期参数',
                'step_name': '步骤1.4：合并图片'
            }
        
        selected_date = progress['date']
        print(f"✓ 从进度文件读取到日期: {selected_date}")

    interval_plot_dir = f"{config.get_date_dir(config.INJ_SIG_TIME_CAL_DIR, selected_date)}/Interval_plot"

    try:
        # 进入Interval_plot目录，进入容器，执行图片合并
        print(f"\n进入目录 {config.INTERVAL_PLOT_DIR} 并执行图片合并...")
        
        # 在容器中执行convert命令合并图片
        command = f"cd {config.INTERVAL_PLOT_DIR} && /cvmfs/container.ihep.ac.cn/bin/hep_container shell SL6 << 'EOF'\nconvert *.png mergedd_IST.pdf\nexit\nEOF"
        result = ssh.execute_command(command)

        if not result['success']:
            return {
                'success': False,
                'message': '执行图片合并失败',
                'step_name': '步骤1.4：合并图片',
                'date': selected_date,
                'output': result['output'],
                'error': result.get('error', '')
            }

        print(f"\n✓ 图片合并成功")
        
        # 检查PDF文件是否生成
        pdf_path = f"{config.INTERVAL_PLOT_DIR}/mergedd_IST.pdf"
        check_result = ssh.execute_command(f"ls -lh {pdf_path}")
        if check_result['success']:
            print(f"PDF文件信息:\n{check_result['output']}")
        
        # 使用SFTP下载PDF文件到本地
        print(f"\n开始下载PDF文件到本地...")
        import os

        # 创建本地下载目录
        local_download_dir = config.get_local_download_dir()
        os.makedirs(local_download_dir, exist_ok=True)

        # 本地文件路径
        local_pdf_path = os.path.join(local_download_dir, f"mergedd_IST_{selected_date}.pdf")

        # 使用SFTP下载文件
        download_result = ssh.download_file(pdf_path, local_pdf_path)
        
        if not download_result['success']:
            return {
                'success': True,
                'message': '图片合并成功，但文件下载失败（文件已保存在服务器上）',
                'step_name': '步骤1.4：合并图片',
                'date': selected_date,
                'output': result['output'],
                'pdf_remote_path': pdf_path,
                'download_error': download_result.get('error', '')
            }

        return {
            'success': True,
            'message': '图片合并成功，文件已下载到本地',
            'step_name': '步骤1.4：合并图片',
            'date': selected_date,
            'output': result['output'],
            'pdf_remote_path': pdf_path,
            'pdf_local_path': local_pdf_path
        }

    except Exception as e:
        return {
            'success': False,
            'message': f'执行merged.sh脚本异常: {str(e)}',
            'step_name': '步骤1.4：合并图片',
            'date': selected_date,
            'error': str(e)
        }


if __name__ == "__main__":
    # 测试步骤1.4
    with TopupSSH() as ssh:
        if ssh.connected:
            result = step1_4_merge_images(ssh, "250519")
            print("\n" + "="*60)
            print("步骤1.4执行结果:")
            print("="*60)
            print(f"成功: {result['success']}")
            print(f"消息: {result['message']}")