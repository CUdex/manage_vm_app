from mysql_lib import MysqlController
import vm_utils

def update_vm_idx():
    vm_list = vm_utils.get_vm_id(info['server_ip'])
    insert_query = "insert into view_vm_vm_list(vm_name, vm_idx, vm_host_server) values"
    insert_data = []

    for name, value in vm_list.items():
        check_query = f"select 1 from view_vm_vm_list where vm_name = '{name}'"
        if db_controller.query_executor(check_query):
            query = f"update view_vm_vm_list set vm_idx = '{value[0]}', vm_host_server = '{value[1]}' where vm_name = '{name}'"
            db_controller.query_executor(query)
        else:
            insert_data.append(f"('{name}', '{value[0]}', '{value[1]}')")

    if insert_data:
        insert_query = insert_query + ",".join(insert_data)
        db_controller.query_executor(insert_query)

def update_server_info(server_list):
    server_status = vm_utils.vm_server_status(server_list)
    print(0)



info = vm_utils.readAppInfo() 
db_controller = MysqlController(info)
update_vm_idx()


        

