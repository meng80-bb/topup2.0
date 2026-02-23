#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
错误代码定义
用于BESIII Topup数据验证自动化系统的错误处理
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional

# 添加error-dictionary目录到Python路径
ERROR_DICT_DIR = Path(__file__).parent / "error-dictionary"
sys.path.insert(0, str(ERROR_DICT_DIR))

# 导入各步骤的错误字典
try:
    from step1_errors import ERRORS_STEP1
except ImportError:
    ERRORS_STEP1 = {}

try:
    from step2_errors import ERRORS_STEP2
except ImportError:
    ERRORS_STEP2 = {}

try:
    from step3_errors import ERRORS_STEP3
except ImportError:
    ERRORS_STEP3 = {}

try:
    from step4_errors import ERRORS_STEP4
except ImportError:
    ERRORS_STEP4 = {}

try:
    from step5_errors import ERRORS_STEP5
except ImportError:
    ERRORS_STEP5 = {}

try:
    from step6_errors import ERRORS_STEP6
except ImportError:
    ERRORS_STEP6 = {}

try:
    from step7_errors import ERRORS_STEP7
except ImportError:
    ERRORS_STEP7 = {}

try:
    from step8_errors import ERRORS_STEP8
except ImportError:
    ERRORS_STEP8 = {}


# ===== 通用错误字典 (0-999) =====

ERRORS_GENERAL = {
    # 成功
    0: {
        'code': 0,
        'name': 'SUCCESS',
        'message': '操作成功',
        'description': '操作成功完成。',
        'action': 'continue',
        'severity': 'info'
    },

    # SSH连接错误
    1: {
        'code': 1,
        'name': 'SSH_CONNECTION_FAILED',
        'message': 'SSH连接失败',
        'description': '无法连接到SSH服务器。请检查：1) 网络连接；2) 服务器地址和端口；3) 用户名和密码；4) 跳板机和目标服务器是否可达。',
        'action': 'retry',
        'severity': 'error'
    },
    2: {
        'code': 2,
        'name': 'SSH_COMMAND_FAILED',
        'message': 'SSH命令执行失败',
        'description': 'SSH命令执行失败。命令：{{command}}，退出码：{{exit_code}}，错误：{{error}}。',
        'action': 'retry',
        'severity': 'error'
    },
    3: {
        'code': 3,
        'name': 'SSH_TIMEOUT',
        'message': 'SSH命令执行超时',
        'description': 'SSH命令执行超时。命令：{{command}}，超时时间：{{timeout}}秒。',
        'action': 'retry',
        'severity': 'error'
    },
    4: {
        'code': 4,
        'name': 'SSH_AUTHENTICATION_FAILED',
        'message': 'SSH认证失败',
        'description': 'SSH认证失败。请检查用户名和密码是否正确。',
        'action': 'manual',
        'severity': 'error'
    },

    # 文件操作错误
    10: {
        'code': 10,
        'name': 'FILE_NOT_FOUND',
        'message': '文件未找到',
        'description': '未找到文件：{{file_path}}。请检查文件路径是否正确。',
        'action': 'retry',
        'severity': 'error'
    },
    11: {
        'code': 11,
        'name': 'FILE_READ_FAILED',
        'message': '读取文件失败',
        'description': '无法读取文件：{{file_path}}。请检查文件权限和文件完整性。',
        'action': 'retry',
        'severity': 'error'
    },
    12: {
        'code': 12,
        'name': 'FILE_WRITE_FAILED',
        'message': '写入文件失败',
        'description': '无法写入文件：{{file_path}}。请检查文件权限和磁盘空间。',
        'action': 'retry',
        'severity': 'error'
    },
    13: {
        'code': 13,
        'name': 'DIRECTORY_NOT_FOUND',
        'message': '目录未找到',
        'description': '未找到目录：{{dir_path}}。请检查目录路径是否正确。',
        'action': 'retry',
        'severity': 'error'
    },
    14: {
        'code': 14,
        'name': 'DIRECTORY_CREATE_FAILED',
        'message': '创建目录失败',
        'description': '无法创建目录：{{dir_path}}。请检查父目录权限和磁盘空间。',
        'action': 'retry',
        'severity': 'error'
    },

    # 参数错误
    20: {
        'code': 20,
        'name': 'INVALID_PARAMETER',
        'message': '无效的参数',
        'description': '参数 {{param_name}} 的值无效：{{param_value}}。请检查参数值是否正确。',
        'action': 'manual',
        'severity': 'error'
    },
    21: {
        'code': 21,
        'name': 'MISSING_PARAMETER',
        'message': '缺少必需参数',
        'description': '缺少必需参数：{{param_name}}。请提供该参数。',
        'action': 'manual',
        'severity': 'error'
    },
    22: {
        'code': 22,
        'name': 'INVALID_DATE_FORMAT',
        'message': '无效的日期格式',
        'description': '日期格式无效：{{date}}。日期必须是6位数字（如250519）。',
        'action': 'manual',
        'severity': 'error'
    },

    # 系统错误
    30: {
        'code': 30,
        'name': 'SYSTEM_ERROR',
        'message': '系统错误',
        'description': '系统错误：{{error}}。',
        'action': 'retry',
        'severity': 'error'
    },
    31: {
        'code': 31,
        'name': 'UNKNOWN_ERROR',
        'message': '未知错误',
        'description': '发生未知错误。错误信息：{{error}}。',
        'action': 'retry',
        'severity': 'error'
    },
    32: {
        'code': 32,
        'name': 'TIMEOUT_ERROR',
        'message': '操作超时',
        'description': '操作超时。操作：{{operation}}，超时时间：{{timeout}}秒。',
        'action': 'retry',
        'severity': 'error'
    },

    # iFlow CLI错误
    40: {
        'code': 40,
        'name': 'IFLOW_CLI_NOT_CONNECTED',
        'message': 'iFlow CLI未连接',
        'description': 'iFlow CLI未连接。请确保iFlow CLI正在运行。',
        'action': 'manual',
        'severity': 'error'
    },
    41: {
        'code': 41,
        'name': 'IFLOW_CLI_COMMUNICATION_FAILED',
        'message': 'iFlow CLI通信失败',
        'description': '无法与iFlow CLI通信。请检查iFlow CLI是否正在运行。',
        'action': 'retry',
        'severity': 'error'
    },

    # 步骤执行错误
    50: {
        'code': 50,
        'name': 'STEP_NOT_FOUND',
        'message': '步骤未找到',
        'description': '未找到步骤：{{step_key}}。请检查步骤编号是否正确。',
        'action': 'manual',
        'severity': 'error'
    },
    51: {
        'code': 51,
        'name': 'STEP_EXECUTION_FAILED',
        'message': '步骤执行失败',
        'description': '步骤执行失败。步骤：{{step_key}}，错误：{{error}}。',
        'action': 'retry',
        'severity': 'error'
    },
    52: {
        'code': 52,
        'name': 'MAX_RETRIES_EXCEEDED',
        'message': '超过最大重试次数',
        'description': '超过最大重试次数。步骤：{{step_key}}，最大重试次数：{{max_retries}}。',
        'action': 'manual',
        'severity': 'error'
    },

    # 进度文件错误
    60: {
        'code': 60,
        'name': 'PROGRESS_FILE_NOT_FOUND',
        'message': '进度文件未找到',
        'description': '进度文件未找到：{{progress_file}}。请检查文件路径是否正确。',
        'action': 'manual',
        'severity': 'error'
    },
    61: {
        'code': 61,
        'name': 'PROGRESS_FILE_READ_FAILED',
        'message': '读取进度文件失败',
        'description': '无法读取进度文件：{{progress_file}}。请检查文件权限和文件完整性。',
        'action': 'retry',
        'severity': 'error'
    },
    62: {
        'code': 62,
        'name': 'PROGRESS_FILE_WRITE_FAILED',
        'message': '写入进度文件失败',
        'description': '无法写入进度文件：{{progress_file}}。请检查文件权限和磁盘空间。',
        'action': 'retry',
        'severity': 'error'
    },
    63: {
        'code': 63,
        'name': 'PROGRESS_FILE_CORRUPTED',
        'message': '进度文件损坏',
        'description': '进度文件损坏：{{progress_file}}。请删除文件并重新开始。',
        'action': 'manual',
        'severity': 'error'
    },

    # 数据验证错误
    70: {
        'code': 70,
        'name': 'DATA_VALIDATION_FAILED',
        'message': '数据验证失败',
        'description': '数据验证失败。验证规则：{{rule}}，验证值：{{value}}。',
        'action': 'manual',
        'severity': 'error'
    },
    71: {
        'code': 71,
        'name': 'DATA_INCOMPLETE',
        'message': '数据不完整',
        'description': '数据不完整。缺少：{{missing_data}}。',
        'action': 'retry',
        'severity': 'error'
    },
    72: {
        'code': 72,
        'name': 'DATA_INCONSISTENT',
        'message': '数据不一致',
        'description': '数据不一致。不一致项：{{inconsistent_items}}。',
        'action': 'manual',
        'severity': 'error'
    },

    # 容器错误
    80: {
        'code': 80,
        'name': 'CONTAINER_NOT_AVAILABLE',
        'message': '容器不可用',
        'description': '容器不可用。容器：{{container}}。',
        'action': 'retry',
        'severity': 'error'
    },
    81: {
        'code': 81,
        'name': 'CONTAINER_COMMAND_FAILED',
        'message': '容器命令执行失败',
        'description': '容器命令执行失败。容器：{{container}}，命令：{{command}}，错误：{{error}}。',
        'action': 'retry',
        'severity': 'error'
    },

    # 环境错误
    90: {
        'code': 90,
        'name': 'ENVIRONMENT_NOT_SET',
        'message': '环境未设置',
        'description': '环境未设置。环境变量：{{env_var}}。',
        'action': 'manual',
        'severity': 'error'
    },
    91: {
        'code': 91,
        'name': 'ENVIRONMENT_SCRIPT_FAILED',
        'message': '环境脚本加载失败',
        'description': '环境脚本加载失败。脚本：{{script}}。',
        'action': 'retry',
        'severity': 'error'
    },

    # 配置错误
    100: {
        'code': 100,
        'name': 'CONFIG_FILE_NOT_FOUND',
        'message': '配置文件未找到',
        'description': '配置文件未找到：{{config_file}}。请检查文件路径是否正确。',
        'action': 'manual',
        'severity': 'error'
    },
    101: {
        'code': 101,
        'name': 'CONFIG_FILE_READ_FAILED',
        'message': '读取配置文件失败',
        'description': '无法读取配置文件：{{config_file}}。请检查文件权限和文件完整性。',
        'action': 'retry',
        'severity': 'error'
    },
    102: {
        'code': 102,
        'name': 'CONFIG_FILE_INVALID',
        'message': '配置文件无效',
        'description': '配置文件无效：{{config_file}}。请检查配置文件格式。',
        'action': 'manual',
        'severity': 'error'
    },
    103: {
        'code': 103,
        'name': 'UNKNOWN_ERROR',
        'message': '出现了未知的错误',
        'description': '出现了未知的错误',
        'action': 'ai',
        'severity': 'error',
        'prompt': '出现了未知的错误，请处理。可以阅读相关提交作业的md文档，也可以使用remote_command.py工具来帮助你判断。'
    },
}


# ===== 所有错误字典的集合 =====

ALL_ERROR_DICTS = {
    'general': ERRORS_GENERAL,
    'step1': ERRORS_STEP1,
    'step2': ERRORS_STEP2,
    'step3': ERRORS_STEP3,
    'step4': ERRORS_STEP4,
    'step5': ERRORS_STEP5,
    'step6': ERRORS_STEP6,
    'step7': ERRORS_STEP7,
    'step8': ERRORS_STEP8,
}


# ===== 错误信息获取函数 =====

def get_error_info(error_code: int, **kwargs) -> Optional[Dict[str, Any]]:
    """
    根据错误代码获取错误信息

    Args:
        error_code: 错误代码
        **kwargs: 用于替换错误描述中的占位符

    Returns:
        错误信息字典，如果未找到则返回未知错误信息
    """
    # 在所有错误字典中查找错误代码
    for error_dict in ALL_ERROR_DICTS.values():
        if error_code in error_dict:
            error_info = error_dict[error_code].copy()

            # 替换描述中的占位符
            if 'description' in error_info and kwargs:
                description = error_info['description']
                for key, value in kwargs.items():
                    placeholder = f'{{{{{key}}}}}'
                    if placeholder in description:
                        description = description.replace(placeholder, str(value))
                error_info['description'] = description

            return error_info

    # 如果未找到错误码，返回未知错误信息
    return {
        'code': 103,
        'name': 'UNKNOWN_ERROR',
        'message': '未知错误',
        'description': f'出现了未知的错误。错误码：{error_code}。',
        'action': 'ai',
        'prompt': '出现了新的错误，请根据日志文件和第n次提交作业的综合说明文档.md来分析，可以使用remote_command.py文件来获取远程服务器的文件内容。',
        'severity': 'error'
    }


def match_error_code(step_name: str, result: Dict[str, Any]) -> Optional[int]:
    """
    根据步骤名称和执行结果智能匹配错误代码

    Args:
        step_name: 步骤名称（如'步骤2.1：第二次作业提交并检查hist文件'）
        result: 步骤执行结果字典

    Returns:
        错误代码，如果匹配成功；如果成功返回对应成功码；如果无法匹配返回None
    """
    # 提取步骤的key（如'2.1'）
    import re
    step_match = re.match(r'步骤(\d+\.?\d*)', step_name)
    if not step_match:
        return None

    step_key = step_match.group(1)

    # 首先检查是否成功，如果成功返回对应成功码
    if result.get('success'):
        # 根据步骤key返回对应成功码
        success_codes = {
            '1': 1000,  # 步骤1成功（所有子步骤）
            '1.1': 1001,
            '1.2': 1002,
            '1.3': 1003,
            '1.4': 1004,
            '1.5': 1005,
            '2.1': 2000,
            '2.2': 2001,
            '2.3': 2002,
            '2.4': 2003,
            '2.5': 2004,
            '3.1': 3000,
            '3.2': 3001,
            '4.1': 4000,  # 步骤4.1成功
            '4.2': 4003,  # 步骤4.2成功
            '5.1': 5000,
            '5.2': 5001,
            '5.3': 5002,
            '5.4': 5003,
            '6.1': 6000,  # 步骤6.1成功
            '6.2': 6001,  # 步骤6.2成功
            '7': 7000    # 步骤7成功
        }
        return success_codes.get(step_key, 0)

    # 获取错误消息
    message = result.get('message', '')
    error = result.get('error', '')

    # 根据步骤名称和消息内容匹配错误码
    if step_key.startswith('1.'):
        # 步骤1的错误匹配
        if step_key == '1.1':
            # 步骤1.1：第一次作业提交并检查结果文件
            if '没有找到未处理的日期' in message:
                return 1101
            elif '获取目录列表失败' in message:
                return 1102
            elif '日期目录不存在' in message:
                return 1103
            elif '未找到数据文件' in message:
                return 1104
            elif '未找到作业文件' in message:
                return 1105
            elif '未完成所有文件的生成' in message:
                return 1106
            elif '数据确认异常' in message:
                return 1100
            elif '作业提交异常' in message:
                return 1107
            else:
                return 1100  # 通用执行失败
        elif step_key == '1.2':
            # 步骤1.2：移动文件
            if '移动文件失败' in message:
                return 1200
            elif '移动文件异常' in message:
                return 1201
            else:
                return 1200
        elif step_key == '1.3':
            # 步骤1.3：IST分析
            if 'IST值不等于预期' in message:
                return 1300
            elif '读取Interval文件失败' in message:
                return 1301
            elif 'IST分析异常' in message:
                return 1302
            else:
                return 1300
        elif step_key == '1.4':
            # 步骤1.4：合并图片
            if '执行图片合并失败' in message:
                return 1400
            elif '执行图片合并异常' in message:
                return 1401
            elif '文件下载失败' in message:
                return 1402
            else:
                return 1400
        elif step_key == '1.5':
            # 步骤1.5：保存进度
            if '保存进度失败' in message:
                return 1500
            else:
                return 1500

    elif step_key.startswith('3.'):
        # 步骤3的错误匹配
        if step_key == '3.1':
            # 步骤3.1：第三次作业提交并检查shield文件
            if '执行genJob.sh脚本失败' in message:
                return 3100
            elif '作业提交异常' in message:
                return 3101
            elif '获取作业文件列表失败' in message:
                return 3102
            elif '未找到作业文件' in message:
                return 3103
            elif '检查shield文件异常' in message:
                return 3104
            elif 'shield文件检查超时' in message:
                return 3105
            elif '作业提交或检查异常' in message:
                return 3106
            else:
                return 3100  # 通用执行失败
        elif step_key == '3.2':
            # 步骤3.2：运行add.sh脚本
            if '执行add.sh脚本失败' in message:
                return 3200
            elif '运行add.sh脚本异常' in message:
                return 3201
            elif '清理window.dat文件失败' in message:
                return 3202
            else:
                return 3200

    elif step_key == '2.1':
        # 步骤2.1的错误匹配
        if '没有日期信息' in message:
            return 2101
        elif '执行genJob脚本失败' in message:
            return 2102
        elif '日期目录' in message and '未创建' in message:
            return 2103
        elif '获取run号子目录列表失败' in message:
            return 2104
        elif '未找到run号子目录' in message:
            return 2105
        elif '未完成所有hist文件的生成' in message:
            return 2106
        elif '作业提交异常' in message:
            return 2107
        else:
            return 2100  # 通用执行失败

    elif step_key == '2.2':
        # 步骤2.2的错误匹配
        if '合并hist文件异常' in message:
            return 2201
        else:
            return 2200

    elif step_key == '2.3':
        # 步骤2.3的错误匹配
        if '生成png文件异常' in message:
            return 2301
        else:
            return 2300

    elif step_key == '2.4':
        # 步骤2.4的错误匹配
        if '获取hist文件列表失败' in message:
            return 2400
        elif '未找到hist文件' in message:
            return 2401
        elif '未完成所有png文件的生成' in message:
            return 2402
        elif '检查png文件异常' in message:
            return 2403
        else:
            return None

    elif step_key == '2.5':
        # 步骤2.5的错误匹配
        if '没有日期信息' in message:
            return 2500
        elif '执行图片合并异常' in message:
            return 2502
        elif '文件下载失败' in message:
            return 2503
        else:
            return 2501

    elif step_key == '4.1':
        # 步骤4.1的错误匹配
        # 首先检查是否成功
        if result.get('success'):
            # 根据消息内容判断是否检查了文件
            if '未检查文件' in message:
                return 4000  # 步骤4.1成功（未检查文件）
            elif '所有' in message and '都已生成' in message:
                return 4001  # 步骤4.1成功（检查文件）
            else:
                return 4000  # 默认为未检查文件
        else:
            # 失败情况
            if '删除旧文件失败' in message:
                return 4100
            elif '执行genJob.sh脚本失败' in message:
                return 4101
            elif '获取作业文件列表失败' in message:
                return 4102
            elif '未找到作业文件' in message:
                return 4103
            elif '文件检查超时' in message:
                return 4104
            elif '作业提交异常' in message:
                return 4105
            else:
                return 4100  # 通用执行失败

    elif step_key == '4.2':
        # 步骤4.2的错误匹配
        if result.get('success'):
            if '没有生成PDF文件' in message:
                return 4002  # 步骤4.2成功（非topup模式，无PDF）
            elif '所有PDF文件' in message and '已下载到本地' in message:
                return 4003  # 步骤4.2成功（所有文件下载成功）
            elif '部分PDF文件下载失败' in message:
                return 4202  # 部分PDF文件下载失败
            else:
                return 4002  # 默认为无PDF（非topup模式）
        else:
            if '没有日期信息' in message:
                return 4200
            elif '执行merged.sh脚本失败' in message:
                return 4201
            elif '执行图片合并失败' in message:
                return 4201
            elif '执行图片合并异常' in message:
                return 4203
            else:
                return 4201  # 通用执行失败

    elif step_key == '5.1':
        # 步骤5.1：第五次作业提交并检查cut和all文件（合并版）
        if result.get('success'):
            # 成功情况：检查submit_job参数
            submit_job = result.get('submit_job', True)
            if submit_job:
                return 5000  # 提交作业并检查文件成功
            else:
                return 5000  # 只检查文件成功
        else:
            # 失败情况
            if '执行genJob.sh脚本失败' in message:
                return 5100
            elif '清理旧文件失败' in message:
                return 5101
            elif '获取作业文件列表失败' in message:
                return 5102
            elif '未找到作业文件' in message:
                return 5103
            elif '未完成所有cut和all文件的生成' in message:
                return 5104
            elif '检查cut和all文件异常' in message:
                return 5105
            elif '作业提交或检查异常' in message:
                return 5106
            else:
                return 5100  # 通用执行失败

    elif step_key == '5.2':
        # 步骤5.2：运行add_shield.sh脚本
        if result.get('success'):
            return 5001
        else:
            if '执行add_shield.sh脚本失败' in message:
                return 5200
            elif '运行add_shield.sh脚本异常' in message:
                return 5201
            else:
                return 5200  # 通用执行失败

    elif step_key == '5.3':
        # 步骤5.3：整理ets_cut.txt文件
        if result.get('success'):
            return 5002
        else:
            if '删除单数字行失败' in message:
                return 5300
            elif '排序失败' in message:
                return 5301
            elif '删除重复行失败' in message:
                return 5302
            elif '整理ets_cut.txt文件异常' in message:
                return 5303
            else:
                return 5300  # 通用执行失败

    elif step_key == '5.4':
        # 步骤5.4：合并图片（ETS Cut）
        if result.get('success'):
            if '文件下载失败' in message:
                return 5004  # 合并成功但下载失败
            else:
                return 5003  # 完全成功
        else:
            if '进度文件中没有日期信息' in message:
                return 5400
            elif '执行图片合并失败' in message:
                return 5401
            elif '执行图片合并异常' in message:
                return 5402
            elif '图片合并成功，但文件下载失败' in message:
                return 5403
            else:
                return 5401  # 通用执行失败

    elif step_key == '6.1':
        # 步骤6.1：第六次作业提交与文件检查（合并版）
        if result.get('success'):
            return 6000  # 步骤6.1成功
        else:
            # 失败情况
            if '执行genJob.sh脚本失败' in message:
                return 6100
            elif '未找到作业文件' in message:
                return 6101
            elif '跳过作业提交但未找到作业文件' in message:
                return 6102
            elif '未完成所有png和root文件的生成' in message:
                return 6103
            elif '文件检查异常' in message:
                return 6104
            else:
                return 6100  # 通用执行失败

    elif step_key == '6.2':
        # 步骤6.2：合并图片（Check ETScut CalibConst）
        if result.get('success'):
            if '图片合并成功，但文件下载失败' in message:
                return 6203  # 合并成功但下载失败
            else:
                return 6001  # 完全成功
        else:
            if '进度文件中没有日期信息' in message:
                return 6201
            elif '执行图片合并失败' in message:
                return 6200
            elif '执行图片合并异常' in message:
                return 6202
            else:
                return 6200  # 通用执行失败

    elif step_key == '7':
        # 步骤7：运行reset.sh脚本
        if result.get('success'):
            return 7000  # 步骤7成功
        else:
            if '执行reset.sh脚本失败' in message:
                return 7100
            elif '执行reset.sh脚本异常' in message:
                return 7103
            else:
                return 7100  # 通用执行失败

    # 其他步骤暂不处理，返回未知错误码
    return 103


def format_error_message(error_code: int, **kwargs) -> str:
    """
    格式化错误消息

    Args:
        error_code: 错误代码
        **kwargs: 用于替换错误描述中的占位符

    Returns:
        格式化后的错误消息
    """
    error_info = get_error_info(error_code, **kwargs)

    if error_info:
        return f"[错误 {error_info['code']}] {error_info['name']}: {error_info['message']}"
    else:
        return f"[错误 {error_code}] 未知错误"


def get_all_errors() -> Dict[str, Dict[int, Dict[str, Any]]]:
    """
    获取所有错误字典

    Returns:
        包含所有错误字典的字典
    """
    return ALL_ERROR_DICTS


def get_errors_by_step(step_name: str) -> Optional[Dict[int, Dict[str, Any]]]:
    """
    根据步骤名称获取错误字典

    Args:
        step_name: 步骤名称（如'step1', 'step2'等）

    Returns:
        错误字典，如果未找到则返回None
    """
    return ALL_ERROR_DICTS.get(step_name)


# ===== 便捷函数 =====

def success() -> Dict[str, Any]:
    """返回成功错误信息"""
    return get_error_info(0)


def ssh_connection_failed(**kwargs) -> Dict[str, Any]:
    """返回SSH连接失败错误信息"""
    return get_error_info(1, **kwargs)


def file_not_found(file_path: str) -> Dict[str, Any]:
    """返回文件未找到错误信息"""
    return get_error_info(10, file_path=file_path)


def invalid_parameter(param_name: str, param_value: Any) -> Dict[str, Any]:
    """返回无效参数错误信息"""
    return get_error_info(20, param_name=param_name, param_value=param_value)


def step_not_found(step_key: str) -> Dict[str, Any]:
    """返回步骤未找到错误信息"""
    return get_error_info(50, step_key=step_key)


def max_retries_exceeded(step_key: str, max_retries: int) -> Dict[str, Any]:
    """返回超过最大重试次数错误信息"""
    return get_error_info(52, step_key=step_key, max_retries=max_retries)


if __name__ == '__main__':
    # 测试代码
    print("测试error_codes模块")

    # 测试获取错误信息
    error_info = get_error_info(1, command='ls -l', exit_code=1, error='Permission denied')
    print(f"错误代码1的信息：{error_info}")

    # 测试格式化错误消息
    error_msg = format_error_message(10, file_path='/tmp/test.txt')
    print(f"格式化错误消息：{error_msg}")

    # 测试获取所有错误字典
    all_errors = get_all_errors()
    print(f"所有错误字典：{list(all_errors.keys())}")

    # 测试获取步骤1的错误字典
    step1_errors = get_errors_by_step('step1')
    if step1_errors:
        print(f"步骤1的错误代码数量：{len(step1_errors)}")