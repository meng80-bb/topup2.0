#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
步骤1错误字典
"""

ERRORS_STEP1 = {
    # ===== 步骤1.1错误 (1100-1199) =====
    # 步骤1.1：第一次作业提交并检查结果文件（合并版）

    # 阶段1：确定日期参数失败
    1100: {
        'code': 1100,
        'name': 'STEP1_1_DATA_CONFIRMATION_EXCEPTION',
        'message': '数据确认异常',
        'description': '步骤1.1：在对比已处理和可用数据目录时发生异常。错误信息：{{error}}。',
        'action': 'manual',
        'severity': 'error'
    },
    1101: {
        'code': 1101,
        'name': 'STEP1_1_NO_AVAILABLE_DATA',
        'message': '没有找到未处理的日期',
        'description': '步骤1.1：所有可用数据目录都已被处理。已处理目录：{{config.INJ_SIG_TIME_CAL_DIR}}，可用数据目录：{{config.DATA_DIR}}。已处理日期列表：{{processed_dates}}，所有可用日期列表：{{all_dates}}。',
        'action': 'exit',
        'severity': 'info'
    },

    # 阶段2：获取目录列表失败
    1102: {
        'code': 1102,
        'name': 'STEP1_1_GET_PROCESSED_DIRS_FAILED',
        'message': '获取已处理数据目录失败',
        'description': '步骤1.1：无法获取已处理数据目录列表。尝试执行命令：ls -1 {{config.INJ_SIG_TIME_CAL_DIR}}。输出：{{output}}，错误：{{error}}。',
        'action': 'retry',
        'severity': 'error'
    },
    1103: {
        'code': 1103,
        'name': 'STEP1_1_GET_ALL_DIRS_FAILED',
        'message': '获取所有可用数据目录失败',
        'description': '步骤1.1：无法获取所有可用数据目录列表。尝试执行命令：ls -1 {{config.DATA_DIR}}。输出：{{output}}，错误：{{error}}。',
        'action': 'retry',
        'severity': 'error'
    },

    # 阶段3：提交作业失败
    1104: {
        'code': 1104,
        'name': 'STEP1_1_DELETE_DIR_FAILED',
        'message': '删除已存在的日期目录失败',
        'description': '步骤1.1：无法删除已存在的日期目录 {{date_dir}}（自动重新提交模式）。可能权限不足或目录被占用。输出：{{output}}，错误：{{error}}。',
        'action': 'retry',
        'severity': 'warning'
    },
    1105: {
        'code': 1105,
        'name': 'STEP1_1_GENJOB_SCRIPT_FAILED',
        'message': '执行genJob.sh脚本失败',
        'description': '步骤1.1：无法执行genJob.sh脚本。尝试执行命令：cd {{config.INJ_SIG_TIME_CAL_DIR}} && source {{config.ENV_SCRIPT}} && ./genJob.sh {{date}}。输出：{{output}}，错误：{{error}}。可能原因包括：1) 脚本不存在；2) 环境变量未正确设置；3) 权限不足。',
        'action': 'retry',
        'severity': 'error'
    },
    1106: {
        'code': 1106,
        'name': 'STEP1_1_DATE_DIR_NOT_CREATED',
        'message': '日期目录未创建',
        'description': '步骤1.1：genJob脚本执行后，日期目录 {{date_dir}} 未创建。这可能意味着脚本执行失败或遇到错误。尝试执行命令：ls -la {{date_dir}}。输出：{{output}}，错误：{{error}}。',
        'action': 'retry',
        'severity': 'error'
    },
    1107: {
        'code': 1107,
        'name': 'STEP1_1_JOB_SUBMISSION_EXCEPTION',
        'message': '作业提交异常',
        'description': '步骤1.1：在提交作业时发生异常。日期：{{date}}，错误信息：{{error}}。',
        'action': 'retry',
        'severity': 'error'
    },

    # 阶段4：检查结果文件失败
    1108: {
        'code': 1108,
        'name': 'STEP1_1_GET_JOB_FILES_FAILED',
        'message': '获取作业文件列表失败',
        'description': '步骤1.1：无法获取作业文件列表以确定run号。尝试执行命令：cd {{date_dir}} && ls rec*_1.txt。输出：{{output}}，错误：{{error}}。',
        'action': 'retry',
        'severity': 'error'
    },
    1109: {
        'code': 1109,
        'name': 'STEP1_1_NO_JOB_FILES',
        'message': '未找到作业文件',
        'description': '步骤1.1：日期目录 {{date_dir}} 中没有找到作业文件（rec{run}_1.txt格式）。这可能意味着作业未正确提交。日期：{{date}}。',
        'action': 'retry',
        'severity': 'error'
    },
    1110: {
        'code': 1110,
        'name': 'STEP1_1_FILE_CHECK_EXCEPTION',
        'message': '检查结果文件异常',
        'description': '步骤1.1：在检查结果文件时发生异常。日期：{{date}}，错误信息：{{error}}。',
        'action': 'retry',
        'severity': 'error'
    },
    1111: {
        'code': 1111,
        'name': 'STEP1_1_FILE_CHECK_TIMEOUT',
        'message': '文件检查超时',
        'description': '步骤1.1：在 {{max_wait_minutes}} 分钟内未完成所有文件的生成。总run数：{{total_runs}}，已完成run数：{{complete_runs}}，未完成run数：{{incomplete_runs}}。耗时：{{elapsed_time}}秒。可能原因：1) 作业执行缓慢；2) 部分作业失败；3) 计算资源不足。日期：{{date}}。',
        'action': 'retry',
        'severity': 'warning'
    },
    1112: {
        'code': 1112,
        'name': 'STEP1_1_ANOMALY_FILE_DETECTED',
        'message': '出现了Interval_run0.png的文件，该日期数据不正常',
        'description': '步骤1.1：在检查过程中发现了Interval_run0.png文件，这表示该日期的数据不正常，无法用于topup校准。需要人工干预检查数据质量。日期：{{date}}，异常文件：{{anomaly_file}}。',
        'action': 'manual',
        'severity': 'error'
    },

    # 步骤1.1成功
    1113: {
        'code': 1113,
        'name': 'STEP1_1_SUCCESS',
        'message': '成功提交作业并检查结果文件',
        'description': '步骤1.1：成功完成所有操作。1) 成功确定日期参数（通过对比逻辑或使用传入参数）；2) 成功提交作业（如果submit_job=True）；3) 所有run号的6个必需文件都已成功生成。日期：{{date}}，总run数：{{total_runs}}，完成run数：{{complete_runs}}，耗时：{{elapsed_time}}秒。所有文件保存在目录：{{date_dir}}。',
        'action': 'continue',
        'severity': 'info'
    },

    # ===== 步骤1.2错误 (1200-1299) =====
    # 步骤1.2：移动文件

    1200: {
        'code': 1200,
        'name': 'STEP1_2_MOVE_ROOT_FAILED',
        'message': '移动root文件失败',
        'description': '步骤1.2：无法将root文件从 {{date_dir}} 移动到 {{config.CALIB_CONST_DIR}}。尝试执行命令：cd {{date_dir}} && mv InjSigTime*.root {{config.CALIB_CONST_DIR}}。输出：{{output}}，错误：{{error}}。日期：{{date}}。',
        'action': 'retry',
        'severity': 'error'
    },
    1201: {
        'code': 1201,
        'name': 'STEP1_2_MOVE_PNG_FAILED',
        'message': '移动png文件失败',
        'description': '步骤1.2：无法将png文件从 {{date_dir}} 移动到 {{config.INTERVAL_PLOT_DIR}}。尝试执行命令：cd {{date_dir}} && mv Interval*.png {{config.INTERVAL_PLOT_DIR}}。输出：{{output}}，错误：{{error}}。日期：{{date}}。',
        'action': 'retry',
        'severity': 'error'
    },
    1202: {
        'code': 1202,
        'name': 'STEP1_2_MOVE_EXCEPTION',
        'message': '移动文件异常',
        'description': '步骤1.2：在移动文件时发生异常。日期：{{date}}，错误信息：{{error}}。',
        'action': 'retry',
        'severity': 'error'
    },

    # 步骤1.2成功
    1203: {
        'code': 1203,
        'name': 'STEP1_2_SUCCESS',
        'message': '文件移动成功',
        'description': '步骤1.2：成功将root文件移动到 {{config.CALIB_CONST_DIR}}，将png文件移动到 {{config.INTERVAL_PLOT_DIR}}。日期：{{date}}，剩余文件：{{remaining_files}}。',
        'action': 'continue',
        'severity': 'info'
    },

    # ===== 步骤1.3错误 (1300-1399) =====
    # 步骤1.3：IST分析

    1300: {
        'code': 1300,
        'name': 'STEP1_3_GET_INTERVAL_FILES_FAILED',
        'message': '获取Interval文件列表失败',
        'description': '步骤1.3：无法获取日期目录 {{date_dir}} 中的Interval文件列表。尝试执行命令：cd {{date_dir}} && ls Interval_run*.txt。输出：{{output}}，错误：{{error}}。日期：{{date}}。',
        'action': 'retry',
        'severity': 'error'
    },
    1301: {
        'code': 1301,
        'name': 'STEP1_3_NO_INTERVAL_FILES',
        'message': '未找到Interval文件',
        'description': '步骤1.3：日期目录 {{date_dir}} 中没有找到Interval文件（Interval_run{run}.txt格式）。无法进行IST分析。日期：{{date}}。',
        'action': 'retry',
        'severity': 'error'
    },
    1302: {
        'code': 1302,
        'name': 'STEP1_3_INVALID_IST_VALUES',
        'message': 'IST的值不全为15000000，不为非topup模式',
        'description': '步骤1.3：发现部分run号的IST值不等于15000000，不为非topup模式，需要人工干预。无效run号：{{invalid_runs}}。IST结果：{{ist_results}}。日期：{{date}}。注意：这是当前为了处理非topup数据而设置的特定检测条件，未来需要支持处理IST不等于15000000的模式。',
        'action': 'manual',
        'severity': 'warning'
    },
    1303: {
        'code': 1303,
        'name': 'STEP1_3_APPEND_FAILED',
        'message': '追加到全局interval.txt文件失败',
        'description': '步骤1.3：无法将IST分析结果追加到全局interval.txt文件。尝试执行命令：echo \'{{content}}\' >> {{config.INJ_SIG_TIME_CAL_DIR}}/interval.txt。输出：{{output}}，错误：{{error}}。日期：{{date}}，IST结果：{{ist_results}}。',
        'action': 'retry',
        'severity': 'error'
    },
    1304: {
        'code': 1304,
        'name': 'STEP1_3_ANALYSIS_EXCEPTION',
        'message': 'IST分析异常',
        'description': '步骤1.3：在执行IST分析时发生异常。日期：{{date}}，错误信息：{{error}}。',
        'action': 'retry',
        'severity': 'error'
    },

    # 步骤1.3成功
    1305: {
        'code': 1305,
        'name': 'STEP1_3_SUCCESS',
        'message': 'IST分析完成，所有run号的IST值都等于15000000',
        'description': '步骤1.3：成功完成IST分析，所有run号的IST值都等于15000000（非topup模式）。已将结果追加到全局interval.txt文件。日期：{{date}}，IST结果：{{ist_results}}，interval.txt内容：{{interval_file_content}}。',
        'action': 'continue',
        'severity': 'info'
    },

    # ===== 步骤1.4错误 (1400-1499) =====
    # 步骤1.4：合并图片

    1400: {
        'code': 1400,
        'name': 'STEP1_4_NO_DATE_IN_PROGRESS',
        'message': '进度文件中没有日期信息，请指定日期参数',
        'description': '步骤1.4：未传递date参数，且进度文件中没有保存的日期信息。进度文件路径：{{config.get_step_progress_file()}}。步骤1.4需要从进度文件读取之前步骤（1.1-1.3）使用的日期。',
        'action': 'manual',
        'severity': 'error'
    },
    1401: {
        'code': 1401,
        'name': 'STEP1_4_MERGE_FAILED',
        'message': '执行图片合并失败',
        'description': '步骤1.4：无法在容器中执行图片合并命令。尝试执行命令：cd {{config.INTERVAL_PLOT_DIR}} && /cvmfs/container.ihep.ac.cn/bin/hep_container shell SL6 && convert *.png mergedd_IST.pdf && exit。输出：{{output}}，错误：{{error}}。日期：{{date}}。可能原因：1) 容器不可用；2) ImageMagick未安装；3) 权限不足；4) 目录中没有png文件。',
        'action': 'retry',
        'severity': 'error'
    },
    1402: {
        'code': 1402,
        'name': 'STEP1_4_DOWNLOAD_FAILED',
        'message': '图片合并成功，但文件下载失败',
        'description': '步骤1.4：图片合并成功，PDF文件已保存在服务器上（{{pdf_remote_path}}），但下载到本地失败。下载错误：{{download_error}}。日期：{{date}}。输出：{{output}}。',
        'action': 'continue',
        'severity': 'warning'
    },
    1403: {
        'code': 1403,
        'name': 'STEP1_4_MERGE_EXCEPTION',
        'message': '执行图片合并异常',
        'description': '步骤1.4：在执行图片合并时发生异常。日期：{{date}}，错误信息：{{error}}。',
        'action': 'retry',
        'severity': 'error'
    },

    # 步骤1.4成功
    1404: {
        'code': 1404,
        'name': 'STEP1_4_SUCCESS',
        'message': '图片合并成功，文件已下载到本地',
        'description': '步骤1.4：成功合并Interval_plot目录中的图片为PDF文件，并下载到本地。PDF文件路径：{{pdf_local_path}}。服务器端路径：{{pdf_remote_path}}。日期：{{date}}。输出：{{output}}。',
        'action': 'continue',
        'severity': 'info'
    },
}