#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
初始化工作流到数据库
"""

import sys
import json
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app import app, db
from models.task import Workflow, WorkflowStep

def load_workflow_from_json(json_path):
    """从JSON文件加载工作流"""
    with open(json_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    workflow_config = config['workflow']

    # 检查工作流是否已存在
    existing = Workflow.query.filter_by(name=workflow_config['name']).first()
    if existing:
        print(f"工作流 '{workflow_config['name']}' 已存在，跳过")
        return existing

    # 创建工作流
    workflow = Workflow(
        name=workflow_config['name'],
        description=workflow_config['description'],
        version=workflow_config['version'],
        config_path=str(json_path),
        status='active'
    )
    db.session.add(workflow)
    db.session.flush()  # 获取workflow.id

    # 创建步骤
    for step_config in config['steps']:
        step = WorkflowStep(
            workflow_id=workflow.id,
            step_order=step_config['order'],
            step_name=step_config['id'],
            step_display_name=step_config['display_name'],
            step_module=step_config['module'],
            step_function=step_config['function'],
            description=step_config['description'],
            timeout_minutes=step_config.get('timeout_minutes', 30),
            retry_count=step_config.get('retry_count', 3),
            required_files=step_config.get('parameters', {})
        )
        db.session.add(step)

    db.session.commit()
    print(f"✅ 工作流 '{workflow_config['name']}' 加载成功")
    return workflow

def init_all_workflows():
    """初始化所有工作流"""
    with app.app_context():
        workflows_dir = Path(__file__).parent / 'workflows'

        # 加载所有JSON工作流文件
        for json_file in workflows_dir.glob('*.json'):
            print(f"加载工作流: {json_file.name}")
            try:
                load_workflow_from_json(json_file)
            except Exception as e:
                print(f"❌ 加载工作流失败 {json_file.name}: {e}")
                import traceback
                traceback.print_exc()

        # 显示所有工作流
        print("\n当前数据库中的工作流:")
        workflows = Workflow.query.all()
        for wf in workflows:
            print(f"  - {wf.name} ({wf.version})")

if __name__ == '__main__':
    init_all_workflows()