import re
import subprocess

#app.conf 파일에 있는 db정보를 가져오는 함수
def readAppInfo(want = 'all') -> dict:
    """
    app.conf 파일에서 필요한 정보를 딕셔너리 형태로 반환하는 함수, want parameter를 통해 db, server_ip 두개 중 원하는 정보만 가져올 수 있음
    """
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
    """
    esxi 서버의 esxcli vm process list 명령어를 통해 동작 중인 vm의 이름들을 가져옴
    """
    list = []

    for server in server_list:
        test = subprocess.check_output("ssh root@%s esxcli vm process list | grep \"Display Name\" | awk -F': ' '{print $2}'" % server, shell=True).decode('utf-8')
        list += test.split('\n')
        list.remove('')
    
    return list

def vm_status(vm_id, server_ip):
    """
    vm의 status를 가져오는 함수로 여기서 vmid라는 vm 식별자를 통해 vm 정보를 조회하고 해당 자원 사용량 power 상태 등을 체크 가능 
    """
    print(vm_id)

def vm_server_status(server_ip):
    """
    vm 서버의 자원 사용량을 체크하기 위한 함수
    """
    print(server_ip)

def get_vm_id(server_list):
    """
    vm index를 가져오는 함수
    """
    vm_list_dict = {}
    for server in server_list:
        vm_list = subprocess.check_output("ssh root@%s vim-cmd vmsvc/getallvms | grep -v Vmid | awk '{print $1, $2}'" % server, shell=True).decode('utf-8')
        vm_list = vm_list.split('\n')
        vm_list.remove('')

        #vmidx 와 name을 분리하고 server_ip 리스트로 딕셔너리 저장
        for vm in vm_list:
            vm_index_name = vm.split(' ')
            vm_list_dict[vm_index_name[1]] = [vm_index_name[0], server]

    return vm_list_dict