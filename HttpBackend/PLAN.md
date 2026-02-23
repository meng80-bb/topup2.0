# Topup HTTP API 任务计划

## 项目概述

将现有的Step1-8任务转换为HTTP API形式，提供基于Web的任务管理和执行接口。

**项目目标：**
- 提供RESTful API接口来创建和管理Topup任务
- 支持工作流版本管理
- 实时追踪任务执行状态和进度
- 记录每步的输出结果
- 支持任务暂停、恢复和取消
- 提供任务历史记录和日志查询

## 系统架构

### 核心组件

1. **API服务层 (Flask/FastAPI)**
   - RESTful API端点
   - 请求验证和响应处理
   - 用户认证和授权

2. **数据库层 (SQLite)**
   - 任务实例管理
   - 步骤执行记录
   - 输出文件追踪
   - 日志存储

3. **任务执行引擎**
   - 工作流解析器
   - 步骤调度器
   - 状态管理器
   - 错误处理器

4. **配置管理层**
   - 工作流配置加载
   - 动态参数管理
   - 版本控制

### 目录结构

```
HttpBackend/
├── api/                          # API接口
│   ├── __init__.py
│   ├── app.py                    # Flask/FastAPI应用
│   ├── routes/                   # 路由定义
│   │   ├── __init__.py
│   │   ├── tasks.py              # 任务相关路由
│   │   ├── workflows.py          # 工作流相关路由
│   │   ├── executions.py         # 执行记录路由
│   │   └── logs.py               # 日志查询路由
│   └── middleware/               # 中间件
│       ├── __init__.py
│       ├── auth.py               # 认证中间件
│       └── error_handler.py      # 错误处理
├── core/                         # 核心业务逻辑
│   ├── __init__.py
│   ├── task_engine.py            # 任务执行引擎
│   ├── workflow_parser.py        # 工作流解析器
│   ├── step_executor.py          # 步骤执行器
│   ├── status_manager.py         # 状态管理器
│   └── output_tracker.py         # 输出追踪器
├── models/                       # 数据模型
│   ├── __init__.py
│   ├── database.py               # 数据库连接
│   ├── task.py                   # 任务模型
│   ├── workflow.py               # 工作流模型
│   ├── execution.py              # 执行记录模型
│   └── log.py                    # 日志模型
├── services/                     # 业务服务
│   ├── __init__.py
│   ├── task_service.py           # 任务服务
│   ├── workflow_service.py       # 工作流服务
│   ├── execution_service.py      # 执行服务
│   └── notification_service.py   # 通知服务
├── workflows/                    # 工作流配置
│   ├── topup_standard.json       # 标准工作流
│   ├── topu_quick.json           # 快速工作流（可选）
│   └── custom/                   # 自定义工作流
├── database_schema.sql           # 数据库Schema
├── requirements.txt              # 依赖列表
└── README.md                     # API文档
```

## 数据库设计

### 表结构

#### 1. workflows - 工作流定义表
- `id`: 主键
- `name`: 工作流名称（唯一）
- `description`: 描述
- `version`: 版本号
- `config_path`: 配置文件路径
- `status`: 状态 (active, inactive, deprecated)
- `created_at`, `updated_at`: 时间戳

#### 2. workflow_steps - 工作流步骤定义表
- `id`: 主键
- `workflow_id`: 工作流ID（外键）
- `step_order`: 步骤顺序
- `step_name`: 步骤名称（如 step1_1）
- `step_display_name`: 显示名称
- `step_module`: Python模块名
- `step_function`: Python函数名
- `description`: 描述
- `required_files`: 需要的文件列表（JSON）
- `timeout_minutes`: 超时时间
- `retry_count`: 重试次数
- `status`: 状态
- `created_at`, `updated_at`: 时间戳

#### 3. tasks - 任务实例表
- `id`: 主键
- `user_id`: 用户标识
- `workflow_id`: 工作流ID（外键）
- `task_name`: 任务名称
- `date_param`: 日期参数
- `status`: 状态 (pending, running, success, failed, paused, cancelled)
- `progress_percentage`: 进度百分比
- `current_step`: 当前步骤
- `error_message`: 错误信息
- `created_at`, `started_at`, `completed_at`: 时间戳
- `estimated_completion_time`: 预计完成时间

#### 4. task_executions - 任务步骤执行记录表
- `id`: 主键
- `task_id`: 任务ID（外键）
- `step_name`: 步骤名称
- `step_display_name`: 显示名称
- `step_order`: 步骤顺序
- `status`: 状态 (pending, running, success, failed, timeout, cancelled)
- `start_time`, `end_time`: 开始/结束时间
- `duration_seconds`: 执行耗时
- `retry_count`: 重试次数
- `output_summary`: 输出摘要
- `error_details`: 错误详情
- `created_at`: 创建时间

#### 5. step_outputs - 任务步骤输出表
- `id`: 主键
- `execution_id`: 执行记录ID（外键）
- `output_type`: 输出类型
- `output_path`: 文件路径
- `file_size_bytes`: 文件大小
- `file_hash`: 文件哈希
- `content_type`: 内容类型
- `metadata`: 元数据（JSON）
- `created_at`: 创建时间

#### 6. task_logs - 任务日志表
- `id`: 主键
- `task_id`: 任务ID（外键）
- `execution_id`: 执行记录ID（外键，可选）
- `level`: 日志级别 (info, warning, error, debug)
- `message`: 日志消息
- `timestamp`: 时间戳
- `source`: 日志来源

#### 7. task_parameters - 任务参数表
- `id`: 主键
- `task_id`: 任务ID（外键）
- `param_name`: 参数名
- `param_value`: 参数值
- `param_type`: 参数类型 (text, integer, boolean)
- `created_at`: 创建时间

#### 8. user_preferences - 用户配置表
- `id`: 主键
- `user_id`: 用户标识（唯一）
- `default_workflow_id`: 默认工作流
- `default_timeout`: 默认超时时间
- `preferred_date`: 偏好的日期格式
- `notification_preferences`: 通知设置（JSON）
- `created_at`, `updated_at`: 时间戳

## API接口设计

### 任务管理接口

#### 1. 创建任务
```
POST /api/tasks
Request:
{
    "user_id": "user123",
    "workflow_name": "topup_standard_workflow",
    "task_name": "处理250624日期数据",
    "parameters": {
        "date_param": "250624",
        "submit_job": true,
        "max_wait_minutes": 25
    }
}
Response:
{
    "success": true,
    "task_id": 1,
    "status": "pending",
    "message": "任务创建成功"
}
```

#### 2. 获取任务列表
```
GET /api/tasks?user_id=user123&status=running&limit=10&offset=0
Response:
{
    "success": true,
    "tasks": [...],
    "total": 100,
    "page": 1
}
```

#### 3. 获取任务详情
```
GET /api/tasks/{task_id}
Response:
{
    "success": true,
    "task": {
        "id": 1,
        "user_id": "user123",
        "workflow_name": "topup_standard_workflow",
        "task_name": "处理250624日期数据",
        "status": "running",
        "progress_percentage": 45,
        "current_step": "step3_1",
        "created_at": "2025-02-23T10:00:00Z",
        "started_at": "2025-02-23T10:01:00Z",
        "estimated_completion_time": "2025-02-23T12:30:00Z"
    }
}
```

#### 4. 获取任务执行记录
```
GET /api/tasks/{task_id}/executions
Response:
{
    "success": true,
    "executions": [
        {
            "step_name": "step1_1",
            "step_display_name": "第一次作业提交并检查结果文件",
            "status": "success",
            "start_time": "2025-02-23T10:01:00Z",
            "end_time": "2025-02-23T10:25:30Z",
            "duration_seconds": 1470
        },
        ...
    ]
}
```

#### 5. 获取步骤输出
```
GET /api/tasks/{task_id}/executions/{execution_id}/outputs
Response:
{
    "success": true,
    "outputs": [
        {
            "output_type": "root_file",
            "output_path": "/path/to/file.root",
            "file_size_bytes": 1024000,
            "content_type": "root"
        },
        ...
    ]
}
```

#### 6. 暂停任务
```
POST /api/tasks/{task_id}/pause
Response:
{
    "success": true,
    "message": "任务已暂停"
}
```

#### 7. 恢复任务
```
POST /api/tasks/{task_id}/resume
Response:
{
    "success": true,
    "message": "任务已恢复"
}
```

#### 8. 取消任务
```
POST /api/tasks/{task_id}/cancel
Response:
{
    "success": true,
    "message": "任务已取消"
}
```

#### 9. 获取任务日志
```
GET /api/tasks/{task_id}/logs?level=error&limit=100
Response:
{
    "success": true,
    "logs": [...]
}
```

#### 10. 获取任务实时进度（WebSocket）
```
WS /api/tasks/{task_id}/progress
```

### 工作流管理接口

#### 1. 获取工作流列表
```
GET /api/workflows
Response:
{
    "success": true,
    "workflows": [...]
}
```

#### 2. 获取工作流详情
```
GET /api/workflows/{workflow_id}
Response:
{
    "success": true,
    "workflow": {
        "id": 1,
        "name": "topup_standard_workflow",
        "version": "1.0.0",
        "steps": [...]
    }
}
```

#### 3. 创建自定义工作流
```
POST /api/workflows
Request:
{
    "name": "custom_workflow",
    "description": "自定义工作流",
    "steps": [...]
}
```

## 实施计划

### 第一阶段：基础设施搭建（1-2周）
- [ ] 搭建Flask/FastAPI项目框架
- [ ] 实现数据库连接和模型
- [ ] 创建基础中间件（认证、错误处理）
- [ ] 编写配置加载器
- [ ] 单元测试框架搭建

### 第二阶段：核心功能实现（3-4周）
- [ ] 工作流解析器
- [ ] 任务执行引擎
- [ ] 步骤执行器
- [ ] 状态管理器
- [ ] 输出追踪器
- [ ] 实现任务CRUD接口
- [ ] 实现工作流管理接口

### 第三阶段：高级功能实现（2-3周）
- [ ] 任务暂停/恢复/取消
- [ ] 实时进度推送（WebSocket）
- [ ] 任务重试机制
- [ ] 并发任务管理
- [ ] 日志查询接口
- [ ] 输出文件管理

### 第四阶段：优化和测试（2-3周）
- [ ] 性能优化
- [ ] 安全性增强
- [ ] API文档完善
- [ ] 集成测试
- [ ] 压力测试
- [ ] Bug修复

### 第五阶段：部署和监控（1-2周）
- [ ] 部署脚本编写
- [ ] 监控系统搭建
- [ ] 日志收集系统
- [ ] 备份和恢复策略
- [ ] 用户文档编写

## 技术栈

### 后端框架
- **Flask 3.0+** 或 **FastAPI** - Web框架
- **SQLAlchemy 2.0+** - ORM
- **Alembic** - 数据库迁移

### 数据库
- **SQLite 3.38+** - 主数据库（开发/小规模部署）
- **PostgreSQL** - 生产环境可选

### 异步任务
- **Celery** - 任务队列（可选）
- **Redis** - 消息队列（可选）

### 认证和安全
- **JWT** - 用户认证
- **Flask-CORS** - 跨域支持
- **python-dotenv** - 环境变量管理

### 通信和实时更新
- **WebSocket** - 实时进度推送
- **Socket.IO** - 事件通信（可选）

### 监控和日志
- **Prometheus** - 指标收集
- **Grafana** - 监控面板
- **ELK Stack** - 日志管理（可选）

## 配置文件说明

### 工作流配置格式

工作流配置文件采用JSON格式，包含以下主要部分：

1. **workflow**: 工作流基本信息
   - name, version, description等

2. **execution**: 执行策略
   - 并行任务数、超时时间、重试策略等

3. **steps**: 步骤定义数组
   - 每个步骤包含：id, order, module, function, dependencies等

4. **parameters**: 参数定义
   - required: 必需参数
   - optional: 可选参数及默认值

5. **notifications**: 通知配置
   - 各种事件的通知设置

6. **output**: 输出配置
   - 目录路径、下载设置等

## 注意事项

1. **并发控制**: 需要控制同一用户的并发任务数量
2. **超时处理**: 每个步骤需要独立的超时控制
3. **错误恢复**: 支持从失败步骤恢复执行
4. **资源管理**: 及时清理临时文件和资源
5. **日志记录**: 详细记录每个步骤的执行日志
6. **安全性**: 验证用户输入，防止命令注入等安全问题
7. **可扩展性**: 设计应支持未来添加新的工作流和步骤

## 依赖关系

```
Flask/FastAPI应用
    ├─> 数据库层 (SQLAlchemy)
    ├─> 任务执行引擎
    │   ├─> 工作流解析器
    │   ├─> 步骤执行器
    │   └─> 状态管理器
    ├─> 业务服务层
    │   ├─> 任务服务
    │   ├─> 工作流服务
    │   └─> 通知服务
    └─> 现有Step模块 (step1_1, step1_2, ...)
```

## 数据流

```
用户请求 -> API接口 -> 任务服务 -> 任务执行引擎
    -> 工作流解析 -> 步骤调度 -> 步骤执行 -> 输出收集
    -> 状态更新 -> 数据库存储 -> 用户响应
```

## 测试策略

1. **单元测试**: 每个核心组件的单元测试
2. **集成测试**: API端点的集成测试
3. **端到端测试**: 完整工作流的执行测试
4. **性能测试**: 并发任务和大数据量的性能测试
5. **安全测试**: 输入验证和权限控制测试

## 部署建议

1. **开发环境**: SQLite + Flask开发服务器
2. **测试环境**: PostgreSQL + Gunicorn
3. **生产环境**: PostgreSQL + Gunicorn + Nginx + Supervisor

## 文档和培训

1. **API文档**: 使用Swagger/OpenAPI自动生成
2. **部署文档**: 详细的部署和配置说明
3. **用户手册**: API使用指南
4. **开发文档**: 架构设计和代码规范

## 未来扩展

1. **Web界面**: 基于React/Vue的管理界面
2. **任务调度**: 支持定时任务和cron表达式
3. **多租户**: 支持多用户隔离
4. **分布式执行**: 支持多节点分布式执行
5. **机器学习**: 智能参数优化和错误预测