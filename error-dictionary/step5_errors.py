#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
步骤5错误字典
根据步骤5各子步骤的返回字典结构定义错误代码
"""

ERRORS_STEP5 = {
    # ===== 步骤5成功情况 (5000-5099) =====

    5000: {
        'code': 5000,
        'name': 'STEP5_1_SUCCESS',
        'message': '步骤5.1成功',
        'description': '步骤5.1：成功提交作业并检查cut和all文件。提交作业：{{submit_job}}，日期：{{date}}，总run数：{{total_runs}}，完成run数：{{complete_runs}}，耗时：{{elapsed_time}}秒。',
        'action': 'continue',
        'severity': 'info'
    },

    5001: {
        'code': 5001,
        'name': 'STEP5_2_SUCCESS',
        'message': '步骤5.2成功',
        'description': '步骤5.2：add_shield.sh脚本执行成功。输出：{{output}}。',
        'action': 'continue',
        'severity': 'info'
    },

    5002: {
        'code': 5002,
        'name': 'STEP5_3_SUCCESS',
        'message': '步骤5.3成功',
        'description': '步骤5.3：ets_cut.txt文件整理完成。文件内容：{{file_content}}。',
        'action': 'continue',
        'severity': 'info'
    },

    5003: {
        'code': 5003,
        'name': 'STEP5_4_SUCCESS',
        'message': '步骤5.4成功',
        'description': '步骤5.4：图片合并成功，文件已下载到本地。日期：{{date}}，远程路径：{{pdf_remote_path}}，本地路径：{{pdf_local_path}}。',
        'action': 'continue',
        'severity': 'info'
    },

    5004: {
        'code': 5004,
        'name': 'STEP5_4_MERGE_SUCCESS_DOWNLOAD_WARNING',
        'message': '图片合并成功，但文件下载失败',
        'description': '步骤5.4：图片合并成功，但文件下载失败（文件已保存在服务器上）。日期：{{date}}，远程路径：{{pdf_remote_path}}，下载错误：{{download_error}}。',
        'action': 'continue',
        'severity': 'warning'
    },

    # ===== 步骤5.1错误 (5100-5199) =====
    # 步骤5.1：第五次作业提交并检查cut和all文件（合并版）

    # 阶段1：提交作业失败（仅当submit_job=True时）
    5100: {
        'code': 5100,
        'name': 'STEP5_1_GENJOB_FAILED',
        'message': '执行genJob.sh脚本失败',
        'description': '步骤5.1：无法执行genJob.sh脚本。尝试执行命令：cd {{config.ETS_CUT_DIR}} && source {{config.ENV_SCRIPT}} && ./genJob.sh。输出：{{output}}，错误：{{error}}。可能原因包括：1) 脚本不存在；2) 环境变量未正确设置；3) 权限不足；4) 跳板机连接问题。提交作业：{{submit_job}}，日期：{{date}}。',
        'action': 'retry',
        'severity': 'error'
    },

    5101: {
        'code': 5101,
        'name': 'STEP5_1_CLEAN_FAILED',
        'message': '清理旧文件失败',
        'description': '步骤5.1：清理旧文件（删除以plot和run开头的文件）失败。执行命令：cd {{config.ETS_CUT_DIR}} && rm -f plot* run*。错误：{{error}}。这不影响后续操作，但可能导致旧文件残留。提交作业：{{submit_job}}，日期：{{date}}。',
        'action': 'continue',
        'severity': 'warning'
    },

    5102: {
        'code': 5102,
        'name': 'STEP5_1_GET_JOB_FILES_FAILED',
        'message': '获取作业文件列表失败',
        'description': '步骤5.1：无法获取作业文件列表以确定run号。尝试执行命令：cd {{config.ETS_CUT_DIR}} && ls plot_ETS_*.txt。输出：{{output}}，错误：{{error}}。提交作业：{{submit_job}}，日期：{{date}}。',
        'action': 'retry',
        'severity': 'error'
    },

    5103: {
        'code': 5103,
        'name': 'STEP5_1_NO_JOB_FILES',
        'message': '未找到作业文件',
        'description': '步骤5.1：ETS_cut目录中没有找到作业文件（plot_ETS_{run}.txt格式）。这可能意味着：1) 如果submit_job=True，作业未正确提交；2) 如果submit_job=False，之前没有提交过作业。提交作业：{{submit_job}}，日期：{{date}}。',
        'action': 'manual',
        'severity': 'error'
    },

    5104: {
        'code': 5104,
        'name': 'STEP5_1_FILE_CHECK_TIMEOUT',
        'message': 'cut和all文件检查超时',
        'description': '步骤5.1：在 {{max_wait_minutes}} 分钟内未完成所有cut和all文件的生成。总run数：{{total_runs}}，已完成run数：{{complete_runs}}，未完成run数：{{incomplete_runs}}。耗时：{{elapsed_time}}秒。可能原因：1) 作业执行缓慢；2) 部分作业失败；3) 计算资源不足；4) ETS_cut.cpp程序问题。提交作业：{{submit_job}}，日期：{{date}}。',
        'action': 'retry',
        'severity': 'warning'
    },

    5105: {
        'code': 5105,
        'name': 'STEP5_1_FILE_CHECK_EXCEPTION',
        'message': '检查cut和all文件异常',
        'description': '步骤5.1：在检查cut和all文件时发生异常。错误信息：{{error}}。提交作业：{{submit_job}}，日期：{{date}}。',
        'action': 'retry',
        'severity': 'error'
    },

    5106: {
        'code': 5106,
        'name': 'STEP5_1_EXECUTION_EXCEPTION',
        'message': '作业提交或检查异常',
        'description': '步骤5.1：在执行作业提交或cut和all文件检查时发生异常。错误信息：{{error}}。提交作业：{{submit_job}}，日期：{{date}}。',
        'action': 'retry',
        'severity': 'error'
    },

    # ===== 步骤5.2错误 (5200-5299) =====
    # 步骤5.2：运行add_shield.sh脚本

    5200: {
        'code': 5200,
        'name': 'STEP5_2_SCRIPT_FAILED',
        'message': '执行add_shield.sh脚本失败',
        'description': '步骤5.2：无法执行add_shield.sh脚本。尝试执行命令：cd {{config.ETS_CUT_DIR}} && ./add_shield.sh。输出：{{output}}，错误：{{error}}。这个错误无关紧要。',
        'action': 'continue',
        'severity': 'warning'
    },

    5201: {
        'code': 5201,
        'name': 'STEP5_2_SCRIPT_EXCEPTION',
        'message': '运行add_shield.sh脚本异常',
        'description': '步骤5.2：在运行add_shield.sh脚本时发生异常。错误信息：{{error}}。',
        'action': 'retry',
        'severity': 'error'
    },

    # ===== 步骤5.3错误 (5300-5399) =====
    # 步骤5.3：整理ets_cut.txt文件

    5300: {
        'code': 5300,
        'name': 'STEP5_3_REMOVE_SINGLE_DIGIT_FAILED',
        'message': '删除单数字行失败',
        'description': '步骤5.3：无法删除ets_cut.txt文件中只有一个数字的行。尝试执行命令：cd {{config.ETS_CUT_DIR}} && grep -vE \'^[0-9]+$\' ets_cut.txt > ets_cut_temp.txt && mv ets_cut_temp.txt ets_cut.txt。输出：{{output}}，错误：{{error}}。',
        'action': 'retry',
        'severity': 'error'
    },

    5301: {
        'code': 5301,
        'name': 'STEP5_3_SORT_FAILED',
        'message': '排序失败',
        'description': '步骤5.3：无法根据每行的第一个数字排序。尝试执行命令：cd {{config.ETS_CUT_DIR}} && sort -n -k1,1 ets_cut.txt > ets_cut_temp.txt && mv ets_cut_temp.txt ets_cut.txt。输出：{{output}}，错误：{{error}}。',
        'action': 'retry',
        'severity': 'error'
    },

    5302: {
        'code': 5302,
        'name': 'STEP5_3_REMOVE_DUPLICATE_FAILED',
        'message': '删除重复行失败',
        'description': '步骤5.3：无法删除ets_cut.txt文件中的重复行。尝试执行命令：cd {{config.ETS_CUT_DIR}} && uniq ets_cut.txt > ets_cut_temp.txt && mv ets_cut_temp.txt ets_cut.txt。输出：{{output}}，错误：{{error}}。',
        'action': 'retry',
        'severity': 'error'
    },

    5303: {
        'code': 5303,
        'name': 'STEP5_3_ORGANIZE_EXCEPTION',
        'message': '整理ets_cut.txt文件异常',
        'description': '步骤5.3：在整理ets_cut.txt文件时发生异常。错误信息：{{error}}。',
        'action': 'retry',
        'severity': 'error'
    },

    # ===== 步骤5.4错误 (5400-5499) =====
    # 步骤5.4：合并图片（ETS Cut）

    5400: {
        'code': 5400,
        'name': 'STEP5_4_NO_DATE_IN_PROGRESS',
        'message': '进度文件中没有日期信息',
        'description': '步骤5.4：进度文件中没有日期信息，请指定日期参数。',
        'action': 'manual',
        'severity': 'error'
    },

    5401: {
        'code': 5401,
        'name': 'STEP5_4_MERGE_FAILED',
        'message': '执行图片合并失败',
        'description': '步骤5.4：无法执行图片合并。尝试执行命令：cd {{config.ETS_CUT_DIR}} && /cvmfs/container.ihep.ac.cn/bin/hep_container shell SL6 << \'EOF\'\nconvert *.png mergedd_ETSCut.pdf\nexit\nEOF。输出：{{output}}，错误：{{error}}。日期：{{date}}。可能原因包括：1) 容器环境问题；2) ImageMagick未安装；3) 没有PNG文件；4) 磁盘空间不足。',
        'action': 'retry',
        'severity': 'error'
    },

    5402: {
        'code': 5402,
        'name': 'STEP5_4_MERGE_EXCEPTION',
        'message': '执行图片合并异常',
        'description': '步骤5.4：在执行图片合并时发生异常。错误信息：{{error}}。日期：{{date}}。',
        'action': 'retry',
        'severity': 'error'
    },

    5403: {
        'code': 5403,
        'name': 'STEP5_4_DOWNLOAD_FAILED',
        'message': '图片合并成功，但文件下载失败',
        'description': '步骤5.4：图片合并成功，但文件下载失败（文件已保存在服务器上）。日期：{{date}}，远程路径：{{pdf_remote_path}}，下载错误：{{download_error}}。',
        'action': 'continue',
        'severity': 'warning'
    },
}
