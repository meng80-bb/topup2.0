#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Topup HTTP API 配置文件
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 项目根目录
BASE_DIR = Path(__file__).parent

# 数据库配置
DATABASE_URL = os.getenv('DATABASE_URL', f'sqlite:///{BASE_DIR}/topup_api.db')

# Flask配置
FLASK_CONFIG = {
    'SECRET_KEY': os.getenv('SECRET_KEY', 'topup-api-secret-key-2025'),
    'DEBUG': os.getenv('DEBUG', 'False').lower() == 'true',
    'JSON_AS_ASCII': False,
    'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # 16MB
}

# 日志配置
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'color': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        }
    },
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': f'{BASE_DIR}/logs/topup_api.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'standard',
            'encoding': 'utf8'
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'color'
        }
    },
    'loggers': {
        '': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False
        },
        'werkzeug': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False
        }
    }
}

# 任务执行配置
TASK_CONFIG = {
    'max_parallel_tasks': int(os.getenv('MAX_PARALLEL_TASKS', '3')),
    'default_timeout_minutes': int(os.getenv('DEFAULT_TIMEOUT_MINUTES', '30')),
    'max_retry_attempts': int(os.getenv('MAX_RETRY_ATTEMPTS', '3')),
    'retry_delay_seconds': int(os.getenv('RETRY_DELAY_SECONDS', '60')),
    'step_check_interval': int(os.getenv('STEP_CHECK_INTERVAL', '5')),
}

# 工作流配置路径
WORKFLOW_CONFIG_DIR = BASE_DIR / 'workflows'

# SSH配置
SSH_CONFIG = {
    "servers": {
        "server1": {
            "name": "lxlogin",
            "host": "lxlogin.ihep.ac.cn",
            "port": 22,
            "username": "topup",
            "env_password": "SSH_PASS_LXLOGIN"
        },
        "server2": {
            "name": "beslogin",
            "host": "beslogin",
            "port": 22,
            "username": "topup",
            "env_password": "SSH_PASS_BESLOGIN"
        }
    }
}

# 通知配置
NOTIFICATION_CONFIG = {
    'enabled': os.getenv('ENABLE_NOTIFICATIONS', 'true').lower() == 'true',
    'websocket_enabled': os.getenv('WEBSOCKET_ENABLED', 'true').lower() == 'true',
}

# 上传配置
UPLOAD_CONFIG = {
    'upload_dir': BASE_DIR / 'uploads',
    'max_file_size': 100 * 1024 * 1024,  # 100MB
    'allowed_extensions': ['.txt', '.log', '.png', '.root', '.json'],
}

# 下载配置
DOWNLOAD_CONFIG = {
    'download_dir': BASE_DIR / 'downloads',
    'allowed_extensions': ['.pdf', '.png', '.jpg', '.jpeg', '.txt', '.log', '.root', '.json'],
    'max_file_size': 500 * 1024 * 1024,  # 500MB
}