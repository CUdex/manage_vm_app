import mysql.connector

class MysqlController:

    #인스턴스 생성 시 mysql connect 진행
    def __init__(self, param):
        self.db_init(param)
        try:
            self.db_connector = mysql.connector.connect(host=param['db_host'], port='3306', database=param['db_database'], user=param['db_user'], password=param['db_passwd'])
            self.db_create_table(self.db_connector)
        except:
            raise ConnectionError('DB connect error')

    def __del__(self):
        self.db_connector.close()

    #쿼리문 실행
    def query_executor(self, query):
        cursor = self.db_connector.cursor(dictionary=True)
        cursor.execute(query)
        
        if query[0] == 's':
            result = cursor.fetchall()
            cursor.close()
            return result

        self.db_connector.commit()
        cursor.close()

    #DB 미존재 시 MANAGE_VM DB 생성
    def db_init(self, param):
        try:
            db_connector = mysql.connector.connect(host=param['db_host'], port='3306', user=param['db_user'], password=param['db_passwd'])
            cursor = db_connector.cursor(dictionary=True)
            query = f"CREATE DATABASE IF NOT EXISTS {param['db_database']};"
            cursor.execute(query)
            db_connector.close()
        except:
            raise ConnectionError('DB init error')

    def db_create_table(self, connector):
        cursor = connector.cursor(dictionary=True)
        query = "select 1 from information_schema.tables where table_name = 'vm_server'"
        cursor.execute(query)
        result = cursor.fetchall()

        if not result:
            create_server_table = """CREATE TABLE vm_server(server_ip VARCHAR(20), 
            server_cpu_percentage TINYINT(1) UNSIGNED NOT NULL, 
            server_memory_percentage TINYINT(1) UNSIGNED NOT NULL, 
            server_disk_percentage TINYINT(1) UNSIGNED NOT NULL, 
            CONSTRAINT vm_server_PK PRIMARY KEY(server_ip));"""
            
            create_list_table = """CREATE TABLE vm_list(vm_name VARCHAR(100) COLLATE utf8_bin, 
            vm_idx VARCHAR(5) NOT NULL, 
            vm_use_memory INT(1) UNSIGNED NULL, 
            vm_use_cpu INT(1) UNSIGNED NULL, 
            vm_use_disk INT(1) UNSIGNED NULL, 
            vm_boot_time INT(1) UNSIGNED NULL, 
            vm_powered BOOL NULL, 
            vm_host_server VARCHAR(20), 
            CONSTRAINT vm_list_PK PRIMARY KEY(vm_name), 
            CONSTRAINT FOREIGN KEY (vm_host_server) REFERENCES vm_server(server_ip) ON DELETE CASCADE);"""
            
            cursor.execute(create_server_table)
            cursor.execute(create_list_table)
            
            connector.commit()
        
        cursor.close()
