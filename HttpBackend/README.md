# Topup HTTP API

基于 Flask 的 Topup 数据处理任务管理系统，提供 RESTful API 接口和 WebSocket 实时通信来管理和执行数据处理工作流。

## 功能特性

- ✅ RESTful API 接口
- ✅ WebSocket 实时任务状态推送
- ✅ 工作流引擎和步骤执行器
- ✅ SSH 远程命令执行
- ✅ 任务日志记录和查询
- ✅ 文件上传下载
- ✅ 数据库持久化存储

## 项目结构

```
HttpBackend/
├── api/                      # API接口层
│   ├── routes/              # 路由定义
│   │   ├── tasks.py         # 任务管理接口
│   │   ├── workflows.py     # 工作流管理接口
│   │   ├── executions.py    # 执行记录接口
│   │   ├── logs.py          # 日志查询接口
│   │   └── downloads.py     # 文件下载接口
│   └── middleware/          # 中间件
│       ├── auth.py          # 认证中间件
│       └── error_handler.py # 错误处理
├── core/                    # 核心业务逻辑
│   ├── task_engine.py       # 任务执行引擎
│   ├── workflow_parser.py   # 工作流解析器
│   ├── step_executor.py     # 步骤执行器
│   └── state_manager.py     # 状态管理器
├── models/                  # 数据模型
│   ├── database.py          # 数据库连接
│   └── task.py              # 任务相关模型
├── services/                # 业务服务
│   ├── task_service.py      # 任务服务
│   ├── database_workflow_service.py  # 工作流数据库服务
│   └── notification_service.py       # 通知服务
├── steps/                   # 步骤实现
│   └── topup_step_v1/       # Topup标准工作流步骤
│       ├── step0_get_available_dates.py    # 获取可用日期
│       ├── step1_1_first_job_submission.py # 作业提交
│       ├── step1_2_move_files.py           # 文件移动
│       ├── step1_3_ist_analysis.py         # IST分析
│       └── step1_4_merge_images.py         # 图像合并
├── workflows/               # 工作流配置
│   ├── topup_standard.json  # 标准工作流定义
│   ├── topup_standard_steps.json  # 标准工作流步骤
│   └── get_available_dates.json   # 获取日期工作流
├── uploads/                 # 上传文件目录
├── downloads/               # 下载文件目录
├── logs/                    # 日志目录
├── app.py                   # Flask应用主文件
├── run.py                   # 启动脚本
├── config.py                # 配置文件
├── topup_ssh.py             # SSH连接管理
├── init_workflows.py        # 工作流初始化脚本
├── reset_workflows.py       # 工作流重置脚本
├── setup.sh                 # 环境设置脚本
├── requirements.txt         # 依赖列表
├── database_schema.sql      # 数据库架构
└── README.md                # 本文件
```

## 快速开始

### 1. 环境要求

- Python 3.8+
- SQLite 3
- SSH 访问权限（lxlogin.ihep.ac.cn 和 beslogin）

### 2. 安装依赖

```bash
cd HttpBackend
pip install -r requirements.txt
```

或使用提供的设置脚本：

```bash
chmod +x setup.sh
./setup.sh
```

### 3. 配置环境变量

复制环境变量示例文件并修改：

```bash
cp .env.example .env
```

编辑 `.env` 文件，设置必要的配置项：

```env
# Flask配置
SECRET_KEY=your-secret-key
DEBUG=False

# SSH配置
SSH_PASS_LXLOGIN=your_lxlogin_password
SSH_PASS_BESLOGIN=your_beslogin_password

# 任务配置
MAX_PARALLEL_TASKS=3
DEFAULT_TIMEOUT_MINUTES=30
MAX_RETRY_ATTEMPTS=3

# 通知配置
ENABLE_NOTIFICATIONS=true
WEBSOCKET_ENABLED=true
```

### 4. 初始化数据库和工作流

```bash
# 初始化工作流数据
python init_workflows.py

# 如需重置工作流
python reset_workflows.py
```

### 5. 启动服务

```bash
python run.py
```

服务将在 `http://0.0.0.0:5000` 启动，WebSocket 服务同时可用。

## API 接口文档

### 健康检查

```bash
GET /api/health
```

返回服务健康状态和版本信息。

### 任务管理

#### 创建任务

```bash
POST /api/tasks
Content-Type: application/json

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
```

#### 获取任务列表

```bash
GET /api/tasks?user_id=user123&status=running&limit=10&offset=0
```

参数：
- `user_id` (必需): 用户ID
- `status` (可选): 任务状态 (pending/running/completed/failed/cancelled)
- `limit` (可选): 返回数量，默认10
- `offset` (可选): 偏移量，默认0

#### 获取任务详情

```bash
GET /api/tasks/{task_id}
```

#### 获取任务进度

```bash
GET /api/tasks/{task_id}/progress
```

#### 启动任务

```bash
POST /api/tasks/{task_id}/start
```

#### 暂停任务

```bash
POST /api/tasks/{task_id}/pause
```

#### 恢复任务

```bash
POST /api/tasks/{task_id}/resume
```

#### 取消任务

```bash
POST /api/tasks/{task_id}/cancel
```

#### 获取任务日志

```bash
GET /api/tasks/{task_id}/logs?level=error&limit=100
```

参数：
- `level` (可选): 日志级别 (info/warning/error/debug)
- `limit` (可选): 返回数量，默认100

### 工作流管理

#### 获取工作流列表

```bash
GET /api/workflows
```

#### 获取工作流详情

```bash
GET /api/workflows/{workflow_name}
```

返回工作流的完整配置，包括步骤定义、执行配置和参数配置。

#### 验证工作流参数

```bash
POST /api/workflows/{workflow_name}/validate
Content-Type: application/json

{
    "parameters": {
        "date_param": "250624",
        "submit_job": true
    }
}
```

### 执行记录

```bash
GET /api/executions?task_id={task_id}
```

获取任务的步骤执行记录。

### 日志查询

```bash
GET /api/logs?task_id={task_id}&level=error
```

查询系统日志。

### 文件下载

#### 下载文件

```bash
GET /api/downloads/{filename}
```

#### 下载任务相关文件

```bash
GET /api/downloads/task/{task_id}?file_type=merged_pdf&date=250519
```

参数：
- `file_type` (必需): 文件类型 (merged_pdf/log/output)
- `date` (可选): 日期参数
- `step_id` (可选): 步骤ID

#### 列出可下载文件

```bash
GET /api/downloads/list?task_id=xxx&file_type=pdf
```

#### 检查文件是否存在

```bash
GET /api/downloads/check/{filename}
```

### WebSocket 实时通信

连接到 WebSocket 服务器以接收实时任务更新：

```javascript
const socket = io('http://localhost:5000');

// 连接成功
socket.on('connected', (data) => {
    console.log(data.message);
});

// 订阅任务更新
socket.emit('subscribe_task', { task_id: 123 });

// 接收任务状态更新
socket.on('task_status', (data) => {
    console.log('Status:', data.status, data.message);
});

// 接收任务进度更新
socket.on('task_progress', (data) => {
    console.log('Progress:', data.progress);
});
```

## 工作流配置

系统支持基于 JSON 的工作流配置，工作流定义包含：

- 工作流元信息（名称、描述、版本）
- 步骤定义（步骤顺序、依赖关系、执行函数）
- 执行配置（超时、重试策略）
- 参数配置（必需参数、可选参数、默认值）

### 标准工作流

项目包含以下预定义工作流：

1. **topup_standard_workflow** - Topup 标准数据处理流程
   - Step 0: 获取可用日期
   - Step 1.1: 作业提交
   - Step 1.2: 文件移动
   - Step 1.3: IST 分析
   - Step 1.4: 图像合并

2. **get_available_dates** - 获取可用日期工作流

工作流配置文件位于 [workflows/](workflows/) 目录。

## 数据库架构

系统使用 SQLite 数据库，包含以下主要表：

- `workflows` - 工作流定义
- `workflow_steps` - 工作流步骤定义
- `tasks` - 任务实例
- `task_executions` - 任务步骤执行记录
- `step_outputs` - 任务步骤输出
- `task_logs` - 任务日志
- `task_parameters` - 任务参数
- `user_preferences` - 用户配置

详细的数据库架构见 [database_schema.sql](database_schema.sql)。

## 配置说明

主要配置项（在 [config.py](config.py) 中定义）：

### Flask 配置
- `SECRET_KEY` - Flask 密钥
- `DEBUG` - 调试模式
- `MAX_CONTENT_LENGTH` - 最大请求大小（16MB）

### 数据库配置
- `DATABASE_URL` - 数据库连接字符串（默认：SQLite）

### 任务执行配置
- `MAX_PARALLEL_TASKS` - 最大并行任务数（默认：3）
- `DEFAULT_TIMEOUT_MINUTES` - 默认超时时间（默认：30分钟）
- `MAX_RETRY_ATTEMPTS` - 最大重试次数（默认：3）
- `RETRY_DELAY_SECONDS` - 重试延迟（默认：60秒）
- `STEP_CHECK_INTERVAL` - 步骤检查间隔（默认：5秒）

### SSH 配置
- `SSH_PASS_LXLOGIN` - lxlogin.ihep.ac.cn 密码
- `SSH_PASS_BESLOGIN` - beslogin 密码

### 通知配置
- `ENABLE_NOTIFICATIONS` - 启用通知（默认：true）
- `WEBSOCKET_ENABLED` - 启用 WebSocket（默认：true）

### 文件配置
- `UPLOAD_CONFIG` - 上传目录和限制
- `DOWNLOAD_CONFIG` - 下载目录和限制

## 日志

日志文件位置：[logs/topup_api.log](logs/topup_api.log)

日志级别：INFO, WARNING, ERROR, DEBUG

日志配置支持：
- 文件日志（自动轮转，最大 10MB，保留 5 个备份）
- 控制台日志（彩色输出）

## 开发指南

### 添加新步骤

1. 在 [steps/topup_step_v1/](steps/topup_step_v1/) 目录创建新的步骤文件
2. 实现步骤函数，遵循以下模板：

```python
def step_function_name(ssh: TopupSSH, **kwargs) -> Dict[str, Any]:
    """
    步骤描述

    Args:
        ssh: SSH连接实例
        **kwargs: 步骤参数

    Returns:
        执行结果字典
    """
    try:
        # 执行步骤逻辑

        return {
            'success': True,
            'message': '步骤执行成功',
            'data': {}  # 其他返回数据
        }
    except Exception as e:
        return {
            'success': False,
            'message': str(e),
            'error': str(e)
        }
```

3. 在工作流配置文件中添加步骤定义
4. 更新 [steps/__init__.py](steps/__init__.py) 导出新步骤

### 添加新工作流

1. 在 [workflows/](workflows/) 目录创建新的 JSON 配置文件
2. 定义工作流结构：

```json
{
    "workflow": {
        "name": "my_workflow",
        "description": "工作流描述",
        "version": "1.0.0"
    },
    "steps": [
        {
            "step_id": "step1",
            "name": "步骤名称",
            "function": "module.function_name",
            "description": "步骤描述"
        }
    ],
    "execution_config": {
        "timeout_minutes": 30,
        "max_retries": 3
    },
    "parameters_config": {
        "required": ["param1"],
        "optional": ["param2"]
    }
}
```

3. 运行 `python init_workflows.py` 初始化到数据库

## 问题排查

### 数据库连接问题

检查 `DATABASE_URL` 配置是否正确，确保数据库文件有读写权限。

### SSH 连接问题

1. 检查 SSH 密码环境变量是否正确设置
2. 验证网络连接到 lxlogin.ihep.ac.cn
3. 检查 SSH 用户名和端口配置

### 任务执行失败

1. 查看 [logs/topup_api.log](logs/topup_api.log) 获取详细错误信息
2. 检查任务日志：`GET /api/tasks/{task_id}/logs`
3. 验证工作流参数是否正确

### WebSocket 连接问题

1. 确保 `WEBSOCKET_ENABLED=true`
2. 检查防火墙设置
3. 验证客户端 Socket.IO 版本兼容性

## 技术栈

- **Web 框架**: Flask 3.x
- **数据库**: SQLite + SQLAlchemy
- **实时通信**: Flask-SocketIO
- **SSH 连接**: Paramiko
- **跨域支持**: Flask-CORS
- **环境变量**: python-dotenv

## 项目状态

### 已完成功能

- ✅ 项目框架搭建
- ✅ 数据库模型和架构
- ✅ 核心执行引擎
- ✅ API 路由和接口
- ✅ WebSocket 实时通信
- ✅ SSH 远程执行
- ✅ 文件上传下载
- ✅ 日志记录和查询
- ✅ 工作流步骤实现（5个步骤）

### 待优化功能

- ⏳ 完善错误处理和异常恢复
- ⏳ 添加单元测试和集成测试
- ⏳ 生成 Swagger/OpenAPI 文档
- ⏳ 添加用户认证和权限管理
- ⏳ 性能优化和监控
- ⏳ Docker 容器化部署

## 贡献

欢迎提交问题和改进建议。

## 许可证

本项目仅供内部使用。