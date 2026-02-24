#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重置工作流数据
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app import app, db
from models.task import Workflow, WorkflowStep

def reset_workflows():
    """重置所有工作流"""
    with app.app_context():
        # 删除所有工作流
        WorkflowStep.query.delete()
        Workflow.query.delete()
        db.session.commit()
        print("✅ 所有工作流已删除")

        # 重新初始化
        import init_workflows
        init_workflows.init_all_workflows()

if __name__ == '__main__':
    reset_workflows()