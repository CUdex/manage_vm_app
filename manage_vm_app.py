from mysql_lib import MysqlController
import vm_utils
import re
import time

#app.conf 파일에 있는 db정보를 가져오는 함수
def readAppInfo() -> dict:
    """
    app.conf 파일에서 동작에 필요한 설정들을 가져온다.
    """
    app_info = {}
    #정규식을 이용하여 필요한 정보만 dictionary array에 저장하기 위해 정규식 설정
    db_match = re.compile('^db|^limit')
    server_match = re.compile('^server|ignore')
    f = open('/etc/app.conf')
    readText = f.readlines()
    f.close()

    for line in readText:
        #db나 boot의 경우 string으로 ignore, serverip는 list로 저장해야 함
        if db_match.match(line):
            split_text = line.split("=")
            app_info[split_text[0]] = split_text[1].strip('\n')

        elif server_match.match(line):
            split_text = line.split("=")
            server_ip = split_text[1].split(',')
            app_info[split_text[0]] = server_ip
            app_info[split_text[0]][-1] = app_info[split_text[0]][-1].strip('\n')

    return app_info

def update_vm_idx(server_list, server_pass):
    vm_list = vm_utils.get_vm_id(server_list, server_pass)
    insert_query = "insert into vm_list(vm_name, vm_idx, vm_host_server) values"
    insert_data = []

    for name, value in vm_list.items():
        check_query = f"select 1 from vm_list where vm_name = '{name}'"
        
        if db_controller.query_executor(check_query):
            query = f"""update vm_list set vm_idx = '{value[0]}', 
            vm_host_server = '{value[1]}' 
            where vm_name = '{name}'"""
            
            db_controller.query_executor(query)
        else:
            insert_data.append(f"('{name}', '{value[0]}', '{value[1]}')")

    if insert_data:
        insert_query = insert_query + ",".join(insert_data)
        db_controller.query_executor(insert_query)

def update_server_info(server_list, server_pass):
    server_status = vm_utils.vm_server_status(server_list, server_pass)
    insert_query = "insert into vm_server(server_ip, server_cpu_percentage, server_memory_percentage, server_disk_percentage) values"
    insert_data = []

    for server_ip, value in server_status.items():
        check_db_server = f"select 1 from vm_server where server_ip = '{server_ip}'"

        if db_controller.query_executor(check_db_server):
            query = f"""update vm_server set server_cpu_percentage = '{value['cpu_percentage']}', 
            server_memory_percentage = '{value['memory_percentage']}',
            server_disk_percentage = '{value['disk_percentage']}' where server_ip = '{server_ip}'"""
            db_controller.query_executor(query)
            if value['memory_percentage'] > 90:
                over_trigger = {'reason' : 'over_memory', 'server_ip': server_ip}
                auto_stop(info['ignore_vm'],"", server_pass, over_trigger)
        else:
            insert_data.append(f"('{server_ip}', '{value['cpu_percentage']}', '{value['memory_percentage']}', '{value['disk_percentage']}')")

    if insert_data:
        insert_query = insert_query + ",".join(insert_data)
        db_controller.query_executor(insert_query)

#vm 상태 업데이트
def update_vm_status(server_pass):
    query = "select vm_name, vm_idx, vm_host_server from vm_list"
    vm_list = db_controller.query_executor(query)

    for vm in vm_list:
        vm_status = vm_utils.vm_status(vm['vm_idx'], vm['vm_host_server'], server_pass)

        if not vm_status:
            query = f"delete from vm_list where vm_idx = '{vm['vm_idx']}' and vm_host_server = '{vm['vm_host_server']}'"
        else:
            #쿼리문 powered의 경우 1이 on을 의미한다.
            query = f"""update vm_list set vm_use_memory = {int(vm_status['hostMemoryUsage']) / 1024}, 
            vm_use_cpu = {vm_status['overallCpuUsage']}, 
            vm_use_disk = {int(vm_status['committed']) / 1073741824}, 
            vm_boot_time = {vm_status['uptimeSeconds']},
            vm_powered = {0 if vm_status['uptimeSeconds'] == '0' else 1} 
            where vm_name = '{vm['vm_name']}'"""

        db_controller.query_executor(query)
    
#app.conf에 설정된 limit_boot_time을 초과한 vm 종료, trigger에 따라 memory 혹은 booting time
def auto_stop(ignore_vm, limit_boot_time, server_pass, trigger):

    ignore_list = ""
    for name in ignore_vm:
        ignore_list += f" and vm_name != '{name}'"

    # vm server 메모리 사용량이 90%가 넘어가면 정지 예외 vm을 제외한 메모리 소비 top vm을 정지하기 위한 query
    if trigger['reason'] == 'over_memory':
        #stop 할 vm 수
        number_of_stop_vm = 3
        #vm 쿼리
        query = f"select vm_name, vm_idx, vm_host_server from vm_list where vm_host_server = '{trigger['server_ip']}' {ignore_list} order by vm_use_memory desc limit {number_of_stop_vm}"        
    else:
        query = f"select vm_name, vm_idx, vm_host_server from vm_list where vm_boot_time >= {limit_boot_time}"
        query = query + ignore_list
    
    stop_list = db_controller.query_executor(query)

    for vm in stop_list:
        vm_utils.vm_stop(vm['vm_idx'], vm['vm_host_server'], server_pass)

#main 시작 부분
info = readAppInfo() 
db_controller = MysqlController(info)
main_trigger = {'reason': 'main'}

while True:
    try:
        update_server_info(info['server_ip'], info['server_pass'][0])
        update_vm_idx(info['server_ip'], info['server_pass'][0])
        update_vm_status(info['server_pass'][0])
        auto_stop(info['ignore_vm'],info['limit_boot_time'], info['server_pass'][0], main_trigger)  
    except ConnectionError as e:
        print(f"error: {e.args[0]}") 

    print("sleep start")
    time.sleep(180) 
    print("sleep end")