#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
步骤3.2：运行add.sh脚本
运行search_peak目录下的add.sh脚本
"""

from typing import Dict, Any
from topup_ssh import TopupSSH
import config


def step3_2_run_add_script(ssh: TopupSSH) -> Dict[str, Any]:
    """
    运行add.sh脚本
    
    运行search_peak目录下的add.sh脚本
    
    Args:
        ssh: SSH连接实例
        
    Returns:
        dict: 执行结果
    """
    print("\n" + "="*60)
    print("步骤3.2：运行add.sh脚本")
    print("="*60)
    
    try:
        # 进入search_peak目录
        search_peak_dir = config.SEARCH_PEAK_DIR
        print(f"\n进入search_peak目录: {search_peak_dir}")

        # 执行add.sh脚本
        print(f"\n执行add.sh脚本...")
        result = ssh.execute_command(f"cd {search_peak_dir} && ./add.sh")

        if not result['success']:
            return {
                'success': False,
                'message': '执行add.sh脚本失败',
                'step_name': '步骤3.2：运行add.sh脚本',
                'output': result['output'],
                'error': result.get('error', '')
            }

        print(f"\n✓ add.sh脚本执行成功")
        print(f"输出:\n{result['output']}")
        
        # 删除window.dat文件中只有run号的行（只有一个数字的行）
        print(f"\n清理window.dat文件，删除只有run号的行...")
        window_file = f"{search_peak_dir}/window.dat"
        result_clean = ssh.execute_command(
            f"cd {search_peak_dir} && sed '/^[0-9]\\+$/d' window.dat > window.dat.tmp && mv window.dat.tmp window.dat"
        )
        
        if not result_clean['success']:
            return {
                'success': False,
                'message': '清理window.dat文件失败',
                'step_name': '步骤3.2：运行add.sh脚本',
                'output': result_clean['output'],
                'error': result_clean.get('error', '')
            }
        
        print(f"✓ window.dat文件清理完成")
        
        return {
            'success': True,
            'message': 'add.sh脚本执行成功，window.dat文件已清理',
            'step_name': '步骤3.2：运行add.sh脚本',
            'output': result['output']
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'运行add.sh脚本异常: {str(e)}',
            'step_name': '步骤3.2：运行add.sh脚本',
            'error': str(e)
        }


if __name__ == "__main__":
    # 测试步骤3.2
    with TopupSSH() as ssh:
        if ssh.connected:
            result = step3_2_run_add_script(ssh)
            print("\n" + "="*60)
            print("步骤3.2执行结果:")
            print("="*60)
            print(f"成功: {result['success']}")
            print(f"消息: {result['message']}")