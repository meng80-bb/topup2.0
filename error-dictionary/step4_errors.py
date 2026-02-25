#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
步骤4错误字典
"""

ERRORS_STEP4 = {
    # ===== 步骤4成功情况 (4000-4099) =====

    # 步骤4.1成功（未检查文件）
    4000: {
        'code': 4000,
        'name': 'STEP4_1_SUCCESS_NO_CHECK',
        'message': '作业提交成功（未检查文件）',
        'description': '步骤4.1：成功提交作业（check=False）。日期：{{date}}，输出：{{output}}。',
        'action': 'continue',
        'severity': 'info'
    },

    # 步骤4.1成功（检查文件）
    4001: {
        'code': 4001,
        'name': 'STEP4_1_SUCCESS_WITH_CHECK',
        'message': '作业提交成功，所有文件的文件都已生成',
        'description': '步骤4.1：成功提交作业并完成文件检查（check=True）。所有 {{total_runs}} 个run的4个文件都已成功生成。日期：{{date}}，总run数：{{total_runs}}，完成run数：{{complete_runs}}，耗时：{{elapsed_time}}秒。所有文件保存在目录：{{config.CHECK_SHIELD_CALIB_DIR}}。',
        'action': 'continue',
        'severity': 'info'
    },

    # ===== 步骤4.1错误 (4100-4199) =====
    # 步骤4.1：第四次作业提交并检查文件

    # 阶段1：删除旧文件失败
    4100: {
        'code': 4100,
        'name': 'STEP4_1_DELETE_OLD_FILES_FAILED',
        'message': '删除旧文件失败',
        'description': '步骤4.1：无法删除checkShieldCalib目录中的旧文件（PDF和run开头的文件）。尝试执行命令：cd {{config.CHECK_SHIELD_CALIB_DIR}} && rm -f *.pdf && rm -f run*。输出：{{output}}，错误：{{error}}。日期：{{date}}。可能原因：1) 权限不足；2) 文件被占用；3) 目录不存在。',
        'action': 'retry',
        'severity': 'warning'
    },

    # 阶段2：提交作业失败
    4101: {
        'code': 4101,
        'name': 'STEP4_1_GENJOB_SCRIPT_FAILED',
        'message': '执行genJob.sh脚本失败',
        'description': '步骤4.1：无法执行genJob.sh脚本。尝试执行命令：cd {{config.CHECK_SHIELD_CALIB_DIR}} && source {{config.ENV_SCRIPT}} && ./genJob.sh。输出：{{output}}，错误：{{error}}。日期：{{date}}。可能原因：1) 脚本不存在；2) 环境变量未正确设置；3) 权限不足。',
        'action': 'retry',
        'severity': 'error'
    },

    # 阶段3：获取作业文件列表失败
    4102: {
        'code': 4102,
        'name': 'STEP4_1_GET_JOB_FILES_FAILED',
        'message': '获取作业文件列表失败',
        'description': '步骤4.1：无法获取作业文件列表以确定run号。尝试执行命令：cd {{config.CHECK_SHIELD_CALIB_DIR}} && ls run_*_4.txt。输出：{{output}}，错误：{{error}}。日期：{{date}}。',
        'action': 'retry',
        'severity': 'error'
    },

    # 阶段4：未找到作业文件
    4103: {
        'code': 4103,
        'name': 'STEP4_1_NO_JOB_FILES',
        'message': '未找到作业文件',
        'description': '步骤4.1：checkShieldCalib目录中没有找到作业文件（run_{runNo}_4.txt格式）。这可能意味着作业未正确提交。日期：{{date}}。',
        'action': 'retry',
        'severity': 'error'
    },

    # 阶段5：文件检查超时
    4104: {
        'code': 4104,
        'name': 'STEP4_1_FILE_CHECK_TIMEOUT',
        'message': '文件检查超时',
        'description': '步骤4.1：在 {{max_wait_minutes}} 分钟内未完成所有文件的生成。总run数：{{total_runs}}，已完成run数：{{complete_runs}}，未完成run数：{{incomplete_runs}}。耗时：{{elapsed_time}}秒。可能原因：1) 作业执行缓慢；2) 部分作业失败；3) 计算资源不足。日期：{{date}}。',
        'action': 'retry',
        'severity': 'warning'
    },

    # 阶段6：作业提交异常
    4105: {
        'code': 4105,
        'name': 'STEP4_1_JOB_SUBMISSION_EXCEPTION',
        'message': '作业提交异常',
        'description': '步骤4.1：在提交作业时发生异常。日期：{{date}}，错误信息：{{error}}。',
        'action': 'retry',
        'severity': 'error'
    },

    # ===== 步骤4.2错误 (4200-4299) =====
    # 步骤4.2：合并checkShieldCalib图片

    # 阶段1：进度文件中没有日期信息
    4200: {
        'code': 4200,
        'name': 'STEP4_2_NO_DATE_IN_PROGRESS',
        'message': '进度文件中没有日期信息，请指定日期参数',
        'description': '步骤4.2：未传递date参数，且进度文件中没有保存的日期信息。进度文件路径：{{config.get_step_progress_file()}}。步骤4.2需要从进度文件读取之前步骤（4.1）使用的日期。',
        'action': 'manual',
        'severity': 'error'
    },

    # 阶段2：merged.sh脚本执行失败
    4201: {
        'code': 4201,
        'name': 'STEP4_2_MERGE_FAILED',
        'message': '执行merged.sh脚本失败',
        'description': '步骤4.2：无法在容器中执行图片合并命令。尝试执行命令：cd {{config.CHECK_SHIELD_CALIB_DIR}} && /cvmfs/container.ihep.ac.cn/bin/hep_container shell SL6 && convert *cut_detail.png cut_detail.pdf && convert *after_cut.png after_cut.pdf && convert *before_cut.png before_cut.pdf && convert *check.png check.pdf && exit。输出：{{output}}，错误：{{error}}。日期：{{date}}。可能原因：1) 容器不可用；2) ImageMagick未安装；3) 权限不足；4) 目录中没有png文件。（注：非topup模式下不会产生图片，此错误可忽略）',
        'action': 'continue',
        'severity': 'warning'
    },

    # 阶段3：部分PDF文件下载失败
    4202: {
        'code': 4202,
        'name': 'STEP4_2_PARTIAL_DOWNLOAD_FAILED',
        'message': '部分PDF文件下载失败',
        'description': '步骤4.2：merged.sh脚本执行成功，但部分PDF文件下载失败。成功下载：{{success_count}}，失败：{{failed_count}}。失败的文件：{{failed_files}}。日期：{{date}}。',
        'action': 'continue',
        'severity': 'warning'
    },

    # 阶段4：图片合并异常
    4203: {
        'code': 4203,
        'name': 'STEP4_2_MERGE_EXCEPTION',
        'message': '执行图片合并异常',
        'description': '步骤4.2：在执行图片合并时发生异常。日期：{{date}}，错误信息：{{error}}。（注：非topup模式下不会产生图片，此错误可忽略）',
        'action': 'continue',
        'severity': 'warning'
    },

    # ===== 步骤4.2成功情况 =====

    # 步骤4.2成功：没有生成PDF文件（非topup模式）
    4002: {
        'code': 4002,
        'name': 'STEP4_2_SUCCESS_NO_PDF',
        'message': '没有生成PDF文件（非topup模式）',
        'description': '步骤4.2：merged.sh脚本执行成功，但没有生成任何PDF文件。这是因为非topup模式下IST=15000000，不会生成检查图片。日期：{{date}}。这是正常现象，可以忽略。',
        'action': 'continue',
        'severity': 'info'
    },

    # 步骤4.2成功：所有PDF文件都下载成功
    4003: {
        'code': 4003,
        'name': 'STEP4_2_SUCCESS_ALL_DOWNLOADED',
        'message': '图片合并成功，所有PDF文件已下载到本地',
        'description': '步骤4.2：成功合并所有图片为PDF文件，并下载到本地。日期：{{date}}，下载的文件：{{downloaded_files}}。所有文件保存在目录：{{config.get_local_download_dir()}}。',
        'action': 'continue',
        'severity': 'info'
    },
}