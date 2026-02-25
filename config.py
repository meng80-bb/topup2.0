#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Topup操作配置文件
包含所有目录路径和配置参数
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 环境配置
ENV_SCRIPT = "~/w720"

# Round参数（便于切换不同的round）
ROUND = "round18"

# boss版本号
BOSS = "7.2.0"
BOSSE = "720"

# 目录基础路径
BASE_DIR = f"/besfs5/groups/cal/topup/{ROUND}/DataValid"
DATA_DIR = f"/bes3fs/offline/data/cal/{ROUND}"

# 步骤1相关目录
INJ_SIG_TIME_CAL_DIR = f"{BASE_DIR}/InjSigTimeCal"
CALIB_CONST_DIR = f"{BASE_DIR}/InjSigTimeCal/calibConst"
INTERVAL_PLOT_DIR = f"{BASE_DIR}/InjSigTimeCal/Interval_plot"

# 步骤2相关目录
DATA_VALID_DIR = f"{BASE_DIR}"
HIST_DIR = f"{BASE_DIR}/hist"

# 步骤3相关目录
SEARCH_PEAK_DIR = f"{BASE_DIR}/Determining_50Hz_cut/search_peak"

# 步骤4相关目录
CHECK_SHIELD_CALIB_DIR = f"{BASE_DIR}/Determining_50Hz_cut/checkShieldCalib"

# 步骤5相关目录
ETS_CUT_DIR = f"{BASE_DIR}/Determining_ETS_cut/ETS_cut"

# 步骤6相关目录
CHECK_ETSCUT_CALIBCONST_DIR = f"{BASE_DIR}/Determining_ETS_cut/check_ETScut_CalibConst"

# 步骤8相关目录（InjSigInterval提交数据库）
GEN_CONST_DIR = f"{BASE_DIR}/sub_database/InjSigInterval/genConst"
CONST_RUN_FORM_RUN_TO_DIR = f"{GEN_CONST_DIR}/const_runForm_runTo"
INJ_SIG_INTERVAL_DB_DIR = f"/afs/ihep.ac.cn/bes3/offline/CalibConst/OfflineEvtFilter/InjSigInterval/{BOSS}"


# 步骤8相关目录（InjSigTime提交数据库）
INJ_SIG_TIME_DB_DIR = f"/afs/ihep.ac.cn/bes3/offline/CalibConst/OfflineEvtFilter/InjSigTime/{BOSS}/{ROUND}"

# 步骤8相关目录（OfflineEvtFilter提交数据库）
OFFLINE_EVT_DIR = f"{BASE_DIR}/sub_database/OfflineEvtFilter"
OFFLINE_EVT_DB_DIR = f"/afs/ihep.ac.cn/bes3/offline/CalibConst/OfflineEvtFilter/OfflineEvtFilter/{BOSS}/{ROUND}/"
CHECK_DB_ALG_DIR = f"/besfs5/users/topup/boss720/workarea/workarea-7.2.0/Analysis/checkDBAlg/checkDBAlg-00-00-00/share"

# 本地下载目录配置
LOCAL_DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), "downloads")

# SSH服务器配置
SSH_CONFIG = {
    "servers": {
        "server1": {
            "name": "lxlogin",
            "host": "lxlogin.ihep.ac.cn",
            "port": 22,
            "username": "topup",
            "env_password": "SSH_PASS_LXLOGIN"
        },
        "server2": {
            "name": "beslogin",
            "host": "beslogin",
            "port": 22,
            "username": "topup",
            "env_password": "SSH_PASS_BESLOGIN"
        }
    }
}

# 定时检查配置
DEFAULT_MAX_WAIT_MINUTES = 25  # 默认最大等待时间（分钟）
CHECK_INTERVAL_SECONDS = 30    # 检查间隔（秒）

# 文件名配置
REQUIRED_FILES_STEP1 = {
    "job_file": "rec{run}_1.txt",
    "error_file": "rec{run}_1.txt.bosserr",
    "log_file": "rec{run}_1.txt.bosslog",
    "root_file": "InjSigTime_00{run}_720.root",
    "png_file": "Interval_run{run}.png",
    "txt_file": "Interval_run{run}.txt"
}

REQUIRED_FILES_STEP3 = {
    "job_file": "run_{run}_3.txt",
    "error_file": "run_{run}_3.txt.err.{node}",
    "output_file": "run_{run}_3.txt.out.{node}",
    "shield_file": "shield_run{run}.txt"
}

REQUIRED_FILES_STEP5 = {
    "job_file": "plot_ETS_{run}.txt",
    "error_file": "plot_ETS_{run}.txt.err.{node}",
    "output_file": "plot_ETS_{run}.txt.out.{node}",
    "cut_file": "run{run}_cut.png",
    "all_file": "run{run}_total.png"
}

REQUIRED_FILES_STEP6 = {
    "job_file": "ETScut_check_{run}.txt",
    "error_file": "ETScut_check_{run}.txt.err.{node}",
    "output_file": "ETScut_check_{run}.txt.out.{node}",
    "png_file": "run{run}.png",
    "root_file": "run{run}.root"
}

def get_date_dir(base_dir, date):
    """获取日期目录路径"""
    return f"{base_dir}/{date}"

def get_interval_value():
    """获取标准的interval值"""
    return 15000000

def validate_date(date_str):
    """验证日期格式（6位数字）"""
    import re
    return bool(re.match(r'^\d{6}$', date_str))

def get_step_progress_file():
    """获取步骤进度文件路径"""
    import os
    return os.path.join(os.path.dirname(__file__), ".step_progress")

def save_step_progress(step_name, date=None):
    """保存当前步骤进度"""
    import os
    import json
    progress_file = get_step_progress_file()
    # 读取现有进度文件以保留现有信息
    existing_progress = {}
    if os.path.exists(progress_file):
        try:
            with open(progress_file, 'r', encoding='utf-8') as f:
                existing_progress = json.load(f)
        except json.JSONDecodeError:
            pass
    
    # 更新进度信息
    progress_data = {
        'step_name': step_name,
        'date': date if date is not None else existing_progress.get('date')
    }
    with open(progress_file, 'w', encoding='utf-8') as f:
        json.dump(progress_data, f)

def load_step_progress():
    """加载上次保存的步骤进度"""
    import os
    import json
    progress_file = get_step_progress_file()
    if os.path.exists(progress_file):
        with open(progress_file, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                return data
            except json.JSONDecodeError:
                return {'step_name': None, 'date': None}
    return {'step_name': None, 'date': None}

def clear_step_progress():
    """清除步骤进度"""
    import os
    progress_file = get_step_progress_file()
    if os.path.exists(progress_file):
        os.remove(progress_file)

def get_local_download_dir():
    """获取本地下载目录路径"""
    return LOCAL_DOWNLOAD_DIR