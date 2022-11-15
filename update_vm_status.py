from mysql_lib import MysqlController
import vm_utils

# app_info = readAppInfo()
# db_controller = MysqlController(app_info)
# query = "select * from information_schema.schemata" #테스트용 쿼리
# db_cursor = db_controller.query_executor(query)
#def all_vm_list(server_list):

info = vm_utils.readAppInfo() 
print(vm_utils.power_on_vm_list(info["server_ip"]))



