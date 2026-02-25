#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
错误处理中间件
"""

from flask import jsonify
import logging

logger = logging.getLogger(__name__)


def setup_error_handler(app):
    """设置错误处理器"""

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'success': False, 'error': 'Bad Request', 'message': str(error)}), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'success': False, 'error': 'Not Found', 'message': str(error)}), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {str(error)}")
        return jsonify({'success': False, 'error': 'Internal Server Error', 'message': 'An unexpected error occurred'}), 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': 'Internal Server Error', 'message': str(e)}), 500