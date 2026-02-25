#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务相关数据模型
"""

from datetime import datetime
from sqlalchemy import JSON, Column, Integer, String, Text, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from models.database import db


class Workflow(db.Model):
    """工作流定义表"""
    __tablename__ = 'workflows'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    version = Column(String(20), nullable=False)
    config_path = Column(String(255), nullable=False)
    status = Column(String(20), default='active')  # active, inactive, deprecated
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关联关系
    steps = relationship('WorkflowStep', back_populates='workflow', cascade='all, delete-orphan')
    tasks = relationship('Task', back_populates='workflow')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'version': self.version,
            'config_path': self.config_path,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class WorkflowStep(db.Model):
    """工作流步骤定义表"""
    __tablename__ = 'workflow_steps'

    id = Column(Integer, primary_key=True, autoincrement=True)
    workflow_id = Column(Integer, ForeignKey('workflows.id', ondelete='CASCADE'), nullable=False)
    step_order = Column(Integer, nullable=False)
    step_name = Column(String(50), nullable=False)
    step_display_name = Column(String(100), nullable=False)
    step_module = Column(String(100), nullable=False)
    step_function = Column(String(100), nullable=False)
    description = Column(Text)
    required_files = Column(JSON)  # 存储为JSON字符串
    timeout_minutes = Column(Integer, default=30)
    retry_count = Column(Integer, default=3)
    status = Column(String(20), default='active')
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关联关系
    workflow = relationship('Workflow', back_populates='steps')

    def to_dict(self):
        return {
            'id': self.id,
            'workflow_id': self.workflow_id,
            'step_order': self.step_order,
            'step_name': self.step_name,
            'step_display_name': self.step_display_name,
            'step_module': self.step_module,
            'step_function': self.step_function,
            'description': self.description,
            'required_files': self.required_files,
            'timeout_minutes': self.timeout_minutes,
            'retry_count': self.retry_count,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class Task(db.Model):
    """任务实例表"""
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), nullable=False, index=True)
    workflow_id = Column(Integer, ForeignKey('workflows.id', ondelete='CASCADE'), nullable=False)
    task_name = Column(String(200), nullable=False)
    date_param = Column(String(10))
    status = Column(String(20), default='pending', index=True)  # pending, running, success, failed, paused, cancelled
    progress_percentage = Column(Integer, default=0)
    current_step = Column(String(50))
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    estimated_completion_time = Column(DateTime)

    # 关联关系
    workflow = relationship('Workflow', back_populates='tasks')
    executions = relationship('TaskExecution', back_populates='task', cascade='all, delete-orphan')
    parameters = relationship('TaskParameter', back_populates='task', cascade='all, delete-orphan')
    logs = relationship('TaskLog', back_populates='task', cascade='all, delete-orphan')

    def to_dict(self, include_details=False):
        result = {
            'id': self.id,
            'user_id': self.user_id,
            'workflow_id': self.workflow_id,
            'task_name': self.task_name,
            'date_param': self.date_param,
            'status': self.status,
            'progress_percentage': self.progress_percentage,
            'current_step': self.current_step,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'estimated_completion_time': self.estimated_completion_time.isoformat() if self.estimated_completion_time else None,
        }

        if include_details:
            result['executions'] = [e.to_dict() for e in self.executions]
            result['parameters'] = {p.param_name: p.param_value for p in self.parameters}

        return result


class TaskExecution(db.Model):
    """任务步骤执行记录表"""
    __tablename__ = 'task_executions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False, index=True)
    step_name = Column(String(50), nullable=False, index=True)
    step_display_name = Column(String(100))
    step_order = Column(Integer, nullable=False)
    status = Column(String(20), default='pending', index=True)  # pending, running, success, failed, timeout, cancelled
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    duration_seconds = Column(Integer)
    retry_count = Column(Integer, default=0)
    output_summary = Column(Text)
    error_details = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 关联关系
    task = relationship('Task', back_populates='executions')
    outputs = relationship('StepOutput', back_populates='execution', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'task_id': self.task_id,
            'step_name': self.step_name,
            'step_display_name': self.step_display_name,
            'step_order': self.step_order,
            'status': self.status,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_seconds': self.duration_seconds,
            'retry_count': self.retry_count,
            'output_summary': self.output_summary,
            'error_details': self.error_details,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class StepOutput(db.Model):
    """任务步骤输出表"""
    __tablename__ = 'step_outputs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    execution_id = Column(Integer, ForeignKey('task_executions.id', ondelete='CASCADE'), nullable=False, index=True)
    output_type = Column(String(50), nullable=False)
    output_path = Column(String(500))
    file_size_bytes = Column(Integer)
    file_hash = Column(String(64))
    content_type = Column(String(50))
    step_metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 关联关系
    execution = relationship('TaskExecution', back_populates='outputs')

    def to_dict(self):
        return {
            'id': self.id,
            'execution_id': self.execution_id,
            'output_type': self.output_type,
            'output_path': self.output_path,
            'file_size_bytes': self.file_size_bytes,
            'file_hash': self.file_hash,
            'content_type': self.content_type,
            'metadata': self.step_metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class TaskLog(db.Model):
    """任务日志表"""
    __tablename__ = 'task_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False, index=True)
    execution_id = Column(Integer, ForeignKey('task_executions.id', ondelete='CASCADE'), index=True)
    level = Column(String(10), nullable=False)  # info, warning, error, debug
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    source = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 关联关系
    task = relationship('Task', back_populates='logs')

    def to_dict(self):
        return {
            'id': self.id,
            'task_id': self.task_id,
            'execution_id': self.execution_id,
            'level': self.level,
            'message': self.message,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'source': self.source,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class TaskParameter(db.Model):
    """任务参数表"""
    __tablename__ = 'task_parameters'

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False)
    param_name = Column(String(50), nullable=False)
    param_value = Column(Text, nullable=False)
    param_type = Column(String(20), default='text')  # text, integer, boolean
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 关联关系
    task = relationship('Task', back_populates='parameters')

    def to_dict(self):
        return {
            'id': self.id,
            'task_id': self.task_id,
            'param_name': self.param_name,
            'param_value': self.param_value,
            'param_type': self.param_type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class UserPreference(db.Model):
    """用户配置表"""
    __tablename__ = 'user_preferences'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), unique=True, nullable=False)
    default_workflow_id = Column(Integer, ForeignKey('workflows.id', ondelete='SET NULL'))
    default_timeout = Column(Integer)
    preferred_date = Column(String(20))
    notification_preferences = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'default_workflow_id': self.default_workflow_id,
            'default_timeout': self.default_timeout,
            'preferred_date': self.preferred_date,
            'notification_preferences': self.notification_preferences,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }