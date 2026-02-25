#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
步骤3错误字典
根据步骤3各子步骤的返回字典结构定义错误代码
"""

ERRORS_STEP3 = {
    # ===== 步骤3成功情况 (3000-3099) =====

    3000: {
        'code': 3000,
        'name': 'STEP3_1_SUCCESS',
        'message': '步骤3.1成功',
        'description': '步骤3.1：成功提交作业并检查shield文件。提交作业：{{submit_job}}，总run数：{{total_runs}}，完成run数：{{complete_runs}}，耗时：{{elapsed_time}}秒。',
        'action': 'continue',
        'severity': 'info'
    },

    3001: {
        'code': 3001,
        'name': 'STEP3_2_SUCCESS',
        'message': '步骤3.2成功',
        'description': '步骤3.2：add.sh脚本执行成功，window.dat文件已清理（删除只有run号的行）。',
        'action': 'continue',
        'severity': 'info'
    },

    # ===== 步骤3.1错误 (3100-3199) =====
    # 步骤3.1：第三次作业提交并检查shield文件（合并版）

    # 阶段1：提交作业失败（仅当submit_job=True时）
    3100: {
        'code': 3100,
        'name': 'STEP3_1_GENJOB_FAILED',
        'message': '执行genJob.sh脚本失败',
        'description': '步骤3.1：无法执行genJob.sh脚本。尝试执行命令：cd {{config.SEARCH_PEAK_DIR}} && source {{config.ENV_SCRIPT}} && ./genJob.sh。输出：{{output}}，错误：{{error}}。可能原因包括：1) 脚本不存在；2) 环境变量未正确设置；3) 权限不足；4) 跳板机连接问题。',
        'action': 'retry',
        'severity': 'error'
    },

    3101: {
        'code': 3101,
        'name': 'STEP3_1_SUBMIT_JOB_EXCEPTION',
        'message': '作业提交异常',
        'description': '步骤3.1：在提交作业时发生异常。错误信息：{{error}}。提交作业：{{submit_job}}。',
        'action': 'retry',
        'severity': 'error'
    },

    # 阶段2：检查shield文件失败
    3102: {
        'code': 3102,
        'name': 'STEP3_1_GET_JOB_FILES_FAILED',
        'message': '获取作业文件列表失败',
        'description': '步骤3.1：无法获取作业文件列表以确定run号。尝试执行命令：cd {{config.SEARCH_PEAK_DIR}} && ls run_*_3.txt。输出：{{output}}，错误：{{error}}。提交作业：{{submit_job}}。',
        'action': 'retry',
        'severity': 'error'
    },

    3103: {
        'code': 3103,
        'name': 'STEP3_1_NO_JOB_FILES',
        'message': '未找到作业文件',
        'description': '步骤3.1：search_peak目录中没有找到作业文件（run_{run}_3.txt格式）。这可能意味着：1) 如果submit_job=True，作业未正确提交；2) 如果submit_job=False，之前没有提交过作业。提交作业：{{submit_job}}。',
        'action': 'manual',
        'severity': 'error'
    },

    3104: {
        'code': 3104,
        'name': 'STEP3_1_FILE_CHECK_EXCEPTION',
        'message': '检查shield文件异常',
        'description': '步骤3.1：在检查shield文件时发生异常。错误信息：{{error}}。提交作业：{{submit_job}}。',
        'action': 'retry',
        'severity': 'error'
    },

    3105: {
        'code': 3105,
        'name': 'STEP3_1_FILE_CHECK_TIMEOUT',
        'message': 'shield文件检查超时',
        'description': '步骤3.1：在 {{max_wait_minutes}} 分钟内未完成所有shield文件的生成。总run数：{{total_runs}}，已完成run数：{{complete_runs}}，未完成run数：{{incomplete_runs}}。耗时：{{elapsed_time}}秒。可能原因：1) 作业执行缓慢；2) 部分作业失败；3) 计算资源不足；4) shield文件生成脚本问题。提交作业：{{submit_job}}。',
        'action': 'retry',
        'severity': 'warning'
    },

    3106: {
        'code': 3106,
        'name': 'STEP3_1_EXECUTION_EXCEPTION',
        'message': '作业提交或检查异常',
        'description': '步骤3.1：在执行作业提交或shield文件检查时发生异常。错误信息：{{error}}。提交作业：{{submit_job}}。',
        'action': 'retry',
        'severity': 'error'
    },

    # ===== 步骤3.2错误 (3200-3299) =====
    # 步骤3.2：运行add.sh脚本（原步骤3.3）

    3200: {
        'code': 3200,
        'name': 'STEP3_2_SCRIPT_FAILED',
        'message': '执行add.sh脚本失败',
        'description': '步骤3.2：无法执行add.sh脚本。尝试执行命令：cd {{config.SEARCH_PEAK_DIR}} && ./add.sh。输出：{{output}}，错误：{{error}}。可能原因包括：1) 脚本不存在；2) 权限不足；3) 脚本依赖的文件不存在。',
        'action': 'continue',
        'severity': 'warning'
    },

    3201: {
        'code': 3201,
        'name': 'STEP3_2_SCRIPT_EXCEPTION',
        'message': '运行add.sh脚本异常',
        'description': '步骤3.2：在运行add.sh脚本时发生异常。错误信息：{{error}}。',
        'action': 'continue',
        'severity': 'warning'
    },

    3202: {
        'code': 3202,
        'name': 'STEP3_2_CLEAN_WINDOW_FAILED',
        'message': '清理window.dat文件失败',
        'description': '步骤3.2：add.sh脚本执行成功，但清理window.dat文件失败。尝试执行命令：cd {{config.SEARCH_PEAK_DIR}} && sed \'/^[0-9]\\+$/d\' window.dat > window.dat.tmp && mv window.dat.tmp window.dat。输出：{{output}}，错误：{{error}}。可能原因包括：1) window.dat文件不存在；2) 文件权限不足；3) 磁盘空间不足。',
        'action': 'continue',
        'severity': 'warning'
    },
}