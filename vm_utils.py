import subprocess
import re
import manage_lib
import log_config

custom_log = log_config.CustomLog()
logger = custom_log.logger

# process list를 조회하여 power on 상태의 vm list 조회
def power_on_vm_list(server_list, server_pass) -> list:
    """
    esxi 서버의 esxcli vm process list 명령어를 통해 동작 중인 vm의 이름들을 가져옴
    """
    list = []

    for server in server_list:
        try:
            connect_server = ['sshpass', '-p',f'{server_pass}', 'ssh', '-o StrictHostKeyChecking=no', '-o ConnectTimeout=3', f'root@{server}']
            get_vm_cmd = ["esxcli vm process list | grep \"Display Name\" | awk -F': ' '{print $2}'"]
            vm_list = subprocess.check_output(connect_server + get_vm_cmd).decode('utf-8')
            list += vm_list.split('\n')
            list.remove('')
        except:
            error_message = 'fail update vm list'
            logger.error(error_message)
            raise ConnectionError(error_message)
    logger.info('sucess get vm list')
    return list

def vm_status(vm_id, server_ip, server_pass) -> dict:
    """
    vm의 status를 가져오는 함수로 여기서 vmid라는 vm 식별자를 통해 vm 정보를 조회하고 해당 자원 사용량 power 상태 등을 체크 가능 
    """
    try:
        result_resource = {}
        connect_server = ['sshpass', '-p',f'{server_pass}', 'ssh', '-o StrictHostKeyChecking=no', '-o ConnectTimeout=3', f'root@{server_ip}']
        cli_command = [f"vim-cmd vmsvc/get.summary {vm_id} | grep -i -E 'uptimeseconds|overallcpuusage|committed|hostmemoryusage' | grep -iv uncommitted | sed -E 's/,| //g'"]
        result_usage = subprocess.check_output(connect_server + cli_command).decode('utf-8')
        result_usage = result_usage.splitlines()
    except:
        error_message = 'fail get vm status'
        logger.error(error_message)
        raise ConnectionError(error_message)

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
            ssh_server = ['sshpass', '-p',f'{server_pass}', 'ssh', '-o StrictHostKeyChecking=no', '-o ConnectTimeout=3', f'root@{server}']
            
            get_cpu_cmd = ["esxtop -n1 -b | awk -F',' '{print $6}' | tail -n 1 | sed 's/\"//g' | awk '{printf \"%d\", $1 * 100}'"]
            cpu_percentage = subprocess.check_output(ssh_server + get_cpu_cmd).decode('utf-8')
            
            get_memory_cmd = ["vsish -e get /memory/comprehensive | grep -E \"Physical|Free\" | sed 's/ KB//g' | awk -F':' '{arr[i++]=$2} END {printf \"%d\", ((arr[0] - arr[1]) / arr[0] + 0.005) * 100}'"]
            memory_percentage = subprocess.check_output(ssh_server + get_memory_cmd).decode('utf-8')
            
            get_disk_cmd = ["df | grep VMFS | awk '{max+=$2; use+=$3} END {printf \"%d\", (use / max + 0.005) * 100}'"]
            disk_percentage = subprocess.check_output(ssh_server + get_disk_cmd).decode('utf-8')

            server_resource[server] = {"cpu_percentage": cpu_percentage, "memory_percentage": memory_percentage, "disk_percentage": disk_percentage}
        except:
            error_message = 'fail get server status'
            logger.error(error_message)
            raise ConnectionError(error_message)
    logger.info('suceess get server status')
    return server_resource

def get_vm_id(server_list, server_pass):
    """
    vm index를 가져오는 함수
    """
    vm_list_dict = {}
    for server in server_list:
        ssh_server = ['sshpass', '-p',f'{server_pass}', 'ssh', '-o StrictHostKeyChecking=no', '-o ConnectTimeout=3', f'root@{server}']
        # VM 이름에 띄어쓰기가 있는 경우
        get_vm_list_id_cmd = ["vim-cmd vmsvc/getallvms | grep -v Vmid"]
        vm_list = subprocess.check_output(ssh_server + get_vm_list_id_cmd).decode('utf-8')
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
    
    logger.info('success get vm id list')
    return vm_list_dict

def vm_stop(vm_idx, host_server, server_pass):
    try:
        ssh_server = ['sshpass', '-p',f'{server_pass}', 'ssh', '-o StrictHostKeyChecking=no', '-o ConnectTimeout=3', f'root@{host_server}']
        vm_stop_cmd = [f"vim-cmd vmsvc/power.off {vm_idx}"]
        subprocess.run(ssh_server + vm_stop_cmd)
    except:
        logger.error('fail vm stop')
        raise ConnectionError()
    
def on_off_vm(order_info):
    """
    socket server에서 on/off 명령을 받으면 수행하는 함수
    """
    if not order_info:
        return 'empty order info'
    # 서버 operation에 필요한 변수 바인딩
    server = order_info['server']
    server_pass = order_info['server_pass']
    vm_id = order_info['vm_id']
    oper = order_info['oper']
    
    #manage web에서 가지고 있는 패스워드 정보 검증
    pass_info = manage_lib.readAppInfo()
    pass_info = pass_info['server_pass']

    if server_pass != pass_info:
        logger.error('password fail, please check your app.conf file')
        return 'fail to Invalid password, please check your app.conf file'
    
    try:
        logger.info('start connection to ESXI server')
        connect_server = ['sshpass', '-p',f'{server_pass}', 'ssh', '-o StrictHostKeyChecking=no', '-o ConnectTimeout=3', f'root@{server}']
        oper_cmd = [f'vim-cmd vmsvc/power.{oper} {vm_id}']
        result = subprocess.check_output(connect_server + oper_cmd).decode('utf-8').strip('\n')
        if result == 'Powering off VM:' or result == 'Powering on VM:':
            message = f'success {oper} {vm_id} {server}'
            return message
    
    #return code가 ssh가 정상 연결에서 명령 수행 결과가 fail이면 1이 리턴되고 그외 timeout이나 패스워드 오류의 경우 5, 255 에러코드가 나옴
    except subprocess.CalledProcessError as e:
        if e.returncode != 1:
            raise ConnectionError()
        else:
            return f'fail your {oper} order to {server}'