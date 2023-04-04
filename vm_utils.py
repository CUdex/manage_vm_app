import subprocess
import re

# process list를 조회하여 power on 상태의 vm list 조회
def power_on_vm_list(server_list, server_pass) -> list:
    """
    esxi 서버의 esxcli vm process list 명령어를 통해 동작 중인 vm의 이름들을 가져옴
    """
    list = []

    for server in server_list:
        try:
            connect_server = "sshpass -p{} ssh root@{} ".format(server_pass, server)
            vm_list = subprocess.check_output(connect_server + "esxcli vm process list | grep \"Display Name\" | awk -F': ' '{print $2}'", shell=True).decode('utf-8')
            list += vm_list.split('\n')
            list.remove('')
        except:
            raise ConnectionError(f'vm server connect error, you might check vm server ip-{server} or password')
    
    return list

def vm_status(vm_id, server_ip, server_pass) -> dict:
    """
    vm의 status를 가져오는 함수로 여기서 vmid라는 vm 식별자를 통해 vm 정보를 조회하고 해당 자원 사용량 power 상태 등을 체크 가능 
    """
    try:
        result_resource = {}
        connect_server = "sshpass -p{} ssh root@{} ".format(server_pass, server_ip)
        cli_command = "vim-cmd vmsvc/get.summary {} | grep -i -E 'uptimeseconds|overallcpuusage|committed|hostmemoryusage' | grep -iv uncommitted | sed -E 's/,| //g'".format(vm_id)
        result_usage = subprocess.check_output(connect_server + cli_command, shell=True).decode('utf-8')
        result_usage = result_usage.splitlines()
    except:
        raise ConnectionError(f'vm server connect error, you might check vm server ip-{server_ip} or password')

    #해당 vm이 조회되지 않으면 빈 dict 반환
    if not result_usage:
        return {}

    for usage in result_usage:
        split_usage = usage.split('=')
        if split_usage[1] == '<unset>':
            split_usage[1] = '0'
        
        result_resource[split_usage[0]] = split_usage[1]

    return result_resource

def vm_server_status(server_list, server_pass):
    """
    vm 서버의 자원 사용량을 체크하기 위한 함수
    """
    server_resource = {}

    for server in server_list:
        try:
            ssh_server = "sshpass -p{} ssh root@{} ".format(server_pass, server)
            print(ssh_server)
            cpu_percentage = subprocess.check_output(ssh_server + "esxtop -n1 -b | awk -F',' '{print $6}' | tail -n 1 | sed 's/\"//g' | awk '{printf \"%d\", $1 * 100}'", shell=True).decode('utf-8')
            memory_percentage = subprocess.check_output(ssh_server + "vsish -e get /memory/comprehensive | grep -E \"Physical|Free\" | sed 's/ KB//g' | awk -F':' '{arr[i++]=$2} END {printf \"%d\", ((arr[0] - arr[1]) / arr[0] + 0.005) * 100}'", shell=True).decode('utf-8')
            disk_percentage = subprocess.check_output(ssh_server + "df | grep VMFS | awk '{max+=$2; use+=$3} END {printf \"%d\", (use / max + 0.005) * 100}'", shell=True).decode('utf-8')

            server_resource[server] = {"cpu_percentage": cpu_percentage, "memory_percentage": memory_percentage, "disk_percentage": disk_percentage}
        except:
            raise ConnectionError(f'vm server connect error, you might check vm server ip-{server} or password')

    return server_resource

def get_vm_id(server_list, server_pass):
    """
    vm index를 가져오는 함수
    """
    vm_list_dict = {}
    for server in server_list:
        ssh_server = "sshpass -p{} ssh root@{} ".format(server_pass, server)
        # VM 이름에 띄어쓰기가 있는 경우 
        vm_list = subprocess.check_output(ssh_server + "vim-cmd vmsvc/getallvms | grep -v Vmid", shell=True).decode('utf-8')
        vm_list = vm_list.split('\n')
        vm_list.remove('')

        #vmidx 와 name을 분리하고 server_ip 리스트로 딕셔너리 저장
        for line in vm_list:
            # 문자열에서 필요한 값을 추출합니다.
            vm_line_list = line.split(' ')
            vm_line_list = [x for x in vm_line_list if x != '']
            match_index = 1

            for list in vm_line_list:
                if re.match(r"^\[", list):
                    match_index = vm_line_list.index(list)
                    break

            value = vm_line_list[0]
            subset_key = vm_line_list[1:match_index]
            key = ' '.join(subset_key) + "-" + server.split('.')[-1]
            vm_list_dict[key] = [value, server]

    return vm_list_dict

def vm_stop(vm_idx, host_server, server_pass):
    try:
        subprocess.run(f"sshpass -p{server_pass} ssh root@{host_server} vim-cmd vmsvc/power.off {vm_idx}",shell=True)
    except:
        raise ConnectionError(f'vm server connect error, you might check vm server ip-{host_server} or password')