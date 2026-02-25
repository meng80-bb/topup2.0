#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
步骤8：提交数据库
包括InjSigInterval、InjSigTime和OfflineEvtFilter三个部分的数据库提交
"""

import config
import re
from typing import Dict, Any
from topup_ssh import TopupSSH


def step8_submit_injsiginterval_db(ssh: TopupSSH) -> Dict[str, Any]:
    """
    步骤8：提交数据库

    包含三个部分：
    1. InjSigInterval提交数据库
    2. InjSigTime提交数据库
    3. OfflineEvtFilter提交数据库

    Args:
        ssh: SSH连接实例

    Returns:
        dict: 执行结果
    """
    print("\n" + "="*60)
    print("步骤8：提交数据库")
    print("="*60)

    try:
        # 首先读取interval.txt获取run号范围
        print("\n[前置步骤] 读取interval.txt的run号范围")
        interval_file = f"{config.INJ_SIG_TIME_CAL_DIR}/interval.txt"

        result_interval = ssh.execute_command(f"cat {interval_file}")

        if not result_interval['success']:
            return {
                'success': False,
                'message': '读取interval.txt失败',
                'step_name': '步骤8：提交数据库',
                'output': result_interval['output'],
                'error': result_interval.get('error', '')
            }

        # 解析interval.txt内容
        lines = result_interval['output'].strip().split('\n')
        if not lines:
            return {
                'success': False,
                'message': 'interval.txt为空',
                'step_name': '步骤8：提交数据库'
            }

        # 获取第一行第一个数字（起始run号）
        first_line_parts = lines[0].strip().split()
        if not first_line_parts:
            return {
                'success': False,
                'message': 'interval.txt第一行格式错误',
                'step_name': '步骤8：提交数据库'
            }
        run_from = first_line_parts[0]

        # 获取最后一行第一个数字（结束run号）
        last_line_parts = lines[-1].strip().split()
        if not last_line_parts:
            return {
                'success': False,
                'message': 'interval.txt最后一行格式错误',
                'step_name': '步骤8：提交数据库'
            }
        run_to = last_line_parts[0]

        print(f"起始run号: {run_from}")
        print(f"结束run号: {run_to}")

        # 验证run号格式
        if not re.match(r'^\d{5,}$', run_from) or not re.match(r'^\d{5,}$', run_to):
            return {
                'success': False,
                'message': f'run号格式错误: run_from={run_from}, run_to={run_to}',
                'step_name': '步骤8：提交数据库'
            }

        # 执行步骤8.1：InjSigInterval提交数据库
        result_part1 = _execute_injsiginterval_db(ssh, run_from, run_to)
        if not result_part1['success']:
            return result_part1

        # 执行步骤8.2：InjSigTime提交数据库
        result_part2 = _execute_injsigtime_db(ssh, run_from, run_to)
        if not result_part2['success']:
            return result_part2

        # 执行步骤8.3：OfflineEvtFilter提交数据库
        result_part3 = _execute_offlineevtfilter_db(ssh, run_from, run_to)
        if not result_part3['success']:
            return result_part3

        return {
            'success': True,
            'message': '步骤8完成：InjSigInterval、InjSigTime、OfflineEvtFilter提交数据库',
            'step_name': '步骤8：提交数据库',
            'run_from': run_from,
            'run_to': run_to,
            'part1_result': result_part1,
            'part2_result': result_part2,
            'part3_result': result_part3
        }

    except Exception as e:
        return {
            'success': False,
            'message': f'步骤8执行异常: {str(e)}',
            'step_name': '步骤8：提交数据库',
            'error': str(e)
        }


def _execute_injsiginterval_db(ssh: TopupSSH, run_from: str, run_to: str) -> Dict[str, Any]:
    """
    步骤8.1：InjSigInterval提交数据库

    Args:
        ssh: SSH连接实例
        run_from: 起始run号
        run_to: 结束run号

    Returns:
        dict: 执行结果
    """
    print("\n" + "="*60)
    print("步骤8.1：InjSigInterval提交数据库")
    print("="*60)

    try:
        # 1. 进入InjSigTimeCal目录，运行clean_interval.sh
        print("\n[步骤8.1.1] 进入InjSigTimeCal目录，运行clean_interval.sh")
        print(f"目录: {config.INJ_SIG_TIME_CAL_DIR}")

        result_clean = ssh.execute_command(f"cd {config.INJ_SIG_TIME_CAL_DIR} && source {config.ENV_SCRIPT} && bash clean_interval.sh")

        if not result_clean['success']:
            return {
                'success': False,
                'message': 'clean_interval.sh执行失败',
                'part': '8.1',
                'output': result_clean['output'],
                'error': result_clean.get('error', '')
            }

        print(f"✓ clean_interval.sh执行成功")

        # 2. 进入genConst目录，激活环境，编译genConst.cpp并运行生成常数文件（合并原8.1.2和8.1.3）
        print("\n[步骤8.1.2] 进入genConst目录，编译genConst.cpp并运行生成常数文件")
        print(f"目录: {config.GEN_CONST_DIR}")

        # 编译genConst.cpp
        result_compile = ssh.execute_command(
            f"cd {config.GEN_CONST_DIR} && source {config.ENV_SCRIPT} && g++ -Wall genConst.cpp"
        )

        if not result_compile['success']:
            return {
                'success': False,
                'message': '编译genConst.cpp失败',
                'part': '8.1',
                'output': result_compile['output'],
                'error': result_compile.get('error', '')
            }

        print(f"✓ genConst.cpp编译成功")

        # 运行./a.out XXXXX（起始run号）
        print(f"  运行./a.out {run_from}")
        result_aout = ssh.execute_command(f"cd {config.GEN_CONST_DIR} && source {config.ENV_SCRIPT} && ./a.out {run_from}")

        if not result_aout['success']:
            return {
                'success': False,
                'message': f'./a.out {run_from}执行失败',
                'part': '8.1',
                'output': result_aout['output'],
                'error': result_aout.get('error', '')
            }

        print(f"✓ ./a.out {run_from}执行成功")

        # 3. 为copy.sh添加执行权限并执行（原8.1.4）
        print("\n[步骤8.1.3] 为copy.sh添加执行权限并执行")

        result_copy = ssh.execute_command(f"cd {config.GEN_CONST_DIR} && source {config.ENV_SCRIPT} && chmod +x copy.sh && ./copy.sh")

        if not result_copy['success']:
            return {
                'success': False,
                'message': 'copy.sh执行失败',
                'part': '8.1',
                'output': result_copy['output'],
                'error': result_copy.get('error', '')
            }

        print(f"✓ copy.sh执行成功")

        # 4. 进入const_runForm_runTo目录，运行rootmove.sh（原8.1.5）
        print("\n[步骤8.1.4] 进入const_runForm_runTo目录，运行rootmove.sh")
        print(f"目录: {config.CONST_RUN_FORM_RUN_TO_DIR}")

        result_rootmove = ssh.execute_command(
            f"cd {config.CONST_RUN_FORM_RUN_TO_DIR} && source {config.ENV_SCRIPT} && ./rootmove.sh"
        )

        if not result_rootmove['success']:
            return {
                'success': False,
                'message': 'rootmove.sh执行失败',
                'part': '8.1',
                'output': result_rootmove['output'],
                'error': result_rootmove.get('error', '')
            }

        print(f"✓ rootmove.sh执行成功")

        # 5. 进入数据库目录，验证提交命令（原8.1.6）
        print("\n[步骤8.1.5] 进入数据库目录，验证提交命令")
        print(f"目录: {config.INJ_SIG_INTERVAL_DB_DIR}")
        print(f"命令: genInsertCmd.sh -runfrom {run_from} -runto {run_to} -sub_switch 0")

        result_verify = ssh.execute_command(
            f"cd {config.INJ_SIG_INTERVAL_DB_DIR} && source {config.ENV_SCRIPT} && bash genInsertCmd.sh -runfrom {run_from} -runto {run_to} -sub_switch 0"
        )

        if not result_verify['success']:
            return {
                'success': False,
                'message': '验证提交命令失败',
                'part': '8.1',
                'output': result_verify['output'],
                'error': result_verify.get('error', '')
            }

        print(f"✓ 验证提交命令成功")

        # 6. 提交到数据库（原8.1.7）
        print("\n[步骤8.1.6] 提交到数据库")
        print(f"命令: genInsertCmd.sh -runfrom {run_from} -runto {run_to} -sub_switch 1")

        result_db = ssh.execute_command(
            f"cd {config.INJ_SIG_INTERVAL_DB_DIR} && source {config.ENV_SCRIPT} && bash genInsertCmd.sh -runfrom {run_from} -runto {run_to} -sub_switch 1"
        )

        if not result_db['success']:
            return {
                'success': False,
                'message': '提交数据库失败',
                'part': '8.1',
                'output': result_db['output'],
                'error': result_db.get('error', '')
            }

        print(f"✓ InjSigInterval提交数据库成功")

        return {
            'success': True,
            'message': 'InjSigInterval提交数据库完成',
            'part': '8.1',
            'output': result_db.get('output', '')
        }

    except Exception as e:
        return {
            'success': False,
            'message': f'步骤8.1执行异常: {str(e)}',
            'part': '8.1',
            'error': str(e)
        }


def _execute_injsigtime_db(ssh: TopupSSH, run_from: str, run_to: str) -> Dict[str, Any]:
    """
    步骤8.2：InjSigTime提交数据库

    Args:
        ssh: SSH连接实例
        run_from: 起始run号
        run_to: 结束run号

    Returns:
        dict: 执行结果
    """
    print("\n" + "="*60)
    print("步骤8.2：InjSigTime提交数据库")
    print("="*60)

    try:
        # 1. 进入calibConst目录，执行rootmove.sh
        print("\n[步骤8.2.1] 进入calibConst目录，执行rootmove.sh")
        print(f"目录: {config.CALIB_CONST_DIR}")

        result_rootmove = ssh.execute_command(
            f"cd {config.CALIB_CONST_DIR} && source {config.ENV_SCRIPT} && ./rootmove.sh"
        )

        if not result_rootmove['success']:
            return {
                'success': False,
                'message': 'rootmove.sh执行失败',
                'part': '8.2',
                'output': result_rootmove['output'],
                'error': result_rootmove.get('error', '')
            }

        print(f"✓ rootmove.sh执行成功")

        # 2. 进入InjSigTime数据库目录，验证提交命令（sub_switch=0）
        print("\n[步骤8.2.2] 进入InjSigTime数据库目录，验证提交命令")
        print(f"目录: {config.INJ_SIG_TIME_DB_DIR}")
        print(f"命令: genInsertCmd.sh -runfrom {run_from} -runto {run_to} -sub_switch 0")

        result_generate = ssh.execute_command(
            f"cd {config.INJ_SIG_TIME_DB_DIR} && source {config.ENV_SCRIPT} && bash genInsertCmd.sh -runfrom {run_from} -runto {run_to} -sub_switch 0"
        )

        if not result_generate['success']:
            return {
                'success': False,
                'message': '验证提交命令失败',
                'part': '8.2',
                'output': result_generate['output'],
                'error': result_generate.get('error', '')
            }

        print(f"✓ 验证提交命令成功")

        # 3. 提交到数据库（sub_switch=1）
        print("\n[步骤8.2.3] 提交到数据库")
        print(f"命令: genInsertCmd.sh -runfrom {run_from} -runto {run_to} -sub_switch 1")

        result_submit = ssh.execute_command(
            f"cd {config.INJ_SIG_TIME_DB_DIR} && source {config.ENV_SCRIPT} && bash genInsertCmd.sh -runfrom {run_from} -runto {run_to} -sub_switch 1"
        )

        if not result_submit['success']:
            return {
                'success': False,
                'message': '提交数据库失败',
                'part': '8.2',
                'output': result_submit['output'],
                'error': result_submit.get('error', '')
            }

        print(f"✓ InjSigTime提交数据库成功")

        return {
            'success': True,
            'message': 'InjSigTime提交数据库完成',
            'part': '8.2',
            'output': result_submit.get('output', '')
        }

    except Exception as e:
        return {
            'success': False,
            'message': f'步骤8.2执行异常: {str(e)}',
            'part': '8.2',
            'error': str(e)
        }


def _execute_offlineevtfilter_db(ssh: TopupSSH, run_from: str, run_to: str) -> Dict[str, Any]:
    """
    步骤8.3：OfflineEvtFilter提交数据库

    Args:
        ssh: SSH连接实例
        run_from: 起始run号
        run_to: 结束run号

    Returns:
        dict: 执行结果
    """
    print("\n" + "="*60)
    print("步骤8.3：OfflineEvtFilter提交数据库")
    print("="*60)

    try:
        # 1. 进入OfflineEvtFilter目录，运行cp_3files.sh
        print("\n[步骤8.3.1] 进入OfflineEvtFilter目录，运行cp_3files.sh")
        print(f"目录: {config.OFFLINE_EVT_DIR}")

        result_cp3files = ssh.execute_command(
            f"cd {config.OFFLINE_EVT_DIR} && source {config.ENV_SCRIPT} && ./cp_3files.sh"
        )

        if not result_cp3files['success']:
            return {
                'success': False,
                'message': 'cp_3files.sh执行失败',
                'part': '8.3',
                'output': result_cp3files['output'],
                'error': result_cp3files.get('error', '')
            }

        print(f"✓ cp_3files.sh执行成功")

        # 2. 进入duration_caculate目录，执行a.out
        print("\n[步骤8.3.2] 进入duration_caculate目录，执行a.out")
        duration_dir = f"{config.OFFLINE_EVT_DIR}/duration_caculate"
        print(f"目录: {duration_dir}")

        result_duration = ssh.execute_command(
            f"cd {duration_dir} && source {config.ENV_SCRIPT} && ./a.out"
        )

        if not result_duration['success']:
            return {
                'success': False,
                'message': 'duration_caculate/a.out执行失败',
                'part': '8.3',
                'output': result_duration['output'],
                'error': result_duration.get('error', '')
            }

        print(f"✓ duration_caculate/a.out执行成功")

        # 3. 进入ccompare目录，执行a.out并检查错误
        print("\n[步骤8.3.3] 进入ccompare目录，执行a.out并检查错误")
        ccompare_dir = f"{config.OFFLINE_EVT_DIR}/ccompare"
        print(f"目录: {ccompare_dir}")

        result_ccompare = ssh.execute_command(
            f"cd {ccompare_dir} && source {config.ENV_SCRIPT} && ./a.out 2>&1"
        )

        if not result_ccompare['success']:
            return {
                'success': False,
                'message': 'ccompare/a.out执行失败',
                'part': '8.3',
                'output': result_ccompare['output'],
                'error': result_ccompare.get('error', '')
            }

        # 检查是否包含特定错误关键词
        output = result_ccompare.get('output', '')
        if re.search(r'error:\s+(repeat|order|miss)', output, re.IGNORECASE):
            error_match = re.search(r'error:\s+(repeat|order|miss)', output, re.IGNORECASE)
            return {
                'success': False,
                'message': f'ccompare/a.out执行出错，包含关键词: {error_match.group(0)}',
                'part': '8.3',
                'output': output
            }

        print(f"✓ ccompare/a.out执行成功")

        # 4. 返回OfflineEvtFilter目录，执行a.out BOSSE run_from run_to
        print(f"\n[步骤8.3.4] 执行a.out {config.BOSSE} {run_from} {run_to}")
        print(f"目录: {config.OFFLINE_EVT_DIR}")

        result_aout_params = ssh.execute_command(
            f"cd {config.OFFLINE_EVT_DIR} && source {config.ENV_SCRIPT} && ./a.out {config.BOSSE} {run_from} {run_to}"
        )

        if not result_aout_params['success']:
            return {
                'success': False,
                'message': f'a.out 720 {run_from} {run_to}执行失败',
                'part': '8.3',
                'output': result_aout_params['output'],
                'error': result_aout_params.get('error', '')
            }

        print(f"✓ a.out 720 {run_from} {run_to}执行成功")

        # 5. 进入check目录，生成file.txt
        print("\n[步骤8.3.5] 进入check目录，生成file.txt")
        check_dir = f"{config.OFFLINE_EVT_DIR}/check"
        print(f"目录: {check_dir}")

        result_file_txt = ssh.execute_command(
            f"cd {check_dir} && source {config.ENV_SCRIPT} && ls ../OfflineEvtFilter_00*.root > file.txt 2>/dev/null"
        )

        if not result_file_txt['success']:
            return {
                'success': False,
                'message': '生成file.txt失败',
                'part': '8.3',
                'output': result_file_txt['output'],
                'error': result_file_txt.get('error', '')
            }

        print(f"✓ file.txt生成成功")

        # 6. 执行check目录下的a.out BOSSE run_from run_to
        print(f"\n[步骤8.3.6] 执行check/a.out {config.BOSSE} {run_from} {run_to}")

        result_check_aout = ssh.execute_command(
            f"cd {check_dir} && source {config.ENV_SCRIPT} && ./a.out {config.BOSSE} {run_from} {run_to} 2>&1"
        )

        if not result_check_aout['success']:
            return {
                'success': False,
                'message': f'check/a.out 720 {run_from} {run_to}执行失败',
                'part': '8.3',
                'output': result_check_aout['output'],
                'error': result_check_aout.get('error', '')
            }

        # 检查是否有错误输出
        check_output = result_check_aout.get('output', '')
        if check_output.strip():
            return {
                'success': False,
                'message': f'check/a.out执行后出现非预期输出',
                'part': '8.3',
                'output': check_output
            }

        print(f"✓ check/a.out 720 {run_from} {run_to}执行成功")

        # 7. 返回OfflineEvtFilter目录，运行rootmove.sh
        print("\n[步骤8.3.7] 返回OfflineEvtFilter目录，运行rootmove.sh")

        result_rootmove2 = ssh.execute_command(
            f"cd {config.OFFLINE_EVT_DIR} && source {config.ENV_SCRIPT} && ./rootmove.sh"
        )

        if not result_rootmove2['success']:
            return {
                'success': False,
                'message': 'rootmove.sh执行失败',
                'part': '8.3',
                'output': result_rootmove2['output'],
                'error': result_rootmove2.get('error', '')
            }

        print(f"✓ rootmove.sh执行成功")

        # 8. 进入OfflineEvtFilter数据库目录，验证提交命令
        print("\n[步骤8.3.8] 进入OfflineEvtFilter数据库目录，验证提交命令")
        print(f"目录: {config.OFFLINE_EVT_DB_DIR}")
        print(f"命令: genInsertCmd.sh -runfrom {run_from} -runto {run_to} -sub_switch 0")

        result_verify = ssh.execute_command(
            f"cd {config.OFFLINE_EVT_DB_DIR} && source {config.ENV_SCRIPT} && bash genInsertCmd.sh -runfrom {run_from} -runto {run_to} -sub_switch 0"
        )

        if not result_verify['success']:
            return {
                'success': False,
                'message': '验证提交命令失败',
                'part': '8.3',
                'output': result_verify['output'],
                'error': result_verify.get('error', '')
            }

        print(f"✓ 验证提交命令成功")

        # 9. 提交到数据库
        print("\n[步骤8.3.9] 提交到数据库")
        print(f"命令: genInsertCmd.sh -runfrom {run_from} -runto {run_to} -sub_switch 1")

        result_db_submit = ssh.execute_command(
            f"cd {config.OFFLINE_EVT_DB_DIR} && source {config.ENV_SCRIPT} && bash genInsertCmd.sh -runfrom {run_from} -runto {run_to} -sub_switch 1"
        )

        if not result_db_submit['success']:
            return {
                'success': False,
                'message': '提交数据库失败',
                'part': '8.3',
                'output': result_db_submit['output'],
                'error': result_db_submit.get('error', '')
            }

        print(f"✓ OfflineEvtFilter提交数据库成功")

        # 10. 进入checkDBAlg的share目录，运行reset_root.sh
        print("\n[步骤8.3.10] 进入checkDBAlg的share目录，运行reset_root.sh")
        print(f"目录: {config.CHECK_DB_ALG_DIR}")

        result_reset_root = ssh.execute_command(
            f"cd {config.CHECK_DB_ALG_DIR} && source {config.ENV_SCRIPT} && bash reset_root.sh"
        )

        if not result_reset_root['success']:
            return {
                'success': False,
                'message': 'reset_root.sh执行失败',
                'part': '8.3',
                'output': result_reset_root['output'],
                'error': result_reset_root.get('error', '')
            }

        print(f"✓ reset_root.sh执行成功")

        return {
            'success': True,
            'message': 'OfflineEvtFilter提交数据库完成',
            'part': '8.3',
            'output': result_db_submit.get('output', '')
        }

    except Exception as e:
        return {
            'success': False,
            'message': f'步骤8.3执行异常: {str(e)}',
            'part': '8.3',
            'error': str(e)
        }


if __name__ == "__main__":
    # 测试步骤8
    with TopupSSH() as ssh:
        if ssh.connected:
            result = step8_submit_injsiginterval_db(ssh)
            print("\n" + "="*60)
            print("步骤8执行结果:")
            print("="*60)
            print(f"成功: {result['success']}")
            print(f"消息: {result['message']}")
            if 'run_from' in result:
                print(f"run号范围: {result['run_from']} ~ {result['run_to']}")
            if 'part1_result' in result:
                print(f"\n步骤8.1: {'成功' if result['part1_result']['success'] else '失败'}")
            if 'part2_result' in result:
                print(f"步骤8.2: {'成功' if result['part2_result']['success'] else '失败'}")
            if 'part3_result' in result:
                print(f"步骤8.3: {'成功' if result['part3_result']['success'] else '失败'}")