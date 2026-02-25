#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Blueprint, jsonify

# 创建新蓝图
tasks_bp = Blueprint('test_tasks', __name__)

@tasks_bp.route('', methods=['GET'])
def get_tasks():
    return {'message': 'This is a test task route'}

@tasks_bp.route('', methods=['POST'])
def create_task():
    return {'message': 'Task created successfully'}

if __name__ == '__main__':
    print("Test routes:")
    for rule in tasks_bp.url_map.iter_rules():
        print(f'{rule.rule} -> {rule.endpoint}')