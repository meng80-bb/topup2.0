#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件下载相关API路由
"""

from flask import request, jsonify, send_file, abort
from flask import Blueprint
import os
from pathlib import Path
from config import DOWNLOAD_CONFIG
from typing import Optional

# 创建蓝图
downloads_bp = Blueprint('downloads', __name__)


@downloads_bp.route('/<filename>', methods=['GET'])
def download_file(filename: str):
    """
    下载文件
    GET /api/downloads/{filename}

    Args:
        filename: 要下载的文件名

    支持的查询参数:
    - task_id: 可选，任务ID，用于验证文件访问权限
    - file_type: 可选，文件类型（如 pdf, png, log 等）
    """
    try:
        # 验证文件名，防止路径遍历攻击
        if '..' in filename or filename.startswith('/'):
            return jsonify({
                'success': False,
                'error': 'Invalid filename'
            }), 400

        # 检查文件扩展名
        file_ext = Path(filename).suffix.lower()
        if file_ext not in DOWNLOAD_CONFIG['allowed_extensions']:
            return jsonify({
                'success': False,
                'error': f'File type {file_ext} is not allowed'
            }), 400

        # 构建文件路径
        download_dir = DOWNLOAD_CONFIG['download_dir']
        file_path = download_dir / filename

        # 检查文件是否存在
        if not file_path.exists():
            return jsonify({
                'success': False,
                'error': 'File not found'
            }), 404

        # 检查文件大小
        file_size = file_path.stat().st_size
        if file_size > DOWNLOAD_CONFIG['max_file_size']:
            return jsonify({
                'success': False,
                'error': f'File size exceeds maximum allowed size of {DOWNLOAD_CONFIG["max_file_size"]} bytes'
            }), 400

        # 获取任务ID参数（用于验证访问权限）
        task_id = request.args.get('task_id', type=int)

        # 如果提供了task_id，可以在这里添加权限验证逻辑
        # 例如：检查该文件是否属于该任务
        if task_id:
            # TODO: 添加权限验证逻辑
            pass

        # 设置下载文件的MIME类型
        mimetype = None
        if file_ext == '.pdf':
            mimetype = 'application/pdf'
        elif file_ext in ['.png', '.jpg', '.jpeg']:
            mimetype = f'image/{file_ext[1:]}'
        elif file_ext == '.txt':
            mimetype = 'text/plain'
        elif file_ext == '.json':
            mimetype = 'application/json'
        elif file_ext == '.log':
            mimetype = 'text/plain'

        # 发送文件
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype=mimetype
        )

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@downloads_bp.route('/task/<int:task_id>', methods=['GET'])
def download_task_file(task_id: int):
    """
    下载任务相关文件
    GET /api/downloads/task/{task_id}?file_type=merged_pdf&date=250519

    Args:
        task_id: 任务ID

    支持的查询参数:
    - file_type: 文件类型（merged_pdf, log, output 等）
    - date: 日期参数（如 250519）
    - step_id: 步骤ID（可选）
    """
    try:
        file_type = request.args.get('file_type')
        date = request.args.get('date')
        step_id = request.args.get('step_id')

        if not file_type:
            return jsonify({
                'success': False,
                'error': 'file_type parameter is required'
            }), 400

        # 根据文件类型构建文件名
        if file_type == 'merged_pdf':
            if not date:
                return jsonify({
                    'success': False,
                    'error': 'date parameter is required for merged_pdf'
                }), 400
            filename = f"mergedd_IST_{date}.pdf"
        elif file_type == 'log':
            filename = f"task_{task_id}.log"
        elif file_type == 'output':
            filename = f"task_{task_id}_output.txt"
        else:
            return jsonify({
                'success': False,
                'error': f'Unknown file_type: {file_type}'
            }), 400

        # 构建文件路径
        download_dir = DOWNLOAD_CONFIG['download_dir']
        file_path = download_dir / filename

        # 检查文件是否存在
        if not file_path.exists():
            return jsonify({
                'success': False,
                'error': f'File not found: {filename}',
                'filename': filename
            }), 404

        # 设置下载文件的MIME类型
        file_ext = Path(filename).suffix.lower()
        mimetype = None
        if file_ext == '.pdf':
            mimetype = 'application/pdf'
        elif file_ext == '.log':
            mimetype = 'text/plain'

        # 发送文件
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype=mimetype
        )

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@downloads_bp.route('/list', methods=['GET'])
def list_files():
    """
    列出可下载的文件
    GET /api/downloads/list?task_id=xxx&file_type=pdf

    支持的查询参数:
    - task_id: 可选，过滤特定任务的文件
    - file_type: 可选，文件类型（pdf, png, log 等）
    """
    try:
        download_dir = DOWNLOAD_CONFIG['download_dir']

        # 确保下载目录存在
        if not download_dir.exists():
            return jsonify({
                'success': True,
                'files': [],
                'total': 0
            })

        # 获取过滤参数
        task_id = request.args.get('task_id')
        file_type = request.args.get('file_type')

        # 获取所有文件
        files = []
        for file_path in download_dir.iterdir():
            if file_path.is_file():
                filename = file_path.name
                file_ext = file_path.suffix.lower()

                # 检查文件扩展名
                if file_type and file_ext != f'.{file_type}':
                    continue

                # 检查任务ID（如果文件名包含task_id）
                if task_id and f'task_{task_id}' not in filename:
                    continue

                # 检查文件扩展名是否在允许列表中
                if file_ext not in DOWNLOAD_CONFIG['allowed_extensions']:
                    continue

                files.append({
                    'filename': filename,
                    'size': file_path.stat().st_size,
                    'modified_time': file_path.stat().st_mtime,
                    'url': f'/api/downloads/{filename}'
                })

        # 按修改时间排序（最新的在前）
        files.sort(key=lambda x: x['modified_time'], reverse=True)

        return jsonify({
            'success': True,
            'files': files,
            'total': len(files)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@downloads_bp.route('/check/<filename>', methods=['GET'])
def check_file(filename: str):
    """
    检查文件是否存在
    GET /api/downloads/check/{filename}

    Args:
        filename: 要检查的文件名

    Returns:
        文件信息（大小、修改时间等）
    """
    try:
        # 验证文件名，防止路径遍历攻击
        if '..' in filename or filename.startswith('/'):
            return jsonify({
                'success': False,
                'error': 'Invalid filename'
            }), 400

        # 构建文件路径
        download_dir = DOWNLOAD_CONFIG['download_dir']
        file_path = download_dir / filename

        # 检查文件是否存在
        if not file_path.exists():
            return jsonify({
                'success': False,
                'exists': False,
                'filename': filename
            })

        # 获取文件信息
        stat = file_path.stat()

        return jsonify({
            'success': True,
            'exists': True,
            'filename': filename,
            'size': stat.st_size,
            'modified_time': stat.st_mtime,
            'download_url': f'/api/downloads/{filename}'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
