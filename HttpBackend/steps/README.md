# Step 函数开发指南

本指南详细说明了如何在 HttpBackend 项目中编写符合要求的步骤函数。

## 目录
- [核心架构](#核心架构)
- [执行流程](#执行流程)
- [Step 函数编写规范](#step-函数编写规范)
- [自动参数注入](#自动参数注入)
- [返回值规范](#返回值规范)
- [常用代码模式](#常用代码模式)
- [完整示例](#完整示例)
- [检查清单](#检查清单)

## 核心架构

### 项目结构
```
HttpBackend/
├── core/                 # 核心执行引擎
│   ├── task_engine.py   # 任务编排器
│   ├── step_executor.py # 步骤执行器
│   └── workflow_parser.py # 工作流解析器
├── steps/               # 步骤实现 (本目录)
│   └── topup_step_v1/   # 工作流版本目录
│       ├── step0_get_available_dates.py
│       ├── step1_1_first_job_submission.py
│       └── ...
├── workflows/           # 工作流配置
│   └── topup_standard.json
├── models/              # 数据模型
│   └── task.py         # 任务、执行记录等模型
└── api/                # HTTP API 层
```

### 核心模块职责

| 文件 | 职责 |
|------|------|
| [task_engine.py](../core/task_engine.py) | 主任务编排器，管理任务生命周期、线程池、SSH连接 |
| [step_executor.py](../core/step_executor.py) | 步骤执行器，动态加载和执行单个步骤，捕获返回值 |
| [workflow_parser.py](../core/workflow_parser.py) | 工作流配置解析器 |

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
                                      ↓
                            保存到数据库 (TaskExecution)
```

1. **TaskEngine** 通过线程池管理任务执行
2. **WorkflowParser** 解析 JSON 配置文件
3. **StepExecutor** 动态加载步骤模块并注入参数
4. 每个步骤函数获得 TopupSSH 实例执行远程命令
5. 返回值被完整记录到数据库的 `task_executions` 表

## Step 函数编写规范

### 1. 函数签名模板

```python
from typing import Dict, Any, Optional
from topup_ssh import TopupSSH

def step_xxx(
    ssh: TopupSSH,
    round: str,
    date_param: Optional[str] = None,
    task_id: Optional[int] = None,
    user_id: Optional[str] = None,
    submit_job: bool = True,
    max_wait_minutes: int = 25,
    local_file_dir: Optional[str] = None,
    step_order: Optional[int] = None,
) -> Dict[str, Any]:
    """
    步骤描述 - 简要说明此步骤的功能

    Args:
        ssh: TopupSSH 实例，用于执行远程命令（必需，自动注入）
        round: 轮次标识符（必需，从工作流配置获取）
        date_param: 任务的日期参数（自动注入）
        task_id: 任务ID（自动注入）
        user_id: 用户ID（自动注入）
        submit_job: 是否提交作业（自动注入，默认True）
        max_wait_minutes: 最大等待分钟数（自动注入，默认25）
        local_file_dir: 本地文件下载目录（自动注入，格式：downloads/{task_id}_{step_order}）
        step_order: 当前步骤序号（自动注入）

    Returns:
        包含以下键的字典：
            - success (bool, 必需): 是否成功
            - message (str, 必需): 人类可读的消息
            - console_logs (list, 推荐): 执行过程日志列表
            - error (str, 可选): 失败时的错误详情
            - 其他业务数据: 如 all_dates, processed_dates 等
    """
    console_logs = []
    console_logs.append("步骤开始执行...")

    # 你的业务逻辑

    return {
        'success': True,
        'message': '步骤执行成功',
        'console_logs': console_logs,
        'step_name': 'step_xxx',
        # 其他业务数据
    }
```

### 2. 重要说明

**不要从 config 文件读取路径等信息**，所有配置通过参数传递：
- ❌ 错误：`data_dir = config.DATA_DIR`
- ✅ 正确：使用函数参数或从 `round` 参数构建路径

**不要硬编码路径**，使用参数动态构建：
```python
# 从 round 参数构建路径
data_dir = f"/data/topup/{round}/data"
inj_sig_time_cal_dir = f"/data/topup/{round}/inj_sig_time_cal"
```

**只声明你需要的参数**：
- StepExecutor 会校验函数签名，只传递函数声明的参数
- ❌ 不要使用 `**kwargs` 接收未使用的参数
- ✅ 只在函数签名中声明你实际需要的参数

## 自动参数注入

StepExecutor 会自动为你的函数注入以下参数（只要函数签名中声明了这些参数）：

### 1. 必需参数（总是注入）
```python
ssh: TopupSSH  # SSH连接实例
```

### 2. 任务相关参数（自动注入）
```python
date_param: str    # 任务的日期参数，Column(String(10))
task_id: int       # 任务ID
user_id: str       # 用户ID
```

### 3. 常用控制参数（自动注入，有默认值）
```python
submit_job: bool = True           # 是否提交作业
max_wait_minutes: int = 25        # 最大等待时间（分钟）
local_file_dir: str               # 本地文件目录，格式：downloads/{task_id}_{step_order}
step_order: int                   # 当前步骤序号
```

### 4. 工作流配置参数
在 `workflows/topup_standard.json` 中定义的参数也会被传递：
此处是一个映射关系，如"include_processed": "step_0_include_processed",step函数应该使用的参数名为"include_processed"， "step_0_include_processed"用于方便管理工作流的所有输入参数
```json
{
  "id": "step0",
  "parameters": {
    "include_processed": "step_0_include_processed",
    "sort_order": "step_0_sort_order",
    "round": "round"
  }
}
```

### 5. 参数使用示例

```python
def step1_example(
    ssh: TopupSSH,           # 必需
    round: str,              # 从工作流配置
    date_param: str,         # 自动注入
    task_id: int,            # 自动注入
    submit_job: bool = True, # 自动注入
    max_wait_minutes: int = 25,  # 自动注入
) -> Dict[str, Any]:
    """只声明你需要的参数，StepExecutor会自动过滤和传递"""

    # 使用参数
    work_dir = f"/data/topup/{round}/work/{date_param}"

    if submit_job:
        # 提交作业逻辑
        pass
```

## 返回值规范

### 1. 返回字典结构

Step函数的返回值会被分类存储到数据库：

| 返回值字段 | 存储位置 | 说明 |
|-----------|---------|------|
| `success` | `execution.status` | 转换为 'success' 或 'failed' |
| `message` | `execution.output_summary` | 人类可读的摘要 |
| `error` | `execution.error_details` | 错误详情 |
| `console_logs` | `execution.console_output` | 执行日志（list转为文本） |
| **其他所有字段** | `execution.step_result_json` | 完整业务数据（JSON格式） |

### 2. 成功返回示例

```python
return {
    'success': True,
    'message': '成功获取日期信息：共15个，已处理8个，未处理7个',
    'console_logs': [
        "步骤0：获取所有可用数据目录的日期列表",
        "找到 15 个可用日期目录",
        "找到 8 个已处理日期目录",
        "统计信息: 总日期数: 15"
    ],
    'step_name': 'step0',
    # 以下字段会被保存到 step_result_json
    'all_dates': ['250601', '250602', ...],
    'processed_dates': ['250601', '250602', ...],
    'unprocessed_dates': ['250608', '250609', ...],
    'total_count': 15,
    'processed_count': 8,
    'unprocessed_count': 7,
    'sort_order': 'asc'
}
```

### 3. 失败返回示例

```python
return {
    'success': False,
    'message': '获取日期列表失败',
    'error': '数据目录不存在: /data/topup/round2.0/data',
    'console_logs': [
        "步骤0：获取所有可用数据目录的日期列表",
        "检查数据目录...",
        "错误: 目录不存在"
    ],
    'step_name': 'step0'
}
```

### 4. console_logs 使用建议

使用列表收集日志，而不是 print：

```python
def step_example(ssh: TopupSSH, **kwargs) -> Dict[str, Any]:
    console_logs = []

    console_logs.append("="*60)
    console_logs.append("步骤开始执行")
    console_logs.append("="*60)

    # 执行操作
    result = ssh.execute_command("ls /data")
    console_logs.append(f"执行命令: ls /data")
    console_logs.append(f"命令输出: {result['output'][:100]}")

    if result['success']:
        console_logs.append("✓ 命令执行成功")
    else:
        console_logs.append("✗ 命令执行失败")

    return {
        'success': result['success'],
        'message': '步骤完成',
        'console_logs': console_logs
    }
```

## 常用代码模式

### 1. SSH 命令执行

```python
# 简单命令
result = ssh.execute_command(f"ls -1 {directory}")
if not result['success']:
    return {
        'success': False,
        'message': '执行失败',
        'error': result.get('error', '未知错误'),
        'console_logs': console_logs
    }

# 解析输出
lines = [line.strip() for line in result['output'].split('\n') if line.strip()]
```

### 2. 交互式命令（带完成标记）

```python
result = ssh.execute_interactive_command(
    f"cd {work_dir} && source setup.sh && ./genJob.sh {date_param}",
    completion_marker="DONE",
    timeout=300
)
```

### 3. 文件/目录检查

```python
# 检查目录是否存在
check_result = ssh.execute_command(f"ls -d {date_dir} 2>/dev/null")
if not check_result['success'] or not check_result['output'].strip():
    console_logs.append(f"目录不存在: {date_dir}")
    return {
        'success': False,
        'message': f'目录不存在: {date_dir}',
        'console_logs': console_logs
    }
```

### 4. 超时轮询监控

```python
import time

max_wait_seconds = max_wait_minutes * 60
elapsed_time = 0
check_interval = 10  # 10秒检查一次

console_logs.append(f"开始等待，最大等待时间: {max_wait_minutes} 分钟")

while elapsed_time < max_wait_seconds:
    # 检查完成条件
    result = ssh.execute_command(f"ls {expected_file} 2>/dev/null")
    if result['success'] and result['output'].strip():
        console_logs.append(f"✓ 文件已生成: {expected_file}")
        break

    time.sleep(check_interval)
    elapsed_time += check_interval
    console_logs.append(f"等待中... ({elapsed_time}/{max_wait_seconds}秒)")
else:
    console_logs.append(f"✗ 超时: 等待超过 {max_wait_minutes} 分钟")
    return {
        'success': False,
        'message': f'超时: 等待超过 {max_wait_minutes} 分钟',
        'console_logs': console_logs
    }
```

### 5. 正则表达式匹配

```python
import re

# 匹配6位数字的日期目录
dates = [
    line.strip() for line in output.split('\n')
    if line.strip() and re.match(r'^\d{6}$', line.strip())
]

# 提取作业ID
match = re.match(r'rec(\d+)_1\.txt', filename)
if match:
    job_id = match.group(1)
```

### 6. 辅助函数模式

```python
def _get_available_dates(ssh: TopupSSH, data_dir: str, console_logs: list) -> Dict[str, Any]:
    """
    辅助函数：获取可用日期列表

    注意：辅助函数也接收 console_logs 参数，用于记录日志
    """
    console_logs.append(f"检查数据目录: {data_dir}")

    result = ssh.execute_command(f"ls -1 {data_dir}")

    if not result['success']:
        return {
            'success': False,
            'message': '获取目录列表失败',
            'error': result.get('error', '未知错误')
        }

    dates = [
        line.strip() for line in result['output'].split('\n')
        if line.strip() and re.match(r'^\d{6}$', line.strip())
    ]

    console_logs.append(f"找到 {len(dates)} 个日期目录")

    return {
        'success': True,
        'dates': dates
    }

# 在主函数中调用
def step_main(ssh: TopupSSH, round: str, **kwargs) -> Dict[str, Any]:
    console_logs = []

    data_dir = f"/data/topup/{round}/data"
    result = _get_available_dates(ssh, data_dir, console_logs)

    if not result['success']:
        return {
            'success': False,
            'message': result['message'],
            'error': result.get('error'),
            'console_logs': console_logs
        }

    dates = result['dates']
    # 继续处理...
```

## 完整示例

### 示例：step0_get_available_dates.py

参考 [step0_get_available_dates.py](topup_step_v1/step0_get_available_dates.py) 的完整实现。

关键要点：
1. 使用 `console_logs` 列表记录执行过程
2. 从 `round` 参数构建路径，不从 config 读取
3. 返回完整的业务数据（dates, counts等）
4. 辅助函数也接收 `console_logs` 参数

```python
from typing import Dict, Any, Optional
from topup_ssh import TopupSSH
import re

def step0_get_available_dates(
    ssh: TopupSSH,
    round: str,
    include_processed: bool = True,
    sort_order: str = 'asc'
) -> Dict[str, Any]:
    """获取所有可用数据目录的日期列表"""

    console_logs = []
    console_logs.append("="*60)
    console_logs.append("步骤0：获取所有可用数据目录的日期列表")
    console_logs.append("="*60)

    # 从 round 参数构建路径
    data_dir = f"/data/topup/{round}/data"
    inj_sig_time_cal_dir = f"/data/topup/{round}/inj_sig_time_cal"

    try:
        # 1. 获取所有可用日期
        all_dates_result = _get_all_available_dates(ssh, data_dir, console_logs)

        if not all_dates_result['success']:
            return {
                'success': False,
                'message': all_dates_result['message'],
                'error': all_dates_result.get('error', ''),
                'console_logs': console_logs
            }

        all_dates = all_dates_result['dates']

        # 应用排序
        if sort_order == 'desc':
            all_dates.sort(reverse=True)

        # 2. 如果需要，获取已处理日期信息
        if include_processed:
            processed_dates_result = _get_processed_dates(ssh, inj_sig_time_cal_dir, console_logs)

            if not processed_dates_result['success']:
                console_logs.append("⚠ 获取已处理日期失败，仅返回所有可用日期")
                return {
                    'success': True,
                    'message': f'成功获取 {len(all_dates)} 个可用日期（无法获取已处理日期信息）',
                    'all_dates': all_dates,
                    'total_count': len(all_dates),
                    'console_logs': console_logs
                }

            processed_dates = processed_dates_result['dates']
            unprocessed_dates = [d for d in all_dates if d not in processed_dates]

            console_logs.append(f"\n统计信息:")
            console_logs.append(f"  总日期数: {len(all_dates)}")
            console_logs.append(f"  已处理: {len(processed_dates)}")
            console_logs.append(f"  未处理: {len(unprocessed_dates)}")

            return {
                'success': True,
                'message': f'成功获取日期信息：共{len(all_dates)}个，已处理{len(processed_dates)}个，未处理{len(unprocessed_dates)}个',
                'console_logs': console_logs,
                'all_dates': all_dates,
                'processed_dates': processed_dates,
                'unprocessed_dates': unprocessed_dates,
                'total_count': len(all_dates),
                'processed_count': len(processed_dates),
                'unprocessed_count': len(unprocessed_dates)
            }

        else:
            return {
                'success': True,
                'message': f'成功获取 {len(all_dates)} 个可用日期',
                'console_logs': console_logs,
                'all_dates': all_dates,
                'total_count': len(all_dates)
            }

    except Exception as e:
        console_logs.append(f"异常: {str(e)}")
        return {
            'success': False,
            'message': f'获取日期列表异常: {str(e)}',
            'error': str(e),
            'console_logs': console_logs
        }


def _get_all_available_dates(ssh: TopupSSH, data_dir: str, console_logs: list) -> Dict[str, Any]:
    """辅助函数：获取所有可用日期"""
    console_logs.append(f"\n获取所有可用数据目录...")
    console_logs.append(f"数据目录: {data_dir}")

    result = ssh.execute_command(f"ls -1 {data_dir}")

    if not result['success']:
        return {
            'success': False,
            'message': '获取数据目录失败',
            'error': result.get('error', '未知错误')
        }

    # 解析日期列表（只保留6位数字的目录名）
    dates = [
        line.strip() for line in result['output'].split('\n')
        if line.strip() and re.match(r'^\d{6}$', line.strip())
    ]

    dates.sort()

    console_logs.append(f"找到 {len(dates)} 个可用日期目录")

    return {
        'success': True,
        'dates': dates
    }
```

## 检查清单

在编写步骤函数时，请确保检查以下项目：

- [ ] 函数接受 `ssh: TopupSSH` 作为第一个参数
- [ ] 返回字典包含 `success` 和 `message` 键
- [ ] 返回字典包含 `console_logs` 列表（推荐）
- [ ] 只声明实际需要的参数，不使用 `**kwargs`
- [ ] 不从 config 文件读取路径，使用参数传递
- [ ] 从 `round` 参数动态构建路径
- [ ] 每次 SSH 调用后检查 `result['success']`
- [ ] 长时间操作有超时处理
- [ ] 使用 `console_logs` 列表记录执行过程（不用 print）
- [ ] 失败时返回结构化错误信息
- [ ] 辅助函数也接收 `console_logs` 参数
- [ ] 函数名与工作流配置中的 `function` 匹配
- [ ] 添加适当的文档字符串
- [ ] 处理所有可能的错误情况
- [ ] 返回有用的业务数据供后续步骤或API使用

## 常见问题

### 1. 如何获取配置路径？

❌ **错误做法**：
```python
import config
data_dir = config.DATA_DIR  # 不要这样做
```

✅ **正确做法**：
```python
def step_example(ssh: TopupSSH, round: str, **kwargs):
    data_dir = f"/data/topup/{round}/data"  # 从参数构建
```

### 2. 如何记录执行日志？

❌ **错误做法**：
```python
print("开始执行...")  # 不推荐
```

✅ **正确做法**：
```python
console_logs = []
console_logs.append("开始执行...")
return {'console_logs': console_logs, ...}
```

### 3. 如何处理可选参数？

```python
def step_example(
    ssh: TopupSSH,
    round: str,
    date_param: Optional[str] = None,  # 可选参数
    submit_job: bool = True,           # 有默认值
    **kwargs                           # 接收其他参数
):
    if not date_param:
        return {
            'success': False,
            'message': '缺少日期参数',
            'error': 'date_param 是必需的'
        }
```

### 4. 返回值中应该包含哪些字段？

**必需字段**：
- `success`: bool
- `message`: str

**推荐字段**：
- `console_logs`: list（执行日志）
- `step_name`: str（步骤名称）

**可选字段**：
- `error`: str（失败时）
- 业务数据：如 `all_dates`, `processed_count` 等

所有业务数据都会被保存到数据库的 `step_result_json` 字段，可以通过API查询。

---

*本指南基于 step0_get_available_dates.py 的实现编写。如有问题，请参考现有的步骤实现。*
