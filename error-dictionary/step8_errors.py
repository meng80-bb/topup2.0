#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
步骤8错误字典（占位符）
"""

ERRORS_STEP8 = {
    # ===== 步骤8错误 (8100-8199) =====
    # 步骤8：提交InjSigInterval数据库

    8100: {
        'code': 8100,
        'name': 'STEP8_DB_SUBMISSION_FAILED',
        'message': '提交InjSigInterval数据库失败',
        'description': '步骤8：无法将InjSigInterval数据提交到数据库。',
        'action': 'retry',
        'severity': 'error'
    },
}