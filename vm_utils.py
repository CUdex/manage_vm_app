import re
import subprocess

#app.conf 파일에 있는 db정보를 가져오는 함수
def readAppInfo(want = 'all') -> dict:
    app_info = {}
    #정규식을 이용하여 필요한 정보만 dictionary array에 저장하기 위해 정규식 설정
    db_match = re.compile('^db')
    server_match = re.compile('^server')
    f = open('/etc/app.conf')
    readText = f.readlines()
    f.close()

    for line in readText:
        #원하는 정보만 딕셔너리로 리턴
        if db_match.match(line) and (want == 'db' or want == 'all'):
            split_text = line.split("=")
            app_info[split_text[0]] = split_text[1].strip('\n')

        elif server_match.match(line) and (want == 'server_ip' or want == 'all'):
            split_text = line.split("=")
            server_ip = split_text[1].split(",")
            app_info[split_text[0]] = server_ip
            app_info[split_text[0]][-1] = app_info[split_text[0]][-1].strip('\n')

    
    return app_info

# process list를 조회하여 power on 상태의 vm list 조회
def power_on_vm_list(server_list) -> list:
    list = []

    for server in server_list:
        test = subprocess.check_output("ssh root@%s esxcli vm process list | grep \"Display Name\" | awk -F': ' '{print $2}'" % server, shell=True).decode('utf-8')
        list += test.split('\n')
        list.remove('')
    
    return list