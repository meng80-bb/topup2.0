#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
步骤2错误字典
根据步骤2各子步骤的返回字典结构定义错误代码
"""

ERRORS_STEP2 = {
    # ===== 步骤2成功情况 (2000-2099) =====

    2000: {
        'code': 2000,
        'name': 'STEP2_1_SUCCESS',
        'message': '步骤2.1成功',
        'description': '步骤2.1：成功提交作业并检查hist文件。日期：{{date}}，总run数：{{total_runs}}，完成run数：{{complete_runs}}。',
        'action': 'continue',
        'severity': 'info'
    },

    2001: {
        'code': 2001,
        'name': 'STEP2_2_SUCCESS',
        'message': '步骤2.2成功',
        'description': '步骤2.2：hist文件合并成功。日期：{{date}}。',
        'action': 'continue',
        'severity': 'info'
    },

    2002: {
        'code': 2002,
        'name': 'STEP2_3_SUCCESS',
        'message': '步骤2.3成功',
        'description': '步骤2.3：png文件生成成功。',
        'action': 'continue',
        'severity': 'info'
    },

    2003: {
        'code': 2003,
        'name': 'STEP2_4_SUCCESS',
        'message': '步骤2.4成功',
        'description': '步骤2.4：所有png文件都已生成。总hist文件数：{{total_hist_files}}，总png文件数：{{total_png_files}}。',
        'action': 'continue',
        'severity': 'info'
    },

    2004: {
        'code': 2004,
        'name': 'STEP2_5_SUCCESS',
        'message': '步骤2.5成功',
        'description': '步骤2.5：图片合并成功，文件已下载到本地。日期：{{date}}，本地路径：{{pdf_local_path}}。',
        'action': 'continue',
        'severity': 'info'
    },

    # ===== 步骤2.1错误 (2100-2199) =====
    # 步骤2.1：第二次作业提交并检查hist文件（合并版）

    2100: {
        'code': 2100,
        'name': 'STEP2_1_EXECUTION_FAILED',
        'message': '第二次作业提交或检查失败',
        'description': '步骤2.1：执行失败。原因：{{message}}。日期：{{date}}。',
        'action': 'retry',
        'severity': 'error'
    },

    2101: {
        'code': 2101,
        'name': 'STEP2_1_DATE_NOT_FOUND',
        'message': '进度文件中没有日期信息',
        'description': '步骤2.1：进度文件中没有日期信息，请指定日期参数。',
        'action': 'manual',
        'severity': 'error'
    },

    2102: {
        'code': 2102,
        'name': 'STEP2_1_GENJOB_FAILED',
        'message': '执行genJob脚本失败',
        'description': '步骤2.1：执行genJob脚本失败。日期：{{date}}。错误：{{error}}。',
        'action': 'retry',
        'severity': 'error'
    },

    2103: {
        'code': 2103,
        'name': 'STEP2_1_DATE_DIR_NOT_CREATED',
        'message': '日期目录未创建',
        'description': '步骤2.1：日期目录 {{date}} 未创建。',
        'action': 'retry',
        'severity': 'error'
    },

    2104: {
        'code': 2104,
        'name': 'STEP2_1_GET_RUNS_FAILED',
        'message': '获取run号子目录列表失败',
        'description': '步骤2.1：获取run号子目录列表失败。日期：{{date}}。',
        'action': 'retry',
        'severity': 'error'
    },

    2105: {
        'code': 2105,
        'name': 'STEP2_1_NO_RUNS_FOUND',
        'message': '未找到run号子目录',
        'description': '步骤2.1：未找到run号子目录。日期：{{date}}。',
        'action': 'manual',
        'severity': 'error'
    },

    2106: {
        'code': 2106,
        'name': 'STEP2_1_HIST_TIMEOUT',
        'message': 'hist文件生成超时',
        'description': '步骤2.1：在 {{elapsed_time}} 秒内未完成所有hist文件的生成。总run数：{{total_runs}}，完成run数：{{complete_runs}}，未完成run数：{{incomplete_runs}}。',
        'action': 'retry',
        'severity': 'warning'
    },

    2107: {
        'code': 2107,
        'name': 'STEP2_1_SUBMIT_JOB_EXCEPTION',
        'message': '作业提交异常',
        'description': '步骤2.1：作业提交异常。日期：{{date}}。错误：{{error}}。',
        'action': 'retry',
        'severity': 'error'
    },

    # ===== 步骤2.2错误 (2200-2299) =====
    # 步骤2.2：合并hist文件

    2200: {
        'code': 2200,
        'name': 'STEP2_2_MERGE_FAILED',
        'message': '合并hist文件失败',
        'description': '步骤2.2：执行mergeHist.sh脚本失败。日期：{{date}}。',
        'action': 'retry',
        'severity': 'error'
    },

    2201: {
        'code': 2201,
        'name': 'STEP2_2_MERGE_EXCEPTION',
        'message': '合并hist文件异常',
        'description': '步骤2.2：合并hist文件异常。日期：{{date}}。错误：{{error}}。',
        'action': 'retry',
        'severity': 'error'
    },

    # ===== 步骤2.3错误 (2300-2399) =====
    # 步骤2.3：生成png文件

    2300: {
        'code': 2300,
        'name': 'STEP2_3_GENERATE_FAILED',
        'message': '生成png文件失败',
        'description': '步骤2.3：执行01go.sh脚本失败。',
        'action': 'retry',
        'severity': 'error'
    },

    2301: {
        'code': 2301,
        'name': 'STEP2_3_GENERATE_EXCEPTION',
        'message': '生成png文件异常',
        'description': '步骤2.3：生成png文件异常。错误：{{error}}。',
        'action': 'retry',
        'severity': 'error'
    },

    # ===== 步骤2.4错误 (2400-2499) =====
    # 步骤2.4：检查png文件

    2400: {
        'code': 2400,
        'name': 'STEP2_4_GET_HIST_FAILED',
        'message': '获取hist文件列表失败',
        'description': '步骤2.4：获取hist文件列表失败。',
        'action': 'retry',
        'severity': 'error'
    },

    2401: {
        'code': 2401,
        'name': 'STEP2_4_NO_HIST_FILES',
        'message': '未找到hist文件',
        'description': '步骤2.4：未找到hist文件，无法检查png文件。',
        'action': 'manual',
        'severity': 'error'
    },

    2402: {
        'code': 2402,
        'name': 'STEP2_4_PNG_TIMEOUT',
        'message': 'png文件生成超时',
        'description': '步骤2.4：在 {{elapsed_time}} 秒内未完成所有png文件的生成。总hist文件数：{{total_hist_files}}，总png文件数：{{total_png_files}}。',
        'action': 'retry',
        'severity': 'warning'
    },

    2403: {
        'code': 2403,
        'name': 'STEP2_4_CHECK_EXCEPTION',
        'message': '检查png文件异常',
        'description': '步骤2.4：检查png文件异常。错误：{{error}}。',
        'action': 'retry',
        'severity': 'error'
    },

    # ===== 步骤2.5错误 (2500-2599) =====
    # 步骤2.5：合并hist图片

    2500: {
        'code': 2500,
        'name': 'STEP2_5_NO_DATE_IN_PROGRESS',
        'message': '进度文件中没有日期信息',
        'description': '步骤2.5：进度文件中没有日期信息，请指定日期参数。',
        'action': 'manual',
        'severity': 'error'
    },

    2501: {
        'code': 2501,
        'name': 'STEP2_5_MERGE_FAILED',
        'message': '执行图片合并失败',
        'description': '步骤2.5：执行图片合并失败。日期：{{date}}。',
        'action': 'retry',
        'severity': 'error'
    },

    2502: {
        'code': 2502,
        'name': 'STEP2_5_MERGE_EXCEPTION',
        'message': '执行图片合并异常',
        'description': '步骤2.5：执行图片合并异常。日期：{{date}}。错误：{{error}}。',
        'action': 'retry',
        'severity': 'error'
    },

    2503: {
        'code': 2503,
        'name': 'STEP2_5_DOWNLOAD_FAILED',
        'message': '图片合并成功，但文件下载失败',
        'description': '步骤2.5：图片合并成功，但文件下载失败（文件已保存在服务器上）。日期：{{date}}。远程路径：{{pdf_remote_path}}。',
        'action': 'continue',
        'severity': 'warning'
    },
}