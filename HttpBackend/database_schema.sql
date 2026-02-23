-- Topup任务管理系统数据库Schema
-- 用于存储任务、步骤和工作流信息

-- 1. 工作流定义表
CREATE TABLE workflows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    version TEXT NOT NULL,
    config_path TEXT NOT NULL,  -- 配置文件路径
    status TEXT DEFAULT 'active', -- active, inactive, deprecated
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 工作流步骤定义表
CREATE TABLE workflow_steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workflow_id INTEGER NOT NULL,
    step_order INTEGER NOT NULL,  -- 步骤顺序
    step_name TEXT NOT NULL,     -- 步骤名称（如 step1_1, step2_2）
    step_display_name TEXT NOT NULL, -- 显示名称（如 "第一次作业提交"）
    step_module TEXT NOT NULL,   -- Python模块名
    step_function TEXT NOT NULL, -- Python函数名
    description TEXT,
    required_files JSON,         -- 该步骤需要生成的文件列表
    timeout_minutes INTEGER DEFAULT 30, -- 默认超时时间
    retry_count INTEGER DEFAULT 3,      -- 重试次数
    status TEXT DEFAULT 'active', -- active, inactive
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (workflow_id) REFERENCES workflows (id) ON DELETE CASCADE
);

-- 3. 任务实例表
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,        -- 用户标识
    workflow_id INTEGER NOT NULL,
    task_name TEXT NOT NULL,      -- 任务名称
    date_param TEXT,              -- 日期参数（如 250624）
    status TEXT DEFAULT 'pending', -- pending, running, success, failed, paused, cancelled
    progress_percentage INTEGER DEFAULT 0, -- 进度百分比
    current_step TEXT,            -- 当前执行的步骤名称
    error_message TEXT,           -- 错误信息
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    estimated_completion_time TIMESTAMP,
    FOREIGN KEY (workflow_id) REFERENCES workflows (id) ON DELETE CASCADE
);

-- 4. 任务步骤执行记录表
CREATE TABLE task_executions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    step_name TEXT NOT NULL,      -- 步骤名称
    step_display_name TEXT,       -- 显示名称
    step_order INTEGER NOT NULL,   -- 步骤顺序
    status TEXT DEFAULT 'pending', -- pending, running, success, failed, timeout, cancelled
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    duration_seconds INTEGER,     -- 执行耗时（秒）
    retry_count INTEGER DEFAULT 0, -- 当前重试次数
    output_summary TEXT,          -- 输出摘要
    error_details TEXT,           -- 错误详情
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE
);

-- 5. 任务步骤输出表
CREATE TABLE step_outputs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_id INTEGER NOT NULL,  -- 关联的执行记录ID
    output_type TEXT NOT NULL,       -- 文件类型或输出类型
    output_path TEXT,               -- 文件路径
    file_size_bytes INTEGER,         -- 文件大小（字节）
    file_hash TEXT,                 -- 文件哈希值
    content_type TEXT,              -- 内容类型（如 png, txt, root等）
    metadata JSON,                  -- 额外的元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (execution_id) REFERENCES task_executions (id) ON DELETE CASCADE
);

-- 6. 任务日志表
CREATE TABLE task_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    execution_id INTEGER,          -- 关联的执行记录ID（可选）
    level TEXT NOT NULL,          -- info, warning, error, debug
    message TEXT NOT NULL,        -- 日志消息
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source TEXT,                 -- 日志来源（函数名）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE,
    FOREIGN KEY (execution_id) REFERENCES task_executions (id) ON DELETE CASCADE
);

-- 7. 任务参数表（存储特定任务的参数）
CREATE TABLE task_parameters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    param_name TEXT NOT NULL,     -- 参数名（如 submit_job, date）
    param_value TEXT NOT NULL,    -- 参数值
    param_type TEXT DEFAULT 'text', -- 参数类型（text, integer, boolean）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE
);

-- 8. 用户配置表（存储用户的工作流偏好）
CREATE TABLE user_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL UNIQUE, -- 用户标识
    default_workflow_id INTEGER,  -- 默认工作流
    default_timeout INTEGER,      -- 默认超时时间
    preferred_date TEXT,         -- 偏好的日期格式
    notification_preferences JSON, -- 通知设置
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (default_workflow_id) REFERENCES workflows (id) ON DELETE SET NULL
);

-- 创建索引以提高查询性能
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_user ON tasks(user_id);
CREATE INDEX idx_tasks_created ON tasks(created_at);
CREATE INDEX idx_executions_task ON task_executions(task_id);
CREATE INDEX idx_executions_status ON task_executions(status);
CREATE INDEX idx_executions_step ON task_executions(step_name);
CREATE INDEX idx_outputs_execution ON step_outputs(execution_id);
CREATE INDEX idx_logs_task ON task_logs(task_id);
CREATE INDEX idx_logs_execution ON task_logs(execution_id);

-- 创建触发器，用于自动更新updated_at字段
CREATE TRIGGER update_workflows_updated_at
    AFTER UPDATE ON workflows
    FOR EACH ROW
BEGIN
    UPDATE workflows SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER update_workflow_steps_updated_at
    AFTER UPDATE ON workflow_steps
    FOR EACH ROW
BEGIN
    UPDATE workflow_steps SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER update_user_preferences_updated_at
    AFTER UPDATE ON user_preferences
    FOR EACH ROW
BEGIN
    UPDATE user_preferences SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- 插入默认工作流数据
INSERT INTO workflows (name, description, version, config_path)
VALUES (
    'topup_standard_workflow',
    '标准Topup数据处理流程（步骤1-8）',
    '1.0.0',
    'workflows/topup_standard.json'
);

-- 插入默认步骤定义（基于现有step1-8）
INSERT INTO workflow_steps (workflow_id, step_order, step_name, step_display_name, step_module, step_function, description, required_files, timeout_minutes)
VALUES
(1, 1, 'step1_1', '第一次作业提交并检查结果文件', 'step1_1_first_job_submission', 'step1_1_first_job_submission', '提交第一次作业并检查结果文件',
'["rec{run}_1.txt", "rec{run}_1.txt.bosserr", "rec{run}_1.txt.bosslog", "InjSigTime_00{run}_720.root", "Interval_run{run}.png", "Interval_run{run}.txt"]', 25),
(1, 2, 'step1_2', '移动文件', 'step1_2_move_files', 'step1_2_move_files', '移动文件到指定目录',
'["rec*_1.txt", "rec*_1.txt.bosserr", "rec*_1.txt.bosslog", "InjSigTime_*.root", "Interval_*.png", "Interval_*.txt"]', 5),
(1, 3, 'step1_3', 'IST分析', 'step1_3_ist_analysis', 'step1_3_ist_analysis', '执行IST分析',
'["hist_*/*.root"]', 60),
(1, 4, 'step1_4', '合并图像', 'step1_4_merge_images', 'step1_4_merge_images', '合并分析图像',
'["merged_interval.png"]', 10),
(1, 5, 'step2_1', '第二次作业提交', 'step2_1_second_job_submission', 'step2_1_second_job_submission', '提交第二次作业',
'["rec*_2.txt", "rec*_2.txt.bosserr", "rec*_2.txt.bosslog", "InjSigTime_*.root"]', 25),
(1, 6, 'step2_2', '合并hist文件', 'step2_2_merge_hist', 'step2_2_merge_hist', '合并hist文件',
'["merged_*.root"]', 10),
(1, 7, 'step2_3', '生成PNG文件', 'step2_3_generate_png', 'step2_3_generate_png', '生成PNG可视化文件',
'["*.png"]', 15),
(1, 8, 'step2_4', '检查PNG文件', 'step2_4_check_png_files', 'step2_4_check_png_files', '检查PNG文件完整性',
'["interval_run*.png"]', 5),
(1, 9, 'step2_5', '合并图像', 'step2_5_merge_images', 'step2_5_merge_images', '合并所有图像',
'["merged_interval_hist.png"]', 10),
(1, 10, 'step3_1', '第三次作业提交', 'step3_1_third_job_submission', 'step3_1_third_job_submission', '提交第三次作业（寻找峰值）',
'["run_*_3.txt", "*.err", "*.out", "shield_run*.txt"]', 30),
(1, 11, 'step3_2', '运行添加脚本', 'step3_2_run_add_script', 'step3_2_run_add_script', '运行添加shield脚本',
'["shield_run*.txt", "shield_run*.png"]', 15),
(1, 12, 'step4_1', '第四次作业提交', 'step4_1_fourth_job_submission', 'step4_1_fourth_job_submission', '提交第四次作业（检查shield校准）',
'["*.txt", "*.err", "*.out", "*.png"]', 30),
(1, 13, 'step4_2', '合并图像', 'step4_2_merge_images', 'step4_2_merge_images', '合并shield校准图像',
'["merged_shield.png"]', 10),
(1, 14, 'step5_1', '第五次作业提交', 'step5_1_fifth_job_submission', 'step5_1_fifth_job_submission', '提交第五次作业（ETS cut）',
'["plot_ETS_*.txt", "*.err", "*.out", "run*_cut.png", "run*_total.png"]', 30),
(1, 15, 'step5_2', '运行添加shield脚本', 'step5_2_run_add_shield_script', 'step5_2_run_add_shield_script', '运行添加shield脚本',
'["shield_run*.txt", "shield_run*.png"]', 15),
(1, 16, 'step5_3', '组织ETS cut文件', 'step5_3_organize_ets_cut_file', 'step5_3_organize_ets_cut_file', '组织ETS cut文件',
'["cut*.root", "run*.cut", "merged_cut*.txt"]', 10),
(1, 17, 'step5_4', '合并图像', 'step5_4_merge_images', 'step5_4_merge_images', '合并ETS cut图像',
'["merged_cut*.png"]', 10),
(1, 18, 'step6_1', '第六次作业提交', 'step6_1_sixth_job_submission', 'step6_1_sixth_job_submission', '提交第六次作业（检查ETS cut校准）',
'["ETScut_check_*.txt", "*.err", "*.out", "*.png", "*.root"]', 30),
(1, 19, 'step6_2', '合并图像', 'step6_2_merge_images', 'step6_2_merge_images', '合并ETS cut校准图像',
'["merged_etscut.png"]', 10),
(1, 20, 'step7', '运行重置脚本', 'step7_run_reset_script', 'step7_run_reset_script', '运行重置脚本',
'["reset_*.txt"]', 10),
(1, 21, 'step8', '提交到数据库', 'step8_submit_injsiginterval_db', 'step8_submit_injsiginterval_db', '提交InjSigInterval到数据库',
'["*.root", "*.txt"]', 45);