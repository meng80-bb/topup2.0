#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务相关API路由
"""

from flask import request, jsonify
from api.routes import tasks_bp
from models.database import db
from models.task import Task, Workflow
from services.task_service import TaskService
from core.task_engine import TaskEngine

# 初始化服务
task_service = TaskService()
task_engine = TaskEngine()


@tasks_bp.route('', methods=['POST'])
def create_task():
    """
    创建新任务
    POST /api/tasks
    """
    try:
        data = request.get_json()

        # 验证必需字段
        required_fields = ['user_id', 'workflow_name']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400

        # 创建任务
        result = task_service.create_task(
            user_id=data['user_id'],
            workflow_name=data['workflow_name'],
            task_name=data.get('task_name'),
            parameters=data.get('parameters', {})
        )

        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@tasks_bp.route('', methods=['GET'])
def get_tasks():
    """
    获取任务列表
    GET /api/tasks?user_id=xxx&status=running&limit=10&offset=0
    """
    try:
        # 获取查询参数
        user_id = request.args.get('user_id')
        status = request.args.get('status')
        limit = int(request.args.get('limit', 10))
        offset = int(request.args.get('offset', 0))

        # 验证user_id
        if not user_id:
            return jsonify({'success': False, 'error': 'user_id is required'}), 400

        # 查询任务
        result = task_service.get_tasks(
            user_id=user_id,
            status=status,
            limit=limit,
            offset=offset
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@tasks_bp.route('/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """
    获取任务详情
    GET /api/tasks/{task_id}
    """
    try:
        result = task_service.get_task(task_id, include_details=True)
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 404

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@tasks_bp.route('/<int:task_id>/start', methods=['POST'])
def start_task(task_id):
    """
    启动任务执行
    POST /api/tasks/{task_id}/start
    """
    try:
        result = task_engine.start_task(task_id)
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@tasks_bp.route('/<int:task_id>/pause', methods=['POST'])
def pause_task(task_id):
    """
    暂停任务
    POST /api/tasks/{task_id}/pause
    """
    try:
        result = task_engine.pause_task(task_id)
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@tasks_bp.route('/<int:task_id>/resume', methods=['POST'])
def resume_task(task_id):
    """
    恢复任务
    POST /api/tasks/{task_id}/resume
    """
    try:
        result = task_engine.resume_task(task_id)
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@tasks_bp.route('/<int:task_id>/cancel', methods=['POST'])
def cancel_task(task_id):
    """
    取消任务
    POST /api/tasks/{task_id}/cancel
    """
    try:
        result = task_engine.cancel_task(task_id)
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@tasks_bp.route('/<int:task_id>/logs', methods=['GET'])
def get_task_logs(task_id):
    """
    获取任务日志
    GET /api/tasks/{task_id}/logs?level=error&limit=100
    """
    try:
        level = request.args.get('level')
        limit = int(request.args.get('limit', 100))

        result = task_service.get_task_logs(task_id, level=level, limit=limit)
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 404

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@tasks_bp.route('/<int:task_id>/progress', methods=['GET'])
def get_task_progress(task_id):
    """
    获取任务进度
    GET /api/tasks/{task_id}/progress
    """
    try:
        result = task_service.get_task_progress(task_id)
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 404

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500