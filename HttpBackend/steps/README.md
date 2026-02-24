# Step 函数开发指南

本指南详细说明了如何在 HttpBackend 项目中编写符合要求的步骤函数。

## 目录
- [核心架构](#核心架构)
- [执行流程](#执行流程)
- [Step 函数编写规范](#step-函数编写规范)
- [常用代码模式](#常用代码模式)
- [完整示例](#完整示例)
- [检查清单](#检查清单)
- [参考实现](#参考实现)

## 核心架构

### 项目结构
```
HttpBackend/
├── core/                 # 核心执行引擎
│   ├── task_engine.py   # 任务编排器
│   ├── step_executor.py # 步骤执行器
│   ├── workflow_parser.py # 工作流解析器
│   └── state_manager.py # 状态管理器
├── steps/               # 步骤实现 (本目录)
├── workflows/           # 工作流配置
│   └── topup_standard.json
├── models/              # 数据模型
├── services/            # 业务逻辑层
└── api/                # HTTP API 层
```

### 核心模块职责

| 文件 | 职责 |
|------|------|
| [task_engine.py](../core/task_engine.py) | 主任务编排器，管理任务生命周期、线程池、SSH连接 |
| [step_executor.py](../core/step_executor.py) | 步骤执行器，动态加载和执行单个步骤 |
| [workflow_parser.py](../core/workflow_parser.py) | 工作流配置解析器 |
| [state_manager.py](../core/state_manager.py) | 任务和步骤状态管理器 |

## 执行流程

```
用户请求 → API路由 → TaskService → TaskEngine → WorkflowParser
                                      ↓
                                加载步骤配置
                                      ↓
                                StepExecutor
                                      ↓
                            动态导入 steps/{module_name}.py
                                      ↓
                              调用步骤函数并记录结果
```

1. **TaskEngine** 通过线程池管理任务执行
2. **WorkflowParser** 解析 JSON 配置文件
3. **StepExecutor** 动态加载步骤模块
4. 每个步骤函数获得 TopupSSH 实例执行远程命令
5. 结果记录到数据库并更新状态

## Step 函数编写规范

### 1. 函数签名模板

```python
from typing import Dict, Any, Optional
from topup_ssh import TopupSSH
import config

def step_xxx(
    ssh: TopupSSH,
    date: Optional[str] = None,
    submit_job: bool = True,
    max_wait_minutes: Optional[int] = None
) -> Dict[str, Any]:
    """
    步骤描述 - 简要说明此步骤的功能

    Args:
        ssh: TopupSSH 实例，用于执行远程命令
        date: 日期参数（从任务参数映射而来）
        submit_job: 是否提交作业
        max_wait_minutes: 最大等待分钟数

    Returns:
        包含以下键的字典：
            - success (bool, 必需): 是否成功
            - message (str, 必需): 人类可读的消息
            - error (str, 可选): 失败时的错误详情
            - requires_manual_intervention (bool, 可选): 是否需要人工干预
    """
```

### 2. 返回字典结构

**成功情况：**
```python
{
    'success': True,
    'message': '步骤完成描述',
    'step_name': 'step1_1',          # 推荐
    'date': '250624',                # 步骤特定数据
    'output': '命令输出',             # 可选
    'output_summary': '摘要'          # 可选
}
```

**失败情况：**
```python
{
    'success': False,
    'message': '步骤失败描述',
    'error': '详细错误信息',
    'requires_manual_intervention': False  # 如需暂停工作流
}
```

### 3. 工作流配置中的映射

在 [workflows/topup_standard.json](../workflows/topup_standard.json) 中，步骤配置如下：

```json
{
  "id": "step1_1",
  "order": 1,
  "module": "step1_1_first_job_submission",
  "function": "step1_1_first_job_submission",
  "parameters": {
    "date": "date_param",
    "submit_job": "submit_job"
  },
  "timeout_minutes": 25,
  "retry_count": 3
}
```

这会将：
- `date_param` 任务参数映射到 `date` 参数
- `submit_job` 任务参数映射到 `submit_job` 参数

## 常用代码模式

### 1. SSH 命令执行

```python
# 简单命令
result = ssh.execute_command(f"cd {directory} && ls -la")
if not result['success']:
    return {
        'success': False,
        'message': '执行失败',
        'error': result.get('error', '未知错误')
    }

# 解析输出
filenames = result['output'].strip().split('\n')
```

### 2. 交互式命令（带完成标记）

```python
result = ssh.execute_interactive_command(
    f"cd {dir} && source {script} && ./genJob.sh {date}",
    completion_marker="DONE"
)
```

### 3. 文件检查

```python
# 检查目录/文件是否存在
check_result = ssh.execute_command(f"ls -d {date_dir} 2>/dev/null")
if not check_result['success'] or not check_result['output'].strip():
    return {
        'success': False,
        'message': f'目录不存在: {date_dir}'
    }
```

### 4. 超时轮询监控

```python
import time

max_wait_seconds = (max_wait_minutes or config.DEFAULT_MAX_WAIT_MINUTES) * 60
elapsed_time = 0
check_interval = config.CHECK_INTERVAL_SECONDS

while elapsed_time < max_wait_seconds:
    # 检查完成条件
    result = ssh.execute_command(f"ls {expected_file} 2>/dev/null")
    if result['success'] and result['output'].strip():
        break

    time.sleep(check_interval)
    elapsed_time += check_interval
else:
    return {
        'success': False,
        'message': f'超时: 等待超过 {max_wait_minutes} 分钟'
    }
```

### 5. 正则表达式匹配

```python
import re

# 解析文件名
text = "rec123_1.txt\nrec456_1.txt"
filenames = text.split('\n')

for filename in filenames:
    match = re.match(r'rec(\d+)_1\.txt', filename)
    if match:
        job_id = match.group(1)  # '123', '456'
```

### 6. 进度保存与加载

```python
# 保存进度供后续步骤使用
config.save_step_progress('1.1', {'date': selected_date})

# 在后续步骤中加载
progress = config.load_step_progress()
previous_date = progress.get('date')
```

### 7. 异常处理与检查

```python
# 检查异常情况
check_anomaly_cmd = f"cd {date_dir} && ls Interval_run0.png 2>/dev/null"
anomaly_result = ssh.execute_command(check_anomaly_cmd)
if anomaly_result['success'] and anomaly_result['output'].strip():
    return {
        'success': False,
        'message': '检测到异常',
        'requires_manual_intervention': True
    }
```

### 8. 并行文件处理

```python
# 处理多个匹配的文件
file_pattern = f"cd {dir} && ls rec*1.txt"
result = ssh.execute_command(file_pattern)

if result['success']:
    files = [f.strip() for f in result['output'].split('\n') if f.strip()]
    processed_files = []
    for filename in files:
        # 处理每个文件
        file_result = ssh.execute_command(f"cat {dir}/{filename}")
        if file_result['success']:
            processed_files.append(filename)

    return {
        'success': True,
        'message': f'处理了 {len(processed_files)} 个文件',
        'processed_count': len(processed_files)
    }
```

## 完整示例

### 示例 1：作业提交与等待

```python
from typing import Dict, Any, Optional
from topup_ssh import TopupSSH
import config
import time

def step1_1_first_job_submission(
    ssh: TopupSSH,
    date: Optional[str] = None,
    submit_job: bool = True,
    max_wait_minutes: Optional[int] = None
) -> Dict[str, Any]:
    """
    提交第一个作业并等待完成
    """
    if not date:
        return {
            'success': False,
            'message': '缺少日期参数',
            'error': 'date 参数是必需的'
        }

    if max_wait_minutes is None:
        max_wait_minutes = config.DEFAULT_MAX_WAIT_MINUTES

    # 1. 检查工作目录
    work_dir = f"/path/to/work/{date}"
    check_result = ssh.execute_command(f"ls -d {work_dir} 2>/dev/null")
    if not check_result['success']:
        return {
            'success': False,
            'message': f'工作目录不存在: {work_dir}',
            'error': check_result.get('error')
        }

    # 2. 提交作业
    if submit_job:
        result = ssh.execute_interactive_command(
            f"cd {work_dir} && ./submit.sh",
            completion_marker="Job submitted"
        )
        if not result['success']:
            return {
                'success': False,
                'message': '作业提交失败',
                'error': result.get('error')
            }

    # 3. 等待完成
    max_wait_seconds = max_wait_minutes * 60
    elapsed_time = 0

    while elapsed_time < max_wait_seconds:
        result = ssh.execute_command(f"ls {work_dir}/DONE 2>/dev/null")
        if result['success'] and result['output'].strip():
            # 保存进度
            config.save_step_progress('1.1', {'date': date})

            return {
                'success': True,
                'message': f'作业完成，日期: {date}',
                'step_name': 'step1_1',
                'date': date
            }

        time.sleep(config.CHECK_INTERVAL_SECONDS)
        elapsed_time += config.CHECK_INTERVAL_SECONDS

    return {
        'success': False,
        'message': f'等待超时（{max_wait_minutes}分钟）',
        'step_name': 'step1_1'
    }
```

### 示例 2：文件合并处理

```python
from typing import Dict, Any, Optional
from topup_ssh import TopupSSH
import config
import re
import time

def step6_2_merge_images(
    ssh: TopupSSH,
    date: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    合并图像文件
    """
    if not date:
        return {
            'success': False,
            'message': '缺少日期参数',
            'error': 'date 参数是必需的'
        }

    dir_name = f"/path/to/merged_{date}"
    command = f"python /path/to/merge.py {dir_name}"

    # 执行合并命令
    result = ssh.execute_command(command)

    if result['success']:
        # 检查输出文件
        check_result = ssh.execute_command(f"ls {dir_name}/*.png 2>/dev/null")

        if check_result['success'] and check_result['output'].strip():
            # 提取文件信息
            png_files = re.findall(r'\w+\.png', check_result['output'])

            return {
                'success': True,
                'message': f'成功合并 {len(png_files)} 个图像文件',
                'step_name': 'step6_2',
                'date': date,
                'output_summary': f'合并了 {len(png_files)} 个图像',
                'output': result['output']
            }
        else:
            return {
                'success': True,
                'message': '合并命令执行成功，但未找到输出文件',
                'step_name': 'step6_2'
            }
    else:
        return {
            'success': False,
            'message': '合并失败',
            'error': result.get('error'),
            'step_name': 'step6_2'
        }
```

## 检查清单

在编写步骤函数时，请确保检查以下项目：

- [ ] 函数接受 `ssh: TopupSSH` 作为第一个参数
- [ ] 返回字典包含 `success` 和 `message` 键
- [ ] 可选参数有合理的默认值
- [ ] 每次 SSH 调用后检查 `result['success']`
- [ ] 长时间操作有超时处理
- [ ] 使用 `print` 输出进度（会被捕获到日志）
- [ ] 失败时返回结构化错误信息
- [ ] 使用 `config` 模块获取配置
- [ ] 检查文件存在性和异常情况
- [ ] 函数名与工作流配置中的 `module` 和 `function` 匹配
- [ ] 添加适当的文档字符串
- [ ] 处理所有可能的错误情况
- [ ] 考虑返回有用的元数据供后续步骤使用

## 参考实现

### 最佳实践

1. **参数验证**：验证所有必需参数
2. **错误处理**：对所有远程操作进行错误检查
3. **超时控制**：设置合理的超时时间
4. **进度反馈**：使用 print 输出进度信息
5. **状态保存**：在必要时保存中间状态
6. **资源清理**：确保 SSH 连接等资源正确清理
7. **日志记录**：所有重要操作都有相应的日志输出

### 常见问题

1. **模块导入错误**
   - 确保 Python 文件名与工作流配置中的 `module` 一致
   - 模块文件必须在 steps 目录下

2. **SSH 连接超时**
   - 检查 SSH 连接是否活跃
   - 使用合适的超时参数

3. **参数映射错误**
   - 检查工作流配置中的参数映射是否正确
   - 确保任务参数与步骤参数名匹配

4. **状态不一致**
   - 及时保存进度到 config
   - 避免长时间运行的状态不一致

---

*本指南将随着项目发展持续更新。如有问题，请参考现有的步骤实现或与开发团队讨论。*