#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
步骤6错误字典
步骤6包含两个子步骤：
- 6.1：第六次作业提交与文件检查
- 6.2：合并图片（Check ETScut CalibConst）
"""

ERRORS_STEP6 = {
    # ===== 步骤6成功错误码 (6000-6099) =====

    6000: {
        'code': 6000,
        'name': 'STEP6_1_SUCCESS',
        'message': '步骤6.1执行成功',
        'description': '步骤6.1：第六次作业提交与文件检查成功。总共 {{total_runs}} 个run，已完成 {{complete_runs}} 个，耗时 {{elapsed_time}} 秒。submit_job={{submit_job}}。',
        'action': 'continue',
        'severity': 'info'
    },

    6001: {
        'code': 6001,
        'name': 'STEP6_2_SUCCESS',
        'message': '步骤6.2执行成功',
        'description': '步骤6.2：合并图片成功，文件已下载到本地。PDF远程路径：{{pdf_remote_path}}，本地路径：{{pdf_local_path}}。',
        'action': 'continue',
        'severity': 'info'
    },

    # ===== 步骤6.1错误 (6100-6199) =====
    # 步骤6.1：第六次作业提交与文件检查（合并版）

    6100: {
        'code': 6100,
        'name': 'STEP6_1_JOB_SUBMISSION_FAILED',
        'message': '第六次作业提交失败',
        'description': '步骤6.1：无法提交第六次作业。尝试执行命令：cd {{config.CHECK_ETSCUT_CALIBCONST_DIR}} && source {{config.ENV_SCRIPT}} && ./genJob.sh。输出：{{output}}，错误：{{error}}。可能原因包括：1) genJob.sh脚本不存在；2) 环境变量未正确加载；3) 目录权限不足。',
        'action': 'retry',
        'severity': 'error'
    },

    6101: {
        'code': 6101,
        'name': 'STEP6_1_NO_JOB_FILES',
        'message': '未找到作业文件',
        'description': '步骤6.1：执行genJob.sh脚本后，未找到生成的作业文件（ETScut_check_*.txt）。run_numbers={{run_numbers}}。可能原因包括：1) 脚本执行失败；2) 作业文件生成在错误的目录；3) 文件命名规则已更改。',
        'action': 'retry',
        'severity': 'error'
    },

    6102: {
        'code': 6102,
        'name': 'STEP6_1_NO_JOB_FILES_WHEN_SKIP',
        'message': '跳过作业提交但未找到作业文件',
        'description': '步骤6.1：submit_job=False，但未找到已有的作业文件（ETScut_check_*.txt）。错误：{{error}}。请先提交作业或检查作业文件是否存在于正确目录。',
        'action': 'manual',
        'severity': 'error'
    },

    6103: {
        'code': 6103,
        'name': 'STEP6_1_FILE_CHECK_TIMEOUT',
        'message': '文件检查超时',
        'description': '步骤6.1：在 {{max_wait_minutes}} 分钟内未完成所有png和root文件的生成。总共 {{total_runs}} 个run，已完成 {{complete_runs}} 个，未完成 {{incomplete_runs}} 个，耗时 {{elapsed_time}} 秒。可能原因包括：1) 作业卡在队列中；2) 作业执行失败；3) 磁盘空间不足。',
        'action': 'retry',
        'severity': 'warning'
    },

    6104: {
        'code': 6104,
        'name': 'STEP6_1_FILE_CHECK_EXCEPTION',
        'message': '文件检查异常',
        'description': '步骤6.1：检查png和root文件时发生异常。错误：{{error}}。submit_job={{submit_job}}。可能原因包括：1) SSH连接中断；2) 文件系统错误；3) 代码逻辑错误。',
        'action': 'retry',
        'severity': 'error'
    },

    # ===== 步骤6.2错误 (6200-6299) =====
    # 步骤6.2：合并图片（Check ETScut CalibConst）

    6200: {
        'code': 6200,
        'name': 'STEP6_2_MERGE_FAILED',
        'message': '执行图片合并失败',
        'description': '步骤6.2：无法在容器中执行图片合并命令。尝试执行命令：cd {{config.CHECK_ETSCUT_CALIBCONST_DIR}} && /cvmfs/container.ihep.ac.cn/bin/hep_container shell SL6 convert ./run*.png mergedd_ETS_checkall.pdf。输出：{{output}}，错误：{{error}}。可能原因包括：1) 容器启动失败；2) ImageMagick未安装；3) 没有可用的png文件。',
        'action': 'retry',
        'severity': 'error'
    },

    6201: {
        'code': 6201,
        'name': 'STEP6_2_NO_DATE_IN_PROGRESS',
        'message': '进度文件中没有日期信息',
        'description': '步骤6.2：未传递date参数，且进度文件中也没有日期信息。请指定date参数或确保之前的步骤已正确执行并保存了进度。',
        'action': 'manual',
        'severity': 'error'
    },

    6202: {
        'code': 6202,
        'name': 'STEP6_2_MERGE_EXCEPTION',
        'message': '执行图片合并异常',
        'description': '步骤6.2：执行图片合并时发生异常。错误：{{error}}。date={{date}}。可能原因包括：1) SSH连接中断；2) 容器执行错误；3) 文件系统错误。',
        'action': 'retry',
        'severity': 'error'
    },

    6203: {
        'code': 6203,
        'name': 'STEP6_2_DOWNLOAD_FAILED',
        'message': '图片合并成功但文件下载失败',
        'description': '步骤6.2：图片合并成功，但文件下载失败。PDF远程路径：{{pdf_remote_path}}，错误：{{download_error}}。可能原因包括：1) SFTP连接问题；2) 本地目录权限不足；3) 磁盘空间不足。文件已保存在服务器上。',
        'action': 'continue',
        'severity': 'warning'
    },
}