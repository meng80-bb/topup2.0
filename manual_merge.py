from topup_ssh import TopupSSH

ssh = TopupSSH()
ssh.connect()

# 检查是否有run*.png文件
result = ssh.execute_command('ls /besfs5/groups/cal/topup/round18/DataValid/Determining_ETS_cut/check_ETScut_CalibConst/run*.png 2>/dev/null | head -5')
print(f'run*.png files (first 5):')
print(result['output'])

# 尝试手动合并
print('\nAttempting manual merge...')
result = ssh.execute_command('cd /besfs5/groups/cal/topup/round18/DataValid/Determining_ETS_cut/check_ETScut_CalibConst && ls run*.png | wc -l')
print(f'Total run*.png files: {result["output"].strip()}')

ssh.close()