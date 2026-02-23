#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作流相关API路由
"""

from flask import request, jsonify
from api.routes import workflows_bp
from models.database import db
from models.task import Workflow
from core.workflow_parser import workflow_parser


@workflows_bp.route('', methods=['GET'])
def get_workflows():
    """获取工作流列表"""
    try:
        workflows = Workflow.query.all()
        result = {
            'success': True,
            'workflows': [workflow.to_dict() for workflow in workflows]
        }
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@workflows_bp.route('/<workflow_name>', methods=['GET'])
def get_workflow(workflow_name):
    """获取工作流详情"""
    try:
        # 获取工作流信息
        workflow_info = workflow_parser.get_workflow_info(workflow_name)

        # 获取步骤列表
        steps = workflow_parser.get_workflow_steps(workflow_name)

        result = {
            'success': True,
            'workflow': {
                'name': workflow_info['name'],
                'description': workflow_info.get('description', ''),
                'version': workflow_info['version'],
                'steps': steps,
                'execution_config': workflow_parser.get_execution_config(workflow_name),
                'parameters_config': workflow_parser.get_parameters_config(workflow_name)
            }
        }
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@workflows_bp.route('/<workflow_name>/validate', methods=['POST'])
def validate_workflow(workflow_name):
    """验证工作流配置"""
    try:
        data = request.get_json()
        parameters = data.get('parameters', {})

        is_valid, error_msg = workflow_parser.validate_parameters(workflow_name, parameters)

        return jsonify({
            'success': True,
            'valid': is_valid,
            'error': error_msg if not is_valid else None
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500