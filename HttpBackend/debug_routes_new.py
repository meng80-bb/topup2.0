#!/usr/bin/env python3
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from flask import Flask
from api.routes import tasks_bp

print("Creating new Flask app...")
app = Flask(__name__)

print("Registering tasks blueprint...")
app.register_blueprint(tasks_bp, url_prefix='/api/tasks')

@app.route('/api/debug')
def debug():
    """调试端点"""
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append(f'{rule.rule} -> {rule.endpoint}')
    return {'routes': routes}

if __name__ == '__main__':
    print("注册的路由:")
    for rule in app.url_map.iter_rules():
        print(f'{rule.rule} -> {rule.endpoint}')
    app.run(host='127.0.0.1', port=5002, debug=True)
