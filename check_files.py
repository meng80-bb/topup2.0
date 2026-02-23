from topup_ssh import TopupSSH

ssh = TopupSSH()
ssh.connect()
result = ssh.execute_command('ls /besfs5/groups/cal/topup/round18/DataValid/Determining_ETS_cut/check_ETScut_CalibConst/*.png /besfs5/groups/cal/topup/round18/DataValid/Determining_ETS_cut/check_ETScut_CalibConst/*.root 2>/dev/null | wc -l')
print(f'Generated files count: {result["output"].strip()}')
ssh.close()