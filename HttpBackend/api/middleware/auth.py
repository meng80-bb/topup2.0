#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
认证中间件
"""

from flask import request, jsonify, g
import jwt
from functools import wraps
import logging

logger = logging.getLogger(__name__)


def setup_auth(app):
    """设置认证机制"""

    # JWT密钥（应该从环境变量获取）
    SECRET_KEY = app.config.get('SECRET_KEY', 'your-secret-key-here')

    def token_required(f):
        """JWT Token验证装饰器"""
        @wraps(f)
        def decorated(*args, **kwargs):
            token = None

            # 从请求头获取token
            if 'Authorization' in request.headers:
                auth_header = request.headers['Authorization']
                if auth_header.startswith('Bearer '):
                    token = auth_header.split(' ')[1]

            if not token:
                return jsonify({'success': False, 'error': 'Token is missing'}), 401

            try:
                # 验证token
                data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
                g.current_user = data['user_id']
            except jwt.ExpiredSignatureError:
                return jsonify({'success': False, 'error': 'Token has expired'}), 401
            except jwt.InvalidTokenError:
                return jsonify({'success': False, 'error': 'Invalid token'}), 401

            return f(*args, **kwargs)

        return decorated

    # 目前我们暂时使用简单的认证，后续可以扩展
    @app.before_request
    def before_request():
        """请求前处理"""
        # 为所有请求添加user_id（临时方案，实际应该从token获取）
        if 'user_id' not in g:
            g.user_id = request.args.get('user_id', 'default_user')

    def generate_token(user_id):
        """生成JWT token"""
        return jwt.encode({
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, SECRET_KEY, algorithm='HS256')

    app.jwt_required = token_required
    app.generate_token = generate_token