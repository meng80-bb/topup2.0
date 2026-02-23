#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
步骤7：运行reset.sh脚本
进入INJ_SIG_TIME_CAL_DIR目录并执行./reset.sh脚本

---
reset.sh脚本内容：
#!/bin/bash

#ntuplePath=`wk`
date=`date +%y%m%d`
ntuplePath=`pwd`

cp interval.txt InjSigIntervalCal/${date}

#cd ${ntuplePath}/calibConst
#mv *.root period

cd ${ntuplePath}/Interval_plot
mv *.png  tmp/
#rm merged.pdf -f

cd ${ntuplePath}/../hist
mv hist*.root tmp/
rm *.png

cd ${ntuplePath}/../plot
mv run*  tmp
mv *.png tmp

cd ${ntuplePath}/../Determining_50Hz_cut/search_peak
#mv output*      tmp
mv run*	    tmp/
mv shield_run*  raw_shield
cp window.dat   time_final/${date}
#cp log ../ShieldConst/${date}

cd ${ntuplePath}/../Determining_50Hz_cut/checkShieldCalib
mv run*  tmp/
mv *pdf  tmp/
#mv before_cut/*       tmp
#mv after_cut/*        tmp
#mv check_detail/*     tmp
#mv cut_detail/*.png   tmp
#mv before_cut/*       backup/png_backup/before_cut
#mv after_cut/*        backup/png_backup/after_cut
#mv check_detail/*     backup/png_backup/check_detail
#mv cut_detail/*.png   backup/png_backup/cut_detail

cd ${ntuplePath}/../Determining_ETS_cut/ETS_cut
mv plot_ETS_*  tmp
mv run*        tmp
#mv run*.root   period
mv shield*     tmp
cp ets_cut.txt ../ETScutCalibConst/${date}

cd ${ntuplePath}/../Determining_ETS_cut/check_ETScut_CalibConst
mv ETScut_check_*     tmp
mv run*.png           tmp
mv run*.root          tmp

cd ${ntuplePath}/   #go back to wk

echo "done"
---
"""

from typing import Dict, Any
from topup_ssh import TopupSSH
import config


def step7_run_reset_script(ssh: TopupSSH) -> Dict[str, Any]:
    """
    进入INJ_SIG_TIME_CAL_DIR目录并执行./reset.sh脚本

    Args:
        ssh: SSH连接实例

    Returns:
        dict: 执行结果
    """
    print("\n" + "="*60)
    print("步骤7：运行reset.sh脚本")
    print("="*60)

    try:
        # 进入INJ_SIG_TIME_CAL_DIR目录并执行reset.sh脚本
        print(f"\n进入目录 {config.INJ_SIG_TIME_CAL_DIR} 并执行reset.sh脚本...")
        result = ssh.execute_command(f"cd {config.INJ_SIG_TIME_CAL_DIR} && ./reset.sh", use_pty=False)

        if not result['success']:
            return {
                'success': False,
                'message': '执行reset.sh脚本失败',
                'step_name': '步骤7：运行reset.sh脚本',
                'output': result['output'],
                'error': result.get('error', '')
            }

        print(f"\n✓ reset.sh脚本执行成功")
        print(f"输出:\n{result['output']}")

        return {
            'success': True,
            'message': 'reset.sh脚本执行成功',
            'step_name': '步骤7：运行reset.sh脚本',
            'output': result['output']
        }

    except Exception as e:
        return {
            'success': False,
            'message': f'执行reset.sh脚本异常: {str(e)}',
            'step_name': '步骤7：运行reset.sh脚本',
            'error': str(e)
        }


if __name__ == "__main__":
    # 测试步骤7
    with TopupSSH() as ssh:
        if ssh.connected:
            result = step7_run_reset_script(ssh)
            print("\n" + "="*60)
            print("步骤7执行结果:")
            print("="*60)
            print(f"成功: {result['success']}")
            print(f"消息: {result['message']}")
