from mysql_lib import MysqlController

db_connect_info = {
    "host":"localhost",
    "user":"admin",
    "passwd":"Asdfg123!",
    "database":"MANAGE_VM"}

db_controller = MysqlController(db_connect_info)

#db_cursor = db_connector.cursor()
query = "select * from information_schema.schemata"
db_cursor = db_controller.query_executor(query)
#mysql_lib.query_executor(db_cursor, query)

for raw in db_cursor:
    print(raw)