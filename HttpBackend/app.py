#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Topup HTTP API 应用主文件
"""

from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
import logging
import logging.config
from pathlib import Path

from config import FLASK_CONFIG, LOGGING_CONFIG, DATABASE_URL, NOTIFICATION_CONFIG
from models.database import db
from api.routes import tasks_bp, workflows_bp, executions_bp, logs_bp
from api.middleware import setup_middleware

# 创建应用实例
app = Flask(__name__)
app.config.update(FLASK_CONFIG)

# 配置CORS
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# 配置日志
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

# 初始化数据库
db.init_app(app)

# 初始化SocketIO（用于实时通信）
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# 设置中间件
setup_middleware(app)

# 注册蓝图
app.register_blueprint(tasks_bp, url_prefix='/api/tasks')
app.register_blueprint(workflows_bp, url_prefix='/api/workflows')
app.register_blueprint(executions_bp, url_prefix='/api/executions')
app.register_blueprint(logs_bp, url_prefix='/api/logs')

@app.route('/api/health')
def health_check():
    """健康检查接口"""
    return {
        'status': 'healthy',
        'message': 'Topup HTTP API is running',
        'version': '1.0.0'
    }

@app.route('/')
def index():
    """根路径"""
    return {
        'message': 'Topup HTTP API',
        'version': '1.0.0',
        'endpoints': {
            'tasks': '/api/tasks',
            'workflows': '/api/workflows',
            'executions': '/api/executions',
            'logs': '/api/logs'
        }
    }

# 数据库初始化函数
def init_database():
    """初始化数据库表"""
    with app.app_context():
        # 创建所有表
        db.create_all()
        logger.info("Database tables created successfully")

        # 这里可以添加初始化数据
        # init_default_data()

def init_default_data():
    """初始化默认数据"""
    from models.task import Workflow
    from workflows.topup_standard import get_workflow_config

    # 检查是否存在标准工作流
    workflow = Workflow.query.filter_by(name='topup_standard_workflow').first()
    if not workflow:
        # 创建标准工作流
        config = get_workflow_config()
        workflow = Workflow(
            name=config['workflow']['name'],
            description=config['workflow']['description'],
            version=config['workflow']['version'],
            config_path=config['workflow']['config_path'],
            status='active'
        )
        db.session.add(workflow)
        db.session.commit()
        logger.info("Default workflow created successfully")

# WebSocket事件处理
@socketio.on('connect')
def handle_connect():
    """客户端连接"""
    logger.info(f"Client connected: {request.sid}")
    socketio.emit('connected', {'message': 'Connected to Topup API'})

@socketio.on('disconnect')
def handle_disconnect():
    """客户端断开连接"""
    logger.info(f"Client disconnected: {request.sid}")

@socketio.on('subscribe_task')
def handle_task_subscribe(data):
    """订阅任务更新"""
    task_id = data.get('task_id')
    if task_id:
        logger.info(f"Client {request.sid} subscribed to task {task_id}")
        # 这里可以实现房间订阅逻辑

# 工具函数
def emit_task_update(task_id, event_type, data):
    """发送任务更新事件"""
    if NOTIFICATION_CONFIG['websocket_enabled']:
        socketio.emit(f'task_{event_type}', data, room=f'task_{task_id}')
        logger.debug(f"Emitted task_{event_type} for task {task_id}")

def emit_progress_update(task_id, progress):
    """发送进度更新"""
    emit_task_update(task_id, 'progress', {
        'task_id': task_id,
        'progress': progress,
        'timestamp': datetime.utcnow().isoformat()
    })

def emit_status_update(task_id, status, message=None):
    """发送状态更新"""
    emit_task_update(task_id, 'status', {
        'task_id': task_id,
        'status': status,
        'message': message,
        'timestamp': datetime.utcnow().isoformat()
    })

if __name__ == '__main__':
    # 初始化数据库
    init_database()

    # 运行应用
    logger.info("Starting Topup HTTP API server...")
    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=app.config['DEBUG'],
        use_reloader=False
    )