# Topup HTTP API

基于Flask的Topup数据处理任务管理系统，提供RESTful API接口来管理和执行数据处理工作流。

## 项目结构

```
HttpBackend/
├── api/                      # API接口层
│   ├── routes/              # 路由定义
│   │   ├── tasks.py         # 任务管理接口
│   │   ├── workflows.py     # 工作流管理接口
│   │   ├── executions.py    # 执行记录接口
│   │   └── logs.py          # 日志查询接口
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
│   └── task_service.py      # 任务服务
├── steps/                   # 步骤实现（待添加）
├── workflows/               # 工作流配置
│   └── topup_standard.json  # 标准工作流
├── logs/                    # 日志目录
├── app.py                   # Flask应用主文件
├── run.py                   # 启动脚本
├── config.py                # 配置文件
├── requirements.txt         # 依赖列表
└── README.md                # 本文件
```

## 快速开始

### 1. 安装依赖

```bash
cd HttpBackend
pip install -r requirements.txt
```

### 2. 配置环境变量

复制环境变量示例文件并修改：

```bash
cp .env.example .env
```

编辑 `.env` 文件，设置必要的配置项：

```env
SECRET_KEY=your-secret-key
SSH_PASS_LXLOGIN=your_lxlogin_password
SSH_PASS_BESLOGIN=your_beslogin_password
```

### 3. 初始化数据库

数据库会在首次运行时自动创建。

### 4. 启动服务

```bash
python run.py
```

服务将在 `http://0.0.0.0:5000` 启动。

## API接口

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

#### 获取任务详情

```bash
GET /api/tasks/{task_id}
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

### 工作流管理

#### 获取工作流列表

```bash
GET /api/workflows
```

#### 获取工作流详情

```bash
GET /api/workflows/{workflow_name}
```

## 开发计划

### 当前状态

- ✅ 项目框架搭建完成
- ✅ 数据库模型定义完成
- ✅ 核心执行引擎实现完成
- ✅ API路由框架搭建完成
- ⏳ 步骤具体实现待完成

### 待实现功能

1. **步骤实现** - 在 `steps/` 目录下实现各个步骤
2. **数据库初始化** - 添加默认工作流数据
3. **完善错误处理** - 增强错误处理和日志记录
4. **添加单元测试** - 编写测试用例
5. **API文档** - 生成Swagger文档
6. **WebSocket实时更新** - 实现任务进度实时推送

## 步骤实现指南

每个步骤需要：

1. 在 `steps/` 目录下创建对应的Python文件
2. 实现步骤函数，接受SSH连接和参数
3. 返回标准格式的执行结果

### 步骤函数模板

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
            # 其他返回数据
        }
    except Exception as e:
        return {
            'success': False,
            'message': str(e),
            'error': str(e)
        }
```

## 数据库架构

数据库使用SQLite，包含以下主要表：

- `workflows` - 工作流定义
- `workflow_steps` - 工作流步骤定义
- `tasks` - 任务实例
- `task_executions` - 任务步骤执行记录
- `step_outputs` - 任务步骤输出
- `task_logs` - 任务日志
- `task_parameters` - 任务参数
- `user_preferences` - 用户配置

详细的数据库架构见 `database_schema.sql`。

## 配置说明

主要配置项：

- `DATABASE_URL` - 数据库连接字符串
- `MAX_PARALLEL_TASKS` - 最大并行任务数
- `DEFAULT_TIMEOUT_MINUTES` - 默认超时时间
- `MAX_RETRY_ATTEMPTS` - 最大重试次数
- `SSH_PASS_LXLOGIN` - 跳板机密码
- `SSH_PASS_BESLOGIN` - 目标服务器密码

## 日志

日志文件位置：`logs/topup_api.log`

日志级别：INFO, WARNING, ERROR, DEBUG

## 问题排查

### 数据库连接问题

检查 `DATABASE_URL` 配置是否正确。

### SSH连接问题

检查SSH密码环境变量是否正确设置。

### 任务执行失败

查看日志文件获取详细错误信息。

## 下一步

1. 实现具体的步骤函数
2. 测试各个步骤的执行
3. 完善错误处理
4. 添加监控和告警
5. 编写API文档

## 贡献

欢迎提交问题和改进建议。