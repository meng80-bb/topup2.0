#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
步骤7错误字典（占位符）
"""

ERRORS_STEP7 = {
    # ===== 步骤7成功错误码 (7000-7099) =====

    7000: {
        'code': 7000,
        'name': 'STEP7_SUCCESS',
        'message': '步骤7执行成功',
        'description': '步骤7：reset.sh脚本执行成功，系统状态已重置。所有临时文件已移动到tmp目录，重要数据已备份到对应日期目录。',
        'action': 'continue',
        'severity': 'info'
    },

    # ===== 步骤7错误 (7100-7199) =====
    # 步骤7：运行reset.sh脚本

    7100: {
        'code': 7100,
        'name': 'STEP7_SCRIPT_FAILED',
        'message': '执行reset.sh脚本失败',
        'description': '步骤7：无法执行reset.sh脚本。尝试执行命令：cd {{config.INJ_SIG_TIME_CAL_DIR}} && ./reset.sh。输出：{{output}}，错误：{{error}}。可能原因包括：1) reset.sh脚本不存在；2) 脚本权限不足；3) 脚本执行错误。',
        'action': 'retry',
        'severity': 'error'
    },

    7101: {
        'code': 7101,
        'name': 'STEP7_SCRIPT_NOT_FOUND',
        'message': 'reset.sh脚本未找到',
        'description': '步骤7：在目录 {{config.INJ_SIG_TIME_CAL_DIR}} 中未找到reset.sh脚本。请确认脚本路径是否正确。',
        'action': 'manual',
        'severity': 'error'
    },

    7102: {
        'code': 7102,
        'name': 'STEP7_SCRIPT_PERMISSION_DENIED',
        'message': 'reset.sh脚本权限不足',
        'description': '步骤7：reset.sh脚本没有执行权限。请运行 chmod +x reset.sh 添加执行权限。',
        'action': 'manual',
        'severity': 'error'
    },

    7103: {
        'code': 7103,
        'name': 'STEP7_SCRIPT_EXCEPTION',
        'message': '执行reset.sh脚本异常',
        'description': '步骤7：执行reset.sh脚本时发生异常。错误：{{error}}。可能原因包括：1) SSH连接中断；2) 脚本执行错误；3) 文件系统错误。',
        'action': 'retry',
        'severity': 'error'
    },

    7104: {
        'code': 7104,
        'name': 'STEP7_BACKUP_FAILED',
        'message': '备份文件失败',
        'description': '步骤7：reset.sh脚本执行时，备份文件失败。输出：{{output}}。可能原因包括：1) 目标目录不存在；2) 磁盘空间不足；3) 文件权限问题。',
        'action': 'retry',
        'severity': 'warning'
    },
}