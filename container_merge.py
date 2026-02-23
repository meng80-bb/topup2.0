from topup_ssh import TopupSSH
import time

ssh = TopupSSH()
ssh.connect()

# 尝试使用容器合并图片
print('Merging PNG files using container...')
cmd = '''cd /besfs5/groups/cal/topup/round18/DataValid/Determining_ETS_cut/check_ETScut_CalibConst && /cvmfs/container.ihep.ac.cn/bin/hep_container shell SL6 << 'CONTAINER_EOF'
convert ./run*.png mergedd_ETS_checkall.pdf
exit
CONTAINER_EOF
'''

print(f'Executing command...')
result = ssh.execute_command(cmd, timeout=300)
print(f'Exit code: {result.get("exit_code", "N/A")}')
print(f'Success: {result.get("success", False)}')
if result.get('output'):
    print(f'Output:\n{result["output"]}')
if result.get('error'):
    print(f'Error: {result["error"]}')

# 检查是否生成了文件
time.sleep(2)
result = ssh.execute_command('ls -lh /besfs5/groups/cal/topup/round18/DataValid/Determining_ETS_cut/check_ETScut_CalibConst/mergedd_ETS_checkall.pdf 2>/dev/null')
print(f'\nChecking for merged file:')
print(result['output'])

ssh.close()