#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
执行记录相关API路由
"""

from flask import request, jsonify
from flask import Blueprint

# 创建蓝图
executions_bp = Blueprint('executions', __name__)


@executions_bp.route('/<int:task_id>', methods=['GET'])
def get_task_executions(task_id):
    """获取任务执行记录"""
    try:
        # 这里需要从数据库查询执行记录
        # 暂时返回空列表
        return jsonify({
            'success': True,
            'executions': [],
            'total': 0
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@executions_bp.route('/<int:execution_id>/outputs', methods=['GET'])
def get_execution_outputs(execution_id):
    """获取执行记录的输出文件"""
    try:
        # 这里需要从数据库查询输出文件
        # 暂时返回空列表
        return jsonify({
            'success': True,
            'outputs': []
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500