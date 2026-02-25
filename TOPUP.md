# BESIII Topup 数据验证自动化系统

## 项目概述

这是一个用于自动化执行 BESIII Topup 数据验证流程的 Python 项目。系统通过 SSH 双跳连接连接到远程服务器，自动执行 21 个主要步骤的数据验证任务，包括作业提交、文件检查、数据分析、结果整理、图片合并和系统重置。系统集成了 AI 驱动的智能分析功能，能够自动判断执行结果并决定后续操作，并支持自动下载生成的 PDF 报告到本地。

## 技术栈

- **Python**: 3.13+
- **SSH 连接**: paramiko
- **环境配置**: python-dotenv
- **架构**: 模块化设计，每个步骤独立封装
- **AI 集成**: 智能结果分析和决策

## 核心模块

### 1. 配置管理

**config.py** - 集中配置文件
- **ROUND 参数**: "round18"，便于切换不同的 round
- **目录配置**: 所有远程服务器目录路径（基于 ROUND 参数动态生成）
- **SSH 配置**: 服务器连接信息（从 .env 文件读取密码）
- **定时检查配置**:
  - `DEFAULT_MAX_WAIT_MINUTES = 25`：默认最大等待时间（分钟）
  - `CHECK_INTERVAL_SECONDS = 30`：检查间隔（秒）
- **文件名配置**: 各步骤所需的文件命名规则
  - REQUIRED_FILES_STEP1：步骤1所需文件格式（InjSigTime_00{run}_720.root）
  - REQUIRED_FILES_STEP3：步骤3所需文件格式
  - REQUIRED_FILES_STEP5：步骤5所需文件格式
  - REQUIRED_FILES_STEP6：步骤6所需文件格式
- **进度管理**: 步骤进度保存和加载功能（.step_progress文件）

**.env** - 环境变量
- `SSH_PASS_LXLOGIN`: 跳板机密码
- `SSH_PASS_BESLOGIN`: 目标服务器密码

### 2. SSH 连接管理

**topup_ssh.py** - SSH 双跳连接管理
- 支持通过跳板机（lxlogin）连接到目标服务器（beslogin）
- 提供 `execute_command()` 方法执行远程命令
- 提供 `execute_interactive_command()` 方法执行交互式命令
- 提供 `download_file()` 方法通过SFTP下载文件到本地
- 自动管理连接生命周期（支持上下文管理器）
- 从 config.py 读取服务器配置
- 改进的命令输出显示：成功时显示输出内容
- 支持超时控制和错误处理

### 3. 步骤模块

项目包含 21 个独立的步骤模块：

**步骤 1 - 第一次作业**（4个子步骤）
- `step1_1_first_job_submission.py`: 第一次作业提交（合并版，支持自动对比获取日期或手动指定日期）
- `step1_2_move_files.py`: 移动 root 和 png 文件
- `step1_3_ist_analysis.py`: IST 分析，验证 interval 值
- `step1_4_merge_images.py`: 合并 Interval_plot 目录中的图片为 PDF 并下载到本地

**步骤 2 - 第二次作业**（5个子步骤）
- `step2_1_second_job_submission.py`: 第二次作业提交（自动重新提交）
- `step2_2_merge_hist.py`: 合并 hist 文件
- `step2_3_generate_png.py`: 生成 png 文件
- `step2_4_check_png_files.py`: 检查 png 文件（定时检查，默认25分钟，30秒间隔）
- `step2_5_merge_images.py`: 合并 hist 目录中的图片为 PDF 并下载到本地

**步骤 3 - 第三次作业**（2个子步骤）
- `step3_1_third_job_submission.py`: 提交第三次作业
- `step3_2_run_add_script.py`: 运行 add.sh 脚本并清理 window.dat 文件（删除只有 run 号的行）

**步骤 4 - 第四次作业**（2个子步骤）
- `step4_1_fourth_job_submission.py`: 提交第四次作业
- `step4_2_merge_images.py`: 合并 checkShieldCalib 目录中的图片为 PDF 并下载到本地

**步骤 5 - 第五次作业**（4个子步骤）
- `step5_1_fifth_job_submission.py`: 提交第五次作业
- `step5_2_run_add_shield_script.py`: 运行 add_shield.sh 脚本
- `step5_3_organize_ets_cut_file.py`: 整理 ets_cut.txt 文件
- `step5_4_merge_images.py`: 合并 ETS_cut 目录中的图片为 PDF 并下载到本地

**步骤 6 - 第六次作业**（2个子步骤）
- `step6_1_sixth_job_submission.py`: 提交第六次作业
- `step6_2_merge_images.py`: 合并 check_ETScut_CalibConst 目录中的图片为 PDF 并下载到本地

**步骤 7 - 系统重置**（1个子步骤）
- `step7_run_reset_script.py`: 运行 reset.sh 脚本，重置系统状态

**步骤 8 - 数据库提交**（19个子步骤）
- `step8_submit_injsiginterval_db.py`: 完整数据库提交流程
  - **8.1**: InjSigInterval 数据库提交（6个子步骤）
  - **8.2**: InjSigTime 数据库提交（3个子步骤）
  - **8.3**: OfflineEvtFilter 数据库提交（10个子步骤）

### 4. 执行控制

**run.py** - 单步执行脚本（推荐，已增强）
- 支持从任意步骤开始执行
- 支持批量执行（--all 模式）
- 支持批量处理所有日期（--total 模式）
- 命令行参数化控制
- 提供步骤列表功能
- **集成了 AI 分析功能**（analyze_result函数）
- 支持自定义最大等待时间（--max-wait 参数）
- 支持作业提交控制（--submit-job 参数）
- 支持文件检查控制（--check 参数）
- 提供详细的执行摘要和 AI 分析结果
- 自动重试机制（最多3次）

### 5. 错误处理系统

**error_codes.py** - 错误代码匹配系统
- 错误代码范围：1000-8999（按步骤分组）
- 错误字典结构：
  - `code`: 错误代码号
  - `name`: 错误名称
  - `message`: 简短错误消息
  - `description`: 详细错误描述
  - `action`: 推荐操作（continue/retry/manual）
  - `severity`: 严重程度（info/warning/error）

**error-dictionary/** - 错误字典模块
- `step1_errors.py`: 步骤1错误定义（1000-1999）
- `step2_errors.py`: 步骤2错误定义（2000-2999）
- `step3_errors.py`: 步骤3错误定义（3000-3999）
- `step4_errors.py`: 步骤4错误定义（4000-4999）
- `step5_errors.py`: 步骤5错误定义（5000-5999）
- `step6_errors.py`: 步骤6错误定义（6000-6999）
- `step7_errors.py`: 步骤7错误定义（7000-7999）
- `step8_errors.py`: 步骤8错误定义（8000-8999）

### 6. 日志系统

**logger.py** - 增强日志记录系统
- 步骤开始/完成记录
- 命令执行日志
- 输出和错误记录
- 模式退出状态跟踪
- 时间戳记录
- 错误上下文（当前步骤和日期）
- 日志文件：`logs/step_execution.log`

### 7. iFlow CLI 集成

**iflow_cli_client.py** - iFlow CLI 客户端
- 与 iFlow CLI 通信
- 发送错误分析请求
- 接收 AI 处理响应
- 支持自动配置文件修正

## 使用方法

### 安装依赖

```bash
pip install paramiko python-dotenv
```

### 配置环境变量

在项目根目录创建 `.env` 文件：

```env
SSH_PASS_LXLOGIN=你的跳板机密码
SSH_PASS_BESLOGIN=你的目标服务器密码
```

### 执行步骤

#### 方法 1：执行单个步骤（推荐）

```bash
# 查看所有可用步骤
python run.py --list

# 执行特定步骤
python run.py --step 1.4 --date 250519

# 执行特定步骤（自定义最大等待时间，用于定时检查步骤）
python run.py --step 2.4 --date 250519 --max-wait 30

# 执行特定步骤（控制作业提交）
python run.py --step 1.1 --date 250519 --submit-job false

# 执行特定步骤（控制文件检查）
python run.py --step 4.1 --date 250519 --check true
```

#### 方法 2：批量执行

```bash
# 执行所有步骤
python run.py --all --date 250519

# 执行所有步骤（自定义最大等待时间）
python run.py --all --date 250519 --max-wait 30

# 执行所有步骤（控制作业提交和文件检查）
python run.py --all --date 250519 --submit-job false --check true
```

#### 方法 3：批量处理所有日期

```bash
# Total模式：批量处理所有可用日期
python run.py --total
```

#### 方法 4：数据库提交

```bash
# 执行步骤8（数据库提交）
python run.py --step 8
```

### 定时检查参数配置

所有定时检查步骤都支持两种方式配置等待时间：

**方式 1：使用配置文件的默认值**

```python
# config.py 中
DEFAULT_MAX_WAIT_MINUTES = 25  # 默认25分钟

# 调用时
result = step2_4_check_png_files.step2_4_check_png_files(ssh, "250519")
# 自动使用 25 分钟
```

**方式 2：传入自定义参数**

```python
# 覆盖默认值
result = step2_4_check_png_files.step2_4_check_png_files(ssh, "250519", max_wait_minutes=30)
# 使用 30 分钟
```

**方式 3：使用命令行参数**

```bash
python run.py --step 2.4 --date 250519 --max-wait 30
```

**支持定时检查的步骤**：
- 步骤 2.4：检查 png 文件

**图片合并步骤（自动下载PDF）**：
- 步骤 1.4：合并 Interval_plot 图片
- 步骤 2.5：合并 hist 图片
- 步骤 4.2：合并 checkShieldCalib 图片
- 步骤 5.4：合并 ETS_cut 图片
- 步骤 6.2：合并 check_ETScut 图片

### 自动重新提交功能

步骤 1.1 和 2.1 在执行时会自动删除已存在的日期目录，确保干净的作业提交。

```bash
# 执行步骤1.1时，系统会自动清理旧数据
python run.py --step 1.1 --date 250519

# 执行步骤2.1时，系统会自动处理重新提交
python run.py --step 2.1 --date 250519
```

### 切换 Round

修改 `config.py` 中的 ROUND 参数：

```python
ROUND = "round19"  # 切换到 round19
```

所有目录路径会自动更新。

### 切换 BOSS 版本

修改 `config.py` 中的 BOSS 版本参数：

```python
BOSS = "7.3.0"     # 更新完整版本
BOSSE = "730"      # 更新短版本（用于命令参数）
```

所有命令参数会自动更新。

## 步骤流程

1. **步骤 1**: 第一次作业（确定日期/提交作业 → 检查文件 → 移动文件 → IST 分析 → 合并图片并下载）
2. **步骤 2**: 第二次作业（提交作业 → 检查hist → 合并hist → 生成png → 检查png → 合并图片并下载）
3. **步骤 3**: 第三次作业（提交作业 → 检查shield → 运行脚本）
4. **步骤 4**: 第四次作业（提交作业 → 合并图片并下载）
5. **步骤 5**: 第五次作业（提交作业 → 检查文件 → 运行脚本 → 整理文件 → 合并图片并下载）
6. **步骤 6**: 第六次作业（提交作业 → 合并图片并下载）
7. **步骤 7**: 系统重置（运行reset.sh脚本）
8. **步骤 8**: 数据库提交（InjSigInterval + InjSigTime + OfflineEvtFilter）

## 返回格式

每个步骤返回标准化的结果字典：

```python
{
    'success': bool,           # 执行是否成功
    'message': str,            # 状态消息
    'exit_code': int,          # 命令退出码
    'output': str,             # 命令标准输出
    'error': str,              # 命令标准错误
    'ai_analysis': dict,      # AI分析结果（如果启用AI分析）
    # ... 其他步骤特定字段
}
```

## AI 分析功能

### AI 分析能力

系统集成了智能分析功能，能够：

1. **成功检测**：自动识别步骤是否成功执行
2. **人工干预检测**：自动检测是否需要人工干预
3. **智能建议**：提供继续、重试或人工检查的建议
4. **自动停止**：遇到问题时自动停止，避免继续执行错误步骤
5. **详细分析**：显示完整的分析结果和建议操作
6. **错误码匹配**：使用结构化错误码系统进行精确错误识别

### AI 分析结果格式

```python
{
    'should_continue': bool,   # 是否继续下一步
    'message': str,            # 分析消息
    'action': str              # 推荐操作 ('continue', 'retry', 'manual')
}
```

### 自动重试机制

系统支持最多 3 次自动重试：

1. 首次执行失败
2. 进行错误分析
3. 如果 action 为 'retry'，自动重试
4. 最多重试 3 次
5. 超过重试次数后，请求 iFlow CLI 处理

## 错误代码系统

### 错误代码范围

- **通用错误**: 0-999
- **步骤 1**: 1000-1999
- **步骤 2**: 2000-2999
- **步骤 3**: 3000-3999
- **步骤 4**: 4000-4999
- **步骤 5**: 5000-5999
- **步骤 6**: 6000-6999
- **步骤 7**: 7000-7999
- **步骤 8**: 8000-8999
- **未知错误**: 9999

### 错误字典结构

每个错误定义包括：
- `code`: 错误代码号
- `name`: 错误名称
- `message`: 简短错误消息
- `description`: 详细错误描述
- `action`: 推荐操作（continue/retry/manual）
- `severity`: 严重程度（info/warning/error）

### 使用示例

```python
import error_codes

# 获取错误信息
error_info = error_codes.get_error_info(1101)
print(f"错误名称: {error_info['name']}")
print(f"错误描述: {error_info['description']}")
print(f"推荐操作: {error_info['action']}")

# 匹配错误码
error_code = error_codes.match_error_code("步骤1.1：第一次作业提交", result)
print(f"匹配的错误码: {error_code}")
```

## 步骤 8：数据库提交详细说明

### 步骤 8.1：InjSigInterval 数据库提交

1. 运行 clean_interval.sh 清理
2. 编译 genConst.cpp 并生成常量文件
3. 执行 copy.sh 复制文件
4. 运行 rootmove.sh 移动 root 文件
5. 验证提交命令（sub_switch=0）
6. 提交到数据库（sub_switch=1）

### 步骤 8.2：InjSigTime 数据库提交

1. 执行 rootmove.sh 移动 root 文件
2. 验证提交命令（sub_switch=0）
3. 提交到数据库（sub_switch=1）

### 步骤 8.3：OfflineEvtFilter 数据库提交

1. 运行 cp_3files.sh 复制文件
2. 执行 duration_caculate/a.out 计算持续时间
3. 执行 ccompare/a.out 进行比较检查
4. 执行 a.out（使用 config.BOSSE 参数）
5. 生成 file.txt
6. 执行 check/a.out（使用 config.BOSSE 参数）
7. 运行 rootmove.sh 移动 root 文件
8. 验证提交命令（sub_switch=0）
9. 提交到数据库（sub_switch=1）
10. 运行 reset_root.sh 重置 root 文件

### 环境激活标准

步骤 8 的所有子步骤在执行前都会激活 BOSS 环境：

```bash
source ~/w720
```

### 配置文件使用

- 所有路径使用 config.py 变量
- BOSS 版本使用 config.BOSSE 参数
- 环境脚本使用 config.ENV_SCRIPT

## 图片合并与下载

系统在以下步骤会自动合并 PNG 图片为 PDF 文件并下载到本地：

- **步骤 1.4**: 合并 Interval_plot 目录中的图片 → `mergedd_IST_{date}.pdf`
- **步骤 2.5**: 合并 hist 目录中的图片 → `mergedd_Hist_{date}.pdf`
- **步骤 4.2**: 合并 checkShieldCalib 目录中的图片 → `mergedd_CheckShield_{date}.pdf`
- **步骤 5.4**: 合并 ETS_cut 目录中的图片 → `mergedd_ETSCut_{date}.pdf`
- **步骤 6.2**: 合并 check_ETScut_CalibConst 目录中的图片 → `mergedd_CheckETScut_{date}.pdf`

所有下载的 PDF 文件保存在项目根目录的 `downloads/` 文件夹中。

### SFTP 文件下载

`topup_ssh.py` 提供 `download_file()` 方法，支持通过 SFTP 协议下载远程文件：

```python
result = ssh.download_file(remote_path, local_path)
```

该方法会自动处理文件传输，并在下载完成后返回详细信息。

## 开发规范

### 代码风格

- 使用 UTF-8 编码
- 每个步骤都是独立的 Python 模块
- 函数命名格式：`stepX_Y_step_name`
- 使用类型提示（Type Hints）
- 完整的 docstring 文档

### 配置管理

- 所有配置集中在 `config.py`
- 使用环境变量存储敏感信息
- ROUND 参数便于版本切换
- 定时检查参数可全局配置或局部覆盖
- 文件名格式统一配置在 REQUIRED_FILES_STEPX 中

### 错误处理

- 每个步骤都包含异常处理
- 返回标准化的错误信息
- 支持人工干预检测
- 提供清晰的错误消息

### AI 集成

- AI 分析功能集成在 `run.py` 中
- 每个步骤执行后自动调用 AI 分析
- AI 结果包含在返回结果的 `ai_analysis` 字段中
- 自动重试机制（最多3次）

### 日志记录

- 使用 `logger.py` 记录所有操作
- 记录步骤开始/完成
- 记录命令执行和输出
- 记录模式退出状态
- 记录错误上下文

## 项目结构

```
topup/
├── config.py                          # 配置文件（目录、SSH、定时参数、ROUND、文件名格式）
├── .env                               # 环境变量（密码）
├── topup_ssh.py                       # SSH 连接管理（改进的输出显示，支持SFTP下载）
├── run.py                             # 主执行脚本（推荐，已增强，支持AI分析）
├── error_codes.py                     # 错误代码匹配系统
├── error-dictionary/                  # 错误字典模块
│   ├── step1_errors.py                # 步骤1错误定义
│   ├── step2_errors.py                # 步骤2错误定义
│   ├── step3_errors.py                # 步骤3错误定义
│   ├── step4_errors.py                # 步骤4错误定义
│   ├── step5_errors.py                # 步骤5错误定义
│   ├── step6_errors.py                # 步骤6错误定义
│   ├── step7_errors.py                # 步骤7错误定义
│   └── step8_errors.py                # 步骤8错误定义
├── logger.py                          # 增强日志记录系统
├── iflow_cli_client.py                # iFlow CLI 客户端
├── remote_command.py                  # 远程命令执行工具
├── step1_1_first_job_submission.py    # 步骤 1.1
├── step1_2_move_files.py              # 步骤 1.2
├── step1_3_ist_analysis.py            # 步骤 1.3
├── step1_4_merge_images.py            # 步骤 1.4 - 合并图片
├── step2_1_second_job_submission.py   # 步骤 2.1
├── step2_2_merge_hist.py              # 步骤 2.2
├── step2_3_generate_png.py            # 步骤 2.3
├── step2_4_check_png_files.py         # 步骤 2.4
├── step2_5_merge_images.py            # 步骤 2.5 - 合并图片
├── step3_1_third_job_submission.py    # 步骤 3.1
├── step3_2_run_add_script.py          # 步骤 3.2
├── step4_1_fourth_job_submission.py   # 步骤 4.1
├── step4_2_merge_images.py            # 步骤 4.2 - 合并图片
├── step5_1_fifth_job_submission.py    # 步骤 5.1
├── step5_2_run_add_shield_script.py   # 步骤 5.2
├── step5_3_organize_ets_cut_file.py   # 步骤 5.3
├── step5_4_merge_images.py            # 步骤 5.4 - 合并图片
├── step6_1_sixth_job_submission.py    # 步骤 6.1
├── step6_2_merge_images.py            # 步骤 6.2 - 合并图片
├── step7_run_reset_script.py          # 步骤 7 - 运行reset脚本
├── step8_submit_injsiginterval_db.py  # 步骤 8 - 数据库提交
├── TOPUP.md                           # 本文档
├── .step_progress                     # 步骤进度文件
├── downloads/                         # 本地下载目录（存放自动下载的PDF文件）
├── logs/                              # 日志目录
│   └── step_execution.log             # 步骤执行日志
└── .iflow/                            # iFlow 配置
    └── skills/
        └── topup/                     # topup skill 目录
            └── SKILL.md               # Skill 定义文件
```

## 故障排查

### SSH 连接失败

- 检查 .env 文件中的密码是否正确
- 确认网络连接正常
- 验证服务器地址和端口

### 文件检查超时

- 增加等待时间参数：`--max-wait 30`
- 检查远程服务器上的作业状态
- 确认作业是否正常提交

### 步骤执行失败

- 查看错误消息和退出码
- 检查 SSH 连接是否正常
- 验证日期参数格式是否正确（6位数字）
- 查看 AI 分析结果以获取详细建议

### AI 分析建议重试

- 检查步骤的具体错误信息
- 确认 SSH 连接是否仍然活跃
- 考虑手动检查远程服务器状态

### AI 分析建议人工干预

- 查看未完成的 run 号列表
- 检查相关的错误日志文件
- 手动验证作业状态
- 解决问题后使用断点续传继续

### 目录已存在错误

- 步骤 1.1 和 2.1 会自动删除已存在的日期目录
- 如果仍然遇到问题，可以手动清理远程服务器上的旧数据
- 确保目录权限正确

### 文件名格式错误

- 检查 config.py 中的文件名配置
- 确保与实际生成的文件名格式一致
- 验证 REQUIRED_FILES_STEPX 中的格式字符串

## 注意事项

1. **环境变量安全**: .env 文件包含敏感信息，不要提交到版本控制系统
2. **SSH 连接**: 使用双跳连接，确保跳板机和目标服务器都可访问
3. **定时检查**: 默认等待时间为 25 分钟，可根据实际情况调整
4. **日期格式**: 日期参数必须是 6 位数字（如 250519）
5. **Round 切换**: 修改 ROUND 参数后，所有目录路径自动更新
6. **BOSS 版本切换**: 修改 BOSS 版本参数后，所有命令参数自动更新
7. **AI 分析**: 默认启用，提供智能结果分析和决策
8. **参数覆盖**: 定时检查参数可在调用时覆盖默认值
9. **智能停止**: AI 检测到问题会自动停止，避免错误扩散
10. **灵活执行**: 支持单步、批量执行、Total模式等多种执行方式
11. **自动重新提交**: 步骤1.1和2.1会自动清理旧数据
12. **自动重试**: 失败后最多自动重试3次
13. **图片合并**: 步骤1.4、2.5、4.2、5.4、6.2会自动合并PNG图片为PDF文件
14. **自动下载**: 图片合并步骤会自动下载生成的PDF文件到本地downloads目录
15. **容器环境**: 图片合并使用 SL6 容器环境，确保 ImageMagick 可用
16. **系统重置**: 步骤7会运行reset.sh脚本，谨慎使用
17. **超时配置**: 使用 `run_shell_command` 执行长时间步骤时，需要显式设置 `timeout` 参数
18. **错误码系统**: 使用结构化错误码系统进行精确错误识别和处理
19. **日志记录**: 所有操作都会记录到日志文件，便于故障排查
20. **环境激活**: 所有脚本执行前必须先激活 BOSS 环境

## 依赖项

- Python 3.13+
- paramiko（SSH 连接）
- python-dotenv（环境变量管理）

## 作者

iFlow CLI

## 版本

5.0.0