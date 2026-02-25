#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API中间件包
"""

from .error_handler import setup_error_handler
from .auth import setup_auth

def setup_middleware(app):
    """设置所有中间件"""
    setup_error_handler(app)
    setup_auth(app)